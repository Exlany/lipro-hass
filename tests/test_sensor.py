"""Tests for Lipro sensor platform."""

from __future__ import annotations

import pytest

from custom_components.lipro.core.device import LiproDevice


class TestLiproOutletPowerSensor:
    """Tests for LiproOutletPowerSensor entity."""

    def test_power_info_available(self, make_device):
        """Test power info is available."""
        device = make_device(
            "outlet",
            extra_data={
                "power_info": {
                    "nowPower": 150.5,
                    "energyList": [{"t": "20240101", "v": 10.5}],
                }
            },
        )

        power_info = device.extra_data.get("power_info")
        assert power_info is not None
        assert power_info["nowPower"] == 150.5

    def test_power_info_not_available(self, make_device):
        """Test power info is not available."""
        device = make_device("outlet")

        power_info = device.extra_data.get("power_info")
        assert power_info is None

    def test_now_power_value(self, make_device):
        """Test nowPower value extraction."""
        device = make_device(
            "outlet",
            extra_data={"power_info": {"nowPower": 75.3}},
        )

        power_info = device.extra_data.get("power_info")
        assert power_info["nowPower"] == 75.3


class TestLiproOutletEnergySensor:
    """Tests for LiproOutletEnergySensor entity."""

    def test_energy_list_sum(self, make_device):
        """Test energy list sum calculation."""
        device = make_device(
            "outlet",
            extra_data={
                "power_info": {
                    "energyList": [
                        {"t": "20240101", "v": 10.5},
                        {"t": "20240102", "v": 20.3},
                        {"t": "20240103", "v": 5.2},
                    ],
                }
            },
        )

        power_info = device.extra_data.get("power_info")
        energy_list = power_info.get("energyList", [])

        total_energy = 0.0
        for item in energy_list:
            energy_value = item.get("v")
            if energy_value is not None:
                total_energy += float(energy_value)

        assert total_energy == pytest.approx(36.0, rel=0.01)

    def test_energy_list_empty(self, make_device):
        """Test empty energy list."""
        device = make_device(
            "outlet",
            extra_data={"power_info": {"energyList": []}},
        )

        power_info = device.extra_data.get("power_info")
        energy_list = power_info.get("energyList", [])

        assert len(energy_list) == 0

    def test_energy_list_missing(self, make_device):
        """Test missing energy list."""
        device = make_device("outlet", extra_data={"power_info": {}})

        power_info = device.extra_data.get("power_info")
        energy_list = power_info.get("energyList", [])

        assert energy_list == []


class TestLiproBatterySensor:
    """Tests for LiproBatterySensor entity."""

    def test_battery_level(self, make_device):
        """Test battery level property."""
        device = make_device("light", properties={"battery": "85"})
        assert device.battery_level == 85

    def test_battery_level_low(self, make_device):
        """Test low battery level."""
        device = make_device("light", properties={"battery": "5"})
        assert device.battery_level == 5

    def test_battery_level_full(self, make_device):
        """Test full battery level."""
        device = make_device("light", properties={"battery": "100"})
        assert device.battery_level == 100

    def test_battery_level_none(self, make_device):
        """Test battery level when not available."""
        device = make_device("light")
        assert device.battery_level is None

    def test_is_charging_true(self, make_device):
        """Test is_charging when charging."""
        device = make_device("light", properties={"charging": "1"})
        assert device.is_charging is True

    def test_is_charging_false(self, make_device):
        """Test is_charging when not charging."""
        device = make_device("light", properties={"charging": "0"})
        assert device.is_charging is False

    def test_has_battery_true(self, make_device):
        """Test has_battery when device has battery."""
        device = make_device("light", properties={"battery": "50"})
        assert device.has_battery is True

    def test_has_battery_false(self, make_device):
        """Test has_battery when device has no battery."""
        device = make_device("light")
        assert device.has_battery is False


class TestSensorDeviceCategory:
    """Tests for sensor device category detection."""

    def test_outlet_category(self):
        """Test outlet device category."""
        from custom_components.lipro.const.categories import DeviceCategory

        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Outlet",
            device_type=6,
            iot_name="",
            physical_model="outlet",
        )

        assert device.category == DeviceCategory.OUTLET


class TestSensorPropertyConstants:
    """Tests for sensor property constants."""

    def test_property_constants(self):
        """Test property constants are defined."""
        from custom_components.lipro.const import PROP_BATTERY, PROP_CHARGING

        assert PROP_BATTERY == "battery"
        assert PROP_CHARGING == "charging"
