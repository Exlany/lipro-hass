"""Service handlers for diagnostics operations.

This module contains the concrete service handler implementations
for command result queries, sensor history fetching, and other
diagnostics operations.
"""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import NoReturn, cast

from homeassistant.core import HomeAssistant, ServiceCall

from ...core import LiproApiError
from ...core.command.result import (
    CommandResultPayload,
    build_progressive_retry_delays,
    classify_command_result_payload,
    poll_command_result_state,
    query_command_result_once,
)
from ..execution import ServiceErrorRaiser, async_execute_coordinator_call
from .helpers import (
    _async_get_first_coordinator_capability_result,
    _coerce_service_float,
    _coerce_service_int,
    _get_required_service_string,
)
from .types import (
    CapabilityPayload,
    DiagnosticsCoordinator,
    DiagnosticsDevice,
    GetDeviceAndCoordinator,
    LastErrorPayload,
    OptionalCapabilityCaller,
    QueryCommandResultResponse,
    RuntimeCoordinatorIterator,
    SensorHistoryClientMethod,
    SensorHistoryResultBuilder,
)

_LOGGER = logging.getLogger(__name__)
_QUERY_COMMAND_RESULT_DIAGNOSTIC_BASE_DELAY_SECONDS = 0.35
_DEFAULT_QUERY_COMMAND_RESULT_MAX_ATTEMPTS = 6
_DEFAULT_QUERY_COMMAND_RESULT_TIME_BUDGET_SECONDS = 3.0


def _build_last_error_payload(err: LiproApiError | None) -> LastErrorPayload | None:
    """Build serializable last-error details for diagnostics output."""
    if err is None:
        return None
    payload: LastErrorPayload = {}
    if err.code is not None:
        payload["code"] = err.code
    message = str(err).strip()
    if message:
        payload["message"] = message
    return payload or None


async def _async_query_command_result_with_optional_polling(
    *,
    coordinator: DiagnosticsCoordinator,
    device: DiagnosticsDevice,
    msg_sn: str,
    max_attempts: int,
    time_budget_seconds: float,
    raise_service_error: ServiceErrorRaiser,
) -> dict[str, object]:
    """Query command-result diagnostics with bounded polling."""
    retry_delays_seconds = build_progressive_retry_delays(
        base_delay_seconds=_QUERY_COMMAND_RESULT_DIAGNOSTIC_BASE_DELAY_SECONDS,
        time_budget_seconds=time_budget_seconds,
        max_attempts=max_attempts,
    )
    attempt_limit = len(retry_delays_seconds) + 1
    last_error: LiproApiError | None = None

    async def _authenticated_query_command_result(
        *,
        msg_sn: str,
        device_id: str,
        device_type: str,
    ) -> CommandResultPayload:
        nonlocal last_error
        try:
            payload = await async_execute_coordinator_call(
                coordinator,
                call=lambda: coordinator.async_query_command_result(
                    msg_sn=msg_sn,
                    device_id=device_id,
                    device_type=device_type,
                ),
                raise_service_error=raise_service_error,
            )
        except LiproApiError as err:
            last_error = err
            raise
        last_error = None
        return payload

    async def _query_once(attempt: int) -> CommandResultPayload | None:
        return await query_command_result_once(
            query_command_result=_authenticated_query_command_result,
            lipro_api_error=LiproApiError,
            device_name=device.name,
            device_serial=device.serial,
            device_type_hex=device.device_type_hex,
            msg_sn=msg_sn,
            attempt=attempt,
            attempt_limit=attempt_limit,
            logger=_LOGGER,
        )

    state, attempts, result = await poll_command_result_state(
        query_once=_query_once,
        classify_payload=classify_command_result_payload,
        retry_delays_seconds=retry_delays_seconds,
    )
    response: QueryCommandResultResponse = {
        "serial": device.serial,
        "msg_sn": msg_sn,
        "max_attempts": max_attempts,
        "time_budget_seconds": time_budget_seconds,
        "state": state,
        "attempts": attempts,
        "attempt_limit": attempt_limit,
        "retry_delays_seconds": list(retry_delays_seconds),
        "result": result,
    }
    last_error_payload = _build_last_error_payload(last_error)
    if result is None and last_error_payload is not None:
        response["last_error"] = last_error_payload
    return cast(dict[str, object], response)


