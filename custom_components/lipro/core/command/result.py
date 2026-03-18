"""Helpers for command result classification and refresh scheduling."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Protocol

from ..api.request_policy import compute_exponential_retry_wait_time
from ..api.response_safety import normalize_response_code
from ..utils.log_safety import safe_error_placeholder
from ..utils.redaction import redact_identifier

type CommandResultPayload = Mapping[str, object]
type TracePayload = dict[str, object]
type PendingExpectations = dict[str, object]
type CommandFailurePayload = dict[str, object]
type QueryCommandResult = Callable[..., Awaitable[Mapping[str, object]]]
type QueryCommandResultAttempt = Callable[[int], Awaitable[CommandResultPayload | None]]
type ShouldReraiseCommandResultError = Callable[[Exception], bool]
type CommandResultClassifier = Callable[[CommandResultPayload], str]


class LoggerLike(Protocol):
    """Minimal logger surface used by command-result helpers."""

    def debug(self, msg: str, *args: object) -> None:
        """Log one debug message."""

    def warning(self, msg: str, *args: object) -> None:
        """Log one warning message."""


class ApiErrorLike(Protocol):
    """Minimal API error surface used to build failure payloads."""

    code: int | str | None


type UpdateTraceWithException = Callable[..., None]

_MSG_SN_KEYS: tuple[str, ...] = ("msgSn", "msg_sn", "messageSn", "message_sn")
_BOOL_CONFIRMED_VALUES: tuple[object, ...] = (True, 1, "1", "true", "TRUE")
_BOOL_FAILED_VALUES: tuple[object, ...] = (False, 0, "0", "false", "FALSE")
_COMMAND_RESULT_PENDING_CODES = frozenset((100000, 140006))
_COMMAND_RESULT_SUCCESS_CODES = frozenset((0,))


def is_command_push_failed(result: object) -> bool:
    """Return True when command dispatch explicitly reports push failure."""
    return isinstance(result, dict) and result.get("pushSuccess") in _BOOL_FAILED_VALUES


def extract_msg_sn(result: object) -> str | None:
    """Extract command serial number from command response payload."""
    if not isinstance(result, dict):
        return None
    for key in _MSG_SN_KEYS:
        value = result.get(key)
        if isinstance(value, str):
            normalized = value.strip()
            if normalized:
                return normalized
            continue
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
    return None


def _classify_bool_state(value: object) -> str | None:
    """Classify one boolean-like payload field into confirmed/failed/None."""
    if value in _BOOL_CONFIRMED_VALUES:
        return "confirmed"
    if value in _BOOL_FAILED_VALUES:
        return "failed"
    return None


def _extract_command_result_code(payload: CommandResultPayload | None) -> object | None:
    """Extract backend result code from query_command_result payload."""
    if not isinstance(payload, dict):
        return None
    for key in ("errorCode", "code"):
        value = payload.get(key)
        if value not in (None, ""):
            return value
    return None


def _extract_command_result_message(payload: CommandResultPayload | None) -> str | None:
    """Extract non-empty backend message from query_command_result payload."""
    if not isinstance(payload, dict):
        return None
    value = payload.get("message")
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


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


def classify_command_result_payload(payload: CommandResultPayload) -> str:
    """Classify query_command_result payload using the current observed contract."""
    normalized_code = normalize_response_code(_extract_command_result_code(payload))
    if normalized_code in _COMMAND_RESULT_PENDING_CODES:
        return "pending"

    success_state = _classify_bool_state(payload.get("success"))
    if success_state is not None:
        return success_state

    if normalized_code in _COMMAND_RESULT_SUCCESS_CODES:
        return "confirmed"
    if normalized_code is not None:
        return "failed"
    return "unknown"


def should_skip_immediate_post_refresh(
    *,
    command: str,
    properties: list[dict[str, str]] | None,
    slider_like_properties: set[str] | frozenset[str],
) -> bool:
    """Return True when immediate refresh can be skipped for slider-like updates."""
    if command.upper() != "CHANGE_STATE" or not properties:
        return False

    property_keys = {
        item.get("key")
        for item in properties
        if isinstance(item, dict) and isinstance(item.get("key"), str)
    }
    if not property_keys:
        return False
    return property_keys.issubset(slider_like_properties)


def should_schedule_delayed_refresh(
    *,
    mqtt_connected: bool,
    device_serial: str | None,
    pending_expectations: PendingExpectations,
) -> bool:
    """Return True when post-command delayed refresh should be scheduled."""
    if not mqtt_connected:
        return True
    return isinstance(device_serial, str) and device_serial in pending_expectations


def resolve_delayed_refresh_delay(
    *,
    mqtt_connected: bool,
    device_serial: str | None,
    pending_expectations: PendingExpectations,
    get_adaptive_post_refresh_delay: Callable[[str | None], float],
) -> float | None:
    """Return delayed-refresh delay when a fallback refresh should be scheduled."""
    if not should_schedule_delayed_refresh(
        mqtt_connected=mqtt_connected,
        device_serial=device_serial,
        pending_expectations=pending_expectations,
    ):
        return None
    return get_adaptive_post_refresh_delay(device_serial)


def compute_adaptive_post_refresh_delay(
    *,
    learned_latency_seconds: float | None,
    default_delay_seconds: float,
    latency_margin_seconds: float,
    min_delay_seconds: float,
    max_delay_seconds: float,
) -> float:
    """Compute bounded adaptive delayed-refresh seconds."""
    delay = (
        learned_latency_seconds + latency_margin_seconds
        if learned_latency_seconds is not None
        else default_delay_seconds
    )
    return max(min_delay_seconds, min(max_delay_seconds, delay))


async def run_delayed_refresh(
    *,
    delay_seconds: float,
    request_refresh: Callable[[], Awaitable[object]],
) -> None:
    """Run one delayed refresh after command to absorb API status lag."""
    try:
        await asyncio.sleep(delay_seconds)
        await request_refresh()
    except asyncio.CancelledError:
        return


async def query_command_result_once(
    *,
    query_command_result: QueryCommandResult,
    lipro_api_error: type[Exception],
    device_name: str,
    device_serial: str,
    device_type_hex: str,
    msg_sn: str,
    attempt: int,
    attempt_limit: int,
    logger: LoggerLike,
    should_reraise: ShouldReraiseCommandResultError | None = None,
) -> CommandResultPayload | None:
    """Query command result once and return payload when available."""
    try:
        payload = await query_command_result(
            msg_sn=msg_sn,
            device_id=device_serial,
            device_type=device_type_hex,
        )
        return dict(payload)
    except lipro_api_error as err:
        if should_reraise is not None and should_reraise(err):
            raise
        safe_msg_sn = redact_identifier(msg_sn) or "***"
        logger.debug(
            "query_command_result failed (device=%s, msgSn=%s, attempt=%s/%s, code=%s) (%s)",
            device_name,
            safe_msg_sn,
            attempt,
            attempt_limit,
            getattr(err, "code", None),
            safe_error_placeholder(err),
        )
        return None


async def poll_command_result_state(
    *,
    query_once: QueryCommandResultAttempt,
    classify_payload: CommandResultClassifier,
    retry_delays_seconds: Sequence[float],
    on_attempt: Callable[[int, str], None] | None = None,
) -> tuple[str, int, CommandResultPayload | None]:
    """Poll command-result endpoint until confirmed/failed or retry budget ends."""
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
