"""System health thin adapter for the Lipro integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant

from .const.base import VERSION
from .control.system_health_surface import (
    SystemHealthPayload,
    system_health_info as _system_health_info_surface,
)


async def async_register(
    hass: HomeAssistant,
    register: system_health.SystemHealthRegistration,
) -> None:
    """Register system health callbacks."""
    del hass
    register.async_register_info(
        cast(Callable[[HomeAssistant], Awaitable[dict[object, object]]], system_health_info)
    )


async def system_health_info(hass: HomeAssistant) -> SystemHealthPayload:
    """Return system health information for the Lipro integration."""
    return await _system_health_info_surface(hass, version=VERSION)
