"""Firmware update platform for Lipro integration."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import functools
import logging
from pathlib import Path
from time import monotonic
from typing import TYPE_CHECKING, Any

import aiohttp

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .core import LiproApiError
from .core.ota_utils import (
    build_manifest_type_candidates as _build_manifest_type_candidates,
    extract_install_command as _extract_install_command,
    extract_version_set as _extract_version_set,
    first_bool as _first_ota_bool,
    first_text as _first_ota_text,
    load_verified_firmware_manifest_file as _load_verified_firmware_manifest_file,
    matches_certified_versions as _ota_matches_certified_versions,
    matches_manifest_certification as _matches_manifest_certification,
    parse_verified_firmware_manifest_payload as _parse_verified_firmware_manifest_payload,
)
from .entities.base import LiproEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry
    from .core.coordinator import LiproDataUpdateCoordinator
    from .core.device import LiproDevice

_LOGGER = logging.getLogger(__name__)

# Query OTA metadata at a low frequency to avoid extra cloud load.
_OTA_REFRESH_INTERVAL = timedelta(hours=6)
_UNVERIFIED_CONFIRM_WINDOW_SECONDS = 120
_TIME_MIN_UTC = datetime.min.replace(tzinfo=UTC)
_FIRMWARE_SUPPORT_MANIFEST = "firmware_support_manifest.json"
_REMOTE_MANIFEST_CACHE_TTL = timedelta(minutes=30)
_REMOTE_MANIFEST_TIMEOUT_SECONDS = 5
_REMOTE_FIRMWARE_SUPPORT_URLS = (
    "https://lipro-share.lany.me/api/firmware-support",
    "https://lipro-share.lany.me/firmware_support_manifest.json",
)

_SERIAL_KEYS = ("deviceId", "serial", "iotId")
_DEVICE_TYPE_KEYS = (
    "deviceType",
    "iotType",
    "type",
    "fingerprint",
    "deviceFingerprint",
)
_IOT_NAME_KEYS = ("iotName", "fwIotName")
_PRODUCT_ID_KEYS = ("productId", "productID", "pid")
_PHYSICAL_MODEL_KEYS = ("physicalModel", "model", "productModel")
_LATEST_VERSION_KEYS = (
    "latestVersion",
    "latestFirmwareVersion",
    "targetVersion",
    "upgradeVersion",
)
_CURRENT_VERSION_KEYS = ("currentVersion", "currentFirmwareVersion")
_COMMON_VERSION_KEYS = ("firmwareVersion", "version")
_UPDATE_FLAG_KEYS = ("needUpgrade", "upgradeAvailable", "hasUpgrade", "hasUpdate")
_CERTIFIED_FLAG_KEYS = (
    "certified",
    "isCertified",
    "authPassed",
    "isAuthPassed",
    "approved",
)
_CERTIFIED_VERSION_KEYS = (
    "certifiedVersions",
    "certifiedVersionList",
    "certificationList",
    "authVersionList",
)
_RELEASE_SUMMARY_KEYS = ("releaseNotes", "releaseSummary", "description")
_RELEASE_URL_KEYS = ("releaseUrl", "releaseNoteUrl", "changelogUrl")
_COMMAND_CONTAINER_KEYS = (
    "upgradeCommand",
    "installCommand",
    "commandPayload",
    "upgradePayload",
)
_COMMAND_KEYS = ("command", "cmd", "name")
_COMMAND_PROPERTIES_KEYS = ("properties", "params", "arguments", "payload")
_OTA_MATCH_SCORE_SERIAL_EXACT = 8
_OTA_MATCH_SCORE_BLE_NAME_EXACT = 6
_OTA_MATCH_SCORE_DEVICE_TYPE_EXACT = 4
_OTA_MATCH_SCORE_IOT_NAME_EXACT = 3
_OTA_MATCH_SCORE_PRODUCT_ID_EXACT = 3
_OTA_MATCH_SCORE_PHYSICAL_MODEL_EXACT = 2
_OTA_MATCH_SCORE_HAS_VERSION = 1

type _RemoteManifestData = tuple[frozenset[str], dict[str, frozenset[str]]]


@dataclass(slots=True)
class _RemoteManifestState:
    """Remote firmware manifest cache state."""

    time: datetime
    data: _RemoteManifestData


_REMOTE_MANIFEST_STATE = _RemoteManifestState(
    time=_TIME_MIN_UTC,
    data=(frozenset(), {}),
)
_REMOTE_MANIFEST_LOCK = asyncio.Lock()


@dataclass(slots=True)
class _InstallCommand:
    """Normalized install command payload."""

    command: str
    properties: list[dict[str, str]] | None


@dataclass(slots=True)
class _OtaCandidate:
    """Normalized OTA candidate metadata."""

    installed_version: str | None
    latest_version: str | None
    update_available: bool
    certified: bool
    release_summary: str | None
    release_url: str | None
    install_command: _InstallCommand | None


@functools.lru_cache(maxsize=1)
def _load_verified_firmware_manifest() -> tuple[
    frozenset[str], dict[str, frozenset[str]]
]:
    """Load optional local firmware certification manifest."""
    manifest_path = Path(__file__).with_name(_FIRMWARE_SUPPORT_MANIFEST)
    return _load_verified_firmware_manifest_file(
        manifest_path,
        on_error=lambda path, err: _LOGGER.debug(
            "Failed to load firmware support manifest %s: %s",
            path,
            err,
        ),
    )


async def _load_remote_firmware_manifest(
    hass: HomeAssistant,
) -> tuple[frozenset[str], dict[str, frozenset[str]]]:
    """Load firmware certification manifest from remote service with cache."""
    now = dt_util.utcnow()
    cached_time = _REMOTE_MANIFEST_STATE.time
    cached_data = _REMOTE_MANIFEST_STATE.data
    if now - cached_time < _REMOTE_MANIFEST_CACHE_TTL:
        return cached_data

    async with _REMOTE_MANIFEST_LOCK:
        now = dt_util.utcnow()
        cached_time = _REMOTE_MANIFEST_STATE.time
        cached_data = _REMOTE_MANIFEST_STATE.data
        if now - cached_time < _REMOTE_MANIFEST_CACHE_TTL:
            return cached_data

        session = async_get_clientsession(hass)
        timeout = aiohttp.ClientTimeout(total=_REMOTE_MANIFEST_TIMEOUT_SECONDS)
        for url in _REMOTE_FIRMWARE_SUPPORT_URLS:
            try:
                async with session.get(url, timeout=timeout) as response:
                    if response.status != 200:
                        continue
                    payload = await response.json(content_type=None)
            except (aiohttp.ClientError, TimeoutError, ValueError) as err:
                _LOGGER.debug(
                    "Remote firmware manifest fetch failed from %s: %s", url, err
                )
                continue

            versions, versions_by_type = _parse_verified_firmware_manifest_payload(
                payload
            )
            if versions or versions_by_type:
                _REMOTE_MANIFEST_STATE.data = (versions, versions_by_type)
                _REMOTE_MANIFEST_STATE.time = now
                return versions, versions_by_type

        _REMOTE_MANIFEST_STATE.time = now
        return cached_data


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro firmware update entities."""
    del hass
    coordinator = entry.runtime_data
    entities = [
        LiproFirmwareUpdateEntity(coordinator, device)
        for device in coordinator.devices.values()
        if not device.is_group and device.has_valid_iot_id
    ]
    async_add_entities(entities)


