"""Local helper builders for command-result failure arbitration."""

from __future__ import annotations

from ..utils.redaction import redact_identifier
from .result_policy import (
    COMMAND_FAILURE_REASON_COMMAND_RESULT_UNCONFIRMED,
    COMMAND_RESULT_TRACE_STATE_QUERY_ERROR,
    CommandFailurePayload,
    CommandResultPayload,
    CommandResultVerifyTrace,
    LoggerLike,
    classify_command_result_payload,
    extract_command_result_code,
    extract_command_result_message,
)


def build_unconfirmed_command_result_verify(
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


def log_command_result_unconfirmed(
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


def build_unconfirmed_failure(
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
