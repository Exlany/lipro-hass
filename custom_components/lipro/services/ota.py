"""OTA-related service handlers for Lipro integration."""

from __future__ import annotations

from dataclasses import dataclass
import functools
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall

from ..core import LiproApiError
from ..core.ota_utils import (
    extract_ota_versions as extract_ota_versions_from_rows,
    load_verified_firmware_manifest_file,
)


def filter_ota_rows_by_user_devices(rows: Any, coordinator: Any) -> list[dict[str, Any]]:
    """Filter OTA rows to only include device types that user actually has."""
    if not isinstance(rows, list):
        return []

    devices = getattr(coordinator, "devices", {})
    if not isinstance(devices, dict):
        devices = {}

    allowed_types = {
        str(device.device_type_hex).strip().lower()
        for device in devices.values()
        if hasattr(device, "device_type_hex") and str(device.device_type_hex).strip()
    }
    if not allowed_types:
        return [row for row in rows if isinstance(row, dict)]

    filtered: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        row_type = row.get("deviceType")
        if not isinstance(row_type, str) or not row_type.strip():
            filtered.append(row)
            continue
        if row_type.strip().lower() in allowed_types:
            filtered.append(row)
    return filtered


@functools.lru_cache(maxsize=1)
def _load_verified_firmware_versions_cached(
    manifest_path: str,
    logger: Any,
) -> frozenset[str]:
    """Load verified firmware versions from built-in manifest file."""
    verified_versions, _ = load_verified_firmware_manifest_file(
        Path(manifest_path),
        on_error=lambda path, err: logger.warning(
            "Failed to load firmware support manifest %s: %s",
            path,
            err,
        ),
    )
    return verified_versions


@dataclass(frozen=True, slots=True)
class StartOtaCallContext:
    """Normalized context fields extracted from one service call."""

    requested_device_id: str | None
    is_alias_resolution: bool
    confirm_irreversible: bool
    confirm_unverified: bool


@dataclass(frozen=True, slots=True)
class StartOtaVersionSnapshot:
    """Precomputed OTA metadata used by validation and response payload."""

    filtered_rows: list[dict[str, Any]]
    ota_versions: list[str]
    unverified_versions: list[str]


def _resolve_start_ota_call_context(
    call_data: Any,
    resolved_serial: str,
    *,
    attr_device_id: str,
    attr_confirm_irreversible: str,
    attr_confirm_unverified: str,
) -> StartOtaCallContext:
    payload = call_data if isinstance(call_data, dict) else {}
    requested_device_id = payload.get(attr_device_id)
    return StartOtaCallContext(
        requested_device_id=requested_device_id,
        is_alias_resolution=requested_device_id not in (None, "", resolved_serial),
        confirm_irreversible=bool(payload.get(attr_confirm_irreversible, False)),
        confirm_unverified=bool(payload.get(attr_confirm_unverified, False)),
    )


def _analyze_start_ota_versions(
    ota_rows: Any,
    coordinator: Any,
    verified_versions: frozenset[str],
) -> StartOtaVersionSnapshot:
    filtered_rows = filter_ota_rows_by_user_devices(ota_rows, coordinator)
    ota_versions = sorted(extract_ota_versions_from_rows(filtered_rows))
    unverified_versions = [
        version for version in ota_versions if version not in verified_versions
    ]
    return StartOtaVersionSnapshot(
        filtered_rows=filtered_rows,
        ota_versions=ota_versions,
        unverified_versions=unverified_versions,
    )


def _build_start_ota_result(
    serial: str,
    version_snapshot: StartOtaVersionSnapshot,
) -> dict[str, Any]:
    return {
        "success": True,
        "serial": serial,
        "command": "OTA_UPDATE",
        "ota_versions": version_snapshot.ota_versions,
        "ota_rows": version_snapshot.filtered_rows,
        "unverified_versions": version_snapshot.unverified_versions,
        "warning": "Firmware upgrade is irreversible by this integration.",
    }


async def async_handle_query_ota_info(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: Any,
    async_call_optional_capability: Any,
    service_query_ota_info: str,
) -> dict[str, Any]:
    """Developer-only service: query OTA metadata for selected device/group."""
    device, coordinator = await get_device_and_coordinator(hass, call)
    result = await async_call_optional_capability(
        service_query_ota_info,
        coordinator.client.query_ota_info,
        device_id=device.serial,
        device_type=device.device_type,
    )
    result = filter_ota_rows_by_user_devices(result, coordinator)
    return {
        "serial": device.serial,
        "ota": result,
    }


async def async_handle_start_ota_update(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: Any,
    async_send_command_with_service_errors: Any,
    raise_service_error: Any,
    logger: Any,
    load_verified_firmware_versions: Any,
    attr_device_id: str,
    attr_confirm_irreversible: str,
    attr_confirm_unverified: str,
) -> dict[str, Any]:
    """Developer-only service: start OTA update with explicit safety guards."""
    preflight_context = _resolve_start_ota_call_context(
        call.data,
        "",
        attr_device_id=attr_device_id,
        attr_confirm_irreversible=attr_confirm_irreversible,
        attr_confirm_unverified=attr_confirm_unverified,
    )
    if not preflight_context.confirm_irreversible:
        raise_service_error("ota_update_confirm_required")

    device, coordinator = await get_device_and_coordinator(hass, call)
    context = _resolve_start_ota_call_context(
        call.data,
        device.serial,
        attr_device_id=attr_device_id,
        attr_confirm_irreversible=attr_confirm_irreversible,
        attr_confirm_unverified=attr_confirm_unverified,
    )

    try:
        ota_rows = await coordinator.client.query_ota_info(
            device_id=device.serial,
            device_type=device.device_type,
        )
    except LiproApiError as err:
        logger.warning("API error querying OTA versions before upgrade: %s", err)
        raise_service_error("ota_update_version_check_failed", err=err)

    version_snapshot = _analyze_start_ota_versions(
        ota_rows,
        coordinator,
        load_verified_firmware_versions(),
    )
    if version_snapshot.unverified_versions and not context.confirm_unverified:
        raise_service_error("ota_update_unverified_confirm_required")

    logger.warning(
        "Service call: start_ota_update for %s (requested=%s, alias=%s, versions=%s, unverified=%s)",
        device.serial,
        context.requested_device_id,
        context.is_alias_resolution,
        version_snapshot.ota_versions,
        version_snapshot.unverified_versions,
    )

    await async_send_command_with_service_errors(
        coordinator,
        device,
        command="OTA_UPDATE",
        properties=None,
        requested_device_id=context.requested_device_id,
        failure_log=(
            "start_ota_update failed (command=%s, device_id=%s, "
            "resolved_serial=%s, failure=%s)"
        ),
        api_error_log="API error starting OTA update: %s",
    )
    return _build_start_ota_result(device.serial, version_snapshot)
