"""Service handlers for diagnostics operations.

This module keeps the stable handler home for diagnostics while delegating the
heavier command-result and optional-capability branches to focused collaborators.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import NoReturn

from homeassistant.core import HomeAssistant, ServiceCall

from ...core import LiproApiError
from ..execution import ServiceErrorRaiser
from .capability_handlers import (
    async_handle_fetch_body_sensor_history as _async_handle_fetch_body_sensor_history_flow,
    async_handle_fetch_door_sensor_history as _async_handle_fetch_door_sensor_history_flow,
    async_handle_get_city as _async_handle_get_city_flow,
    async_handle_query_user_cloud as _async_handle_query_user_cloud_flow,
)
from .command_result_handlers import (
    _build_last_error_payload,
    async_handle_query_command_result as _async_handle_query_command_result_flow,
)
from .helper_support import (
    _coerce_service_float,
    _coerce_service_int,
    _get_required_service_string,
)
from .helpers import _async_get_first_authenticated_coordinator_capability_result
from .types import (
    CapabilityResponse,
    GetDeviceAndCoordinator,
    OptionalCapabilityCaller,
    QueryCommandResultResponse,
    RuntimeCoordinatorIterator,
    SensorHistoryResponse,
    SensorHistoryResultBuilder,
)


async def async_handle_query_command_result(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    attr_msg_sn: str,
    attr_max_attempts: str,
    attr_time_budget_seconds: str,
    raise_service_error: ServiceErrorRaiser,
) -> QueryCommandResultResponse:
    """Handle the query_command_result service."""
    return await _async_handle_query_command_result_flow(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        get_required_service_string=_get_required_service_string,
        coerce_service_int=_coerce_service_int,
        coerce_service_float=_coerce_service_float,
        attr_msg_sn=attr_msg_sn,
        attr_max_attempts=attr_max_attempts,
        attr_time_budget_seconds=attr_time_budget_seconds,
        raise_service_error=raise_service_error,
    )


async def async_handle_get_city(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    iter_runtime_coordinators: RuntimeCoordinatorIterator,
    raise_optional_error: Callable[[str, LiproApiError], NoReturn],
    service_get_city: str,
) -> CapabilityResponse:
    """Handle the get_city service."""
    return await _async_handle_get_city_flow(
        hass,
        call,
        iter_runtime_coordinators=iter_runtime_coordinators,
        raise_optional_error=raise_optional_error,
        async_get_first_authenticated_coordinator_capability_result=_async_get_first_authenticated_coordinator_capability_result,
        service_get_city=service_get_city,
    )


async def async_handle_query_user_cloud(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    iter_runtime_coordinators: RuntimeCoordinatorIterator,
    raise_optional_error: Callable[[str, LiproApiError], NoReturn],
    service_query_user_cloud: str,
) -> CapabilityResponse:
    """Handle the query_user_cloud service."""
    return await _async_handle_query_user_cloud_flow(
        hass,
        call,
        iter_runtime_coordinators=iter_runtime_coordinators,
        raise_optional_error=raise_optional_error,
        async_get_first_authenticated_coordinator_capability_result=_async_get_first_authenticated_coordinator_capability_result,
        service_query_user_cloud=service_query_user_cloud,
    )


async def async_handle_fetch_body_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    async_call_optional_capability: OptionalCapabilityCaller,
    build_sensor_history_result: SensorHistoryResultBuilder,
    attr_sensor_device_id: str,
    attr_mesh_type: str,
    service_fetch_body_sensor_history: str,
) -> SensorHistoryResponse:
    """Handle the fetch_body_sensor_history service."""
    return await _async_handle_fetch_body_sensor_history_flow(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        async_call_optional_capability=async_call_optional_capability,
        build_sensor_history_result=build_sensor_history_result,
        get_required_service_string=_get_required_service_string,
        attr_sensor_device_id=attr_sensor_device_id,
        attr_mesh_type=attr_mesh_type,
        service_fetch_body_sensor_history=service_fetch_body_sensor_history,
    )


async def async_handle_fetch_door_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    async_call_optional_capability: OptionalCapabilityCaller,
    build_sensor_history_result: SensorHistoryResultBuilder,
    attr_sensor_device_id: str,
    attr_mesh_type: str,
    service_fetch_door_sensor_history: str,
) -> SensorHistoryResponse:
    """Handle the fetch_door_sensor_history service."""
    return await _async_handle_fetch_door_sensor_history_flow(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        async_call_optional_capability=async_call_optional_capability,
        build_sensor_history_result=build_sensor_history_result,
        get_required_service_string=_get_required_service_string,
        attr_sensor_device_id=attr_sensor_device_id,
        attr_mesh_type=attr_mesh_type,
        service_fetch_door_sensor_history=service_fetch_door_sensor_history,
    )


__all__ = [
    "_build_last_error_payload",
    "async_handle_fetch_body_sensor_history",
    "async_handle_fetch_door_sensor_history",
    "async_handle_get_city",
    "async_handle_query_command_result",
    "async_handle_query_user_cloud",
]
