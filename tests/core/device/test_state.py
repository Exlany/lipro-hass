"""Tests for modularized mutable device-state helpers."""

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


def test_device_state_surface_is_explicit() -> None:
    """The state helper should expose concrete properties without __getattr__."""
    assert "__getattr__" not in DeviceState.__dict__
    assert "is_on" in DeviceState.__dict__
    assert "brightness" in DeviceState.__dict__
    assert "fan_mode" in DeviceState.__dict__


def test_device_state_from_api_data_reads_common_properties() -> None:
    """State snapshot should expose normalized common accessors."""
    state = DeviceState.from_api_data(
        {
            PROP_POWER_STATE: 1,
            PROP_CONNECT_STATE: "0",
            PROP_BRIGHTNESS: "66",
        },
        min_color_temp_kelvin=2700,
        max_color_temp_kelvin=6500,
        max_fan_gear=6,
        supports_color_temp=True,
    )

    assert state.is_on is True
    assert state.is_connected is False
    assert state.brightness == 66
    assert state.supports_color_temp is True


def test_device_state_color_temp_conversions_use_device_range() -> None:
    """Per-device color temp conversion should round-trip through percent."""
    state = DeviceState(
        properties={PROP_TEMPERATURE: 50},
        min_color_temp_kelvin=2700,
        max_color_temp_kelvin=6500,
        max_fan_gear=6,
        _supports_color_temp=True,
    )

    assert state.color_temp == 4600
    assert state.kelvin_to_percent_for_device(4600) == 50
    assert state.percent_to_kelvin_for_device(25) == 3650


def test_device_state_update_from_properties_merges_new_values() -> None:
    """State helper should update the live property mapping in place."""
    state = DeviceState(
        properties={PROP_BRIGHTNESS: 10},
        min_color_temp_kelvin=2700,
        max_color_temp_kelvin=6500,
        max_fan_gear=6,
        _supports_color_temp=True,
    )

    state.update_from_properties({PROP_BRIGHTNESS: "88", PROP_POWER_STATE: 1})

    assert state.brightness == 88
    assert state.is_on is True


def test_device_state_clamps_fan_gear_and_position() -> None:
    """Mutable state accessors should clamp fan speed and curtain position."""
    high = DeviceState(
        properties={PROP_POSITION: 120, PROP_FAN_GEAR: 9},
        min_color_temp_kelvin=2700,
        max_color_temp_kelvin=6500,
        max_fan_gear=6,
        _supports_color_temp=True,
    )
    low = DeviceState(
        properties={PROP_POSITION: -10},
        min_color_temp_kelvin=2700,
        max_color_temp_kelvin=6500,
        max_fan_gear=6,
        _supports_color_temp=True,
    )

    assert high.position == 100
    assert low.position == 0
    assert high.fan_gear == 6
