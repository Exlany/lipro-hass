"""Unit tests for declarative entity command objects (Phase G)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.const.properties import (
    CMD_PANEL_CHANGE_STATE,
    CMD_POWER_OFF,
    CMD_POWER_ON,
    PROP_POWER_STATE,
)
from custom_components.lipro.entities.commands import (
    PanelPropertyToggleCommand,
    PowerCommand,
    PropertyToggleCommand,
    SliderCommand,
)


@pytest.mark.asyncio
async def test_power_command_turn_on_off_calls_async_send_command() -> None:
    """PowerCommand delegates to entity.async_send_command with optimistic state."""
    entity = MagicMock()
    entity.async_send_command = AsyncMock(return_value=True)

    command = PowerCommand()
    assert await command.turn_on(entity) is True
    entity.async_send_command.assert_awaited_with(
        CMD_POWER_ON,
        None,
        {PROP_POWER_STATE: "1"},
    )

    entity.async_send_command.reset_mock()
    assert await command.turn_off(entity) is True
    entity.async_send_command.assert_awaited_with(
        CMD_POWER_OFF,
        None,
        {PROP_POWER_STATE: "0"},
    )


@pytest.mark.asyncio
async def test_property_toggle_command_turn_on_off_calls_async_change_state() -> None:
    """PropertyToggleCommand delegates to entity.async_change_state."""
    entity = MagicMock()
    entity.async_change_state = AsyncMock(return_value=True)

    command = PropertyToggleCommand("fadeState")
    assert await command.turn_on(entity) is True
    entity.async_change_state.assert_awaited_with({"fadeState": "1"})

    entity.async_change_state.reset_mock()
    assert await command.turn_off(entity) is True
    entity.async_change_state.assert_awaited_with({"fadeState": "0"})


@pytest.mark.asyncio
async def test_slider_command_clamps_value_and_debounces() -> None:
    """SliderCommand clamps values and always uses debounced change_state."""
    entity = MagicMock()
    entity.async_change_state = AsyncMock(return_value=None)

    command = SliderCommand("brightness", min_value=1, max_value=100)
    await command.set_value(entity, 0)
    entity.async_change_state.assert_awaited_with(
        {"brightness": 1},
        debounced=True,
    )


@pytest.mark.asyncio
async def test_panel_property_toggle_command_builds_panel_payload() -> None:
    """PanelPropertyToggleCommand includes panelType as second payload item."""
    device = MagicMock()
    device.panel_type = 1

    entity = MagicMock()
    entity.device = device
    entity.async_send_command = AsyncMock(return_value=True)

    command = PanelPropertyToggleCommand("led")
    assert await command.turn_on(entity) is True
    entity.async_send_command.assert_awaited_with(
        CMD_PANEL_CHANGE_STATE,
        [
            {"key": "led", "value": "1"},
            {"key": "panelType", "value": "1"},
        ],
        {"led": "1"},
    )
