"""Tests for coordinator developer-report helpers."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from custom_components.lipro.const import (
    CONF_DEBUG_MODE,
    CONF_ENABLE_POWER_MONITORING,
    CONF_LIGHT_TURN_ON_ON_ADJUST,
    CONF_MQTT_ENABLED,
    CONF_PHONE,
    CONF_POWER_QUERY_INTERVAL,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
)
from custom_components.lipro.core.developer_report import build_developer_report
from custom_components.lipro.core.device import LiproDevice


def _make_device(
    serial: str,
    *,
    is_group: bool = False,
    name: str = "Device",
    properties: dict[str, Any] | None = None,
) -> LiproDevice:
    return LiproDevice(
        device_number=1,
        serial=serial,
        name=name,
        device_type=1,
        iot_name="lipro_led",
        physical_model="light",
        is_group=is_group,
        properties=properties or {},
    )


def _redact_identifier(identifier: str | None) -> str | None:
    if not isinstance(identifier, str):
        return None
    normalized = identifier.strip()
    if not normalized:
        return None
    if len(normalized) <= 8:
        return "***"
    return f"{normalized[:4]}***{normalized[-4:]}"


def test_build_developer_report_disabled_mode_includes_note_and_mesh_fallback() -> None:
    group = _make_device("mesh_group_10001", is_group=True, name="Group")
    group.extra_data["group_member_ids"] = [
        "03ab5ccd7c111111",
        "03ab5ccd7c222222",
    ]
    group.extra_data["group_member_count"] = "unknown"
    group.extra_data["gateway_device_id"] = "03ab5ccd7c333333"
    light = _make_device("03ab5ccd7c999999", name="Light")

    config_entry = SimpleNamespace(
        entry_id="entry-1234567890",
        unique_id="unique-1234567890",
        data={CONF_PHONE: "13800000000"},
        options={},
    )

    report = build_developer_report(
        config_entry=config_entry,
        debug_mode=False,
        mqtt_enabled=True,
        mqtt_connected=False,
        polling_interval_seconds=30,
        last_update_success=True,
        devices={group.serial: group, light.serial: light},
        group_count=1,
        individual_count=1,
        outlet_count=0,
        pending_devices=2,
        pending_errors=1,
        command_traces=[],
        redact_identifier=_redact_identifier,
    )

    assert report["debug_mode_enabled"] is False
    assert "note" in report
    assert report["devices"]["total"] == 2
    assert report["anonymous_share_pending"] == {"devices": 2, "errors": 1}
    assert report["entry_id"] != config_entry.entry_id
    assert report["unique_id"] != config_entry.unique_id
    assert report["phone"] != config_entry.data[CONF_PHONE]

    mesh = report["mesh_groups"][0]
    assert mesh["member_count"] == 2
    assert mesh["gateway_device_id"] == _redact_identifier("03ab5ccd7c333333")
    assert mesh["member_ids"] == [
        _redact_identifier("03ab5ccd7c111111"),
        _redact_identifier("03ab5ccd7c222222"),
    ]


def test_build_developer_report_honors_option_overrides_when_debug_enabled() -> None:
    options = {
        CONF_SCAN_INTERVAL: 25,
        CONF_MQTT_ENABLED: False,
        CONF_ENABLE_POWER_MONITORING: False,
        CONF_LIGHT_TURN_ON_ON_ADJUST: True,
        CONF_POWER_QUERY_INTERVAL: 90,
        CONF_REQUEST_TIMEOUT: 40,
        CONF_DEBUG_MODE: True,
    }
    config_entry = SimpleNamespace(
        entry_id="entry-1234567890",
        unique_id="unique-1234567890",
        data={CONF_PHONE: "13800000000"},
        options=options,
    )

    report = build_developer_report(
        config_entry=config_entry,
        debug_mode=True,
        mqtt_enabled=False,
        mqtt_connected=True,
        polling_interval_seconds=None,
        last_update_success=False,
        devices={},
        group_count=0,
        individual_count=0,
        outlet_count=0,
        pending_devices=0,
        pending_errors=0,
        command_traces=[{"route": "device_direct", "success": True}],
        redact_identifier=_redact_identifier,
    )

    assert "note" not in report
    assert report["runtime"]["polling_interval_seconds"] is None
    assert report["runtime"]["last_update_success"] is False
    assert report["options"]["scan_interval"] == 25
    assert report["options"]["mqtt_enabled"] is False
    assert report["options"]["power_monitoring_enabled"] is False
    assert report["options"]["light_turn_on_on_adjust"] is True
    assert report["options"]["power_query_interval"] == 90
    assert report["options"]["request_timeout"] == 40
    assert report["options"]["debug_mode"] is True
    assert report["recent_commands"] == [{"route": "device_direct", "success": True}]
