"""Formal control-plane owner for service lifecycle and registration tables."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from typing import Final, Protocol

from homeassistant.core import HomeAssistant, SupportsResponse

from ..services import contracts as _contracts
from ..services.registry import ServiceRegistration
from .runtime_access import (
    has_debug_mode_runtime_entry,
    is_debug_mode_enabled_for_entry,
)
from .service_router import (
    async_handle_add_schedule,
    async_handle_delete_schedules,
    async_handle_fetch_body_sensor_history,
    async_handle_fetch_door_sensor_history,
    async_handle_get_anonymous_share_report,
    async_handle_get_city,
    async_handle_get_developer_report,
    async_handle_get_schedules,
    async_handle_query_command_result,
    async_handle_query_user_cloud,
    async_handle_refresh_devices,
    async_handle_send_command,
    async_handle_submit_anonymous_share,
    async_handle_submit_developer_feedback,
)

type ServiceRegistrations = Sequence[object]
type SetupServicesFn = Callable[..., Awaitable[None]]
type RemoveServicesFn = Callable[..., None]
type HasDebugModeRuntimeEntryFn = Callable[[HomeAssistant], bool]
type GetRuntimeInfraLockFn = Callable[[HomeAssistant], asyncio.Lock | None]


PUBLIC_SERVICE_REGISTRATIONS: Final[tuple[ServiceRegistration, ...]] = (
    ServiceRegistration(
        _contracts.SERVICE_SEND_COMMAND,
        async_handle_send_command,
        _contracts.SERVICE_SEND_COMMAND_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_GET_SCHEDULES,
        async_handle_get_schedules,
        _contracts.SERVICE_GET_SCHEDULES_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_ADD_SCHEDULE,
        async_handle_add_schedule,
        _contracts.SERVICE_ADD_SCHEDULE_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_DELETE_SCHEDULES,
        async_handle_delete_schedules,
        _contracts.SERVICE_DELETE_SCHEDULES_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_SUBMIT_ANONYMOUS_SHARE,
        async_handle_submit_anonymous_share,
        _contracts.SERVICE_SUBMIT_ANONYMOUS_SHARE_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_GET_ANONYMOUS_SHARE_REPORT,
        async_handle_get_anonymous_share_report,
        _contracts.SERVICE_GET_ANONYMOUS_SHARE_REPORT_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_REFRESH_DEVICES,
        async_handle_refresh_devices,
        _contracts.SERVICE_REFRESH_DEVICES_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
)

DEVELOPER_SERVICE_REGISTRATIONS: Final[tuple[ServiceRegistration, ...]] = (
    ServiceRegistration(
        _contracts.SERVICE_GET_DEVELOPER_REPORT,
        async_handle_get_developer_report,
        _contracts.SERVICE_GET_DEVELOPER_REPORT_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
        async_handle_submit_developer_feedback,
        _contracts.SERVICE_SUBMIT_DEVELOPER_FEEDBACK_SCHEMA,
        SupportsResponse.OPTIONAL,
    ),
    ServiceRegistration(
        _contracts.SERVICE_QUERY_COMMAND_RESULT,
        async_handle_query_command_result,
        _contracts.SERVICE_QUERY_COMMAND_RESULT_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_GET_CITY,
        async_handle_get_city,
        None,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_QUERY_USER_CLOUD,
        async_handle_query_user_cloud,
        None,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_FETCH_BODY_SENSOR_HISTORY,
        async_handle_fetch_body_sensor_history,
        _contracts.SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
        SupportsResponse.ONLY,
    ),
    ServiceRegistration(
        _contracts.SERVICE_FETCH_DOOR_SENSOR_HISTORY,
        async_handle_fetch_door_sensor_history,
        _contracts.SERVICE_FETCH_SENSOR_HISTORY_SCHEMA,
        SupportsResponse.ONLY,
    ),
)

SERVICE_REGISTRATIONS: Final[tuple[ServiceRegistration, ...]] = (
    PUBLIC_SERVICE_REGISTRATIONS + DEVELOPER_SERVICE_REGISTRATIONS
)


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


__all__ = [
    'DEVELOPER_SERVICE_REGISTRATIONS',
    'PUBLIC_SERVICE_REGISTRATIONS',
    'SERVICE_REGISTRATIONS',
    'ServiceRegistry',
    'ServiceRegistryLike',
    'has_debug_mode_runtime_entry',
    'is_debug_mode_enabled_for_entry',
]
