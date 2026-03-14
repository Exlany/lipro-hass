"""Developer report assembly helpers for coordinator diagnostics."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, Any

from ...const.config import (
    CONF_DEBUG_MODE,
    CONF_ENABLE_POWER_MONITORING,
    CONF_LIGHT_TURN_ON_ON_ADJUST,
    CONF_MQTT_ENABLED,
    CONF_PHONE,
    CONF_POWER_QUERY_INTERVAL,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
    DEFAULT_DEBUG_MODE,
    DEFAULT_ENABLE_POWER_MONITORING,
    DEFAULT_LIGHT_TURN_ON_ON_ADJUST,
    DEFAULT_MQTT_ENABLED,
    DEFAULT_POWER_QUERY_INTERVAL,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
)
from ...const.device_types import DEVICE_TYPE_PANEL
from ...const.properties import PROP_LED, PROP_MEMORY, PROP_PAIR_KEY_FULL

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from ..device import LiproDevice

_IR_EMIT_MIN_GATEWAY_VERSION = (9, 2, 20)


def _build_mesh_group_entries(
    devices: Mapping[str, LiproDevice],
    *,
    redact_identifier: Callable[[str | None], str | None],
) -> list[dict[str, Any]]:
    """Build mesh-group diagnostics section."""
    mesh_groups: list[dict[str, Any]] = []
    for dev in devices.values():
        if not dev.is_group:
            continue

        member_ids = dev.extra_data.get("group_member_ids")
        safe_member_ids = (
            [redact_identifier(mid) for mid in member_ids if isinstance(mid, str)]
            if isinstance(member_ids, list)
            else []
        )
        member_count = dev.extra_data.get("group_member_count")
        if not isinstance(member_count, int):
            member_count = len(safe_member_ids)

        mesh_groups.append(
            {
                "group_id": redact_identifier(dev.serial),
                "iot_name": dev.iot_name,
                "device_type": dev.device_type,
                "physical_model": dev.physical_model,
                "member_count": member_count,
                "gateway_device_id": redact_identifier(
                    dev.extra_data.get("gateway_device_id")
                ),
                "member_ids": safe_member_ids,
            }
        )
    return mesh_groups


def _build_report_options(options: Mapping[str, Any]) -> dict[str, Any]:
    """Build normalized developer-report options section."""
    return {
        "scan_interval": options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        "mqtt_enabled": options.get(CONF_MQTT_ENABLED, DEFAULT_MQTT_ENABLED),
        "power_monitoring_enabled": options.get(
            CONF_ENABLE_POWER_MONITORING,
            DEFAULT_ENABLE_POWER_MONITORING,
        ),
        "light_turn_on_on_adjust": options.get(
            CONF_LIGHT_TURN_ON_ON_ADJUST,
            DEFAULT_LIGHT_TURN_ON_ON_ADJUST,
        ),
        "power_query_interval": options.get(
            CONF_POWER_QUERY_INTERVAL,
            DEFAULT_POWER_QUERY_INTERVAL,
        ),
        "request_timeout": options.get(
            CONF_REQUEST_TIMEOUT,
            DEFAULT_REQUEST_TIMEOUT,
        ),
        "debug_mode": options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE),
    }


def _sanitize_last_command_failure(
    failure: Mapping[str, Any] | None,
    *,
    device_id: str,
) -> dict[str, Any] | None:
    """Return a minimal failure summary when it belongs to this device."""
    if not isinstance(failure, Mapping):
        return None
    failure_device_id = failure.get("device_id")
    if not isinstance(failure_device_id, str) or failure_device_id != device_id:
        return None

    result: dict[str, Any] = {}
    for key in ("reason", "code", "route"):
        value = failure.get(key)
        if isinstance(value, str) and value:
            result[key] = value
    return result or None


def _sanitize_panel_info_entry(
    entry: dict[str, Any],
    *,
    redact_identifier: Callable[[str | None], str | None],
) -> dict[str, Any]:
    """Sanitize one panelInfo entry for developer diagnostics."""
    result: dict[str, Any] = {}
    for key in ("index", "mode", "addr", "iconIndex", "roomId"):
        value = entry.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            result[key] = value
    relay = entry.get("relay")
    if isinstance(relay, bool):
        result["relay"] = relay
    key_name = entry.get("keyName")
    if isinstance(key_name, str) and key_name.strip():
        result["keyName"] = key_name.strip()
    mac = entry.get("mac")
    if isinstance(mac, str) and mac.strip():
        result["mac"] = redact_identifier(mac)
    return result


def _build_panel_capability_snapshot(
    devices: Mapping[str, LiproDevice],
    *,
    redact_identifier: Callable[[str | None], str | None],
    last_command_failure: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Build developer-only panel capability snapshot from runtime devices."""
    panel_entries: list[dict[str, Any]] = []
    configurable_panel_count = 0
    pair_key_full_count = 0

    for dev in devices.values():
        if dev.is_group or dev.device_type_hex != DEVICE_TYPE_PANEL:
            continue

        supports_led = PROP_LED in dev.properties
        supports_memory = PROP_MEMORY in dev.properties
        pair_key_full_present = PROP_PAIR_KEY_FULL in dev.properties
        panel_info = [
            _sanitize_panel_info_entry(entry, redact_identifier=redact_identifier)
            for entry in dev.panel_info
        ]
        if supports_led or supports_memory or pair_key_full_present or panel_info:
            configurable_panel_count += 1

        pair_key_full = dev.state.panel_pair_key_full if pair_key_full_present else None
        if pair_key_full is True:
            pair_key_full_count += 1

        panel_entries.append(
            {
                "device_id": redact_identifier(dev.serial),
                "name": dev.name,
                "iot_name": dev.iot_name,
                "panel_type": dev.panel_type,
                "available": dev.available,
                "is_connected": dev.is_connected,
                "led": {
                    "supported": supports_led,
                    "enabled": dev.state.panel_led_enabled if supports_led else None,
                },
                "memory": {
                    "supported": supports_memory,
                    "enabled": dev.state.panel_memory_enabled
                    if supports_memory
                    else None,
                },
                "pair_key_full_present": pair_key_full_present,
                "pair_key_full": pair_key_full,
                "panel_info_count": len(panel_info),
                "panel_info": panel_info,
                "last_command_failure": _sanitize_last_command_failure(
                    last_command_failure,
                    device_id=dev.serial,
                ),
            }
        )

    return {
        "panel_count": len(panel_entries),
        "configurable_panel_count": configurable_panel_count,
        "pair_key_full_count": pair_key_full_count,
        "panels": panel_entries,
    }


