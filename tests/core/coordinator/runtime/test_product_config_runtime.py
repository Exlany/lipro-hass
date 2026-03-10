"""Tests for product config runtime helpers."""

from __future__ import annotations

import logging

import pytest

from custom_components.lipro.core.coordinator.runtime.product_config_runtime import (
    apply_product_config,
    coerce_int_or_zero,
    index_product_configs,
    match_product_config,
)
from custom_components.lipro.core.device import LiproDevice


class TestCoerceIntOrZero:
    """Test coerce_int_or_zero."""

    def test_int_value(self) -> None:
        """Test coerces int."""
        assert coerce_int_or_zero(42) == 42

    def test_string_int(self) -> None:
        """Test coerces string int."""
        assert coerce_int_or_zero("123") == 123

    def test_float_value(self) -> None:
        """Test coerces float to int."""
        assert coerce_int_or_zero(3.14) == 3

    def test_invalid_string(self) -> None:
        """Test returns 0 for invalid string."""
        assert coerce_int_or_zero("invalid") == 0

    def test_none_value(self) -> None:
        """Test returns 0 for None."""
        assert coerce_int_or_zero(None) == 0

    def test_empty_string(self) -> None:
        """Test returns 0 for empty string."""
        assert coerce_int_or_zero("") == 0


class TestIndexProductConfigs:
    """Test index_product_configs."""

    def test_empty_list(self) -> None:
        """Test empty config list."""
        by_id, by_name = index_product_configs([])
        assert by_id == {}
        assert by_name == {}

    def test_index_by_id(self) -> None:
        """Test indexes by product ID."""
        configs = [
            {"id": 1, "name": "Config 1"},
            {"id": 2, "name": "Config 2"},
        ]
        by_id, by_name = index_product_configs(configs)
        assert by_id[1]["name"] == "Config 1"
        assert by_id[2]["name"] == "Config 2"

    def test_index_by_iot_name(self) -> None:
        """Test indexes by fwIotName."""
        configs = [
            {"id": 1, "fwIotName": "DeviceA", "name": "Config A"},
            {"id": 2, "fwIotName": "DeviceB", "name": "Config B"},
        ]
        by_id, by_name = index_product_configs(configs)
        assert by_name["devicea"]["name"] == "Config A"
        assert by_name["deviceb"]["name"] == "Config B"

    def test_case_insensitive_iot_name(self) -> None:
        """Test fwIotName is case-insensitive."""
        configs = [{"id": 1, "fwIotName": "MyDevice", "name": "Config"}]
        by_id, by_name = index_product_configs(configs)
        assert "mydevice" in by_name
        assert by_name["mydevice"]["name"] == "Config"

    def test_skips_invalid_id(self) -> None:
        """Test skips configs with invalid or zero ID."""
        configs = [
            {"id": 0, "name": "Zero"},
            {"id": "invalid", "name": "Invalid"},
            {"id": -1, "name": "Negative"},
        ]
        by_id, by_name = index_product_configs(configs)
        assert by_id == {}

    def test_skips_empty_iot_name(self) -> None:
        """Test skips configs with empty fwIotName."""
        configs = [
            {"id": 1, "fwIotName": "", "name": "Empty"},
            {"id": 2, "fwIotName": None, "name": "None"},
            {"id": 3, "name": "Missing"},
        ]
        by_id, by_name = index_product_configs(configs)
        assert by_name == {}


