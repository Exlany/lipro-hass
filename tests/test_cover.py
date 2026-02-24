"""Tests for Lipro cover platform."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


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


class TestLiproCoverEntityCommands:
    """Tests for LiproCover entity command methods."""

    @pytest.mark.asyncio
    async def test_open_cover(self, mock_coordinator, make_device):
        """Test async_open_cover sends CURTAIN_OPEN command."""
        device = make_device("curtain", properties={"position": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.cover import LiproCover

        cover = LiproCover(mock_coordinator, device)
        cover.async_write_ha_state = MagicMock()

        await cover.async_open_cover()

        mock_coordinator.async_send_command.assert_called_once_with(
            device, "CURTAIN_OPEN", None
        )

    @pytest.mark.asyncio
    async def test_close_cover(self, mock_coordinator, make_device):
        """Test async_close_cover sends CURTAIN_CLOSE command."""
        device = make_device("curtain", properties={"position": "100"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.cover import LiproCover

        cover = LiproCover(mock_coordinator, device)
        cover.async_write_ha_state = MagicMock()

        await cover.async_close_cover()

        mock_coordinator.async_send_command.assert_called_once_with(
            device, "CURTAIN_CLOSE", None
        )

    @pytest.mark.asyncio
    async def test_stop_cover(self, mock_coordinator, make_device):
        """Test async_stop_cover sends CURTAIN_STOP command."""
        device = make_device("curtain", properties={"position": "50", "moving": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.cover import LiproCover

        cover = LiproCover(mock_coordinator, device)
        cover.async_write_ha_state = MagicMock()

        await cover.async_stop_cover()

        mock_coordinator.async_send_command.assert_called_once_with(
            device, "CURTAIN_STOP", None
        )

    @pytest.mark.asyncio
    async def test_set_cover_position(self, mock_coordinator, make_device):
        """Test async_set_cover_position sends debounced CHANGE_STATE command."""
        from unittest.mock import AsyncMock

        device = make_device("curtain", properties={"position": "30"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.cover import LiproCover

        cover = LiproCover(mock_coordinator, device)
        cover.async_write_ha_state = MagicMock()

        # Mock the debouncer to call immediately
        cover._debouncer = MagicMock()
        async def _run_immediately(fn, *args):
            await fn(*args)

        cover._debouncer.async_call = AsyncMock(side_effect=_run_immediately)

        await cover.async_set_cover_position(position=75)

        # Verify optimistic state was set (position updated)
        assert device.properties.get("position") == "75"

    @pytest.mark.asyncio
    async def test_set_cover_position_clamps_value(self, mock_coordinator, make_device):
        """Test set_cover_position clamps position to 0-100."""
        from unittest.mock import AsyncMock

        device = make_device("curtain", properties={"position": "50"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.cover import LiproCover

        cover = LiproCover(mock_coordinator, device)
        cover.async_write_ha_state = MagicMock()

        cover._debouncer = MagicMock()
        async def _run_immediately(fn, *args):
            await fn(*args)

        cover._debouncer.async_call = AsyncMock(side_effect=_run_immediately)

        await cover.async_set_cover_position(position=150)

        assert device.properties.get("position") == "100"


class TestLiproCoverEntityProperties:
    """Tests for LiproCover entity property methods."""

    def test_current_cover_position(self, mock_coordinator, make_device):
        """Test current_cover_position returns device position."""
        device = make_device("curtain", properties={"position": "42"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.cover import LiproCover

        cover = LiproCover(mock_coordinator, device)
        assert cover.current_cover_position == 42

    def test_current_cover_position_none_when_missing(self, mock_coordinator, make_device):
        """Test current_cover_position returns None when position not in properties."""
        device = make_device("curtain")
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.cover import LiproCover

        cover = LiproCover(mock_coordinator, device)
        assert cover.current_cover_position is None

    def test_is_closed(self, mock_coordinator, make_device):
        """Test is_closed returns True when position is 0."""
        device = make_device("curtain", properties={"position": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.cover import LiproCover

        cover = LiproCover(mock_coordinator, device)
        assert cover.is_closed is True

    def test_is_not_closed(self, mock_coordinator, make_device):
        """Test is_closed returns False when position > 0."""
        device = make_device("curtain", properties={"position": "50"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.cover import LiproCover

        cover = LiproCover(mock_coordinator, device)
        assert cover.is_closed is False

    def test_is_opening(self, mock_coordinator, make_device):
        """Test is_opening when moving with opening direction."""
        device = make_device(
            "curtain", properties={"moving": "1", "direction": "1"}
        )
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.cover import LiproCover

        cover = LiproCover(mock_coordinator, device)
        assert cover.is_opening is True
        assert cover.is_closing is False

    def test_is_closing(self, mock_coordinator, make_device):
        """Test is_closing when moving with closing direction."""
        device = make_device(
            "curtain", properties={"moving": "1", "direction": "0"}
        )
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.cover import LiproCover

        cover = LiproCover(mock_coordinator, device)
        assert cover.is_closing is True
        assert cover.is_opening is False
