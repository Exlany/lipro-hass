"""Maintenance service helpers for the Lipro integration."""

from __future__ import annotations

from typing import Protocol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError

from .contracts import RefreshDevicesResult


class DeviceRefreshServiceLike(Protocol):
    """Minimal refresh-service contract consumed by maintenance helpers."""

    async def async_refresh_devices(self) -> None:
        """Refresh the devices owned by one runtime coordinator."""


class RefreshCoordinatorLike(Protocol):
    """Coordinator contract needed by refresh_devices."""

    device_refresh_service: DeviceRefreshServiceLike


type RuntimeEntryCoordinator = tuple[object, RefreshCoordinatorLike]


class RuntimeEntryCoordinatorProvider(Protocol):
    """Runtime entry/coordinator reader injected by the control plane."""

    def __call__(
        self,
        hass: HomeAssistant,
        *,
        entry_id: str | None = None,
    ) -> list[RuntimeEntryCoordinator]:
        """Return loaded runtime entry/coordinator pairs."""


async def async_handle_refresh_devices(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    domain: str,
    attr_entry_id: str,
    iter_runtime_entry_coordinators: RuntimeEntryCoordinatorProvider,
) -> RefreshDevicesResult:
    """Handle refresh_devices service call."""
    raw_entry_id = call.data.get(attr_entry_id)
    requested_entry_id = raw_entry_id if isinstance(raw_entry_id, str) else None
    targets = iter_runtime_entry_coordinators(hass, entry_id=requested_entry_id)

    if requested_entry_id and not targets:
        raise ServiceValidationError(
            translation_domain=domain,
            translation_key="entry_not_found",
            translation_placeholders={"entry_id": requested_entry_id},
        )

    refreshed_entries = 0
    for _entry, coordinator in targets:
        await coordinator.device_refresh_service.async_refresh_devices()
        refreshed_entries += 1

    result: RefreshDevicesResult = {
        "success": True,
        "refreshed_entries": refreshed_entries,
    }
    if requested_entry_id:
        result["requested_entry_id"] = requested_entry_id
    return result


__all__ = [
    "RuntimeEntryCoordinatorProvider",
    "async_handle_refresh_devices",
]
