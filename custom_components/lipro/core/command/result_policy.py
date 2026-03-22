"""Policy helpers for command-result polling and post-refresh timing."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Protocol

from ..api.response_safety import normalize_response_code
from ..utils.backoff import compute_exponential_retry_wait_time
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


_MSG_SN_KEYS: tuple[str, ...] = ("msgSn", "msg_sn", "messageSn", "message_sn")
_BOOL_CONFIRMED_VALUES: tuple[object, ...] = (True, 1, "1", "true", "TRUE")
_BOOL_FAILED_VALUES: tuple[object, ...] = (False, 0, "0", "false", "FALSE")
_COMMAND_RESULT_PENDING_CODES = frozenset((100000, 140006))
_COMMAND_RESULT_SUCCESS_CODES = frozenset((0,))


def is_command_push_failed(result: object) -> bool:
    """Return True when command dispatch explicitly reports push failure."""
    return isinstance(result, dict) and result.get("pushSuccess") in _BOOL_FAILED_VALUES



def extract_msg_sn(result: object) -> str | None:
    """Extract the message serial number from one command response payload."""
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
    """Extract backend result code from a command-result payload."""
    if not isinstance(payload, dict):
        return None
    for key in ("errorCode", "code"):
        value = payload.get(key)
        if value not in (None, ""):
            return value
    return None



def _extract_command_result_message(payload: CommandResultPayload | None) -> str | None:
    """Extract a non-empty backend message from a command-result payload."""
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
    """Classify a polled command-result payload using the observed contract."""
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
    """Return True when a post-command delayed refresh should be scheduled."""
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
    """Return the delayed-refresh delay when fallback refresh is required."""
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
    """Run one delayed refresh after a command to absorb API status lag."""
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
    """Query the command-result endpoint once and return the payload when available."""
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


__all__ = [
    "CommandFailurePayload",
    "CommandResultClassifier",
    "CommandResultPayload",
    "LoggerLike",
    "PendingExpectations",
    "QueryCommandResult",
    "QueryCommandResultAttempt",
    "ShouldReraiseCommandResultError",
    "TracePayload",
    "build_progressive_retry_delays",
    "classify_command_result_payload",
    "compute_adaptive_post_refresh_delay",
    "extract_msg_sn",
    "is_command_push_failed",
    "poll_command_result_state",
    "query_command_result_once",
    "resolve_delayed_refresh_delay",
    "run_delayed_refresh",
    "should_schedule_delayed_refresh",
    "should_skip_immediate_post_refresh",
]
