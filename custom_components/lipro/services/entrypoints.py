"""Thin service entrypoint facade for the Lipro integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from ..const.base import DOMAIN
from .registrations import SERVICE_REGISTRATIONS
from .registry import (
    async_setup_services as _async_setup_services_registry,
    remove_services as _remove_services_registry,
)


def remove_services(hass: HomeAssistant) -> None:
    """Remove all Lipro services registered by this integration."""
    _remove_services_registry(
        hass,
        domain=DOMAIN,
        registrations=SERVICE_REGISTRATIONS,
    )


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up Lipro services."""
    await _async_setup_services_registry(
        hass,
        domain=DOMAIN,
        registrations=SERVICE_REGISTRATIONS,
    )


__all__ = ["async_setup_services", "remove_services"]
