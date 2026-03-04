"""Cover platform for Lipro integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)

from .const import (
    CMD_CURTAIN_CLOSE,
    CMD_CURTAIN_OPEN,
    CMD_CURTAIN_STOP,
    DIRECTION_CLOSING,
    DIRECTION_OPENING,
    PROP_DIRECTION,
    PROP_MOVING,
    PROP_POSITION,
)
from .entities.base import LiproEntity
from .helpers.platform import create_platform_entities

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry

# Limit parallel updates to avoid overwhelming the API
PARALLEL_UPDATES = 1

_STATE_OPENING = "opening"
_STATE_CLOSING = "closing"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro covers."""
    entities = create_platform_entities(
        entry.runtime_data,
        device_filter=lambda d: d.is_curtain,
        entity_factory=LiproCover,
    )
    async_add_entities(entities)


class LiproCover(LiproEntity, CoverEntity):
    """Representation of a Lipro curtain."""

    _attr_device_class = CoverDeviceClass.CURTAIN
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )
    _attr_translation_key = "curtain"
    _attr_name = None  # Use device name

    @property
    def current_cover_position(self) -> int | None:
        """Return current position of cover (0-100).

        Lipro API: position 0=fully closed, 100=fully open
        Home Assistant: same convention (0=closed, 100=open)
        No conversion needed.
        """
        if PROP_POSITION not in self.device.properties:
            return None
        return self.device.position

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed.

        Lipro API: position=0 means fully closed.
        """
        if PROP_POSITION not in self.device.properties:
            return None
        return self.device.position == 0

    @property
    def is_opening(self) -> bool:
        """Return if the cover is opening."""
        direction = self.device.direction
        return self.device.is_moving and direction == _STATE_OPENING

    @property
    def is_closing(self) -> bool:
        """Return if the cover is closing."""
        direction = self.device.direction
        return self.device.is_moving and direction == _STATE_CLOSING

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        await self.async_send_command(
            CMD_CURTAIN_OPEN,
            None,
            {PROP_MOVING: "1", PROP_DIRECTION: DIRECTION_OPENING},
        )

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        await self.async_send_command(
            CMD_CURTAIN_CLOSE,
            None,
            {PROP_MOVING: "1", PROP_DIRECTION: DIRECTION_CLOSING},
        )

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        await self.async_send_command(CMD_CURTAIN_STOP, None, {PROP_MOVING: "0"})

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Set cover position."""
        position = max(0, min(100, kwargs[ATTR_POSITION]))
        optimistic: dict[str, str | int] = {PROP_POSITION: position}

        # Optimistically update direction based on target vs current position
        current = self.current_cover_position
        if current is not None and position != current:
            optimistic[PROP_DIRECTION] = (
                DIRECTION_OPENING if position > current else DIRECTION_CLOSING
            )
            optimistic[PROP_MOVING] = "1"

        # Use debounce for position slider to avoid flooding API
        await self.async_change_state(
            {PROP_POSITION: position},
            optimistic_state=optimistic,
            debounced=True,
        )