class LiproFirmwareUpdateEntity(LiproEntity, UpdateEntity):
    """Firmware update entity for one Lipro device."""

    _attr_translation_key = "firmware"
    _attr_name = None  # Use custom device name for easier identification
    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _entity_suffix = "firmware"
    _attr_supported_features = UpdateEntityFeature.INSTALL

    def __init__(
        self,
        coordinator: LiproDataUpdateCoordinator,
        device: LiproDevice,
    ) -> None:
        """Initialize firmware update entity."""
        super().__init__(coordinator, device, self._entity_suffix)
        self._ota_candidate: _OtaCandidate | None = None
        self._last_ota_refresh = _TIME_MIN_UTC
        self._ota_refresh_task: asyncio.Task[None] | None = None
        self._unverified_confirm_until = 0.0
        self._remote_verified_versions: frozenset[str] = frozenset()
        self._remote_versions_by_type: dict[str, frozenset[str]] = {}
        self._attr_installed_version = device.firmware_version
        self._attr_latest_version = device.firmware_version
        self._attr_in_progress = False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose OTA metadata for advanced users."""
        attrs: dict[str, Any] = {
            "certified": self._ota_candidate.certified
            if self._ota_candidate
            else False,
            "confirmation_required": self._has_pending_unverified_confirmation(),
        }

        if self._last_ota_refresh != _TIME_MIN_UTC:
            attrs["ota_checked_at"] = self._last_ota_refresh.isoformat()
        return attrs

    async def async_added_to_hass(self) -> None:
        """Schedule initial OTA metadata refresh."""
        await super().async_added_to_hass()
        self._schedule_ota_refresh(force=True)

    async def async_will_remove_from_hass(self) -> None:
        """Cancel OTA refresh task when entity is removed."""
        if self._ota_refresh_task and not self._ota_refresh_task.done():
            self._ota_refresh_task.cancel()
        self._ota_refresh_task = None
        await super().async_will_remove_from_hass()

    def _handle_coordinator_update(self) -> None:
        """React to coordinator updates and refresh OTA metadata lazily."""
        self._attr_installed_version = self.device.firmware_version
        self._schedule_ota_refresh(force=False)
        super()._handle_coordinator_update()

    async def async_update(self) -> None:
        """Force refresh OTA metadata."""
        await self._async_refresh_ota(force=True)

    async def async_install(
        self,
        version: str | None,
        backup: bool,
        **kwargs: Any,
    ) -> None:
        """Install firmware update."""
        del backup, kwargs
        await self._async_refresh_ota(force=True)

        candidate = self._ota_candidate
        if candidate is None or not candidate.update_available:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="firmware_no_update",
            )

        if (
            version is not None
            and candidate.latest_version is not None
            and version != candidate.latest_version
        ):
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="firmware_version_mismatch",
                translation_placeholders={"version": version},
            )

        if not candidate.certified and not self._consume_unverified_confirmation():
            self._unverified_confirm_until = (
                monotonic() + _UNVERIFIED_CONFIRM_WINDOW_SECONDS
            )
            self.async_write_ha_state()
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="firmware_unverified_confirm_required",
                translation_placeholders={
                    "seconds": str(_UNVERIFIED_CONFIRM_WINDOW_SECONDS),
                },
            )

        if candidate.install_command is None:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="firmware_install_unsupported",
            )

        self._attr_in_progress = True
        self.async_write_ha_state()
        try:
            success = await self.coordinator.async_send_command(
                self.device,
                candidate.install_command.command,
                candidate.install_command.properties,
            )
            if not success:
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="firmware_install_failed",
                )

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
        task.add_done_callback(self._async_clear_refresh_task)

    @staticmethod
    def _async_clear_refresh_task(task: asyncio.Task[None]) -> None:
        """Consume task exception to avoid warning logs."""
        try:
            task.result()
        except asyncio.CancelledError:
            return
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Background OTA refresh task failed: %s", err)

    def _should_refresh_ota(self) -> bool:
        """Return True when OTA metadata is stale."""
        return dt_util.utcnow() - self._last_ota_refresh >= _OTA_REFRESH_INTERVAL

    async def _async_refresh_ota(self, *, force: bool) -> None:
        """Refresh OTA metadata from cloud."""
        if not force and not self._should_refresh_ota():
            return

        try:
            rows = await self.coordinator.client.query_ota_info(
                device_id=self.device.serial,
                device_type=self.device.device_type_hex,
            )
        except LiproApiError as err:
            _LOGGER.debug(
                "Failed to refresh OTA info for %s: %s",
                self.device.serial,
                err,
            )
            return

        if self.hass is not None:
            (
                self._remote_verified_versions,
                self._remote_versions_by_type,
            ) = await _load_remote_firmware_manifest(self.hass)

        row = self._select_best_ota_row(rows)
        self._ota_candidate = self._build_ota_candidate(row)
        self._apply_ota_candidate()
        self._last_ota_refresh = dt_util.utcnow()
        self.async_write_ha_state()

    def _apply_ota_candidate(self) -> None:
        """Apply candidate values to update-entity attributes."""
        candidate = self._ota_candidate
        installed = self.device.firmware_version
        latest = installed
        if candidate is not None:
            installed = candidate.installed_version or installed
            if candidate.latest_version is not None:
                latest = candidate.latest_version
            self._attr_release_summary = candidate.release_summary
            self._attr_release_url = candidate.release_url
        else:
            self._attr_release_summary = None
            self._attr_release_url = None

        self._attr_installed_version = installed
        self._attr_latest_version = latest

    def _build_ota_candidate(self, row: dict[str, Any] | None) -> _OtaCandidate:
        """Normalize one OTA row for update-entity usage."""
        installed = self.device.firmware_version or _first_ota_text(
            row, _CURRENT_VERSION_KEYS
        )
        latest = self._resolve_latest_version(row, installed)
        update_available = self._resolve_update_available(row, installed, latest)
        certified = self._resolve_certification(
            row,
            installed,
            latest,
        )
        install_payload = _extract_install_command(
            row,
            container_keys=_COMMAND_CONTAINER_KEYS,
            command_keys=_COMMAND_KEYS,
            properties_keys=_COMMAND_PROPERTIES_KEYS,
        )
        install_command = (
            _InstallCommand(
                command=install_payload[0],
                properties=install_payload[1],
            )
            if install_payload is not None
            else None
        )
        return _OtaCandidate(
            installed_version=installed,
            latest_version=latest,
            update_available=update_available,
            certified=certified,
            release_summary=_first_ota_text(row, _RELEASE_SUMMARY_KEYS),
            release_url=_first_ota_text(row, _RELEASE_URL_KEYS),
            install_command=install_command,
        )

    def _resolve_latest_version(
        self,
        row: dict[str, Any] | None,
        installed: str | None,
    ) -> str | None:
        """Resolve latest firmware version from OTA row."""
        latest = _first_ota_text(row, _LATEST_VERSION_KEYS)
        if latest is not None:
            return latest

        common = _first_ota_text(row, _COMMON_VERSION_KEYS)
        if common is None:
            return installed

        if installed is None or common != installed:
            return common
        return installed

    def _resolve_update_available(
        self,
        row: dict[str, Any] | None,
        installed: str | None,
        latest: str | None,
    ) -> bool:
        """Resolve whether OTA update is available."""
        explicit_flag = _first_ota_bool(row, _UPDATE_FLAG_KEYS)
        if explicit_flag is not None:
            return explicit_flag

        if latest is None:
            return False
        if installed is None:
            return True
        if latest == installed:
            return False

        try:
            return self.version_is_newer(latest, installed)
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug(
                "Unable to compare firmware versions (%s -> %s): %s",
                installed,
                latest,
                err,
            )
            # Be conservative on parse failures: avoid false positive upgrades.
            return False

    def _resolve_certification(
        self,
        row: dict[str, Any] | None,
        installed: str | None,
        latest: str | None,
    ) -> bool:
        """Resolve certification state by flag and certification-version list."""
        explicit_or_inline = self._resolve_inline_certification(
            row,
            installed=installed,
            latest=latest,
        )
        if explicit_or_inline is not None:
            return explicit_or_inline

        if latest is None:
            return False

        candidate_types = _build_manifest_type_candidates(
            row,
            device_iot_name=self.device.iot_name,
            iot_name_keys=_IOT_NAME_KEYS,
        )
        if _matches_manifest_certification(
            candidate_types,
            self._remote_versions_by_type,
            self._remote_verified_versions,
            installed=installed,
            latest=latest,
            is_version_newer=self._is_version_newer,
        ):
            return True

        local_verified_versions, local_versions_by_type = (
            _load_verified_firmware_manifest()
        )
        return _matches_manifest_certification(
            candidate_types,
            local_versions_by_type,
            local_verified_versions,
            installed=installed,
            latest=latest,
            is_version_newer=self._is_version_newer,
        )

    def _resolve_inline_certification(
        self,
        row: dict[str, Any] | None,
        *,
        installed: str | None,
        latest: str | None,
    ) -> bool | None:
        """Resolve explicit certification flags and inline certification lists."""
        explicit_flag = _first_ota_bool(row, _CERTIFIED_FLAG_KEYS)
        if explicit_flag is not None:
            return explicit_flag

        certified_versions = _extract_version_set(row, _CERTIFIED_VERSION_KEYS)
        if self._matches_certified_versions(
            certified_versions,
            installed=installed,
            latest=latest,
        ):
            return True

        certification_node = row.get("certification") if isinstance(row, dict) else None
        if not isinstance(certification_node, dict):
            return None

        node_flag = _first_ota_bool(certification_node, _CERTIFIED_FLAG_KEYS)
        if node_flag is not None:
            return node_flag

        node_versions = _extract_version_set(
            certification_node, _CERTIFIED_VERSION_KEYS
        )
        if self._matches_certified_versions(
            node_versions,
            installed=installed,
            latest=latest,
        ):
            return True
        return None

    def _matches_certified_versions(
        self,
        certified_versions: set[str] | frozenset[str],
        *,
        installed: str | None,
        latest: str | None,
    ) -> bool:
        """Return True when certification list authorizes current upgrade."""
        return _ota_matches_certified_versions(
            certified_versions,
            installed=installed,
            latest=latest,
            is_version_newer=self._is_version_newer,
        )

    def _is_version_newer(self, candidate: str, current: str) -> bool:
        """Compare versions with HA helper, fallback to conservative False."""
        try:
            return self.version_is_newer(candidate, current)
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug(
                "Unable to compare certification versions (%s -> %s): %s",
                current,
                candidate,
                err,
            )
            return False

    def _select_best_ota_row(self, rows: list[Any]) -> dict[str, Any] | None:
        """Pick the most relevant OTA row for current device."""
        if not rows:
            return None

        best_row: dict[str, Any] | None = None
        best_score = -1
        for row in rows:
            if not isinstance(row, dict):
                continue
            score = self._score_ota_row(row)
            if score > best_score:
                best_score = score
                best_row = row

        return best_row

    def _score_ota_row(self, row: dict[str, Any]) -> int:
        """Score one OTA row against this device."""
        serial = self.device.serial.lower()
        device_type = self.device.device_type_hex.lower()
        iot_name = (self.device.iot_name or "").lower()
        score = 0
        score += self._score_exact_text_match(
            row,
            _SERIAL_KEYS,
            expected=serial,
            weight=_OTA_MATCH_SCORE_SERIAL_EXACT,
        )
        score += self._score_exact_text_match(
            row,
            _DEVICE_TYPE_KEYS,
            expected=device_type,
            weight=_OTA_MATCH_SCORE_DEVICE_TYPE_EXACT,
        )
        score += self._score_exact_text_match(
            row,
            ("bleName",),
            expected=iot_name,
            weight=_OTA_MATCH_SCORE_BLE_NAME_EXACT,
        )
        score += self._score_exact_text_match(
            row,
            _IOT_NAME_KEYS,
            expected=iot_name,
            weight=_OTA_MATCH_SCORE_IOT_NAME_EXACT,
        )
        score += self._score_exact_text_match(
            row,
            _PRODUCT_ID_KEYS,
            expected=str(self.device.product_id),
            weight=_OTA_MATCH_SCORE_PRODUCT_ID_EXACT,
            normalize=False,
        )
        score += self._score_exact_text_match(
            row,
            _PHYSICAL_MODEL_KEYS,
            expected=(self.device.physical_model or "").lower(),
            weight=_OTA_MATCH_SCORE_PHYSICAL_MODEL_EXACT,
        )
        if (
            _first_ota_text(row, _LATEST_VERSION_KEYS + _COMMON_VERSION_KEYS)
            is not None
        ):
            score += _OTA_MATCH_SCORE_HAS_VERSION
        return score

    @staticmethod
    def _score_exact_text_match(
        row: dict[str, Any],
        keys: tuple[str, ...],
        *,
        expected: str,
        weight: int,
        normalize: bool = True,
    ) -> int:
        """Return weight when OTA row text field matches expected value exactly."""
        value = _first_ota_text(row, keys)
        if value is None:
            return 0
        if normalize:
            return weight if value.lower() == expected else 0
        return weight if value == expected else 0

    def _has_pending_unverified_confirmation(self) -> bool:
        """Return True if unverified install confirmation is active."""
        return monotonic() < self._unverified_confirm_until

    def _consume_unverified_confirmation(self) -> bool:
        """Consume current unverified confirmation window if still active."""
        if not self._has_pending_unverified_confirmation():
            return False
        self._unverified_confirm_until = 0.0
        return True
