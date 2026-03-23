"""Focused optional-capability diagnostics handlers."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import NoReturn

from homeassistant.core import HomeAssistant, ServiceCall

from ...core import LiproApiError
from .types import (
    CapabilityPayload,
    CapabilityResponse,
    DiagnosticsCoordinator,
    GetDeviceAndCoordinator,
    OptionalCapabilityCaller,
    RuntimeCoordinatorIterator,
    SensorHistoryClientMethod,
    SensorHistoryResponse,
    SensorHistoryResultBuilder,
)

CapabilityResultGetter = Callable[..., Awaitable[tuple[bool, CapabilityPayload | None, LiproApiError | None]]]
RequiredServiceStringGetter = Callable[[ServiceCall, str], str]


async def async_handle_get_city(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    iter_runtime_coordinators: RuntimeCoordinatorIterator,
    raise_optional_error: Callable[[str, LiproApiError], NoReturn],
    async_get_first_authenticated_coordinator_capability_result: CapabilityResultGetter,
    service_get_city: str,
) -> CapabilityResponse:
    """Handle the get_city service."""
    del call
    has_result, result, last_err = await async_get_first_authenticated_coordinator_capability_result(
        iter_runtime_coordinators(hass),
        capability="get_city",
        collector=lambda coordinator: coordinator.protocol_service.async_get_city(),
    )
    if has_result and result is not None:
        return {"result": result}
    if last_err is not None:
        raise_optional_error(service_get_city, last_err)
    return {"result": {}}


async def async_handle_query_user_cloud(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    iter_runtime_coordinators: RuntimeCoordinatorIterator,
    raise_optional_error: Callable[[str, LiproApiError], NoReturn],
    async_get_first_authenticated_coordinator_capability_result: CapabilityResultGetter,
    service_query_user_cloud: str,
) -> CapabilityResponse:
    """Handle the query_user_cloud service."""
    del call
    has_result, result, last_err = await async_get_first_authenticated_coordinator_capability_result(
        iter_runtime_coordinators(hass),
        capability="query_user_cloud",
        collector=lambda coordinator: coordinator.protocol_service.async_query_user_cloud(),
    )
    if has_result and result is not None:
        return {"result": result}
    if last_err is not None:
        raise_optional_error(service_query_user_cloud, last_err)
    return {"result": {}}


async def _async_handle_fetch_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    async_call_optional_capability: OptionalCapabilityCaller,
    build_sensor_history_result: SensorHistoryResultBuilder,
    get_required_service_string: RequiredServiceStringGetter,
    attr_sensor_device_id: str,
    attr_mesh_type: str,
    service_name: str,
    get_client_method: Callable[[DiagnosticsCoordinator], SensorHistoryClientMethod],
) -> SensorHistoryResponse:
    """Shared handler for sensor-history diagnostics services."""
    device, coordinator = await get_device_and_coordinator(hass, call)
    sensor_device_id = get_required_service_string(call, attr_sensor_device_id)
    mesh_type = get_required_service_string(call, attr_mesh_type)
    result = await async_call_optional_capability(
        service_name,
        get_client_method(coordinator),
        coordinator=coordinator,
        device_id=device.serial,
        device_type=device.device_type,
        sensor_device_id=sensor_device_id,
        mesh_type=mesh_type,
    )
    return build_sensor_history_result(
        device.serial,
        sensor_device_id,
        mesh_type,
        result,
    )


async def async_handle_fetch_body_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    async_call_optional_capability: OptionalCapabilityCaller,
    build_sensor_history_result: SensorHistoryResultBuilder,
    get_required_service_string: RequiredServiceStringGetter,
    attr_sensor_device_id: str,
    attr_mesh_type: str,
    service_fetch_body_sensor_history: str,
) -> SensorHistoryResponse:
    """Handle the fetch_body_sensor_history service."""
    return await _async_handle_fetch_sensor_history(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        async_call_optional_capability=async_call_optional_capability,
        build_sensor_history_result=build_sensor_history_result,
        get_required_service_string=get_required_service_string,
        attr_sensor_device_id=attr_sensor_device_id,
        attr_mesh_type=attr_mesh_type,
        service_name=service_fetch_body_sensor_history,
        get_client_method=lambda coordinator: (
            coordinator.protocol_service.async_fetch_body_sensor_history
        ),
    )


async def async_handle_fetch_door_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    async_call_optional_capability: OptionalCapabilityCaller,
    build_sensor_history_result: SensorHistoryResultBuilder,
    get_required_service_string: RequiredServiceStringGetter,
    attr_sensor_device_id: str,
    attr_mesh_type: str,
    service_fetch_door_sensor_history: str,
) -> SensorHistoryResponse:
    """Handle the fetch_door_sensor_history service."""
    return await _async_handle_fetch_sensor_history(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        async_call_optional_capability=async_call_optional_capability,
        build_sensor_history_result=build_sensor_history_result,
        get_required_service_string=get_required_service_string,
        attr_sensor_device_id=attr_sensor_device_id,
        attr_mesh_type=attr_mesh_type,
        service_name=service_fetch_door_sensor_history,
        get_client_method=lambda coordinator: (
            coordinator.protocol_service.async_fetch_door_sensor_history
        ),
    )
