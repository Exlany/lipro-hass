"""Helpers for command result failure arbitration and stable public exports."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from typing import Protocol

from ..api.request_policy import compute_exponential_retry_wait_time
from ..utils.redaction import redact_identifier
from .result_policy import (
    CommandFailurePayload,
    CommandResultClassifier,
    CommandResultPayload,
    LoggerLike,
    PendingExpectations,
    QueryCommandResult,
    QueryCommandResultAttempt,
    ShouldReraiseCommandResultError,
    TracePayload,
    _extract_command_result_code,
    _extract_command_result_message,
    classify_command_result_payload,
    compute_adaptive_post_refresh_delay,
    extract_msg_sn,
    is_command_push_failed,
    query_command_result_once,
    resolve_delayed_refresh_delay,
    should_schedule_delayed_refresh,
    should_skip_immediate_post_refresh,
)


class ApiErrorLike(Protocol):
    """Minimal API error surface used to build failure payloads."""

    code: int | str | None


type UpdateTraceWithException = Callable[..., None]


def build_progressive_retry_delays(
    *,
    base_delay_seconds: float,
    time_budget_seconds: float,
    max_attempts: int,
) -> tuple[float, ...]:
    """Build bounded exponential retry delays within one total time budget."""
    if max_attempts <= 1 or time_budget_seconds <= 0:
        return ()

    delays: list[float] = []
    elapsed = 0.0
    for retry_count in range(max_attempts - 1):
        remaining_budget = time_budget_seconds - elapsed
        if remaining_budget <= 0:
            break
        wait_time = min(
            remaining_budget,
            compute_exponential_retry_wait_time(
                retry_count=retry_count,
                base_delay_seconds=base_delay_seconds,
                max_delay_seconds=remaining_budget,
            ),
        )
        if wait_time <= 0:
            break
        delays.append(wait_time)
        elapsed += wait_time
    return tuple(delays)


async def run_delayed_refresh(
    *,
    delay_seconds: float,
    request_refresh: Callable[[], Awaitable[object]],
) -> None:
    """Run one delayed refresh after a command to absorb API status lag."""
    try:
        await asyncio.sleep(delay_seconds)
        await request_refresh()
    except asyncio.CancelledError:
        return


async def poll_command_result_state(
    *,
    query_once: QueryCommandResultAttempt,
    classify_payload: CommandResultClassifier,
    retry_delays_seconds: Sequence[float],
    on_attempt: Callable[[int, str], None] | None = None,
) -> tuple[str, int, CommandResultPayload | None]:
    """Poll until the command result is confirmed/failed or the retry budget ends."""
    retry_delays = tuple(max(0.0, float(delay)) for delay in retry_delays_seconds)
    attempt_limit = len(retry_delays) + 1
    last_payload: CommandResultPayload | None = None
    for attempt in range(1, attempt_limit + 1):
        payload = await query_once(attempt)
        if payload is None:
            if attempt < attempt_limit:
                await asyncio.sleep(retry_delays[attempt - 1])
            continue

        last_payload = payload
        state = classify_payload(payload)
        if on_attempt is not None:
            on_attempt(attempt, state)
        if state in {"confirmed", "failed"}:
            return state, attempt, payload
        if attempt < attempt_limit:
            await asyncio.sleep(retry_delays[attempt - 1])

    return "unconfirmed", attempt_limit, last_payload

def apply_command_result_rejected(
    *,
    trace: TracePayload,
    route: str,
    msg_sn: str,
    device_serial: str,
    attempt: int,
    elapsed_seconds: float,
    payload: CommandResultPayload | None,
    logger: LoggerLike,
) -> CommandFailurePayload:
    """Populate trace/failure fields for a rejected query_command_result response."""
    result_code = _extract_command_result_code(payload)
    result_message = _extract_command_result_message(payload)
    command_result_verify: dict[str, object] = {
        "enabled": True,
        "verified": False,
        "attempts": attempt,
        "msg_sn": msg_sn,
        "state": "failed",
    }
    if result_code is not None:
        command_result_verify["code"] = result_code
    if result_message is not None:
        command_result_verify["message"] = result_message

    trace["route"] = route
    trace["success"] = False
    trace["error"] = "CommandResultRejected"
    trace["error_message"] = "command_result_failed"
    trace["command_result_verify"] = command_result_verify
    safe_device_serial = redact_identifier(device_serial) or "***"
    safe_msg_sn = redact_identifier(msg_sn) or "***"
    logger.warning(
        "query_command_result rejected command (device=%s, msgSn=%s, attempts=%s, elapsed=%.3fs, route=%s, code=%s)",
        safe_device_serial,
        safe_msg_sn,
        attempt,
        elapsed_seconds,
        route,
        result_code,
    )
    failure: CommandFailurePayload = {
        "reason": "command_result_failed",
        "code": result_code or "command_result_failed",
        "route": route,
        "msg_sn": msg_sn,
        "device_id": device_serial,
    }
    if result_message is not None:
        failure["message"] = result_message
    return failure


def apply_command_result_unconfirmed(
    *,
    trace: TracePayload,
    route: str,
    msg_sn: str,
    device_serial: str,
    attempt_limit: int,
    elapsed_seconds: float,
    last_payload: CommandResultPayload | None,
    logger: LoggerLike,
) -> CommandFailurePayload:
    """Populate trace/failure fields for unconfirmed command-result polling."""
    last_code = _extract_command_result_code(last_payload)
    last_message = _extract_command_result_message(last_payload)
    command_result_verify: dict[str, object] = {
        "enabled": True,
        "verified": False,
        "attempts": attempt_limit,
        "msg_sn": msg_sn,
        "last_state": (
            classify_command_result_payload(last_payload)
            if isinstance(last_payload, dict)
            else "query_error"
        ),
    }
    if last_code is not None:
        command_result_verify["last_code"] = last_code
    if last_message is not None:
        command_result_verify["last_message"] = last_message

    trace["route"] = route
    trace["success"] = False
    trace["error"] = "CommandResultUnconfirmed"
    trace["error_message"] = "command_result_unconfirmed"
    trace["command_result_verify"] = command_result_verify
    safe_device_serial = redact_identifier(device_serial) or "***"
    safe_msg_sn = redact_identifier(msg_sn) or "***"
    logger.warning(
        "query_command_result not confirmed (device=%s, msgSn=%s, attempts=%s, elapsed=%.3fs, route=%s, last_state=%s, last_code=%s)",
        safe_device_serial,
        safe_msg_sn,
        attempt_limit,
        elapsed_seconds,
        route,
        command_result_verify["last_state"],
        last_code,
    )
    failure: CommandFailurePayload = {
        "reason": "command_result_unconfirmed",
        "code": last_code or "command_result_unconfirmed",
        "route": route,
        "msg_sn": msg_sn,
        "device_id": device_serial,
    }
    if last_message is not None:
        failure["message"] = last_message
    return failure


def apply_command_result_confirmed(
    *,
    trace: TracePayload,
    msg_sn: str,
    attempt: int,
    device_serial: str,
    elapsed_seconds: float,
    logger: LoggerLike,
) -> None:
    """Populate trace fields for polling classified as confirmed."""
    trace["command_result_verify"] = {
        "enabled": True,
        "verified": True,
        "attempts": attempt,
        "msg_sn": msg_sn,
    }
    safe_device_serial = redact_identifier(device_serial) or "***"
    safe_msg_sn = redact_identifier(msg_sn) or "***"
    logger.debug(
        "query_command_result confirmed (device=%s, msgSn=%s, attempts=%s, elapsed=%.3fs)",
        safe_device_serial,
        safe_msg_sn,
        attempt,
        elapsed_seconds,
    )


def apply_missing_msg_sn_failure(
    *,
    trace: TracePayload,
    route: str,
    command: str,
    device_name: str,
    device_serial: str,
    logger: LoggerLike,
) -> CommandFailurePayload:
    """Populate trace/failure fields when command response has no msgSn."""
    trace["route"] = route
    trace["success"] = False
    trace["error"] = "CommandResultMissingMsgSn"
    trace["error_message"] = "command_result_missing_msgsn"
    trace["command_result_verify"] = {
        "enabled": True,
        "verified": False,
        "attempts": 0,
    }
    safe_device_serial = redact_identifier(device_serial) or "***"
    logger.warning(
        "Command sent but msgSn missing for verification (command=%s, device=%s, route=%s, device_id=%s)",
        command,
        device_name,
        route,
        safe_device_serial,
    )
    return {
        "reason": "command_result_unconfirmed",
        "code": "command_result_missing_msgsn",
        "route": route,
        "device_id": device_serial,
        "command": command,
    }


def resolve_polled_command_result(
    *,
    state: str,
    trace: TracePayload,
    route: str,
    msg_sn: str,
    device_serial: str,
    attempt: int,
    attempt_limit: int,
    last_payload: CommandResultPayload | None,
    elapsed_seconds: float,
    logger: LoggerLike,
) -> tuple[bool, CommandFailurePayload | None]:
    """Resolve polled command-result state into success flag and failure payload."""
    if state == "confirmed":
        apply_command_result_confirmed(
            trace=trace,
            msg_sn=msg_sn,
            attempt=attempt,
            device_serial=device_serial,
            elapsed_seconds=elapsed_seconds,
            logger=logger,
        )
        return True, None
    if state == "failed":
        failure = apply_command_result_rejected(
            route=route,
            msg_sn=msg_sn,
            trace=trace,
            device_serial=device_serial,
            attempt=attempt,
            elapsed_seconds=elapsed_seconds,
            payload=last_payload,
            logger=logger,
        )
        return False, failure

    failure = apply_command_result_unconfirmed(
        route=route,
        msg_sn=msg_sn,
        trace=trace,
        device_serial=device_serial,
        attempt_limit=attempt_limit,
        elapsed_seconds=elapsed_seconds,
        last_payload=last_payload,
        logger=logger,
    )
    return False, failure


def apply_push_failure(
    *,
    trace: TracePayload,
    route: str,
    command: str,
    device_name: str,
    device_serial: str,
    logger: LoggerLike,
) -> CommandFailurePayload:
    """Populate trace/failure fields for pushSuccess=false command responses."""
    trace["route"] = route
    trace["success"] = False
    trace["error"] = "PushFailed"
    trace["error_message"] = "pushSuccess=false"
    safe_device_serial = redact_identifier(device_serial) or "***"
    logger.warning(
        "Command push failed (command=%s, device=%s, route=%s, device_id=%s)",
        command,
        device_name,
        route,
        safe_device_serial,
    )
    return {
        "reason": "push_failed",
        "code": "push_failed",
        "route": route,
        "device_id": device_serial,
        "command": command,
    }


def build_command_api_error_failure(
    *,
    trace: TracePayload,
    route: str,
    device_serial: str,
    err: ApiErrorLike,
    update_trace_with_exception: UpdateTraceWithException,
) -> CommandFailurePayload:
    """Update trace and return normalized failure payload for API command errors."""
    update_trace_with_exception(trace, route=route, err=err)
    return {
        "reason": "api_error",
        "code": err.code,
        "message": str(err),
        "route": route,
        "device_id": device_serial,
    }


def apply_successful_command_trace(
    *,
    trace: TracePayload,
    route: str,
    adaptive_delay_seconds: float,
    skip_immediate_refresh: bool,
) -> None:
    """Populate success trace fields after command delivery is accepted."""
    trace["post_refresh_mode"] = (
        "delayed_only" if skip_immediate_refresh else "immediate_and_delayed"
    )
    trace["adaptive_post_refresh_delay_seconds"] = round(adaptive_delay_seconds, 3)
    trace["route"] = route
    trace["success"] = True


__all__ = [
    "ApiErrorLike",
    "CommandFailurePayload",
    "CommandResultClassifier",
    "CommandResultPayload",
    "LoggerLike",
    "PendingExpectations",
    "QueryCommandResult",
    "QueryCommandResultAttempt",
    "ShouldReraiseCommandResultError",
    "TracePayload",
    "UpdateTraceWithException",
    "apply_command_result_confirmed",
    "apply_command_result_rejected",
    "apply_command_result_unconfirmed",
    "apply_missing_msg_sn_failure",
    "apply_push_failure",
    "apply_successful_command_trace",
    "build_command_api_error_failure",
    "build_progressive_retry_delays",
    "classify_command_result_payload",
    "compute_adaptive_post_refresh_delay",
    "extract_msg_sn",
    "is_command_push_failed",
    "poll_command_result_state",
    "query_command_result_once",
    "resolve_delayed_refresh_delay",
    "resolve_polled_command_result",
    "run_delayed_refresh",
    "should_schedule_delayed_refresh",
    "should_skip_immediate_post_refresh",
]
