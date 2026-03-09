"""Tests for coordinator developer-report helpers."""

from __future__ import annotations

from typing import Any

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import (
    CONF_DEBUG_MODE,
    CONF_ENABLE_POWER_MONITORING,
    CONF_LIGHT_TURN_ON_ON_ADJUST,
    CONF_MQTT_ENABLED,
    CONF_PHONE,
    CONF_POWER_QUERY_INTERVAL,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
)
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.utils.developer_report import build_developer_report


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

    config_entry = MockConfigEntry(
        domain=DOMAIN,
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
        diagnostic_gateway_devices=None,
        group_count=1,
        individual_count=1,
        outlet_count=0,
        pending_devices=2,
        pending_errors=1,
        command_traces=[],
        last_command_failure=None,
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
    config_entry = MockConfigEntry(
        domain=DOMAIN,
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
        diagnostic_gateway_devices=None,
        group_count=0,
        individual_count=0,
        outlet_count=0,
        pending_devices=0,
        pending_errors=0,
        command_traces=[{"route": "device_direct", "success": True}],
        last_command_failure=None,
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


def test_build_developer_report_includes_panel_capability_snapshot() -> None:
    panel = LiproDevice(
        device_number=1,
        serial="03ab5ccd7c000099",
        name="Wall Panel",
        device_type=5,
        iot_name="21JD",
        physical_model="switch",
        properties={
            "led": "1",
            "memory": "0",
            "pairKeyFull": "1",
            "panelInfo": '[{"index":0,"mode":2,"addr":49155,"mac":"5CCD7C59ABCD","relay":true,"keyName":"左键","iconIndex":3,"roomId":11}]',
        },
    )
    outlet = LiproDevice(
        device_number=2,
        serial="03ab5ccd7c000088",
        name="Outlet",
        device_type=6,
        iot_name="outlet",
        physical_model="outlet",
        properties={"memory": "1"},
    )

    report = build_developer_report(
        config_entry=None,
        debug_mode=True,
        mqtt_enabled=True,
        mqtt_connected=True,
        polling_interval_seconds=30,
        last_update_success=True,
        devices={panel.serial: panel, outlet.serial: outlet},
        diagnostic_gateway_devices=None,
        group_count=0,
        individual_count=2,
        outlet_count=1,
        pending_devices=0,
        pending_errors=0,
        command_traces=[],
        last_command_failure={
            "device_id": panel.serial,
            "reason": "api_error",
            "code": "140006",
            "route": "mesh_group",
            "command": "PANEL_BIND",
        },
        redact_identifier=_redact_identifier,
    )

    snapshot = report["panel_capability_snapshot"]
    assert snapshot["panel_count"] == 1
    assert snapshot["configurable_panel_count"] == 1
    assert snapshot["pair_key_full_count"] == 1

    panel_entry = snapshot["panels"][0]
    assert panel_entry["device_id"] == _redact_identifier(panel.serial)
    assert panel_entry["name"] == "Wall Panel"
    assert panel_entry["iot_name"] == "21JD"
    assert panel_entry["panel_type"] == 1
    assert panel_entry["available"] is True
    assert panel_entry["is_connected"] is True
    assert panel_entry["led"] == {"supported": True, "enabled": True}
    assert panel_entry["memory"] == {"supported": True, "enabled": False}
    assert panel_entry["pair_key_full_present"] is True
    assert panel_entry["pair_key_full"] is True
    assert panel_entry["panel_info_count"] == 1
    assert panel_entry["panel_info"][0]["index"] == 0
    assert panel_entry["panel_info"][0]["mode"] == 2
    assert panel_entry["panel_info"][0]["addr"] == 49155
    assert panel_entry["panel_info"][0]["mac"] == _redact_identifier("5CCD7C59ABCD")
    assert panel_entry["panel_info"][0]["relay"] is True
    assert panel_entry["panel_info"][0]["keyName"] == "左键"
    assert panel_entry["last_command_failure"] == {
        "reason": "api_error",
        "code": "140006",
        "route": "mesh_group",
    }


def test_build_developer_report_includes_ir_inventory_snapshot() -> None:
    gateway = LiproDevice(
        device_number=1,
        serial="03ab5ccd7c000001",
        name="Main Gateway",
        device_type=11,
        iot_name="M2W1",
        physical_model="gateway",
        properties={
            "irSwitch": "1",
            "rcList": '[{"address":"5ccd7c59abcd","keycount":1,"keyindex":1,"name":"风扇灯遥控器","selfIndex":-1,"timestamp":"1694267294911","version":"3.0.1"}]',
            "version": "9.2.20",
        },
    )
    ir_remote = LiproDevice(
        device_number=2,
        serial="rmt_id_appremote_realremote_03ab5ccd7c000001",
        name="Remote Asset",
        device_type=11,
        iot_name="irRemote",
        physical_model="irRemote",
    )

    report = build_developer_report(
        config_entry=None,
        debug_mode=True,
        mqtt_enabled=True,
        mqtt_connected=True,
        polling_interval_seconds=30,
        last_update_success=True,
        devices={ir_remote.serial: ir_remote},
        diagnostic_gateway_devices={gateway.serial: gateway},
        group_count=0,
        individual_count=1,
        outlet_count=0,
        pending_devices=0,
        pending_errors=0,
        command_traces=[],
        last_command_failure=None,
        redact_identifier=_redact_identifier,
    )

    snapshot = report["ir_remote_inventory_snapshot"]
    assert snapshot["gateway_count"] == 1
    assert snapshot["ir_capable_gateway_count"] == 1
    assert snapshot["bound_remote_total"] == 1
    assert snapshot["ir_remote_device_count"] == 1
    assert snapshot["orphan_ir_remote_count"] == 0

    gateway_entry = snapshot["gateways"][0]
    assert gateway_entry["device_id"] == _redact_identifier(gateway.serial)
    assert gateway_entry["supports_ir_switch"] is True
    assert gateway_entry["ir_switch"] is True
    assert gateway_entry["ir_emit_supported_by_firmware"] is True
    assert gateway_entry["remote_count"] == 1
    assert gateway_entry["rc_list"][0]["name"] == "风扇灯遥控器"
    assert gateway_entry["rc_list"][0]["address"] == _redact_identifier("5ccd7c59abcd")

    remote_entry = snapshot["ir_remote_devices"][0]
    assert remote_entry["device_id"] == _redact_identifier(ir_remote.serial)
    assert remote_entry["gateway_device_id"] == _redact_identifier(gateway.serial)
    assert remote_entry["gateway_present_in_runtime"] is True
    assert remote_entry["orphaned"] is False
