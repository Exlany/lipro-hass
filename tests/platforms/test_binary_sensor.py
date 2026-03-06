"""Tests for Lipro binary sensor platform."""

from __future__ import annotations


class TestLiproConnectivitySensor:
    """Tests for LiproConnectivitySensor entity."""

    def test_is_on_connected(self, make_device):
        """Test is_on when device is connected."""
        device = make_device("light", properties={"connectState": "1"})
        assert device.is_connected is True

    def test_is_on_disconnected(self, make_device):
        """Test is_on when device is disconnected."""
        device = make_device("light", properties={"connectState": "0"})
        assert device.is_connected is False

    def test_default_connected(self, make_device):
        """Test default connection state is True."""
        device = make_device("light")
        assert device.is_connected is True

    def test_translation_key(self):
        """Test translation_key is set for icons.json mapping."""
        from custom_components.lipro.binary_sensor import LiproConnectivitySensor

        assert (
            LiproConnectivitySensor.__dict__["__attr_translation_key"] == "connectivity"
        )

    def test_available_when_device_offline(self, mock_coordinator, make_device):
        """Test connectivity sensor stays available when device goes offline.

        The connectivity sensor must remain available even when the device is
        disconnected, so it can correctly report the 'off' (disconnected) state
        instead of becoming unavailable.
        """
        from custom_components.lipro.binary_sensor import LiproConnectivitySensor

        device = make_device("light", properties={"connectState": "1"})
        mock_coordinator.devices[device.serial] = device
        sensor = LiproConnectivitySensor(mock_coordinator, device)

        # Device goes offline
        device.update_properties({"connectState": "0"})
        assert device.available is False
        assert device.is_connected is False

        # Connectivity sensor should still be available
        assert sensor.available is True
        # And should report disconnected (off)
        assert sensor.is_on is False

    def test_unavailable_when_coordinator_fails(self, mock_coordinator, make_device):
        """Test connectivity sensor is unavailable when coordinator fails."""
        from custom_components.lipro.binary_sensor import LiproConnectivitySensor

        device = make_device("light", properties={"connectState": "1"})
        mock_coordinator.devices[device.serial] = device
        sensor = LiproConnectivitySensor(mock_coordinator, device)

        # Coordinator fails
        mock_coordinator.last_update_success = False
        assert sensor.available is False


class TestLiproMotionSensor:
    """Tests for LiproMotionSensor entity."""

    def test_is_on_activated(self, make_device):
        """Test is_on when motion is detected."""
        device = make_device("bodySensor", properties={"human": "1"})
        assert device.is_activated is True

    def test_is_on_not_activated(self, make_device):
        """Test is_on when no motion."""
        device = make_device("bodySensor", properties={"human": "0"})
        assert device.is_activated is False

    def test_default_not_activated(self, make_device):
        """Test default is not activated."""
        device = make_device("bodySensor")
        assert device.is_activated is False

    def test_translation_key(self):
        """Test translation_key is set for icons.json mapping."""
        from custom_components.lipro.binary_sensor import LiproMotionSensor

        assert LiproMotionSensor.__dict__["__attr_translation_key"] == "motion"

    def test_is_body_sensor(self, make_device):
        """Test device is identified as body sensor."""
        device = make_device("bodySensor")
        assert device.is_body_sensor is True


class TestLiproDoorSensor:
    """Tests for LiproDoorSensor entity."""

    def test_is_on_open(self, make_device):
        """Test is_on when door is open."""
        device = make_device("doorSensor", properties={"doorOpen": "1"})
        assert device.door_is_open is True

    def test_is_on_closed(self, make_device):
        """Test is_on when door is closed."""
        device = make_device("doorSensor", properties={"doorOpen": "0"})
        assert device.door_is_open is False

    def test_default_closed(self, make_device):
        """Test default is closed."""
        device = make_device("doorSensor")
        assert device.door_is_open is False

    def test_translation_key(self):
        """Test translation_key is set for icons.json mapping."""
        from custom_components.lipro.binary_sensor import LiproDoorSensor

        assert LiproDoorSensor.__dict__["__attr_translation_key"] == "door"

    def test_is_door_sensor(self, make_device):
        """Test device is identified as door sensor."""
        device = make_device("doorSensor")
        assert device.is_door_sensor is True


class TestLiproLightLevelSensor:
    """Tests for LiproLightLevelSensor entity."""

    def test_is_on_bright(self, make_device):
        """Test is_on when bright (not dark)."""
        device = make_device("bodySensor", properties={"dark": "0"})
        assert device.is_dark is False

    def test_is_on_dark(self, make_device):
        """Test is_on when dark."""
        device = make_device("bodySensor", properties={"dark": "1"})
        assert device.is_dark is True

    def test_default_not_dark(self, make_device):
        """Test default is not dark."""
        device = make_device("bodySensor")
        assert device.is_dark is False

    def test_invert_class_attribute(self):
        """Test _invert class attribute is set for inverted light level logic."""
        from custom_components.lipro.binary_sensor import LiproLightLevelSensor

        assert LiproLightLevelSensor._invert is True
        assert LiproLightLevelSensor.__dict__["__attr_translation_key"] == "light"


class TestLiproBatteryLowSensor:
    """Tests for LiproBatteryLowSensor entity."""

    def test_is_on_low_battery(self, make_device):
        """Test is_on when battery is low."""
        device = make_device("bodySensor", properties={"lowBattery": "1"})
        assert device.low_battery is True

    def test_is_on_normal_battery(self, make_device):
        """Test is_on when battery is normal."""
        device = make_device("bodySensor", properties={"lowBattery": "0"})
        assert device.low_battery is False

    def test_default_normal_battery(self, make_device):
        """Test default is normal battery."""
        device = make_device("bodySensor")
        assert device.low_battery is False

    def test_translation_key(self):
        """Test translation_key is set for icons.json mapping."""
        from custom_components.lipro.binary_sensor import LiproBatteryLowSensor

        assert LiproBatteryLowSensor.__dict__["__attr_translation_key"] == "battery"