def _parse_version_tuple(version: str | None) -> tuple[int, ...] | None:
    """Parse dotted firmware version into comparable tuple."""
    if not isinstance(version, str):
        return None
    normalized = version.strip()
    if not normalized:
        return None
    parts = normalized.split(".")
    parsed: list[int] = []
    for part in parts:
        if not part.isdigit():
            return None
        parsed.append(int(part))
    return tuple(parsed)


def _firmware_meets_ir_emit_floor(version: str | None) -> bool | None:
    """Return whether firmware meets the APK-observed IR emit minimum."""
    parsed = _parse_version_tuple(version)
    if parsed is None:
        return None
    length = max(len(parsed), len(_IR_EMIT_MIN_GATEWAY_VERSION))
    padded = parsed + (0,) * (length - len(parsed))
    required = _IR_EMIT_MIN_GATEWAY_VERSION + (0,) * (
        length - len(_IR_EMIT_MIN_GATEWAY_VERSION)
    )
    return padded >= required


def _sanitize_rc_entry(
    entry: dict[str, Any],
    *,
    redact_identifier: Callable[[str | None], str | None],
) -> dict[str, Any]:
    """Sanitize one rcList entry for developer diagnostics."""
    result: dict[str, Any] = {}
    name = entry.get("name")
    if isinstance(name, str) and name.strip():
        result["name"] = name.strip()
    result["address"] = redact_identifier(
        entry.get("address") if isinstance(entry.get("address"), str) else None
    )
    for key in ("version", "timestamp", "keycount", "keyindex", "selfIndex"):
        value = entry.get(key)
        if isinstance(value, (str, int)) and not isinstance(value, bool):
            result[key] = value
    return result