class TestMatchProductConfig:
    """Test match_product_config."""

    def test_match_by_product_id(self) -> None:
        """Test matches by product ID."""
        device = LiproDevice(
            device_id="dev1",
            name="Test Device",
            model="model1",
            category="light",
            room_id="room1",
            room_name="Room",
            product_id=123,
        )
        configs_by_id = {123: {"id": 123, "name": "Config 123"}}
        configs_by_iot_name = {}

        result = match_product_config(
            device,
            configs_by_id=configs_by_id,
            configs_by_iot_name=configs_by_iot_name,
            logger=logging.getLogger(__name__),
        )
        assert result is not None
        assert result["name"] == "Config 123"

    def test_match_by_iot_name(self) -> None:
        """Test matches by iot_name when product_id not found."""
        device = LiproDevice(
            device_id="dev1",
            name="Test Device",
            model="model1",
            category="light",
            room_id="room1",
            room_name="Room",
            iot_name="MyDevice",
        )
        configs_by_id = {}
        configs_by_iot_name = {"mydevice": {"fwIotName": "MyDevice", "name": "Config"}}

        result = match_product_config(
            device,
            configs_by_id=configs_by_id,
            configs_by_iot_name=configs_by_iot_name,
            logger=logging.getLogger(__name__),
        )
        assert result is not None
        assert result["name"] == "Config"

    def test_product_id_takes_precedence(self) -> None:
        """Test product_id match takes precedence over iot_name."""
        device = LiproDevice(
            device_id="dev1",
            name="Test Device",
            model="model1",
            category="light",
            room_id="room1",
            room_name="Room",
            product_id=123,
            iot_name="MyDevice",
        )
        configs_by_id = {123: {"id": 123, "name": "By ID"}}
        configs_by_iot_name = {"mydevice": {"fwIotName": "MyDevice", "name": "By Name"}}

        result = match_product_config(
            device,
            configs_by_id=configs_by_id,
            configs_by_iot_name=configs_by_iot_name,
            logger=logging.getLogger(__name__),
        )
        assert result is not None
        assert result["name"] == "By ID"

    def test_no_match(self) -> None:
        """Test returns None when no match found."""
        device = LiproDevice(
            device_id="dev1",
            name="Test Device",
            model="model1",
            category="light",
            room_id="room1",
            room_name="Room",
        )
        configs_by_id = {}
        configs_by_iot_name = {}

        result = match_product_config(
            device,
            configs_by_id=configs_by_id,
            configs_by_iot_name=configs_by_iot_name,
            logger=logging.getLogger(__name__),
        )
        assert result is None


class TestApplyProductConfig:
    """Test apply_product_config."""

    def test_apply_color_temp_range(self) -> None:
        """Test applies color temperature range."""
        device = LiproDevice(
            device_id="dev1",
            name="Test Device",
            model="model1",
            category="light",
            room_id="room1",
            room_name="Room",
        )
        config = {"minTemperature": 2700, "maxTemperature": 6500}

        apply_product_config(device, config, logger=logging.getLogger(__name__))

        assert device.min_color_temp_kelvin == 2700
        assert device.max_color_temp_kelvin == 6500

    def test_apply_max_temp_only(self) -> None:
        """Test applies max temp with default min."""
        device = LiproDevice(
            device_id="dev1",
            name="Test Device",
            model="model1",
            category="light",
            room_id="room1",
            room_name="Room",
        )
        config = {"maxTemperature": 6500}

        apply_product_config(device, config, logger=logging.getLogger(__name__))

        assert device.min_color_temp_kelvin == 2700  # MIN_COLOR_TEMP_KELVIN
        assert device.max_color_temp_kelvin == 6500

    def test_apply_zero_temps_single_color(self) -> None:
        """Test zero temps indicates single color temperature."""
        device = LiproDevice(
            device_id="dev1",
            name="Test Device",
            model="model1",
            category="light",
            room_id="room1",
            room_name="Room",
        )
        config = {"minTemperature": 0, "maxTemperature": 0}

        apply_product_config(device, config, logger=logging.getLogger(__name__))

        assert device.min_color_temp_kelvin == 0
        assert device.max_color_temp_kelvin == 0

    def test_apply_max_fan_gear(self) -> None:
        """Test applies max fan gear."""
        device = LiproDevice(
            device_id="dev1",
            name="Test Device",
            model="model1",
            category="fan",
            room_id="room1",
            room_name="Room",
        )
        device.max_fan_gear = 3
        config = {"maxFanGear": 5}

        apply_product_config(device, config, logger=logging.getLogger(__name__))

        assert device.default_max_fan_gear_in_model == 5
        assert device.max_fan_gear == 5

    def test_fan_gear_preserves_higher_existing(self) -> None:
        """Test fan gear preserves higher existing value."""
        device = LiproDevice(
            device_id="dev1",
            name="Test Device",
            model="model1",
            category="fan",
            room_id="room1",
            room_name="Room",
        )
        device.max_fan_gear = 7
        config = {"maxFanGear": 5}

        apply_product_config(device, config, logger=logging.getLogger(__name__))

        assert device.default_max_fan_gear_in_model == 5
        assert device.max_fan_gear == 7  # Preserved higher value

    def test_empty_config(self) -> None:
        """Test empty config does not modify device."""
        device = LiproDevice(
            device_id="dev1",
            name="Test Device",
            model="model1",
            category="light",
            room_id="room1",
            room_name="Room",
        )
        original_min = device.min_color_temp_kelvin
        original_max = device.max_color_temp_kelvin
        config = {}

        apply_product_config(device, config, logger=logging.getLogger(__name__))

        assert device.min_color_temp_kelvin == original_min
        assert device.max_color_temp_kelvin == original_max
