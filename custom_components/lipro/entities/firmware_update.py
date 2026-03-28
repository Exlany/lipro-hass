"""Firmware update entity for Lipro integration."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
import logging
from time import monotonic
from typing import TYPE_CHECKING, TypedDict

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

from .. import firmware_manifest
from ..const.base import DOMAIN
from ..core import LiproApiError
from ..core.ota.candidate import (
    _OtaCandidate,
    build_candidate,
    consume_confirmation,
    evaluate_install,
    has_pending_confirmation,
    project_candidate,
)
from ..core.ota.row_selector import (
    OtaDeviceFingerprint,
    OtaRow,
    build_device_fingerprint,
)
from ..core.ota.rows_cache import (
    OtaRowsCacheKey,
    async_select_row_with_shared_cache,
    build_ota_rows_cache_key,
    normalize_ota_rows,
)
from ..core.utils.log_safety import safe_error_placeholder
from ..entities.base import LiproEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from ..core.device import LiproDevice
    from ..runtime_types import LiproRuntimeCoordinator

_LOGGER = logging.getLogger(__name__)

_OTA_REFRESH_INTERVAL = timedelta(hours=6)
_UNVERIFIED_CONFIRM_WINDOW_SECONDS = 120
_TIME_MIN_UTC = datetime.min.replace(tzinfo=UTC)
_OTA_REFRESH_CONCURRENCY = 3
_OTA_REFRESH_SEMAPHORE = asyncio.Semaphore(_OTA_REFRESH_CONCURRENCY)

class FirmwareStateAttributes(TypedDict, total=False):
    """Typed extra-state projection exposed by the firmware entity."""

    certified: bool
    confirmation_required: bool
    ota_checked_at: str
    last_error: str
    last_error_type: str


class LiproFirmwareUpdateEntity(LiproEntity, UpdateEntity):
    """Firmware update entity for one Lipro device."""

    _attr_translation_key = "firmware"
    _attr_name = None
    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _entity_suffix = "firmware"
    _attr_supported_features = UpdateEntityFeature.INSTALL

    def __init__(
        self,
        coordinator: LiproRuntimeCoordinator,
        device: LiproDevice,
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        """Initialize firmware update entity."""
        super().__init__(coordinator, device, self._entity_suffix)
        self._ota_candidate: _OtaCandidate | None = None
        self._last_ota_refresh = _TIME_MIN_UTC
        self._ota_refresh_task: asyncio.Task[None] | None = None
        self._on_error = on_error
        self._last_error: Exception | None = None
        self._unverified_confirm_until = 0.0
        self._attr_installed_version = device.network_info.firmware_version
        self._attr_latest_version = device.network_info.firmware_version
        self._attr_in_progress = False

    @property
    def last_error(self) -> Exception | None:
        """Return the last background OTA refresh exception, if any."""
        return self._last_error

    @property
    def extra_state_attributes(self) -> FirmwareStateAttributes:
        """Expose OTA metadata for advanced users."""
        attrs: FirmwareStateAttributes = {
            "certified": self._ota_candidate.certified if self._ota_candidate else False,
            "confirmation_required": self._has_pending_unverified_confirmation(),
        }

        if self._last_ota_refresh != _TIME_MIN_UTC:
            attrs["ota_checked_at"] = self._last_ota_refresh.isoformat()
        if self._last_error is not None:
            attrs["last_error"] = safe_error_placeholder(self._last_error)
            attrs["last_error_type"] = type(self._last_error).__name__
        return attrs

    async def async_added_to_hass(self) -> None:
        """Schedule initial OTA metadata refresh."""
        await super().async_added_to_hass()
        await asyncio.to_thread(firmware_manifest.load_verified_firmware_manifest)
        self._schedule_ota_refresh(force=True)

    async def async_will_remove_from_hass(self) -> None:
        """Cancel OTA refresh task when entity is removed."""
        task = self._ota_refresh_task
        if task is not None and not task.done():
            task.cancel()
            result = await asyncio.gather(task, return_exceptions=True)
            err = self._consume_wait_result(result[0])
            if err is not None:
                _LOGGER.debug(
                    "OTA refresh task failed during removal (%s)",
                    safe_error_placeholder(err),
                )
        self._ota_refresh_task = None
        await super().async_will_remove_from_hass()

    def _handle_coordinator_update(self) -> None:
        """React to coordinator updates and refresh OTA metadata lazily."""
        self._attr_installed_version = self.device.network_info.firmware_version
        self._schedule_ota_refresh(force=False)
        super()._handle_coordinator_update()

    async def async_update(self) -> None:
        """Force refresh OTA metadata."""
        await self._async_refresh_ota(force=True)

    async def async_install(
        self,
        version: str | None,
        backup: bool,
        **kwargs: object,
    ) -> None:
        """Install firmware update."""
        del backup, kwargs
        command, properties = await self._async_prepare_install_command(version)
        await self._async_execute_install_command(
            command=command,
            properties=properties,
        )

    async def _async_prepare_install_command(
        self,
        requested_version: str | None,
    ) -> tuple[str, list[dict[str, str]] | None]:
        """Refresh OTA state and return one validated install command payload."""
        await self._async_refresh_ota(force=True)

        install_eval = evaluate_install(
            self._ota_candidate,
            requested_version=requested_version,
            confirm_until=self._unverified_confirm_until,
            now_monotonic=asyncio.get_running_loop().time(),
            confirmation_window_seconds=_UNVERIFIED_CONFIRM_WINDOW_SECONDS,
        )
        self._unverified_confirm_until = install_eval.confirm_until
        if install_eval.error_key is not None:
            self._raise_install_error(
                install_eval.error_key,
                placeholders=install_eval.error_placeholders,
            )

        install_command = install_eval.install_command
        if install_command is None:
            raise self._build_translated_error("firmware_install_unsupported")
        return install_command.command, install_command.properties

    def _raise_install_error(
        self,
        translation_key: str,
        *,
        placeholders: dict[str, str] | None = None,
    ) -> None:
        """Raise one translated install error after updating observable state."""
        if translation_key == "firmware_unverified_confirm_required":
            self.async_write_ha_state()
        raise self._build_translated_error(
            translation_key,
            placeholders=placeholders,
        )

    async def _async_execute_install_command(
        self,
        *,
        command: str,
        properties: list[dict[str, str]] | None,
    ) -> None:
        """Execute one validated firmware install command and refresh state."""
        self._attr_in_progress = True
        self.async_write_ha_state()
        try:
            success = await self.coordinator.async_send_command(
                self.device,
                command,
                properties,
            )
            if not success:
                raise self._build_translated_error("firmware_install_failed")

            self._unverified_confirm_until = 0.0
            await self.coordinator.async_request_refresh()
            await self._async_refresh_ota(force=True)
        finally:
            self._attr_in_progress = False
            self.async_write_ha_state()

    def _schedule_ota_refresh(self, *, force: bool) -> None:
        """Schedule OTA refresh in background."""
        if not force and not self._should_refresh_ota():
            return
        if self._ota_refresh_task is not None and not self._ota_refresh_task.done():
            return

        task = self.hass.async_create_task(self._async_refresh_ota(force=force))
        self._ota_refresh_task = task
        task.add_done_callback(self._async_finalize_refresh_task)

    def _async_finalize_refresh_task(self, task: asyncio.Task[None]) -> None:
        """Finalize background OTA refresh task with observable error state."""
        if self._ota_refresh_task is task:
            self._ota_refresh_task = None

        err = self._async_clear_refresh_task(task)
        if err is None:
            return

        self._set_last_error(err)
        self.async_write_ha_state()

    @staticmethod
    def _consume_wait_result(result: object) -> Exception | None:
        """Normalize gather(return_exceptions=True) output into an exception."""
        if isinstance(result, asyncio.CancelledError):
            return None
        return result if isinstance(result, Exception) else None

    @staticmethod
    def _async_clear_refresh_task(task: asyncio.Task[None]) -> Exception | None:
        """Consume task exception to avoid warning logs."""
        try:
            err = task.exception()
        except asyncio.CancelledError:
            return None
        if isinstance(err, Exception):
            _LOGGER.debug(
                "Background OTA refresh task failed (%s)",
                safe_error_placeholder(err),
            )
            return err
        return None

    def _set_last_error(self, err: Exception) -> None:
        """Persist last async exception and notify optional observer."""
        self._last_error = err
        if self._on_error is None:
            return
        try:
            self._on_error(err)
        except (
            AttributeError,
            LookupError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as callback_err:
            _LOGGER.error(
                "OTA error callback failed (%s)",
                safe_error_placeholder(callback_err),
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )

    def _clear_last_error(self) -> None:
        """Clear persisted async exception state."""
        self._last_error = None

    def _should_refresh_ota(self) -> bool:
        """Return True when OTA metadata is stale."""
        return dt_util.utcnow() - self._last_ota_refresh >= _OTA_REFRESH_INTERVAL

    def _ota_rows_cache_key(self) -> OtaRowsCacheKey:
        """Build a shared OTA rows cache key scoped by model-like identifiers."""
        return build_ota_rows_cache_key(
            self.coordinator,
            device_type=self.device.device_type_hex,
            iot_name=self.device.iot_name,
            product_id=self.device.product_id,
        )

    def _ota_device_fingerprint(self) -> OtaDeviceFingerprint:
        """Return the normalized fingerprint used for OTA row selection."""
        return build_device_fingerprint(
            serial=self.device.serial,
            device_type=self.device.device_type_hex,
            iot_name=self.device.iot_name,
            product_id=self.device.product_id,
            physical_model=self.device.physical_model,
        )

    async def _query_ota_rows_from_cloud(self) -> list[OtaRow]:
        """Query OTA rows once and normalize unknown payload variants."""
        rows = await self.coordinator.async_query_device_ota_info(
            self.device,
            allow_rich_v2_fallback=self.device.capabilities.is_light,
        )
        return normalize_ota_rows(rows)

    async def _async_refresh_ota(self, *, force: bool) -> None:
        """Refresh OTA metadata from cloud."""
        if not force and not self._should_refresh_ota():
            return

        async with _OTA_REFRESH_SEMAPHORE:
            try:
                selected_row = await async_select_row_with_shared_cache(
                    self._ota_rows_cache_key(),
                    fetcher=self._query_ota_rows_from_cloud,
                    now=dt_util.utcnow,
                    fingerprint=self._ota_device_fingerprint(),
                )
            except LiproApiError as err:
                _LOGGER.debug(
                    "Failed to refresh OTA info for %s: %s",
                    self.device.serial,
                    err,
                )
                self._set_last_error(err)
                self.async_write_ha_state()
                return

            self._ota_candidate = build_candidate(
                selected_row,
                device_firmware_version=self.device.network_info.firmware_version,
                device_iot_name=self.device.iot_name,
                local_manifest=firmware_manifest.load_verified_firmware_manifest(),
                is_version_newer=self._is_version_newer,
            )
            self._apply_ota_candidate()
            self._clear_last_error()
            self._last_ota_refresh = dt_util.utcnow()
            self.async_write_ha_state()

    def _apply_ota_candidate(self) -> None:
        """Apply candidate values to update-entity attributes."""
        projection = project_candidate(
            self._ota_candidate,
            current_installed_version=self.device.network_info.firmware_version,
        )
        self._attr_release_summary = projection.release_summary
        self._attr_release_url = projection.release_url
        self._attr_installed_version = projection.installed_version
        self._attr_latest_version = projection.latest_version

    def _is_version_newer(self, candidate: str, current: str) -> bool:
        """Compare versions with HA helper, fallback to conservative False."""
        try:
            return self.version_is_newer(candidate, current)
        except (ValueError, TypeError) as err:
            _LOGGER.debug(
                "Unable to compare certification versions (%s -> %s): %s",
                current,
                candidate,
                err,
            )
            return False

    def _has_pending_unverified_confirmation(self) -> bool:
        """Return True if unverified install confirmation is active."""
        return has_pending_confirmation(
            self._unverified_confirm_until,
            now_monotonic=monotonic(),
        )

    def _consume_unverified_confirmation(self) -> bool:
        """Consume current unverified confirmation window if still active."""
        consumed, confirm_until = consume_confirmation(
            self._unverified_confirm_until,
            now_monotonic=monotonic(),
        )
        self._unverified_confirm_until = confirm_until
        return consumed

    @staticmethod
    def _build_translated_error(
        translation_key: str,
        *,
        placeholders: dict[str, str] | None = None,
    ) -> HomeAssistantError:
        """Build one Home Assistant translated error instance."""
        if placeholders is None:
            return HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key=translation_key,
            )
        return HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key=translation_key,
            translation_placeholders=placeholders,
        )
