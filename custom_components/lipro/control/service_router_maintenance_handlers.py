"""Maintenance handler family for ``control.service_router``."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall

from ..const.base import DOMAIN
from ..services import contracts as _contracts
from ..services.contracts import RefreshDevicesResult
from ..services.maintenance import (
    async_handle_refresh_devices as _async_handle_refresh_devices_service,
)
from .runtime_access import (
    iter_runtime_entry_coordinators as _iter_runtime_entry_coordinators,
)


async def async_handle_refresh_devices(
    hass: HomeAssistant,
    call: ServiceCall,
) -> RefreshDevicesResult:
    """Handle the public refresh-devices service."""
    return await _async_handle_refresh_devices_service(
        hass,
        call,
        domain=DOMAIN,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
        iter_runtime_entry_coordinators=_iter_runtime_entry_coordinators,
    )


__all__ = ['async_handle_refresh_devices']
