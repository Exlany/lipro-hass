"""Developer report assembly helpers for coordinator diagnostics."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, Any

from ..const import (
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

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .device import LiproDevice


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


def build_developer_report(
    *,
    config_entry: ConfigEntry | None,
    debug_mode: bool,
    mqtt_enabled: bool,
    mqtt_connected: bool,
    polling_interval_seconds: int | None,
    last_update_success: bool,
    devices: Mapping[str, LiproDevice],
    group_count: int,
    individual_count: int,
    outlet_count: int,
    pending_devices: int,
    pending_errors: int,
    command_traces: Sequence[dict[str, Any]],
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
