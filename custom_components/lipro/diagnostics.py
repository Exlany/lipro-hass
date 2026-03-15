"""Diagnostics support thin adapter for the Lipro integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data

from .const.base import DOMAIN
from .control.diagnostics_surface import (
    async_get_config_entry_diagnostics as _async_get_config_entry_diagnostics_surface,
    async_get_device_diagnostics as _async_get_device_diagnostics_surface,
    build_device_diagnostics as _build_device_diagnostics_surface,
    extract_device_serial as _extract_device_serial_surface,
)
from .control.redaction import (
    OPTIONS_TO_REDACT as _OPTIONS_TO_REDACT,
    PROPERTY_KEYS_TO_REDACT as _PROPERTY_KEYS_TO_REDACT,
    TO_REDACT as _TO_REDACT,
    redact_device_properties as _redact_device_properties_surface,
    redact_entry_title as _redact_entry_title_surface,
    redact_property_value as _redact_property_value_surface,
)
from .core.anonymous_share import get_anonymous_share_manager

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceEntry

    from . import LiproConfigEntry
    from .core.device import LiproDevice


PROPERTY_KEYS_TO_REDACT = _PROPERTY_KEYS_TO_REDACT
TO_REDACT = _TO_REDACT
OPTIONS_TO_REDACT = _OPTIONS_TO_REDACT


def _redact_entry_title(title: Any) -> str:
    """Redact sensitive identifiers from config-entry title."""
    return _redact_entry_title_surface(title)


def _redact_property_value(value: Any, key: str | None = None) -> Any:
    """Recursively redact sensitive values in property payloads."""
    return _redact_property_value_surface(value, key)


def _redact_device_properties(properties: object) -> dict[str, Any]:
    """Redact sensitive keys from device properties."""
    if not isinstance(properties, dict):
        return {}
    return _redact_device_properties_surface(properties)


def _get_anonymous_share_manager_for_diagnostics(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> Any:
    """Resolve the anonymous-share manager for diagnostics surfaces."""
    return get_anonymous_share_manager(hass, entry_id=entry_id)


def _build_device_diagnostics(device: LiproDevice) -> dict[str, Any]:
    """Build redacted diagnostics payload for a single device."""
    return _build_device_diagnostics_surface(
        device,
        redact_device_properties=_redact_device_properties,
    )


def _extract_device_serial(device: DeviceEntry) -> str | None:
    """Extract Lipro serial from device identifiers."""
    return _extract_device_serial_surface(device, domain=DOMAIN)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    return await _async_get_config_entry_diagnostics_surface(
        hass,
        entry,
        get_anonymous_share_manager=_get_anonymous_share_manager_for_diagnostics,
        async_redact_data=async_redact_data,
        redact_entry_title=_redact_entry_title,
        build_device_diagnostics_fn=_build_device_diagnostics,
        to_redact=TO_REDACT,
        options_to_redact=OPTIONS_TO_REDACT,
    )


async def async_get_device_diagnostics(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    device: DeviceEntry,
) -> dict[str, Any]:
    """Return diagnostics for a single device entry."""
    return await _async_get_device_diagnostics_surface(
        hass,
        entry,
        device,
        domain=DOMAIN,
        async_redact_data=async_redact_data,
        redact_entry_title=_redact_entry_title,
        build_device_diagnostics_fn=_build_device_diagnostics,
        extract_device_serial_fn=_extract_device_serial,
        to_redact=TO_REDACT,
        options_to_redact=OPTIONS_TO_REDACT,
    )
