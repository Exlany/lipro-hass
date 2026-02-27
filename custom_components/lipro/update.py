"""Firmware update platform for Lipro integration."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import functools
import json
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
    "bleName",
    "productName",
    "fingerprint",
    "deviceFingerprint",
)
_IOT_NAME_KEYS = ("iotName", "fwIotName", "bleName", "productName")
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

_REMOTE_MANIFEST_STATE: dict[str, Any] = {
    "time": _TIME_MIN_UTC,
    "data": (frozenset(), {}),
}
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
    certification_source: str
    release_summary: str | None
    release_url: str | None
    install_command: _InstallCommand | None


@functools.lru_cache(maxsize=1)
def _load_verified_firmware_manifest() -> tuple[frozenset[str], dict[str, frozenset[str]]]:
    """Load optional local firmware certification manifest."""
    manifest_path = Path(__file__).with_name(_FIRMWARE_SUPPORT_MANIFEST)
    try:
        content = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        _LOGGER.debug("Failed to load firmware support manifest %s: %s", manifest_path, err)
        return frozenset(), {}

    verified_versions = _normalize_manifest_version_list(content.get("verified_versions"))
    raw_versions_by_type = content.get("verified_versions_by_type")
    versions_by_type: dict[str, frozenset[str]] = {}
    if isinstance(raw_versions_by_type, dict):
        for raw_type, raw_versions in raw_versions_by_type.items():
            if not isinstance(raw_type, str):
                continue
            normalized_type = raw_type.strip().lower()
            if not normalized_type:
                continue
            normalized_versions = _normalize_manifest_version_list(raw_versions)
            if normalized_versions:
                versions_by_type[normalized_type] = normalized_versions

    return verified_versions, versions_by_type


def _normalize_manifest_version_list(value: Any) -> frozenset[str]:
    """Normalize one manifest version list field."""
    if not isinstance(value, list):
        return frozenset()
    return frozenset(
        text
        for item in value
        if (text := str(item).strip())
    )


def _normalize_manifest_versions_by_type(
    value: Any,
) -> dict[str, frozenset[str]]:
    """Normalize version map by device type from manifest payload."""
    if not isinstance(value, dict):
        return {}
    result: dict[str, frozenset[str]] = {}
    for raw_type, raw_versions in value.items():
        if not isinstance(raw_type, str):
            continue
        normalized_type = raw_type.strip().lower()
        if not normalized_type:
            continue
        normalized_versions = _normalize_manifest_version_list(raw_versions)
        if normalized_versions:
            result[normalized_type] = normalized_versions
    return result


def _parse_remote_manifest_payload(
    payload: Any,
) -> tuple[frozenset[str], dict[str, frozenset[str]]]:
    """Parse remote firmware manifest payload with tolerant schema handling."""
    if isinstance(payload, list):
        return _normalize_manifest_version_list(payload), {}

    if not isinstance(payload, dict):
        return frozenset(), {}

    versions = _normalize_manifest_version_list(
        payload.get("verified_versions") or payload.get("versions")
    )
    versions_by_type = _normalize_manifest_versions_by_type(
        payload.get("verified_versions_by_type") or payload.get("versions_by_type")
    )
    return versions, versions_by_type


async def _load_remote_firmware_manifest(
    hass: HomeAssistant,
) -> tuple[frozenset[str], dict[str, frozenset[str]]]:
    """Load firmware certification manifest from remote service with cache."""
    now = dt_util.utcnow()
    cached_time = _REMOTE_MANIFEST_STATE["time"]
    cached_data = _REMOTE_MANIFEST_STATE["data"]
    if now - cached_time < _REMOTE_MANIFEST_CACHE_TTL:
        return cached_data

    async with _REMOTE_MANIFEST_LOCK:
        now = dt_util.utcnow()
        cached_time = _REMOTE_MANIFEST_STATE["time"]
        cached_data = _REMOTE_MANIFEST_STATE["data"]
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
                _LOGGER.debug("Remote firmware manifest fetch failed from %s: %s", url, err)
                continue

            versions, versions_by_type = _parse_remote_manifest_payload(payload)
            if versions or versions_by_type:
                _REMOTE_MANIFEST_STATE["data"] = (versions, versions_by_type)
                _REMOTE_MANIFEST_STATE["time"] = now
                return _REMOTE_MANIFEST_STATE["data"]

        _REMOTE_MANIFEST_STATE["time"] = now
        return _REMOTE_MANIFEST_STATE["data"]


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
            "certified": self._ota_candidate.certified if self._ota_candidate else False,
            "certification_source": (
                self._ota_candidate.certification_source if self._ota_candidate else "none"
            ),
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
        if self.hass is None:
            return
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
        installed = self.device.firmware_version or self._first_text(row, _CURRENT_VERSION_KEYS)
        latest = self._resolve_latest_version(row, installed)
        update_available = self._resolve_update_available(row, installed, latest)
        certified, certification_source = self._resolve_certification(
            row,
            installed,
            latest,
        )
        install_command = self._extract_install_command(row)
        return _OtaCandidate(
            installed_version=installed,
            latest_version=latest,
            update_available=update_available,
            certified=certified,
            certification_source=certification_source,
            release_summary=self._first_text(row, _RELEASE_SUMMARY_KEYS),
            release_url=self._first_text(row, _RELEASE_URL_KEYS),
            install_command=install_command,
        )

    def _resolve_latest_version(
        self,
        row: dict[str, Any] | None,
        installed: str | None,
    ) -> str | None:
        """Resolve latest firmware version from OTA row."""
        latest = self._first_text(row, _LATEST_VERSION_KEYS)
        if latest is not None:
            return latest

        common = self._first_text(row, _COMMON_VERSION_KEYS)
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
        explicit_flag = self._first_bool(row, _UPDATE_FLAG_KEYS)
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
        except Exception:  # noqa: BLE001
            return latest != installed

    def _resolve_certification(
        self,
        row: dict[str, Any] | None,
        installed: str | None,
        latest: str | None,
    ) -> tuple[bool, str]:
        """Resolve certification state by flag and certification-version list."""
        explicit_flag = self._first_bool(row, _CERTIFIED_FLAG_KEYS)
        if explicit_flag is not None:
            return explicit_flag, "flag"

        certified_versions = self._extract_version_set(row, _CERTIFIED_VERSION_KEYS)
        if self._matches_certified_versions(
            certified_versions,
            installed=installed,
            latest=latest,
        ):
            return True, "list"

        certification_node = row.get("certification") if isinstance(row, dict) else None
        if isinstance(certification_node, dict):
            node_flag = self._first_bool(certification_node, _CERTIFIED_FLAG_KEYS)
            if node_flag is not None:
                return node_flag, "certification.flag"

            node_versions = self._extract_version_set(
                certification_node,
                _CERTIFIED_VERSION_KEYS,
            )
            if self._matches_certified_versions(
                node_versions,
                installed=installed,
                latest=latest,
            ):
                return True, "certification.list"

        if latest:
            candidate_types = self._candidate_manifest_type_keys(row)
            has_remote_type_match = False
            for candidate in candidate_types:
                remote_type_versions = self._remote_versions_by_type.get(candidate)
                if remote_type_versions is None:
                    continue
                has_remote_type_match = True
                if self._matches_certified_versions(
                    remote_type_versions,
                    installed=installed,
                    latest=latest,
                ):
                    return True, "remote_manifest.type"
            if not has_remote_type_match and self._matches_certified_versions(
                self._remote_verified_versions, installed=installed, latest=latest
            ):
                return True, "remote_manifest"

            verified_versions, versions_by_type = _load_verified_firmware_manifest()
            has_local_type_match = False
            for candidate in candidate_types:
                local_type_versions = versions_by_type.get(candidate)
                if local_type_versions is None:
                    continue
                has_local_type_match = True
                if self._matches_certified_versions(
                    local_type_versions,
                    installed=installed,
                    latest=latest,
                ):
                    return True, "manifest.type"
            if not has_local_type_match and self._matches_certified_versions(
                verified_versions, installed=installed, latest=latest
            ):
                return True, "manifest"

        return False, "none"

    def _matches_certified_versions(
        self,
        certified_versions: set[str] | frozenset[str],
        *,
        installed: str | None,
        latest: str | None,
    ) -> bool:
        """Return True when certification list authorizes current upgrade."""
        if not certified_versions:
            return False

        # Keep exact-target match for deterministic OTA payloads.
        if latest and latest in certified_versions:
            return True

        # Relaxed rule: any certified version newer than current firmware
        # means this device generation is considered certified for upgrade.
        if installed is None:
            return False
        return any(
            self._is_version_newer(candidate, installed)
            for candidate in certified_versions
        )

    def _is_version_newer(self, candidate: str, current: str) -> bool:
        """Compare versions with HA helper, fallback to lexicographical order."""
        try:
            return self.version_is_newer(candidate, current)
        except Exception:  # noqa: BLE001
            return candidate != current and candidate > current

    def _extract_install_command(self, row: dict[str, Any] | None) -> _InstallCommand | None:
        """Extract install command payload from OTA row."""
        if not isinstance(row, dict):
            return None

        for key in _COMMAND_CONTAINER_KEYS:
            command = self._parse_install_command_payload(row.get(key))
            if command is not None:
                return command

        return self._parse_install_command_payload(row)

    def _parse_install_command_payload(
        self,
        payload: Any,
    ) -> _InstallCommand | None:
        """Parse install command payload from nested or top-level OTA fields."""
        if isinstance(payload, str):
            command = payload.strip()
            if command:
                return _InstallCommand(command=command, properties=None)
            return None

        if not isinstance(payload, dict):
            return None

        command = self._first_text(payload, _COMMAND_KEYS)
        if command is None:
            return None

        properties = self._normalize_properties(payload)
        return _InstallCommand(command=command, properties=properties)

    def _normalize_properties(
        self,
        payload: dict[str, Any],
    ) -> list[dict[str, str]] | None:
        """Normalize command properties payload to send_command schema."""
        for key in _COMMAND_PROPERTIES_KEYS:
            raw = payload.get(key)
            normalized = self._coerce_properties(raw)
            if normalized is not None:
                return normalized
        return None

    def _coerce_properties(self, value: Any) -> list[dict[str, str]] | None:
        """Coerce property payload to key/value list."""
        if value is None:
            return None

        if isinstance(value, dict):
            result = [
                {"key": str(key), "value": str(item)}
                for key, item in value.items()
                if key is not None and item is not None
            ]
            return result or None

        if not isinstance(value, list):
            return None

        result: list[dict[str, str]] = []
        for item in value:
            if isinstance(item, dict):
                raw_key = item.get("key")
                raw_value = item.get("value")
                if raw_key is None or raw_value is None:
                    continue
                result.append({"key": str(raw_key), "value": str(raw_value)})
        return result or None

    def _select_best_ota_row(self, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
        """Pick the most relevant OTA row for current device."""
        if not isinstance(rows, list) or not rows:
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
        score = 0
        serial = self.device.serial.lower()
        device_type = self.device.device_type_hex.lower()

        row_serial = self._first_text(row, _SERIAL_KEYS)
        if row_serial is not None and row_serial.lower() == serial:
            score += 8

        row_type = self._first_text(row, _DEVICE_TYPE_KEYS)
        if row_type is not None and row_type.lower() == device_type:
            score += 4

        row_iot_name = self._first_text(row, _IOT_NAME_KEYS)
        if row_iot_name is not None and row_iot_name.lower() == (self.device.iot_name or "").lower():
            score += 3

        row_product_id = self._first_text(row, _PRODUCT_ID_KEYS)
        if row_product_id is not None and row_product_id == str(self.device.product_id):
            score += 3

        row_physical_model = self._first_text(row, _PHYSICAL_MODEL_KEYS)
        if row_physical_model is not None and row_physical_model.lower() == (self.device.physical_model or "").lower():
            score += 2

        if self._first_text(row, _LATEST_VERSION_KEYS + _COMMON_VERSION_KEYS) is not None:
            score += 1

        return score

    def _candidate_manifest_type_keys(self, row: dict[str, Any] | None) -> list[str]:
        """Build candidate keys for manifest.type matching in priority order."""
        candidates: list[str] = []

        def add(value: str | None) -> None:
            if value is None:
                return
            normalized = value.strip().lower()
            if not normalized:
                return
            if normalized not in candidates:
                candidates.append(normalized)

        row_iot_name = self._first_text(row, _IOT_NAME_KEYS)
        row_product_id = self._first_text(row, _PRODUCT_ID_KEYS)
        row_physical_model = self._first_text(row, _PHYSICAL_MODEL_KEYS)
        row_device_type = self._first_text(row, _DEVICE_TYPE_KEYS)
        row_fingerprint = self._first_text(row, ("fingerprint", "deviceFingerprint"))
        add(row_fingerprint)

        device_type = self.device.device_type_hex
        iot_name = self.device.iot_name or row_iot_name
        product_id = (
            str(self.device.product_id)
            if self.device.product_id is not None
            else row_product_id
        )
        physical_model = self.device.physical_model or row_physical_model
        if physical_model and iot_name and device_type:
            add(f"{physical_model}|{iot_name}|{product_id or ''}|{device_type}")

        add(row_device_type)
        add(device_type)
        add(row_iot_name)
        add(iot_name)
        add(row_product_id)
        add(product_id)
        add(row_physical_model)
        add(physical_model)

        return candidates

    @staticmethod
    def _first_text(data: dict[str, Any] | None, keys: tuple[str, ...]) -> str | None:
        """Return first non-empty string value."""
        if not isinstance(data, dict):
            return None
        for key in keys:
            value = data.get(key)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
        return None

    @staticmethod
    def _first_bool(data: dict[str, Any] | None, keys: tuple[str, ...]) -> bool | None:
        """Return first bool-like field value."""
        if not isinstance(data, dict):
            return None
        for key in keys:
            value = data.get(key)
            normalized = LiproFirmwareUpdateEntity._coerce_bool(value)
            if normalized is not None:
                return normalized
        return None

    @staticmethod
    def _coerce_bool(value: Any) -> bool | None:
        """Parse bool-like value or return None when unknown."""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            if value in (0, 1):
                return bool(value)
            return None
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "certified", "passed"}:
                return True
            if normalized in {"0", "false", "no", "off", "uncertified", "failed"}:
                return False
        return None

    def _extract_version_set(
        self,
        data: dict[str, Any] | None,
        keys: tuple[str, ...],
    ) -> set[str]:
        """Extract version list from arbitrary fields."""
        if not isinstance(data, dict):
            return set()

        versions: set[str] = set()
        for key in keys:
            raw = data.get(key)
            if not isinstance(raw, list):
                continue
            for item in raw:
                if item is None:
                    continue
                text = str(item).strip()
                if text:
                    versions.add(text)
        return versions

    def _has_pending_unverified_confirmation(self) -> bool:
        """Return True if unverified install confirmation is active."""
        return monotonic() < self._unverified_confirm_until

    def _consume_unverified_confirmation(self) -> bool:
        """Consume current unverified confirmation window if still active."""
        if not self._has_pending_unverified_confirmation():
            return False
        self._unverified_confirm_until = 0.0
        return True
