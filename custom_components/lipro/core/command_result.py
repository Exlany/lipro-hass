"""Helpers for command result classification and refresh scheduling."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


def is_command_push_failed(result: Any) -> bool:
    """Return True when command dispatch explicitly reports push failure."""
    return isinstance(result, dict) and result.get("pushSuccess") is False


def extract_msg_sn(result: Any) -> str | None:
    """Extract command serial number from command response payload."""
    if not isinstance(result, dict):
        return None
    for key in ("msgSn", "msg_sn", "messageSn", "message_sn"):
        value = result.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def classify_command_result_payload(payload: dict[str, Any]) -> str:
    """Classify query_command_result payload as confirmed/failed/pending/unknown."""
    success_value = payload.get("success")
    if success_value is True:
        return "confirmed"
    if success_value is False:
        return "failed"

    push_success = payload.get("pushSuccess")
    if push_success is True:
        return "confirmed"
    if push_success is False:
        return "failed"

    result_value = payload.get("result")
    if result_value in (True, 1, "1", "success", "SUCCESS"):
        return "confirmed"
    if result_value in (False, 0, "0", "failed", "FAIL", "FAILURE"):
        return "failed"
    if result_value in ("pending", "PENDING", "processing", "PROCESSING"):
        return "pending"

    status_value = payload.get("status")
    if status_value in (1, "1", "success", "SUCCESS", "done", "DONE"):
        return "confirmed"
    if status_value in (0, "0", "failed", "FAIL", "failure", "FAILURE"):
        return "failed"
    if status_value in (2, "2", "pending", "PENDING", "processing", "PROCESSING"):
        return "pending"

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
    pending_expectations: dict[str, Any],
) -> bool:
    """Return True when post-command delayed refresh should be scheduled."""
    if not mqtt_connected:
        return True
    return isinstance(device_serial, str) and device_serial in pending_expectations


def resolve_delayed_refresh_delay(
    *,
    mqtt_connected: bool,
    device_serial: str | None,
    pending_expectations: dict[str, Any],
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
    request_refresh: Callable[[], Awaitable[Any]],
) -> None:
    """Run one delayed refresh after command to absorb API status lag."""
    try:
        await asyncio.sleep(delay_seconds)
        await request_refresh()
    except asyncio.CancelledError:
        return


async def query_command_result_once(
    *,
    query_command_result: Callable[..., Awaitable[dict[str, Any]]],
    lipro_api_error: type[Exception],
    device_name: str,
    device_serial: str,
    device_type_hex: str,
    msg_sn: str,
    attempt: int,
    attempt_limit: int,
    logger: Any,
) -> dict[str, Any] | None:
    """Query command result once and return payload when available."""
    try:
        return await query_command_result(
            msg_sn=msg_sn,
            device_id=device_serial,
            device_type=device_type_hex,
        )
    except lipro_api_error as err:
        logger.debug(
            "query_command_result failed (device=%s, msgSn=%s, attempt=%s/%s, code=%s): %s",
            device_name,
            msg_sn,
            attempt,
            attempt_limit,
            err.code,
            err,
        )
        return None


async def poll_command_result_state(
    *,
    query_once: Callable[[int], Awaitable[dict[str, Any] | None]],
    classify_payload: Callable[[dict[str, Any]], str],
    attempt_limit: int,
    interval_seconds: float,
    on_attempt: Callable[[int, str], None] | None = None,
) -> tuple[str, int, dict[str, Any] | None]:
    """Poll command-result endpoint until confirmed/failed or attempts exhausted."""
    last_payload: dict[str, Any] | None = None
    for attempt in range(1, attempt_limit + 1):
        payload = await query_once(attempt)
        if payload is None:
            if attempt < attempt_limit:
                await asyncio.sleep(interval_seconds)
            continue

        last_payload = payload
        state = classify_payload(payload)
        if on_attempt is not None:
            on_attempt(attempt, state)
        if state in {"confirmed", "failed"}:
            return state, attempt, payload
        if attempt < attempt_limit:
            await asyncio.sleep(interval_seconds)

    return "unconfirmed", attempt_limit, last_payload


def apply_command_result_rejected(
    *,
    trace: dict[str, Any],
    route: str,
    msg_sn: str,
    device_serial: str,
    attempt: int,
    elapsed_seconds: float,
    logger: Any,
) -> dict[str, Any]:
    """Populate trace/failure fields for a rejected query_command_result response."""
    trace["route"] = route
    trace["success"] = False
    trace["error"] = "CommandResultRejected"
    trace["error_message"] = "command_result_failed"
    trace["command_result_verify"] = {
        "enabled": True,
        "verified": False,
        "attempts": attempt,
        "msg_sn": msg_sn,
        "state": "failed",
    }
    logger.warning(
        "query_command_result rejected command (device=%s, msgSn=%s, attempts=%s, elapsed=%.3fs, route=%s)",
        device_serial,
        msg_sn,
        attempt,
        elapsed_seconds,
        route,
    )
    return {
        "reason": "command_result_failed",
        "code": "command_result_failed",
        "route": route,
        "msg_sn": msg_sn,
        "device_id": device_serial,
    }


def apply_command_result_unconfirmed(
    *,
    trace: dict[str, Any],
    route: str,
    msg_sn: str,
    device_serial: str,
    attempt_limit: int,
    elapsed_seconds: float,
    last_payload: dict[str, Any] | None,
    logger: Any,
) -> dict[str, Any]:
    """Populate trace/failure fields for unconfirmed command-result polling."""
    trace["route"] = route
    trace["success"] = False
    trace["error"] = "CommandResultUnconfirmed"
    trace["error_message"] = "command_result_unconfirmed"
    trace["command_result_verify"] = {
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
    logger.warning(
        "query_command_result not confirmed (device=%s, msgSn=%s, attempts=%s, elapsed=%.3fs, route=%s, last_state=%s)",
        device_serial,
        msg_sn,
        attempt_limit,
        elapsed_seconds,
        route,
        trace["command_result_verify"]["last_state"],
    )
    return {
        "reason": "command_result_unconfirmed",
        "code": "command_result_unconfirmed",
        "route": route,
        "msg_sn": msg_sn,
        "device_id": device_serial,
    }


def apply_command_result_confirmed(
    *,
    trace: dict[str, Any],
    msg_sn: str,
    attempt: int,
    device_serial: str,
    elapsed_seconds: float,
    logger: Any,
) -> None:
    """Populate trace fields for confirmed command-result polling."""
    trace["command_result_verify"] = {
        "enabled": True,
        "verified": True,
        "attempts": attempt,
        "msg_sn": msg_sn,
    }
    logger.debug(
        "query_command_result confirmed (device=%s, msgSn=%s, attempts=%s, elapsed=%.3fs)",
        device_serial,
        msg_sn,
        attempt,
        elapsed_seconds,
    )


def apply_missing_msg_sn_failure(
    *,
    trace: dict[str, Any],
    route: str,
    command: str,
    device_name: str,
    device_serial: str,
    logger: Any,
) -> dict[str, Any]:
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
    logger.warning(
        "Command sent but msgSn missing for verification (command=%s, device=%s, route=%s, device_id=%s)",
        command,
        device_name,
        route,
        device_serial,
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
    trace: dict[str, Any],
    route: str,
    msg_sn: str,
    device_serial: str,
    attempt: int,
    attempt_limit: int,
    last_payload: dict[str, Any] | None,
    elapsed_seconds: float,
    logger: Any,
) -> tuple[bool, dict[str, Any] | None]:
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
    trace: dict[str, Any],
    route: str,
    command: str,
    device_name: str,
    device_serial: str,
    logger: Any,
) -> dict[str, Any]:
    """Populate trace/failure fields for pushSuccess=false command responses."""
    trace["route"] = route
    trace["success"] = False
    trace["error"] = "PushFailed"
    trace["error_message"] = "pushSuccess=false"
    logger.warning(
        "Command push failed (command=%s, device=%s, route=%s, device_id=%s)",
        command,
        device_name,
        route,
        device_serial,
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
    trace: dict[str, Any],
    route: str,
    device_serial: str,
    err: Any,
    update_trace_with_exception: Any,
) -> dict[str, Any]:
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
    trace: dict[str, Any],
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
