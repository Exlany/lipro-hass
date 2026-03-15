"""Formal control-plane owner for Home Assistant service lifecycle."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from typing import Protocol

from homeassistant.core import HomeAssistant

type ServiceRegistrations = Sequence[object]
type SetupServicesFn = Callable[..., Awaitable[None]]
type RemoveServicesFn = Callable[..., None]
type HasDebugModeRuntimeEntryFn = Callable[[HomeAssistant], bool]
type GetRuntimeInfraLockFn = Callable[[HomeAssistant], asyncio.Lock | None]


class ServiceRegistryLike(Protocol):
    """Protocol for service registry synchronization collaborators."""

    async def async_sync(self, hass: HomeAssistant) -> None:
        """Synchronize services for the current runtime state."""

    async def async_sync_with_lock(self, hass: HomeAssistant) -> None:
        """Synchronize services while holding the shared lock."""

    def remove_all(self, hass: HomeAssistant) -> None:
        """Remove all registered services for the domain."""


class ServiceRegistry:
    """Own service registration, debug gating, and synchronization."""

    def __init__(
        self,
        *,
        domain: str,
        public_registrations: ServiceRegistrations,
        developer_registrations: ServiceRegistrations,
        service_registrations: ServiceRegistrations,
        async_setup_services: SetupServicesFn,
        remove_services: RemoveServicesFn,
        has_debug_mode_runtime_entry: HasDebugModeRuntimeEntryFn,
        get_runtime_infra_lock: GetRuntimeInfraLockFn,
    ) -> None:
        """Initialize the control-plane owner with explicit collaborators."""
        self._domain = domain
        self._public_registrations = public_registrations
        self._developer_registrations = developer_registrations
        self._service_registrations = service_registrations
        self._async_setup_services = async_setup_services
        self._remove_services = remove_services
        self._has_debug_mode_runtime_entry = has_debug_mode_runtime_entry
        self._get_runtime_infra_lock = get_runtime_infra_lock

    async def async_sync(self, hass: HomeAssistant) -> None:
        """Synchronize shared services with active runtime state."""
        await self._async_setup_services(
            hass,
            domain=self._domain,
            registrations=self._public_registrations,
        )
        if self._has_debug_mode_runtime_entry(hass):
            await self._async_setup_services(
                hass,
                domain=self._domain,
                registrations=self._developer_registrations,
            )
            return

        self._remove_services(
            hass,
            domain=self._domain,
            registrations=self._developer_registrations,
        )

    async def async_sync_with_lock(self, hass: HomeAssistant) -> None:
        """Synchronize services while holding the shared runtime-infra lock."""
        lock = self._get_runtime_infra_lock(hass)
        if lock is None:
            await self.async_sync(hass)
            return

        async with lock:
            await self.async_sync(hass)

    def remove_all(self, hass: HomeAssistant) -> None:
        """Remove all registered Lipro services."""
        self._remove_services(
            hass,
            domain=self._domain,
            registrations=self._service_registrations,
        )
