"""Declarative command helpers for Lipro entities.

Phase G introduces small command objects that standardize the write-side
(Commands) of platform entities:

- Entities stay focused on business logic.
- Command payload shapes are unified across platforms.
- Optimistic state handling remains centralized in ``LiproEntity``.

These helpers are intentionally lightweight: they do not implement a full CQRS
framework, only enforce consistent call paths.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from ..const.properties import (
    CMD_PANEL_CHANGE_STATE,
    CMD_POWER_OFF,
    CMD_POWER_ON,
    PROP_POWER_STATE,
)


class CommandEntity(Protocol):
    """Minimal entity surface required by command objects."""

    async def async_send_command(
        self,
        command: str,
        properties: list[dict[str, str]] | None = None,
        optimistic_state: dict[str, Any] | None = None,
    ) -> bool:
        """Send one command via the entity command pipeline."""

    async def async_change_state(
        self,
        properties: Mapping[str, Any],
        *,
        optimistic_state: Mapping[str, Any] | None = None,
        debounced: bool = False,
    ) -> bool | None:
        """Send a CHANGE_STATE command via the entity pipeline."""


class PanelTypeProvider(Protocol):
    """Device surface required for panel feature commands."""

    panel_type: int


class PanelCommandEntity(CommandEntity, Protocol):
    """Entity surface required for panel feature commands."""

    device: PanelTypeProvider


@dataclass(frozen=True, slots=True)
class PowerCommand:
    """Standard on/off command using the POWER_ON/OFF endpoints."""

    on_cmd: str = CMD_POWER_ON
    off_cmd: str = CMD_POWER_OFF
    state_key: str = PROP_POWER_STATE
    on_value: str = "1"
    off_value: str = "0"

    async def turn_on(self, entity: CommandEntity) -> bool:
        """Send a power-on command with optimistic state."""
        return await entity.async_send_command(
            self.on_cmd,
            None,
            {self.state_key: self.on_value},
        )

    async def turn_off(self, entity: CommandEntity) -> bool:
        """Send a power-off command with optimistic state."""
        return await entity.async_send_command(
            self.off_cmd,
            None,
            {self.state_key: self.off_value},
        )


@dataclass(frozen=True, slots=True)
class PropertyToggleCommand:
    """Standard on/off toggle backed by one CHANGE_STATE property."""

    property_key: str
    on_value: str = "1"
    off_value: str = "0"

    async def turn_on(self, entity: CommandEntity) -> bool | None:
        """Enable the feature property."""
        return await entity.async_change_state({self.property_key: self.on_value})

    async def turn_off(self, entity: CommandEntity) -> bool | None:
        """Disable the feature property."""
        return await entity.async_change_state({self.property_key: self.off_value})


@dataclass(frozen=True, slots=True)
class SliderCommand:
    """Continuous value adjustment command using debounced CHANGE_STATE."""

    property_key: str
    min_value: int = 0
    max_value: int = 100

    async def set_value(self, entity: CommandEntity, value: int) -> None:
        """Send a debounced slider update (clamped)."""
        clamped = max(self.min_value, min(self.max_value, value))
        await entity.async_change_state(
            {self.property_key: clamped},
            debounced=True,
        )


@dataclass(frozen=True, slots=True)
class PanelPropertyToggleCommand:
    """Panel feature toggle command requiring an extra panelType property."""

    property_key: str
    command: str = CMD_PANEL_CHANGE_STATE
    panel_type_key: str = "panelType"
    on_value: str = "1"
    off_value: str = "0"

    async def turn_on(self, entity: PanelCommandEntity) -> bool:
        """Enable the panel feature."""
        return await self._send(entity, enabled=True)

    async def turn_off(self, entity: PanelCommandEntity) -> bool:
        """Disable the panel feature."""
        return await self._send(entity, enabled=False)

    async def _send(self, entity: PanelCommandEntity, *, enabled: bool) -> bool:
        value = self.on_value if enabled else self.off_value
        payload = [
            {"key": self.property_key, "value": value},
            {"key": self.panel_type_key, "value": str(entity.device.panel_type)},
        ]
        return await entity.async_send_command(
            self.command,
            payload,
            {self.property_key: value},
        )


__all__ = [
    "CommandEntity",
    "PanelCommandEntity",
    "PanelPropertyToggleCommand",
    "PanelTypeProvider",
    "PowerCommand",
    "PropertyToggleCommand",
    "SliderCommand",
]
