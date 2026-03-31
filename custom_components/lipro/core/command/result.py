"""Helpers for command result failure arbitration and stable public exports."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from ..utils.redaction import redact_identifier
from .result_policy import (
    COMMAND_FAILURE_CODE_MISSING_MSGSN,
    COMMAND_FAILURE_REASON_API_ERROR,
    COMMAND_FAILURE_REASON_COMMAND_RESULT_FAILED,
    COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED,
    COMMAND_FAILURE_REASON_PUSH_FAILED,
    COMMAND_RESULT_POLLING_STATE_UNCONFIRMED,
    COMMAND_RESULT_STATE_CONFIRMED,
    COMMAND_RESULT_STATE_FAILED,
    COMMAND_RESULT_STATE_PENDING,
    COMMAND_RESULT_STATE_UNKNOWN,
    COMMAND_RESULT_TRACE_STATE_QUERY_ERROR,
    COMMAND_VERIFICATION_RESULT_CONFIRMED,
    COMMAND_VERIFICATION_RESULT_FAILED,
    COMMAND_VERIFICATION_RESULT_TIMEOUT,
    CommandFailurePayload,
    CommandFailureReason,
    CommandResultClassifier,
    CommandResultPayload,
    CommandResultPollingState,
    CommandResultState,
    CommandResultVerifyTrace,
    CommandVerificationResult,
    LoggerLike,
    PendingExpectations,
    QueryCommandResult,
    QueryCommandResultAttempt,
    ShouldReraiseCommandResultError,
    TracePayload,
    build_progressive_retry_delays,
    classify_command_result_payload,
    compute_adaptive_post_refresh_delay,
    extract_command_result_code,
    extract_command_result_message,
    extract_msg_sn,
    is_command_push_failed,
    is_terminal_command_result_state,
    poll_command_result_state,
    query_command_result_once,
    resolve_delayed_refresh_delay,
    run_delayed_refresh,
    should_schedule_delayed_refresh,
    should_skip_immediate_post_refresh,
)


class ApiErrorLike(Protocol):
    """Minimal API error surface used to build failure payloads."""

    code: int | str | None


type UpdateTraceWithException = Callable[..., None]


_PUSH_FAILURE_TRACE_MESSAGE = "pushSuccess=false"



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
    result_code = extract_command_result_code(payload)
    result_message = extract_command_result_message(payload)
    command_result_verify: CommandResultVerifyTrace = {
        "enabled": True,
        "verified": False,
        "attempts": attempt,
        "msg_sn": msg_sn,
        "state": COMMAND_RESULT_STATE_FAILED,
    }
    if result_code is not None:
        command_result_verify["code"] = result_code
    if result_message is not None:
        command_result_verify["message"] = result_message

    trace["route"] = route
    trace["success"] = False
    trace["error"] = "CommandResultRejected"
    trace["error_message"] = COMMAND_FAILURE_REASON_COMMAND_RESULT_FAILED
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
        "reason": COMMAND_FAILURE_REASON_COMMAND_RESULT_FAILED,
        "code": result_code or COMMAND_FAILURE_REASON_COMMAND_RESULT_FAILED,
        "route": route,
        "msg_sn": msg_sn,
        "device_id": device_serial,
    }
    if result_message is not None:
        failure["message"] = result_message
    return failure


def _build_unconfirmed_command_result_verify(
    *,
    msg_sn: str,
    attempt_limit: int,
    last_payload: CommandResultPayload | None,
) -> CommandResultVerifyTrace:
    """Build command-result verification trace for an unconfirmed polling outcome."""
    command_result_verify: CommandResultVerifyTrace = {
        "enabled": True,
        "verified": False,
        "attempts": attempt_limit,
        "msg_sn": msg_sn,
        "last_state": (
            classify_command_result_payload(last_payload)
            if isinstance(last_payload, dict)
            else COMMAND_RESULT_TRACE_STATE_QUERY_ERROR
        ),
    }
    last_code = extract_command_result_code(last_payload)
    last_message = extract_command_result_message(last_payload)
    if last_code is not None:
        command_result_verify["last_code"] = last_code
    if last_message is not None:
        command_result_verify["last_message"] = last_message
    return command_result_verify


def _log_command_result_unconfirmed(
    *,
    route: str,
    msg_sn: str,
    device_serial: str,
    attempt_limit: int,
    elapsed_seconds: float,
    logger: LoggerLike,
    command_result_verify: CommandResultVerifyTrace,
    last_code: object | None,
) -> None:
    """Log one unconfirmed command-result polling outcome."""
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


def _build_unconfirmed_failure(
    *,
    route: str,
    msg_sn: str,
    device_serial: str,
    last_payload: CommandResultPayload | None,
) -> CommandFailurePayload:
    """Build failure payload for an unconfirmed command-result polling outcome."""
    last_code = extract_command_result_code(last_payload)
    last_message = extract_command_result_message(last_payload)
    failure: CommandFailurePayload = {
        "reason": COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED,
        "code": last_code or COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED,
        "route": route,
        "msg_sn": msg_sn,
        "device_id": device_serial,
    }
    if last_message is not None:
        failure["message"] = last_message
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
    last_code = extract_command_result_code(last_payload)
    command_result_verify = _build_unconfirmed_command_result_verify(
        msg_sn=msg_sn,
        attempt_limit=attempt_limit,
        last_payload=last_payload,
    )
    trace["route"] = route
    trace["success"] = False
    trace["error"] = "CommandResultUnconfirmed"
    trace["error_message"] = COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED
    trace["command_result_verify"] = command_result_verify
    _log_command_result_unconfirmed(
        route=route,
        msg_sn=msg_sn,
        device_serial=device_serial,
        attempt_limit=attempt_limit,
        elapsed_seconds=elapsed_seconds,
        logger=logger,
        command_result_verify=command_result_verify,
        last_code=last_code,
    )
    return _build_unconfirmed_failure(
        route=route,
        msg_sn=msg_sn,
        device_serial=device_serial,
        last_payload=last_payload,
    )


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
    command_result_verify: CommandResultVerifyTrace = {
        "enabled": True,
        "verified": True,
        "attempts": attempt,
        "msg_sn": msg_sn,
    }
    trace["command_result_verify"] = command_result_verify
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
    trace["error_message"] = COMMAND_FAILURE_CODE_MISSING_MSGSN
    trace["command_result_verify"] = CommandResultVerifyTrace(
        enabled=True,
        verified=False,
        attempts=0,
    )
    safe_device_serial = redact_identifier(device_serial) or "***"
    logger.warning(
        "Command sent but msgSn missing for verification (command=%s, device=%s, route=%s, device_id=%s)",
        command,
        device_name,
        route,
        safe_device_serial,
    )
    return {
        "reason": COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED,
        "code": COMMAND_FAILURE_CODE_MISSING_MSGSN,
        "route": route,
        "device_id": device_serial,
        "command": command,
    }


def resolve_polled_command_result(
    *,
    state: CommandResultPollingState,
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
    if state == COMMAND_RESULT_STATE_CONFIRMED:
        apply_command_result_confirmed(
            trace=trace,
            msg_sn=msg_sn,
            attempt=attempt,
            device_serial=device_serial,
            elapsed_seconds=elapsed_seconds,
            logger=logger,
        )
        return True, None
    if state == COMMAND_RESULT_STATE_FAILED:
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
    trace["error_message"] = _PUSH_FAILURE_TRACE_MESSAGE
    safe_device_serial = redact_identifier(device_serial) or "***"
    logger.warning(
        "Command push failed (command=%s, device=%s, route=%s, device_id=%s)",
        command,
        device_name,
        route,
        safe_device_serial,
    )
    return {
        "reason": COMMAND_FAILURE_REASON_PUSH_FAILED,
        "code": COMMAND_FAILURE_REASON_PUSH_FAILED,
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
        "reason": COMMAND_FAILURE_REASON_API_ERROR,
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
    "COMMAND_FAILURE_CODE_MISSING_MSGSN",
    "COMMAND_FAILURE_REASON_API_ERROR",
    "COMMAND_FAILURE_REASON_COMMAND_RESULT_FAILED",
    "COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED",
    "COMMAND_FAILURE_REASON_PUSH_FAILED",
    "COMMAND_RESULT_POLLING_STATE_UNCONFIRMED",
    "COMMAND_RESULT_STATE_CONFIRMED",
    "COMMAND_RESULT_STATE_FAILED",
    "COMMAND_RESULT_STATE_PENDING",
    "COMMAND_RESULT_STATE_UNKNOWN",
    "COMMAND_RESULT_TRACE_STATE_QUERY_ERROR",
    "COMMAND_VERIFICATION_RESULT_CONFIRMED",
    "COMMAND_VERIFICATION_RESULT_FAILED",
    "COMMAND_VERIFICATION_RESULT_TIMEOUT",
    "ApiErrorLike",
    "CommandFailurePayload",
    "CommandFailureReason",
    "CommandResultClassifier",
    "CommandResultPayload",
    "CommandResultPollingState",
    "CommandResultState",
    "CommandResultVerifyTrace",
    "CommandVerificationResult",
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
    "is_terminal_command_result_state",
    "poll_command_result_state",
    "query_command_result_once",
    "resolve_delayed_refresh_delay",
    "resolve_polled_command_result",
    "run_delayed_refresh",
    "should_schedule_delayed_refresh",
    "should_skip_immediate_post_refresh",
]
