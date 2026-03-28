"""Maintenance service helpers for the Lipro integration."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError

from ..runtime_types import LiproCoordinator
from .contracts import RefreshDevicesResult


class DeviceRefreshServiceLike(Protocol):
    """Minimal refresh-service contract consumed by maintenance helpers."""

    async def async_refresh_devices(self) -> None:
        """Refresh the devices owned by one runtime coordinator."""


type RuntimeEntryCoordinator = tuple[object, LiproCoordinator]


class RuntimeEntryCoordinatorProvider(Protocol):
    """Runtime entry/coordinator reader injected by the control plane."""

    def __call__(
        self,
        hass: HomeAssistant,
        *,
        entry_id: str | None = None,
    ) -> Sequence[RuntimeEntryCoordinator]:
        """Return loaded runtime entry/coordinator pairs."""


def _coerce_requested_entry_id(call: ServiceCall, *, attr_entry_id: str) -> str | None:
    """Return the requested entry id when the service call carries one."""
    raw_entry_id = call.data.get(attr_entry_id)
    return raw_entry_id if isinstance(raw_entry_id, str) else None


def _build_refresh_devices_result(
    *,
    refreshed_entries: int,
    requested_entry_id: str | None,
) -> RefreshDevicesResult:
    """Return the stable refresh-devices service response payload."""
    result: RefreshDevicesResult = {
        "success": True,
        "refreshed_entries": refreshed_entries,
    }
    if requested_entry_id:
        result["requested_entry_id"] = requested_entry_id
    return result


async def async_handle_refresh_devices(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    domain: str,
    attr_entry_id: str,
    iter_runtime_entry_coordinators: RuntimeEntryCoordinatorProvider,
) -> RefreshDevicesResult:
    """Handle refresh_devices service call."""
    requested_entry_id = _coerce_requested_entry_id(call, attr_entry_id=attr_entry_id)
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

    return _build_refresh_devices_result(
        refreshed_entries=refreshed_entries,
        requested_entry_id=requested_entry_id,
    )


__all__ = [
    "RuntimeEntryCoordinatorProvider",
    "async_handle_refresh_devices",
]
