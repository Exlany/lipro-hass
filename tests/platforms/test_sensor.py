"""Tests for Lipro sensor platform."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.core.device import LiproDevice


class TestLiproOutletPowerSensor:
    """Tests for LiproOutletPowerSensor entity."""

    def test_power_info_available_from_formal_primitive(self, make_device):
        """Test power info is available from the formal primitive."""
        device = make_device("outlet")
        device.outlet_power_info = {
            "nowPower": 150.5,
            "energyList": [{"t": "20240101", "v": 10.5}],
        }

        power_info = device.outlet_power_info
        assert power_info is not None
        assert power_info["nowPower"] == 150.5

    def test_power_info_ignores_legacy_sidecar_without_formal_primitive(
        self, make_device
    ):
        """Test legacy side-car data is ignored when the formal primitive is absent."""
        device = make_device(
            "outlet",
            extra_data={
                "power_info": {
                    "nowPower": 150.5,
                    "energyList": [{"t": "20240101", "v": 10.5}],
                }
            },
        )

        power_info = device.outlet_power_info
        assert power_info is None

    def test_power_info_not_available(self, make_device):
        """Test power info is not available."""
        device = make_device("outlet")

        power_info = device.outlet_power_info
        assert power_info is None

    def test_now_power_value(self, make_device):
        """Test nowPower value extraction."""
        device = make_device("outlet")
        device.outlet_power_info = {"nowPower": 75.3}

        power_info = device.outlet_power_info
        assert power_info["nowPower"] == 75.3


class TestLiproOutletEnergySensor:
    """Tests for LiproOutletEnergySensor entity."""

    def test_energy_list_sum(self, make_device):
        """Test energy list sum calculation."""
        device = make_device("outlet")
        device.outlet_power_info = {
            "energyList": [
                {"t": "20240101", "v": 10.5},
                {"t": "20240102", "v": 20.3},
                {"t": "20240103", "v": 5.2},
            ],
        }

        power_info = device.outlet_power_info
        energy_list = power_info.get("energyList", [])

        total_energy = 0.0
        for item in energy_list:
            energy_value = item.get("v")
            if energy_value is not None:
                total_energy += float(energy_value)

        assert total_energy == pytest.approx(36.0, rel=0.01)

    def test_energy_list_empty(self, make_device):
        """Test empty energy list."""
        device = make_device("outlet")
        device.outlet_power_info = {"energyList": []}

        power_info = device.outlet_power_info
        energy_list = power_info.get("energyList", [])

        assert len(energy_list) == 0

    def test_energy_list_missing(self, make_device):
        """Test missing energy list."""
        device = make_device("outlet")
        device.outlet_power_info = {}

        power_info = device.outlet_power_info
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
        from custom_components.lipro.const.properties import PROP_BATTERY, PROP_CHARGING

        assert PROP_BATTERY == "battery"
        assert PROP_CHARGING == "charging"


class TestLiproOutletPowerSensorEntity:
    """Tests for LiproOutletPowerSensor entity."""

    def test_native_value_returns_now_power(self, mock_coordinator, make_device):
        """Test native_value returns nowPower from power_info."""
        from custom_components.lipro.sensor import LiproOutletPowerSensor

        device = make_device("outlet")
        device.outlet_power_info = {"nowPower": 150.5}
        mock_coordinator.set_device(device)
        sensor = LiproOutletPowerSensor(mock_coordinator, device)

        assert sensor.native_value == 150.5

    def test_native_value_none_when_no_power_info(self, mock_coordinator, make_device):
        """Test native_value returns None when no power_info."""
        from custom_components.lipro.sensor import LiproOutletPowerSensor

        device = make_device("outlet")
        mock_coordinator.set_device(device)
        sensor = LiproOutletPowerSensor(mock_coordinator, device)

        assert sensor.native_value is None


class TestLiproOutletEnergySensorEntity:
    """Tests for LiproOutletEnergySensor entity."""

    def test_native_value_sums_energy_list(self, mock_coordinator, make_device):
        """Test native_value sums energy list values."""
        from custom_components.lipro.sensor import LiproOutletEnergySensor

        device = make_device("outlet")
        device.outlet_power_info = {
            "energyList": [
                {"t": "20240101", "v": 10.5},
                {"t": "20240102", "v": 20.3},
            ]
        }
        mock_coordinator.set_device(device)
        sensor = LiproOutletEnergySensor(mock_coordinator, device)

        assert sensor.native_value == pytest.approx(30.8, rel=0.01)

    def test_native_value_none_when_empty_list(self, mock_coordinator, make_device):
        """Test native_value returns None for empty energy list."""
        from custom_components.lipro.sensor import LiproOutletEnergySensor

        device = make_device("outlet")
        device.outlet_power_info = {"energyList": []}
        mock_coordinator.set_device(device)
        sensor = LiproOutletEnergySensor(mock_coordinator, device)

        assert sensor.native_value is None

    def test_native_value_none_when_no_power_info(self, mock_coordinator, make_device):
        """Test native_value returns None when power_info is missing."""
        from custom_components.lipro.sensor import LiproOutletEnergySensor

        device = make_device("outlet")
        mock_coordinator.set_device(device)
        sensor = LiproOutletEnergySensor(mock_coordinator, device)

        assert sensor.native_value is None

    def test_safe_energy_value_handles_invalid(self):
        """Test _safe_energy_value returns 0.0 for invalid values."""
        from custom_components.lipro.sensor import LiproOutletEnergySensor

        assert LiproOutletEnergySensor._safe_energy_value({"v": "invalid"}) == 0.0
        assert LiproOutletEnergySensor._safe_energy_value({"v": None}) == 0.0
        assert LiproOutletEnergySensor._safe_energy_value({}) == 0.0


class TestLiproBatterySensorEntity:
    """Tests for LiproBatterySensor entity."""

    def test_native_value_returns_battery_level(self, mock_coordinator, make_device):
        """Test native_value returns battery level."""
        from custom_components.lipro.sensor import LiproBatterySensor

        device = make_device("light", properties={"battery": "85"})
        mock_coordinator.set_device(device)
        sensor = LiproBatterySensor(mock_coordinator, device)

        assert sensor.native_value == 85

    def test_charging_icon(self, mock_coordinator, make_device):
        """Test icon returns charging icon when charging."""
        from custom_components.lipro.sensor import LiproBatterySensor

        device = make_device("light", properties={"battery": "50", "charging": "1"})
        mock_coordinator.set_device(device)
        sensor = LiproBatterySensor(mock_coordinator, device)

        assert sensor.icon == "mdi:battery-charging"

    def test_no_charging_icon(self, mock_coordinator, make_device):
        """Test icon returns None when not charging (let HA handle)."""
        from custom_components.lipro.sensor import LiproBatterySensor

        device = make_device("light", properties={"battery": "50", "charging": "0"})
        mock_coordinator.set_device(device)
        sensor = LiproBatterySensor(mock_coordinator, device)

        assert sensor.icon is None

    def test_extra_state_attributes_includes_charging(
        self, mock_coordinator, make_device
    ):
        """Test extra_state_attributes exposes charging state."""
        from custom_components.lipro.sensor import LiproBatterySensor

        device = make_device("light", properties={"battery": "50", "charging": "1"})
        mock_coordinator.set_device(device)
        sensor = LiproBatterySensor(mock_coordinator, device)

        assert sensor.extra_state_attributes == {"charging": True}


class TestLiproWiFiSignalSensorEntity:
    """Tests for LiproWiFiSignalSensor entity."""

    def test_native_value_returns_rssi(self, mock_coordinator, make_device):
        """Test native_value returns wifi_rssi."""
        from custom_components.lipro.sensor import LiproWiFiSignalSensor

        device = make_device("light", properties={"wifi_rssi": "-55"})
        mock_coordinator.set_device(device)
        sensor = LiproWiFiSignalSensor(mock_coordinator, device)

        assert sensor.native_value == -55

    def test_icon_excellent_signal(self, mock_coordinator, make_device):
        """Test icon for excellent signal (>= -50 dBm)."""
        from custom_components.lipro.sensor import LiproWiFiSignalSensor

        device = make_device("light", properties={"wifi_rssi": "-45"})
        mock_coordinator.set_device(device)
        sensor = LiproWiFiSignalSensor(mock_coordinator, device)

        assert sensor.icon == "mdi:wifi-strength-4"

    def test_icon_good_signal(self, mock_coordinator, make_device):
        """Test icon for good signal (>= -60 dBm)."""
        from custom_components.lipro.sensor import LiproWiFiSignalSensor

        device = make_device("light", properties={"wifi_rssi": "-58"})
        mock_coordinator.set_device(device)
        sensor = LiproWiFiSignalSensor(mock_coordinator, device)

        assert sensor.icon == "mdi:wifi-strength-3"

    def test_icon_fair_signal(self, mock_coordinator, make_device):
        """Test icon for fair signal (>= -70 dBm)."""
        from custom_components.lipro.sensor import LiproWiFiSignalSensor

        device = make_device("light", properties={"wifi_rssi": "-68"})
        mock_coordinator.set_device(device)
        sensor = LiproWiFiSignalSensor(mock_coordinator, device)

        assert sensor.icon == "mdi:wifi-strength-2"

    def test_icon_weak_signal(self, mock_coordinator, make_device):
        """Test icon for weak signal (>= -80 dBm)."""
        from custom_components.lipro.sensor import LiproWiFiSignalSensor

        device = make_device("light", properties={"wifi_rssi": "-75"})
        mock_coordinator.set_device(device)
        sensor = LiproWiFiSignalSensor(mock_coordinator, device)

        assert sensor.icon == "mdi:wifi-strength-1"

    def test_icon_very_weak_signal(self, mock_coordinator, make_device):
        """Test icon for very weak signal (< -80 dBm)."""
        from custom_components.lipro.sensor import LiproWiFiSignalSensor

        device = make_device("light", properties={"wifi_rssi": "-85"})
        mock_coordinator.set_device(device)
        sensor = LiproWiFiSignalSensor(mock_coordinator, device)

        assert sensor.icon == "mdi:wifi-strength-alert-outline"

    def test_icon_no_signal(self, mock_coordinator, make_device):
        """Test icon when no signal."""
        from custom_components.lipro.sensor import LiproWiFiSignalSensor

        device = make_device("light")
        mock_coordinator.set_device(device)
        sensor = LiproWiFiSignalSensor(mock_coordinator, device)

        assert sensor.icon == "mdi:wifi-off"

    def test_extra_state_attributes_includes_network_type(
        self, mock_coordinator, make_device
    ):
        """Test extra_state_attributes includes network_type when available."""
        from custom_components.lipro.sensor import LiproWiFiSignalSensor

        device = make_device(
            "light", properties={"wifi_rssi": "-55", "net_type": "wifi"}
        )
        mock_coordinator.set_device(device)
        sensor = LiproWiFiSignalSensor(mock_coordinator, device)

        assert sensor.extra_state_attributes == {"network_type": "wifi"}

    def test_extra_state_attributes_empty_without_network_type(
        self, mock_coordinator, make_device
    ):
        """Test extra_state_attributes is empty when network type is missing."""
        from custom_components.lipro.sensor import LiproWiFiSignalSensor

        device = make_device("light", properties={"wifi_rssi": "-55"})
        mock_coordinator.set_device(device)
        sensor = LiproWiFiSignalSensor(mock_coordinator, device)

        assert sensor.extra_state_attributes == {}


class TestSensorPlatformSetupCoverage:
    """Additional coverage for sensor setup helpers."""

    @pytest.mark.asyncio
    async def test_async_setup_entry_adds_entities(self, hass, mock_coordinator):
        """async_setup_entry should pass created entities to HA callback."""
        from custom_components.lipro import sensor as sensor_platform

        expected_entities = [object(), object()]
        create_entities = MagicMock(return_value=expected_entities)
        async_add_entities = MagicMock()
        entry = MockConfigEntry(domain=DOMAIN)
        entry.add_to_hass(hass)
        entry.runtime_data = mock_coordinator

        create_entities_patch = "create_device_entities"
        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(sensor_platform, create_entities_patch, create_entities)
            await sensor_platform.async_setup_entry(hass, entry, async_add_entities)

        create_entities.assert_called_once_with(
            mock_coordinator,
            sensor_platform._build_device_sensors,
        )
        async_add_entities.assert_called_once_with(expected_entities)

    def test_build_device_sensors_builds_expected_entities(
        self, mock_coordinator, make_device
    ):
        """_build_device_sensors should include outlet, battery and WiFi sensors."""
        from custom_components.lipro.sensor import (
            LiproBatterySensor,
            LiproOutletEnergySensor,
            LiproOutletPowerSensor,
            LiproWiFiSignalSensor,
            _build_device_sensors,
        )

        device = make_device(
            "outlet",
            properties={"battery": "85", "wifi_rssi": "-55"},
        )
        mock_coordinator.set_device(device)

        sensors = _build_device_sensors(mock_coordinator, device)

        assert [type(entity) for entity in sensors] == [
            LiproOutletPowerSensor,
            LiproOutletEnergySensor,
            LiproBatterySensor,
            LiproWiFiSignalSensor,
        ]
