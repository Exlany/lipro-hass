"""Tests for derived ``DeviceExtras`` feature flags."""

from __future__ import annotations

from custom_components.lipro.const.properties import (
    PROP_BODY_REACTIVE,
    PROP_IR_SWITCH,
    PROP_IS_SUPPORT_IR_SWITCH,
    PROP_RC_LIST,
    PROP_SLEEP_AID_ENABLE,
)
from custom_components.lipro.core.device.extras import DeviceExtras


def test_device_extras_exposes_sleep_floor_lamp_and_panel_features() -> None:
    extras = DeviceExtras(
        properties={
            PROP_SLEEP_AID_ENABLE: 1,
            PROP_BODY_REACTIVE: 1,
        },
        extra_data={},
        serial="03ab5ccd7c123456",
        iot_name="21jd",
        physical_model="lamp",
    )

    assert extras.has_sleep_wake_features is True
    assert extras.has_floor_lamp_features is True
    assert extras.panel_type == 1


def test_device_extras_resolves_ir_remote_from_explicit_flags() -> None:
    extras = DeviceExtras(
        properties={PROP_IS_SUPPORT_IR_SWITCH: "0"},
        extra_data={"is_ir_remote": "1"},
        serial="03ab5ccd7c123456",
        iot_name="lipro_led",
        physical_model="light",
    )

    assert extras.is_ir_remote_device is True
    assert extras.supports_ir_switch is False


def test_device_extras_resolves_gateway_id_from_remote_gateway_serial_prefix() -> None:
    extras = DeviceExtras(
        properties={},
        extra_data={},
        serial="rmt_id_appremote_realremote_03ab5ccd7c123456",
        iot_name="lipro_led",
        physical_model="light",
    )

    assert extras.is_ir_remote_device is True
    assert extras.ir_remote_gateway_device_id == "03ab5ccd7c123456"
    assert extras.supports_ir_switch is True


def test_device_extras_resolves_gateway_id_from_rc_list_rows() -> None:
    extras = DeviceExtras(
        properties={
            PROP_RC_LIST: [
                {"driverId": "00000000", "iotId": "03ab5ccd7c654321"},
                {"deviceId": "rmt_id_03ab5ccd7c000999"},
            ]
        },
        extra_data={"is_ir_remote": True},
        serial="03ab5ccd7c123456",
        iot_name="lipro_led",
        physical_model="irRemote",
    )

    assert extras.ir_remote_gateway_device_id == "03ab5ccd7c654321"


def test_device_extras_returns_none_for_invalid_gateway_source_and_supports_ir_switch_key() -> (
    None
):
    extras = DeviceExtras(
        properties={PROP_IR_SWITCH: 1, PROP_RC_LIST: [{"deviceId": "rmt_id_invalid"}]},
        extra_data={"is_ir_remote": False},
        serial="03ab5ccd7c123456",
        iot_name="lipro_led",
        physical_model="light",
    )

    assert extras.is_ir_remote_device is False
    assert extras.ir_remote_gateway_device_id is None
    assert extras.supports_ir_switch is True


def test_device_extras_resolves_gateway_id_from_remote_id_prefix() -> None:
    extras = DeviceExtras(
        properties={PROP_RC_LIST: [{"deviceId": "rmt_id_03ab5ccd7c000999"}]},
        extra_data={"is_ir_remote": True},
        serial="03ab5ccd7c123456",
        iot_name="lipro_led",
        physical_model="irRemote",
    )

    assert extras.ir_remote_gateway_device_id == "03ab5ccd7c000999"