def _build_ir_remote_inventory_snapshot(
    devices: Mapping[str, LiproDevice],
    diagnostic_gateway_devices: Mapping[str, LiproDevice] | None = None,
    *,
    redact_identifier: Callable[[str | None], str | None],
) -> dict[str, Any]:
    """Build developer-only IR inventory snapshot from runtime + diagnostics."""
    gateway_entries: list[dict[str, Any]] = []
    runtime_gateway_ids: set[str] = set()
    gateway_devices: dict[str, LiproDevice] = dict(diagnostic_gateway_devices or {})
    ir_capable_gateway_count = 0
    bound_remote_total = 0

    for dev in devices.values():
        if (
            dev.is_group
            or not dev.capabilities.is_gateway
            or dev.extras.is_ir_remote_device
        ):
            continue
        gateway_devices.setdefault(dev.serial, dev)

    for dev in gateway_devices.values():
        runtime_gateway_ids.add(dev.serial.casefold())
        rc_entries = [
            _sanitize_rc_entry(entry, redact_identifier=redact_identifier)
            for entry in dev.rc_list
        ]
        remote_count = len(rc_entries)
        firmware_gate = _firmware_meets_ir_emit_floor(dev.network_info.firmware_version)
        supports_ir = dev.supports_ir_switch
        if supports_ir or remote_count:
            ir_capable_gateway_count += 1
        bound_remote_total += remote_count
        gateway_entries.append(
            {
                "device_id": redact_identifier(dev.serial),
                "name": dev.name,
                "firmware_version": dev.network_info.firmware_version,
                "supports_ir_switch": supports_ir,
                "ir_switch": dev.state.ir_switch_enabled,
                "ir_emit_supported_by_firmware": firmware_gate,
                "remote_count": remote_count,
                "rc_list": rc_entries,
            }
        )

    ir_remote_devices: list[dict[str, Any]] = []
    orphan_count = 0
    for dev in devices.values():
        if not dev.extras.is_ir_remote_device:
            continue

        gateway_device_id = dev.ir_remote_gateway_device_id
        gateway_present = (
            isinstance(gateway_device_id, str)
            and gateway_device_id.casefold() in runtime_gateway_ids
        )
        orphaned = not gateway_present
        if orphaned:
            orphan_count += 1
        ir_remote_devices.append(
            {
                "device_id": redact_identifier(dev.serial),
                "name": dev.name,
                "gateway_device_id": redact_identifier(gateway_device_id),
                "gateway_present_in_runtime": gateway_present,
                "orphaned": orphaned,
            }
        )

    return {
        "gateway_count": len(gateway_entries),
        "ir_capable_gateway_count": ir_capable_gateway_count,
        "bound_remote_total": bound_remote_total,
        "ir_remote_device_count": len(ir_remote_devices),
        "orphan_ir_remote_count": orphan_count,
        "gateways": gateway_entries,
        "ir_remote_devices": ir_remote_devices,
    }


def build_developer_report(
    *,
    config_entry: ConfigEntry | None,
    debug_mode: bool,
    mqtt_enabled: bool,
    mqtt_connected: bool,
    polling_interval_seconds: int | None,
    last_update_success: bool,
    devices: Mapping[str, LiproDevice],
    diagnostic_gateway_devices: Mapping[str, LiproDevice] | None = None,
    group_count: int,
    individual_count: int,
    outlet_count: int,
    pending_devices: int,
    pending_errors: int,
    command_traces: Sequence[dict[str, Any]],
    last_command_failure: Mapping[str, Any] | None,
    redact_identifier: Callable[[str | None], str | None],
) -> dict[str, Any]:
    """Build sanitized coordinator runtime report."""
    entry_id = config_entry.entry_id if config_entry else None
    unique_id = config_entry.unique_id if config_entry else None
    phone = config_entry.data.get(CONF_PHONE) if config_entry else None
    options = config_entry.options if config_entry else {}
    mesh_groups = _build_mesh_group_entries(
        devices,
        redact_identifier=redact_identifier,
    )
    panel_capability_snapshot = _build_panel_capability_snapshot(
        devices,
        redact_identifier=redact_identifier,
        last_command_failure=last_command_failure,
    )
    ir_remote_inventory_snapshot = _build_ir_remote_inventory_snapshot(
        devices,
        diagnostic_gateway_devices,
        redact_identifier=redact_identifier,
    )

    report: dict[str, Any] = {
        "entry_id": redact_identifier(entry_id),
        "unique_id": redact_identifier(unique_id),
        "phone": redact_identifier(phone),
        "debug_mode_enabled": debug_mode,
        "runtime": {
            "mqtt_enabled": mqtt_enabled,
            "mqtt_connected": mqtt_connected,
            "polling_interval_seconds": polling_interval_seconds,
            "last_update_success": last_update_success,
        },
        "options": _build_report_options(options),
        "devices": {
            "total": len(devices),
            "group_count": group_count,
            "individual_count": individual_count,
            "outlet_count": outlet_count,
        },
        "mesh_groups": mesh_groups,
        "panel_capability_snapshot": panel_capability_snapshot,
        "ir_remote_inventory_snapshot": ir_remote_inventory_snapshot,
        "anonymous_share_pending": {
            "devices": pending_devices,
            "errors": pending_errors,
        },
        "recent_commands": list(command_traces),
    }

    if not debug_mode:
        report["note"] = (
            "Debug mode is disabled. Enable it in advanced options "
            "to capture command traces."
        )

    return report
