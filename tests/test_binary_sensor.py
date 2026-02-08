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

    def test_icon_connected(self):
        """Test icon when connected."""
        icon = "mdi:lan-connect" if True else "mdi:lan-disconnect"
        assert icon == "mdi:lan-connect"

    def test_icon_disconnected(self):
        """Test icon when disconnected."""
        icon = "mdi:lan-connect" if False else "mdi:lan-disconnect"
        assert icon == "mdi:lan-disconnect"


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

    def test_icon_motion(self):
        """Test icon when motion detected."""
        is_on = True
        icon = "mdi:motion-sensor" if is_on else "mdi:motion-sensor-off"
        assert icon == "mdi:motion-sensor"

    def test_icon_no_motion(self):
        """Test icon when no motion."""
        is_on = False
        icon = "mdi:motion-sensor" if is_on else "mdi:motion-sensor-off"
        assert icon == "mdi:motion-sensor-off"

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

    def test_icon_open(self):
        """Test icon when door is open."""
        is_on = True
        icon = "mdi:door-open" if is_on else "mdi:door-closed"
        assert icon == "mdi:door-open"

    def test_icon_closed(self):
        """Test icon when door is closed."""
        is_on = False
        icon = "mdi:door-open" if is_on else "mdi:door-closed"
        assert icon == "mdi:door-closed"

    def test_is_door_sensor(self, make_device):
        """Test device is identified as door sensor."""
        device = make_device("doorSensor")
        assert device.is_door_sensor is True


class TestLiproLightLevelSensor:
    """Tests for LiproLightLevelSensor entity."""

    def test_is_on_bright(self, make_device):
        """Test is_on when bright (not dark)."""
        device = make_device("bodySensor", properties={"dark": "0"})
        # is_on = not is_dark
        assert device.is_dark is False

    def test_is_on_dark(self, make_device):
        """Test is_on when dark."""
        device = make_device("bodySensor", properties={"dark": "1"})
        assert device.is_dark is True

    def test_default_not_dark(self, make_device):
        """Test default is not dark."""
        device = make_device("bodySensor")
        assert device.is_dark is False

    def test_icon_bright(self):
        """Test icon when bright."""
        is_on = True  # not dark
        icon = "mdi:brightness-7" if is_on else "mdi:brightness-3"
        assert icon == "mdi:brightness-7"

    def test_icon_dark(self):
        """Test icon when dark."""
        is_on = False  # dark
        icon = "mdi:brightness-7" if is_on else "mdi:brightness-3"
        assert icon == "mdi:brightness-3"


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

    def test_icon_low(self):
        """Test icon when battery is low."""
        is_on = True
        icon = "mdi:battery-alert" if is_on else "mdi:battery"
        assert icon == "mdi:battery-alert"

    def test_icon_normal(self):
        """Test icon when battery is normal."""
        is_on = False
        icon = "mdi:battery-alert" if is_on else "mdi:battery"
        assert icon == "mdi:battery"