async def async_handle_query_command_result(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    attr_msg_sn: str,
    attr_max_attempts: str,
    attr_time_budget_seconds: str,
    raise_service_error: ServiceErrorRaiser,
) -> dict[str, object]:
    """Handle the query_command_result service."""
    raw_device, raw_coordinator = await get_device_and_coordinator(hass, call)
    device = cast(DiagnosticsDevice, raw_device)
    coordinator = cast(DiagnosticsCoordinator, raw_coordinator)
    return await _async_query_command_result_with_optional_polling(
        coordinator=coordinator,
        device=device,
        msg_sn=_get_required_service_string(call, attr_msg_sn),
        max_attempts=_coerce_service_int(
            call,
            attr_max_attempts,
            _DEFAULT_QUERY_COMMAND_RESULT_MAX_ATTEMPTS,
        ),
        time_budget_seconds=_coerce_service_float(
            call,
            attr_time_budget_seconds,
            _DEFAULT_QUERY_COMMAND_RESULT_TIME_BUDGET_SECONDS,
        ),
        raise_service_error=raise_service_error,
    )


async def async_handle_get_city(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    iter_runtime_coordinators: RuntimeCoordinatorIterator,
    raise_optional_error: Callable[[str, LiproApiError], NoReturn],
    service_get_city: str,
) -> dict[str, object]:
    """Handle the get_city service."""
    del call
    has_result, result, last_err = await _async_get_first_coordinator_capability_result(
        (cast(DiagnosticsCoordinator, coordinator) for coordinator in iter_runtime_coordinators(hass)),
        capability="get_city",
        collector=lambda coordinator: coordinator.async_get_city(),
    )
    if has_result:
        return {"result": cast(CapabilityPayload, result)}
    if last_err is not None:
        raise_optional_error(service_get_city, last_err)
    return {"result": {}}


async def async_handle_query_user_cloud(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    iter_runtime_coordinators: RuntimeCoordinatorIterator,
    raise_optional_error: Callable[[str, LiproApiError], NoReturn],
    service_query_user_cloud: str,
) -> dict[str, object]:
    """Handle the query_user_cloud service."""
    del call
    has_result, result, last_err = await _async_get_first_coordinator_capability_result(
        (cast(DiagnosticsCoordinator, coordinator) for coordinator in iter_runtime_coordinators(hass)),
        capability="query_user_cloud",
        collector=lambda coordinator: coordinator.async_query_user_cloud(),
    )
    if has_result:
        return {"result": cast(CapabilityPayload, result)}
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
    attr_sensor_device_id: str,
    attr_mesh_type: str,
    service_name: str,
    get_client_method: Callable[[DiagnosticsCoordinator], SensorHistoryClientMethod],
) -> dict[str, object]:
    """Shared handler for sensor-history diagnostics services."""
    raw_device, raw_coordinator = await get_device_and_coordinator(hass, call)
    device = cast(DiagnosticsDevice, raw_device)
    coordinator = cast(DiagnosticsCoordinator, raw_coordinator)
    sensor_device_id = _get_required_service_string(call, attr_sensor_device_id)
    mesh_type = _get_required_service_string(call, attr_mesh_type)
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
    attr_sensor_device_id: str,
    attr_mesh_type: str,
    service_fetch_body_sensor_history: str,
) -> dict[str, object]:
    """Handle the fetch_body_sensor_history service."""
    return await _async_handle_fetch_sensor_history(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        async_call_optional_capability=async_call_optional_capability,
        build_sensor_history_result=build_sensor_history_result,
        attr_sensor_device_id=attr_sensor_device_id,
        attr_mesh_type=attr_mesh_type,
        service_name=service_fetch_body_sensor_history,
        get_client_method=lambda coordinator: coordinator.async_fetch_body_sensor_history,
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
) -> dict[str, object]:
    """Handle the fetch_door_sensor_history service."""
    return await _async_handle_fetch_sensor_history(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        async_call_optional_capability=async_call_optional_capability,
        build_sensor_history_result=build_sensor_history_result,
        attr_sensor_device_id=attr_sensor_device_id,
        attr_mesh_type=attr_mesh_type,
        service_name=service_fetch_door_sensor_history,
        get_client_method=lambda coordinator: coordinator.async_fetch_door_sensor_history,
    )
