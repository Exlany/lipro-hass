"""Focused command-result diagnostics handlers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.core import HomeAssistant, ServiceCall

from ...core import LiproApiError
from ...core.command.result import (
    CommandResultPayload,
    CommandResultPollingState,
    build_progressive_retry_delays,
    classify_command_result_payload,
    poll_command_result_state,
    query_command_result_once,
)
from ..execution import ServiceErrorRaiser, async_execute_coordinator_call
from .types import (
    DiagnosticsCoordinator,
    DiagnosticsDevice,
    FailureSummaryPayload,
    GetDeviceAndCoordinator,
    LastErrorPayload,
    QueryCommandResultResponse,
)

_LOGGER = logging.getLogger(__name__)
_QUERY_COMMAND_RESULT_DIAGNOSTIC_BASE_DELAY_SECONDS = 0.35
_DEFAULT_QUERY_COMMAND_RESULT_MAX_ATTEMPTS = 6
_DEFAULT_QUERY_COMMAND_RESULT_TIME_BUDGET_SECONDS = 3.0

RequiredServiceStringGetter = Callable[[ServiceCall, str], str]
CoerceServiceInt = Callable[[ServiceCall, str, int], int]
CoerceServiceFloat = Callable[[ServiceCall, str, float], float]


@dataclass(slots=True)
class _CommandResultQueryState:
    last_error: LiproApiError | None = None


@dataclass(slots=True)
class _CommandResultPollingSession:
    coordinator: DiagnosticsCoordinator
    device: DiagnosticsDevice
    msg_sn: str
    raise_service_error: ServiceErrorRaiser
    query_state: _CommandResultQueryState

    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: str,
    ) -> CommandResultPayload:
        del device_id, device_type
        try:
            payload = await async_execute_coordinator_call(
                self.coordinator,
                call=lambda: (
                    self.coordinator.protocol_service.async_query_command_result(
                        msg_sn=msg_sn,
                        device_id=self.device.serial,
                        device_type=self.device.device_type_hex,
                    )
                ),
                raise_service_error=self.raise_service_error,
            )
        except LiproApiError as err:
            self.query_state.last_error = err
            raise
        self.query_state.last_error = None
        return payload

    async def query_once(
        self,
        *,
        attempt: int,
        attempt_limit: int,
    ) -> CommandResultPayload | None:
        return await query_command_result_once(
            query_command_result=self.query_command_result,
            lipro_api_error=LiproApiError,
            device_name=self.device.name,
            device_serial=self.device.serial,
            device_type_hex=self.device.device_type_hex,
            msg_sn=self.msg_sn,
            attempt=attempt,
            attempt_limit=attempt_limit,
            logger=_LOGGER,
        )


def _build_api_failure_summary(err: LiproApiError) -> FailureSummaryPayload:
    """Map one diagnostics-service API error into the shared failure vocabulary."""
    if err.code in {401, 403}:
        failure_category = "auth"
        handling_policy = "reauth"
    elif err.code in {408, 429, 500, 502, 503, 504}:
        failure_category = "network"
        handling_policy = "retry"
    else:
        failure_category = "protocol"
        handling_policy = "inspect"

    return {
        "failure_category": failure_category,
        "failure_origin": "service.api",
        "handling_policy": handling_policy,
        "error_type": type(err).__name__,
    }


def _build_last_error_payload(err: LiproApiError | None) -> LastErrorPayload | None:
    """Build serializable last-error details for diagnostics output."""
    if err is None:
        return None
    payload: LastErrorPayload = {"failure_summary": _build_api_failure_summary(err)}
    if err.code is not None:
        payload["code"] = err.code
    message = str(err).strip()
    if message:
        payload["message"] = message
    return payload or None


def _build_retry_schedule(
    *,
    max_attempts: int,
    time_budget_seconds: float,
) -> tuple[tuple[float, ...], int]:
    retry_delays_seconds = tuple(
        build_progressive_retry_delays(
            base_delay_seconds=_QUERY_COMMAND_RESULT_DIAGNOSTIC_BASE_DELAY_SECONDS,
            time_budget_seconds=time_budget_seconds,
            max_attempts=max_attempts,
        )
    )
    return retry_delays_seconds, len(retry_delays_seconds) + 1


async def _poll_command_result(
    *,
    session: _CommandResultPollingSession,
    attempt_limit: int,
    retry_delays_seconds: tuple[float, ...],
) -> tuple[CommandResultPollingState, int, CommandResultPayload | None]:
    async def _query_once(attempt: int) -> CommandResultPayload | None:
        return await session.query_once(
            attempt=attempt,
            attempt_limit=attempt_limit,
        )

    return await poll_command_result_state(
        query_once=_query_once,
        classify_payload=classify_command_result_payload,
        retry_delays_seconds=retry_delays_seconds,
    )


def _build_query_command_result_response(
    *,
    device: DiagnosticsDevice,
    msg_sn: str,
    max_attempts: int,
    time_budget_seconds: float,
    state: CommandResultPollingState,
    attempts: int,
    attempt_limit: int,
    retry_delays_seconds: tuple[float, ...],
    result: CommandResultPayload | None,
    last_error: LiproApiError | None,
) -> QueryCommandResultResponse:
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
    return response


async def _async_query_command_result_with_optional_polling(
    *,
    coordinator: DiagnosticsCoordinator,
    device: DiagnosticsDevice,
    msg_sn: str,
    max_attempts: int,
    time_budget_seconds: float,
    raise_service_error: ServiceErrorRaiser,
) -> QueryCommandResultResponse:
    """Query command-result diagnostics with bounded polling."""
    retry_delays_seconds, attempt_limit = _build_retry_schedule(
        max_attempts=max_attempts,
        time_budget_seconds=time_budget_seconds,
    )
    query_state = _CommandResultQueryState()
    state, attempts, result = await _poll_command_result(
        session=_CommandResultPollingSession(
            coordinator=coordinator,
            device=device,
            msg_sn=msg_sn,
            raise_service_error=raise_service_error,
            query_state=query_state,
        ),
        attempt_limit=attempt_limit,
        retry_delays_seconds=retry_delays_seconds,
    )
    return _build_query_command_result_response(
        device=device,
        msg_sn=msg_sn,
        max_attempts=max_attempts,
        time_budget_seconds=time_budget_seconds,
        state=state,
        attempts=attempts,
        attempt_limit=attempt_limit,
        retry_delays_seconds=retry_delays_seconds,
        result=result,
        last_error=query_state.last_error,
    )


async def async_handle_query_command_result(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    get_required_service_string: RequiredServiceStringGetter,
    coerce_service_int: CoerceServiceInt,
    coerce_service_float: CoerceServiceFloat,
    attr_msg_sn: str,
    attr_max_attempts: str,
    attr_time_budget_seconds: str,
    raise_service_error: ServiceErrorRaiser,
) -> QueryCommandResultResponse:
    """Handle the query_command_result service."""
    device, coordinator = await get_device_and_coordinator(hass, call)
    return await _async_query_command_result_with_optional_polling(
        coordinator=coordinator,
        device=device,
        msg_sn=get_required_service_string(call, attr_msg_sn),
        max_attempts=coerce_service_int(
            call,
            attr_max_attempts,
            _DEFAULT_QUERY_COMMAND_RESULT_MAX_ATTEMPTS,
        ),
        time_budget_seconds=coerce_service_float(
            call,
            attr_time_budget_seconds,
            _DEFAULT_QUERY_COMMAND_RESULT_TIME_BUDGET_SECONDS,
        ),
        raise_service_error=raise_service_error,
    )
