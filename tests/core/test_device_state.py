"""Tests for extracted mutable device-state helpers."""

from __future__ import annotations

from custom_components.lipro.const.properties import (
    PROP_BRIGHTNESS,
    PROP_CONNECT_STATE,
    PROP_FAN_GEAR,
    PROP_POSITION,
    PROP_POWER_STATE,
    PROP_TEMPERATURE,
)
from custom_components.lipro.core.device import DeviceState


def test_device_state_reads_common_properties() -> None:
    state = DeviceState(
        properties={
            PROP_POWER_STATE: 1,
            PROP_CONNECT_STATE: "0",
            PROP_BRIGHTNESS: "66",
        },
        min_color_temp_kelvin=2700,
        max_color_temp_kelvin=6500,
        max_fan_gear=6,
    )

    assert state.is_on is True
    assert state.is_connected is False
    assert state.brightness == 66


def test_device_state_color_temp_uses_device_range() -> None:
    state = DeviceState(
        properties={PROP_TEMPERATURE: 50},
        min_color_temp_kelvin=2700,
        max_color_temp_kelvin=6500,
        max_fan_gear=6,
    )

    assert state.color_temp == 4600
    assert state.kelvin_to_percent_for_device(4600) == 50


def test_device_state_fan_gear_is_clamped() -> None:
    state = DeviceState(
        properties={PROP_FAN_GEAR: 9},
        min_color_temp_kelvin=2700,
        max_color_temp_kelvin=6500,
        max_fan_gear=6,
    )

    assert state.fan_gear == 6


def test_device_state_position_is_clamped() -> None:
    high = DeviceState(
        properties={PROP_POSITION: 120},
        min_color_temp_kelvin=2700,
        max_color_temp_kelvin=6500,
        max_fan_gear=6,
    )
    low = DeviceState(
        properties={PROP_POSITION: -10},
        min_color_temp_kelvin=2700,
        max_color_temp_kelvin=6500,
        max_fan_gear=6,
    )

    assert high.position == 100
    assert low.position == 0
