"""Local helpers for firmware update entity state and task handling."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import datetime, timedelta
import logging
from typing import TypedDict

from ..core.ota.candidate import _OtaCandidate, has_pending_confirmation
from ..core.utils.log_safety import safe_error_placeholder


class FirmwareStateAttributes(TypedDict, total=False):
    """Typed extra-state projection exposed by the firmware entity."""

    certified: bool
    confirmation_required: bool
    ota_checked_at: str
    last_error: str
    last_error_type: str


def build_firmware_state_attributes(
    *,
    ota_candidate: _OtaCandidate | None,
    confirm_until: float,
    last_ota_refresh: datetime,
    last_error: Exception | None,
    time_min_utc: datetime,
    now_monotonic: Callable[[], float],
) -> FirmwareStateAttributes:
    """Project entity-private OTA state into stable extra attributes."""
    attrs: FirmwareStateAttributes = {
        "certified": ota_candidate.certified if ota_candidate else False,
        "confirmation_required": has_pending_confirmation(
            confirm_until,
            now_monotonic=now_monotonic(),
        ),
    }
    if last_ota_refresh != time_min_utc:
        attrs["ota_checked_at"] = last_ota_refresh.isoformat()
    if last_error is not None:
        attrs["last_error"] = safe_error_placeholder(last_error)
        attrs["last_error_type"] = type(last_error).__name__
    return attrs


def consume_wait_result(result: object) -> Exception | None:
    """Normalize gather(return_exceptions=True) output into an exception."""
    if isinstance(result, asyncio.CancelledError):
        return None
    return result if isinstance(result, Exception) else None


def clear_refresh_task(
    task: asyncio.Task[None],
    *,
    logger: logging.Logger,
) -> Exception | None:
    """Consume task exceptions to avoid background warning noise."""
    try:
        err = task.exception()
    except asyncio.CancelledError:
        return None
    if isinstance(err, Exception):
        logger.debug(
            "Background OTA refresh task failed (%s)",
            safe_error_placeholder(err),
        )
        return err
    return None


def notify_ota_error_callback(
    on_error: Callable[[Exception], None] | None,
    err: Exception,
    *,
    logger: logging.Logger,
) -> None:
    """Notify optional OTA error observer while swallowing callback noise."""
    if on_error is None:
        return
    try:
        on_error(err)
    except (
        AttributeError,
        LookupError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as callback_err:
        logger.error(
            "OTA error callback failed (%s)",
            safe_error_placeholder(callback_err),
            exc_info=logger.isEnabledFor(logging.DEBUG),
        )


def should_refresh_ota(
    *,
    last_ota_refresh: datetime,
    refresh_interval: timedelta,
    now: Callable[[], datetime],
) -> bool:
    """Return True when cached OTA metadata is stale enough to refresh."""
    return now() - last_ota_refresh >= refresh_interval
