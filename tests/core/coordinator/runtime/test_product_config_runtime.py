"""Tests for product config runtime helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.lipro.const.properties import MIN_COLOR_TEMP_KELVIN
from custom_components.lipro.core.coordinator.runtime.product_config_runtime import (
    apply_product_config,
    coerce_int_or_zero,
    index_product_configs,
    match_product_config,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (42, 42),
        ("123", 123),
        (3.14, 3),
        ("invalid", 0),
        (None, 0),
        ("", 0),
    ],
)
def test_coerce_int_or_zero(value: object, expected: int) -> None:
    """Mixed payload values should coerce to ints or a safe zero fallback."""
    assert coerce_int_or_zero(value) == expected


def test_index_product_configs_builds_id_and_iot_name_maps() -> None:
    """Valid config rows should be indexed by id and lowercase fwIotName."""
    by_id, by_name = index_product_configs(
        [
            {"id": 1, "fwIotName": "DeviceA", "name": "Config A"},
            {"id": "2", "fwIotName": "deviceB", "name": "Config B"},
        ]
    )

    assert by_id[1]["name"] == "Config A"
    assert by_id[2]["name"] == "Config B"
    assert by_name["devicea"]["name"] == "Config A"
    assert by_name["deviceb"]["name"] == "Config B"


def test_index_product_configs_skips_invalid_rows() -> None:
    """Invalid ids and empty fwIotName values should not be indexed."""
    by_id, by_name = index_product_configs(
        [
            {"id": 0, "name": "Zero"},
            {"id": "invalid", "name": "Invalid"},
            {"id": -1, "name": "Negative"},
            {"id": 3, "fwIotName": "", "name": "Empty"},
            {"id": 4, "fwIotName": None, "name": "None"},
        ]
    )

    assert by_id == {3: {"id": 3, "fwIotName": "", "name": "Empty"}, 4: {"id": 4, "fwIotName": None, "name": "None"}}
    assert by_name == {}


def test_match_product_config_prefers_product_id_before_iot_name(make_device) -> None:
    """Product-id matches should win over fwIotName fallback matches."""
    device = make_device("light", product_id=123, iot_name="MyDevice")

    result = match_product_config(
        device,
        configs_by_id={123: {"id": 123, "name": "By ID"}},
        configs_by_iot_name={"mydevice": {"fwIotName": "MyDevice", "name": "By Name"}},
        logger=MagicMock(),
    )

    assert result == {"id": 123, "name": "By ID"}


def test_match_product_config_falls_back_to_iot_name_and_none(make_device) -> None:
    """fwIotName fallback should be used only when id lookup misses."""
    matched = match_product_config(
        make_device("light", product_id=None, iot_name="MyDevice"),
        configs_by_id={},
        configs_by_iot_name={"mydevice": {"fwIotName": "MyDevice", "name": "Config"}},
        logger=MagicMock(),
    )
    missing = match_product_config(
        make_device("light", product_id=None, iot_name="Unknown"),
        configs_by_id={},
        configs_by_iot_name={},
        logger=MagicMock(),
    )

    assert matched == {"fwIotName": "MyDevice", "name": "Config"}
    assert missing is None


def test_apply_product_config_updates_color_temperature_ranges(make_device) -> None:
    """Configured temperature bounds should update the device profile."""
    device = make_device("light")

    apply_product_config(
        device,
        {"minTemperature": 3000, "maxTemperature": 6500},
        logger=MagicMock(),
    )

    assert device.min_color_temp_kelvin == 3000
    assert device.max_color_temp_kelvin == 6500


def test_apply_product_config_uses_default_min_temp_when_only_max_present(
    make_device,
) -> None:
    """Missing min temperature should fallback to the integration minimum."""
    device = make_device("light")

    apply_product_config(device, {"maxTemperature": 6500}, logger=MagicMock())

    assert device.min_color_temp_kelvin == MIN_COLOR_TEMP_KELVIN
    assert device.max_color_temp_kelvin == 6500


def test_apply_product_config_handles_single_color_devices(make_device) -> None:
    """Zero temperature bounds should disable tunable color temperature."""
    device = make_device("light")

    apply_product_config(
        device,
        {"minTemperature": 0, "maxTemperature": 0},
        logger=MagicMock(),
    )

    assert device.min_color_temp_kelvin == 0
    assert device.max_color_temp_kelvin == 0


def test_apply_product_config_updates_fan_gear_without_lowering_current_limit(
    make_device,
) -> None:
    """Configured fan gear should raise defaults but never shrink the max range."""
    device = make_device("fanLight", max_fan_gear=8, default_max_fan_gear_in_model=8)

    apply_product_config(device, {"maxFanGear": 6}, logger=MagicMock())
    assert device.default_max_fan_gear_in_model == 6
    assert device.max_fan_gear == 8

    apply_product_config(device, {"maxFanGear": 10}, logger=MagicMock())
    assert device.default_max_fan_gear_in_model == 10
    assert device.max_fan_gear == 10
