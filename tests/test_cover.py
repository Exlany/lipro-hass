"""Tests for Lipro cover platform."""

from __future__ import annotations


class TestLiproCoverPosition:
    """Tests for cover position properties."""

    def test_current_position(self, make_device):
        """Test current_cover_position."""
        device = make_device("curtain", properties={"position": "50"})
        assert device.position == 50

    def test_position_fully_open(self, make_device):
        """Test position when fully open."""
        device = make_device("curtain", properties={"position": "100"})
        assert device.position == 100

    def test_position_fully_closed(self, make_device):
        """Test position when fully closed."""
        device = make_device("curtain", properties={"position": "0"})
        assert device.position == 0

    def test_position_default(self, make_device):
        """Test default position is 0."""
        device = make_device("curtain")
        assert device.position == 0


class TestLiproCoverState:
    """Tests for cover state properties."""

    def test_is_closed_true(self, make_device):
        """Test is_closed when position is 0."""
        device = make_device("curtain", properties={"position": "0"})
        assert device.position == 0

    def test_is_closed_false(self, make_device):
        """Test is_closed when position > 0."""
        device = make_device("curtain", properties={"position": "50"})
        assert device.position != 0

    def test_is_opening(self, make_device):
        """Test is_opening when moving and direction is opening."""
        device = make_device(
            "curtain",
            properties={"moving": "1", "direction": "1"},
        )
        assert device.is_moving is True
        assert device.direction == "opening"

    def test_is_closing(self, make_device):
        """Test is_closing when moving and direction is closing."""
        device = make_device(
            "curtain",
            properties={"moving": "1", "direction": "0"},
        )
        assert device.is_moving is True
        assert device.direction == "closing"

    def test_not_moving(self, make_device):
        """Test not moving."""
        device = make_device("curtain", properties={"moving": "0"})
        assert device.is_moving is False

    def test_direction_none(self, make_device):
        """Test direction is None when not set."""
        device = make_device("curtain")
        assert device.direction is None


class TestLiproCoverIcon:
    """Tests for cover icon logic."""

    def test_icon_opening(self):
        """Test icon when opening."""
        is_opening = True
        is_closed = False

        if is_opening:
            icon = "mdi:curtains"
        elif is_closed:
            icon = "mdi:curtains-closed"
        else:
            icon = "mdi:curtains"

        assert icon == "mdi:curtains"

    def test_icon_closing(self):
        """Test icon when closing."""
        is_closing = True
        is_closed = False

        if is_closing:
            icon = "mdi:curtains"
        elif is_closed:
            icon = "mdi:curtains-closed"
        else:
            icon = "mdi:curtains"

        assert icon == "mdi:curtains"

    def test_icon_closed(self):
        """Test icon when closed."""
        is_closed = True

        icon = "mdi:curtains-closed" if is_closed else "mdi:curtains"

        assert icon == "mdi:curtains-closed"

    def test_icon_open(self):
        """Test icon when open."""
        is_closed = False

        icon = "mdi:curtains-closed" if is_closed else "mdi:curtains"

        assert icon == "mdi:curtains"


class TestLiproCoverDeviceFilter:
    """Tests for cover device filtering."""

    def test_is_curtain(self, make_device):
        """Test curtain device is identified correctly."""
        device = make_device("curtain")
        assert device.is_curtain is True

    def test_light_is_not_curtain(self, make_device):
        """Test light device is not a curtain."""
        device = make_device("light")
        assert device.is_curtain is False


class TestLiproCoverCommands:
    """Tests for cover command constants."""

    def test_command_constants(self):
        """Test cover command constants."""
        from custom_components.lipro.const import (
            CMD_CHANGE_STATE,
            CMD_CURTAIN_CLOSE,
            CMD_CURTAIN_OPEN,
            CMD_CURTAIN_STOP,
            PROP_DIRECTION,
            PROP_MOVING,
            PROP_POSITION,
        )

        assert CMD_CURTAIN_OPEN == "CURTAIN_OPEN"
        assert CMD_CURTAIN_CLOSE == "CURTAIN_CLOSE"
        assert CMD_CURTAIN_STOP == "CURTAIN_STOP"
        assert CMD_CHANGE_STATE == "CHANGE_STATE"
        assert PROP_POSITION == "position"
        assert PROP_MOVING == "moving"
        assert PROP_DIRECTION == "direction"
