"""Tests for device categories module."""

import pytest

from custom_components.lipro.const.categories import (
    DeviceCategory,
    get_device_category,
    is_light_category,
    is_sensor_category,
    is_switch_category,
)
from custom_components.lipro.const.device_types import (
    DEVICE_TYPE_CEILING_LAMP,
    DEVICE_TYPE_CURTAIN,
    DEVICE_TYPE_DESK_LAMP,
    DEVICE_TYPE_FAN_LIGHT,
    DEVICE_TYPE_GATEWAY,
    DEVICE_TYPE_HEATER,
    DEVICE_TYPE_LED,
    DEVICE_TYPE_OUTLET,
    DEVICE_TYPE_PANEL,
    DEVICE_TYPE_SENSOR_D1,
    DEVICE_TYPE_SENSOR_M1,
)


class TestDeviceCategory:
    """Test DeviceCategory enum."""

    def test_all_categories_defined(self) -> None:
        """Test all expected categories are defined."""
        expected = {
            "LIGHT",
            "FAN_LIGHT",
            "CURTAIN",
            "SWITCH",
            "OUTLET",
            "HEATER",
            "BODY_SENSOR",
            "DOOR_SENSOR",
            "GATEWAY",
            "UNKNOWN",
        }
        actual = {category.name for category in DeviceCategory}
        assert actual == expected


class TestGetDeviceCategory:
    """Test get_device_category function."""

    @pytest.mark.parametrize(
        ("device_type", "expected_category"),
        [
            (DEVICE_TYPE_LED, DeviceCategory.LIGHT),
            (DEVICE_TYPE_CEILING_LAMP, DeviceCategory.LIGHT),
            (DEVICE_TYPE_DESK_LAMP, DeviceCategory.LIGHT),
            (DEVICE_TYPE_FAN_LIGHT, DeviceCategory.FAN_LIGHT),
            (DEVICE_TYPE_CURTAIN, DeviceCategory.CURTAIN),
            (DEVICE_TYPE_PANEL, DeviceCategory.SWITCH),
            (DEVICE_TYPE_OUTLET, DeviceCategory.OUTLET),
            (DEVICE_TYPE_HEATER, DeviceCategory.HEATER),
            (DEVICE_TYPE_SENSOR_M1, DeviceCategory.BODY_SENSOR),
            (DEVICE_TYPE_SENSOR_D1, DeviceCategory.DOOR_SENSOR),
            (DEVICE_TYPE_GATEWAY, DeviceCategory.GATEWAY),
        ],
    )
    def test_known_device_types(
        self, device_type: str, expected_category: DeviceCategory
    ) -> None:
        """Test known device types return correct category."""
        assert get_device_category(device_type) == expected_category

    def test_unknown_device_type(self) -> None:
        """Test unknown device type returns UNKNOWN category."""
        assert get_device_category("ff999999") == DeviceCategory.UNKNOWN
        assert get_device_category("invalid") == DeviceCategory.UNKNOWN
        assert get_device_category("") == DeviceCategory.UNKNOWN


class TestIsLightCategory:
    """Test is_light_category function."""

    def test_light_categories(self) -> None:
        """Test light categories return True."""
        assert is_light_category(DeviceCategory.LIGHT) is True
        assert is_light_category(DeviceCategory.FAN_LIGHT) is True

    def test_non_light_categories(self) -> None:
        """Test non-light categories return False."""
        assert is_light_category(DeviceCategory.CURTAIN) is False
        assert is_light_category(DeviceCategory.SWITCH) is False
        assert is_light_category(DeviceCategory.OUTLET) is False
        assert is_light_category(DeviceCategory.HEATER) is False
        assert is_light_category(DeviceCategory.BODY_SENSOR) is False
        assert is_light_category(DeviceCategory.DOOR_SENSOR) is False
        assert is_light_category(DeviceCategory.GATEWAY) is False
        assert is_light_category(DeviceCategory.UNKNOWN) is False


class TestIsSensorCategory:
    """Test is_sensor_category function."""

    def test_sensor_categories(self) -> None:
        """Test sensor categories return True."""
        assert is_sensor_category(DeviceCategory.BODY_SENSOR) is True
        assert is_sensor_category(DeviceCategory.DOOR_SENSOR) is True

    def test_non_sensor_categories(self) -> None:
        """Test non-sensor categories return False."""
        assert is_sensor_category(DeviceCategory.LIGHT) is False
        assert is_sensor_category(DeviceCategory.FAN_LIGHT) is False
        assert is_sensor_category(DeviceCategory.CURTAIN) is False
        assert is_sensor_category(DeviceCategory.SWITCH) is False
        assert is_sensor_category(DeviceCategory.OUTLET) is False
        assert is_sensor_category(DeviceCategory.HEATER) is False
        assert is_sensor_category(DeviceCategory.GATEWAY) is False
        assert is_sensor_category(DeviceCategory.UNKNOWN) is False


class TestIsSwitchCategory:
    """Test is_switch_category function."""

    def test_switch_categories(self) -> None:
        """Test switch categories return True."""
        assert is_switch_category(DeviceCategory.SWITCH) is True
        assert is_switch_category(DeviceCategory.OUTLET) is True

    def test_non_switch_categories(self) -> None:
        """Test non-switch categories return False."""
        assert is_switch_category(DeviceCategory.LIGHT) is False
        assert is_switch_category(DeviceCategory.FAN_LIGHT) is False
        assert is_switch_category(DeviceCategory.CURTAIN) is False
        assert is_switch_category(DeviceCategory.HEATER) is False
        assert is_switch_category(DeviceCategory.BODY_SENSOR) is False
        assert is_switch_category(DeviceCategory.DOOR_SENSOR) is False
        assert is_switch_category(DeviceCategory.GATEWAY) is False
        assert is_switch_category(DeviceCategory.UNKNOWN) is False
