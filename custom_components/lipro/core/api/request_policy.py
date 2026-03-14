"""Request pacing and retry policy helpers for Lipro REST protocol."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from importlib import import_module
import logging
from time import monotonic
from typing import Final

from ...const.api import (
    ERROR_DEVICE_BUSY,
    ERROR_DEVICE_BUSY_STR,
    MAX_RATE_LIMIT_RETRIES,
    MAX_RETRY_AFTER,
)
from ..utils.retry_after import parse_retry_after as _parse_retry_after_util
from . import response_safety as _response_safety
from .errors import LiproApiError, LiproRateLimitError

_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")

COMMAND_BUSY_RETRY_MAX_ATTEMPTS: Final = 3
COMMAND_BUSY_RETRY_BASE_DELAY_SECONDS: Final = 0.25
CHANGE_STATE_MIN_INTERVAL_SECONDS: Final = 0.2
CHANGE_STATE_MAX_INTERVAL_SECONDS: Final = 1.2
CHANGE_STATE_BUSY_MULTIPLIER: Final = 1.6
CHANGE_STATE_RECOVERY_MULTIPLIER: Final = 0.8
COMMAND_PACING_CACHE_MAX_SIZE: Final = 256


def _get_iot_busy_retry_service():
    module = import_module("custom_components.lipro.core.api.command_api_service")
    return module.iot_request_with_busy_retry


def is_change_state_command(command: str) -> bool:
    """Return True when command is CHANGE_STATE."""
    return command.upper() == "CHANGE_STATE"


def normalize_pacing_target(target_id: str) -> str:
    """Normalize command target ID for per-target pacing caches."""
    return target_id.strip().lower()


def enforce_command_pacing_cache_limit(
    *,
    last_change_state_at: dict[str, float],
    change_state_min_interval: dict[str, float],
    change_state_busy_count: dict[str, int],
    command_pacing_target_locks: dict[str, asyncio.Lock],
) -> None:
    """Keep per-target pacing caches bounded."""
    tracked_targets = set(last_change_state_at) | set(change_state_min_interval)
    while len(tracked_targets) > COMMAND_PACING_CACHE_MAX_SIZE:
        if last_change_state_at:
            oldest_target = min(last_change_state_at.items(), key=lambda item: item[1])[
                0
            ]
        else:
            oldest_target = next(iter(tracked_targets))

        last_change_state_at.pop(oldest_target, None)
        change_state_min_interval.pop(oldest_target, None)
        change_state_busy_count.pop(oldest_target, None)
        lock = command_pacing_target_locks.get(oldest_target)
        has_waiters = False
        if lock is not None:
            has_waiters = bool(getattr(lock, "_waiters", None))

        if lock is not None and not lock.locked() and not has_waiters:
            command_pacing_target_locks.pop(oldest_target, None)
        tracked_targets.discard(oldest_target)


async def record_change_state_busy(
    *,
    target_id: str,
    command: str,
    command_pacing_lock: asyncio.Lock,
    change_state_min_interval: dict[str, float],
    change_state_busy_count: dict[str, int],
    last_change_state_at: dict[str, float],
    command_pacing_target_locks: dict[str, asyncio.Lock],
) -> tuple[float, int]:
    """Increase adaptive pacing interval when CHANGE_STATE hits busy error."""
    if not is_change_state_command(command):
        return CHANGE_STATE_MIN_INTERVAL_SECONDS, 0

    normalized_target = normalize_pacing_target(target_id)
    if not normalized_target:
        return CHANGE_STATE_MIN_INTERVAL_SECONDS, 0

    async with command_pacing_lock:
        current_interval = max(
            CHANGE_STATE_MIN_INTERVAL_SECONDS,
            change_state_min_interval.get(
                normalized_target,
                CHANGE_STATE_MIN_INTERVAL_SECONDS,
            ),
        )
        next_interval = min(
            CHANGE_STATE_MAX_INTERVAL_SECONDS,
            current_interval * CHANGE_STATE_BUSY_MULTIPLIER,
        )
        busy_count = change_state_busy_count.get(normalized_target, 0) + 1

        change_state_min_interval[normalized_target] = next_interval
        change_state_busy_count[normalized_target] = busy_count
        enforce_command_pacing_cache_limit(
            last_change_state_at=last_change_state_at,
            change_state_min_interval=change_state_min_interval,
            change_state_busy_count=change_state_busy_count,
            command_pacing_target_locks=command_pacing_target_locks,
        )
        return next_interval, busy_count


async def record_change_state_success(
    *,
    target_id: str,
    command: str,
    command_pacing_lock: asyncio.Lock,
    change_state_min_interval: dict[str, float],
    change_state_busy_count: dict[str, int],
    last_change_state_at: dict[str, float],
    command_pacing_target_locks: dict[str, asyncio.Lock],
) -> None:
    """Recover adaptive pacing interval after successful CHANGE_STATE command."""
    if not is_change_state_command(command):
        return

    normalized_target = normalize_pacing_target(target_id)
    if not normalized_target:
        return

    async with command_pacing_lock:
        current_interval = max(
            CHANGE_STATE_MIN_INTERVAL_SECONDS,
            change_state_min_interval.get(
                normalized_target,
                CHANGE_STATE_MIN_INTERVAL_SECONDS,
            ),
        )
        recovered_interval = max(
            CHANGE_STATE_MIN_INTERVAL_SECONDS,
            current_interval * CHANGE_STATE_RECOVERY_MULTIPLIER,
        )
        change_state_min_interval[normalized_target] = recovered_interval
        change_state_busy_count.pop(normalized_target, None)
        enforce_command_pacing_cache_limit(
            last_change_state_at=last_change_state_at,
            change_state_min_interval=change_state_min_interval,
            change_state_busy_count=change_state_busy_count,
            command_pacing_target_locks=command_pacing_target_locks,
        )


async def throttle_change_state(
    *,
    target_id: str,
    command: str,
    command_pacing_lock: asyncio.Lock,
    command_pacing_target_locks: dict[str, asyncio.Lock],
    last_change_state_at: dict[str, float],
    change_state_min_interval: dict[str, float],
    change_state_busy_count: dict[str, int],
    monotonic: Callable[[], float],
    sleep: Callable[[float], Awaitable[None]],
) -> None:
    """Pace high-frequency CHANGE_STATE sends for the same target."""
    if not is_change_state_command(command):
        return

    normalized_target = normalize_pacing_target(target_id)
    if not normalized_target:
        return

    async with command_pacing_lock:
        target_lock = command_pacing_target_locks.get(normalized_target)
        if target_lock is None:
            target_lock = asyncio.Lock()
            command_pacing_target_locks[normalized_target] = target_lock

    async with target_lock:
        async with command_pacing_lock:
            now = monotonic()
            last = last_change_state_at.get(normalized_target)
            min_interval = max(
                CHANGE_STATE_MIN_INTERVAL_SECONDS,
                change_state_min_interval.get(
                    normalized_target,
                    CHANGE_STATE_MIN_INTERVAL_SECONDS,
                ),
            )
            wait_time = 0.0
            if last is not None:
                wait_time = min_interval - (now - last)
            if wait_time <= 0:
                last_change_state_at[normalized_target] = now
                enforce_command_pacing_cache_limit(
                    last_change_state_at=last_change_state_at,
                    change_state_min_interval=change_state_min_interval,
                    change_state_busy_count=change_state_busy_count,
                    command_pacing_target_locks=command_pacing_target_locks,
                )
                return

        await (sleep or asyncio.sleep)(wait_time)

        async with command_pacing_lock:
            last_change_state_at[normalized_target] = monotonic()
            enforce_command_pacing_cache_limit(
                last_change_state_at=last_change_state_at,
                change_state_min_interval=change_state_min_interval,
                change_state_busy_count=change_state_busy_count,
                command_pacing_target_locks=command_pacing_target_locks,
            )


def parse_retry_after(headers: dict[str, str]) -> float | None:
    """Parse Retry-After header value."""
    return _parse_retry_after_util(headers)


def compute_rate_limit_wait_time(
    *,
    retry_after: float | None,
    retry_count: int,
    max_retry_after: float,
) -> float:
    """Compute clamped wait time for rate-limit retries."""
    if retry_after is not None:
        return min(max_retry_after, max(0.1, retry_after))
    return compute_exponential_retry_wait_time(
        retry_count=retry_count,
        base_delay_seconds=1.0,
        max_delay_seconds=max_retry_after,
    )


def compute_exponential_retry_wait_time(
    *,
    retry_count: int,
    base_delay_seconds: float,
    max_delay_seconds: float | None = None,
    min_delay_seconds: float = 0.1,
) -> float:
    """Compute one exponential retry delay with optional min/max caps."""
    min_delay = float(max(0.0, min_delay_seconds))
    wait_time = float(max(min_delay, base_delay_seconds * (2**retry_count)))
    if max_delay_seconds is None:
        return wait_time
    return float(min(max_delay_seconds, wait_time))


class RequestPolicy:
    """Explicit owner for pacing, busy-retry, and retry/backoff policy state."""

    @staticmethod
    def is_change_state_command(command: str) -> bool:
        """Return whether one command participates in pacing rules."""
        return is_change_state_command(command)

    @staticmethod
    def normalize_pacing_target(target_id: str) -> str:
        """Normalize one pacing target into the cache-key form."""
        return normalize_pacing_target(target_id)

    @staticmethod
    def parse_retry_after(headers: dict[str, str]) -> float | None:
        """Parse one Retry-After header mapping into seconds."""
        return parse_retry_after(headers)

    def __init__(self) -> None:
        """Initialize mutable pacing state owned by the request policy."""
        self.command_pacing_lock = asyncio.Lock()
        self.command_pacing_target_locks: dict[str, asyncio.Lock] = {}
        self.last_change_state_at: dict[str, float] = {}
        self.change_state_min_interval: dict[str, float] = {}
        self.change_state_busy_count: dict[str, int] = {}

    def enforce_command_pacing_cache_limit(self) -> None:
        """Trim per-target pacing caches to the configured maximum size."""
        enforce_command_pacing_cache_limit(
            last_change_state_at=self.last_change_state_at,
            change_state_min_interval=self.change_state_min_interval,
            change_state_busy_count=self.change_state_busy_count,
            command_pacing_target_locks=self.command_pacing_target_locks,
        )

    def _enforce_command_pacing_cache_limit(self) -> None:
        self.enforce_command_pacing_cache_limit()

    async def handle_rate_limit(
        self,
        path: str,
        headers: dict[str, str],
        retry_count: int,
        *,
        logger: logging.Logger = _LOGGER,
        sleep: Callable[[float], Awaitable[None]] | None = None,
    ) -> float:
        """Handle 429 retry/backoff as an explicit policy decision."""
        retry_after = parse_retry_after(headers)
        if retry_count >= MAX_RATE_LIMIT_RETRIES:
            logger.warning(
                "Rate limited on %s after %d retries (retry_after=%s)",
                path,
                MAX_RATE_LIMIT_RETRIES,
                retry_after,
            )
            msg = f"Rate limited after {MAX_RATE_LIMIT_RETRIES} retries"
            raise LiproRateLimitError(msg, retry_after)

        wait_time = compute_rate_limit_wait_time(
            retry_after=retry_after,
            retry_count=retry_count,
            max_retry_after=MAX_RETRY_AFTER,
        )
        logger.debug(
            "Rate limited on %s, waiting %.1fs before retry %d/%d",
            path,
            wait_time,
            retry_count + 1,
            MAX_RATE_LIMIT_RETRIES,
        )
        await (sleep or asyncio.sleep)(wait_time)
        return wait_time

    @staticmethod
    def is_command_busy_error(err: Exception) -> bool:
        """Check whether an API error is a transient command-busy response."""
        normalized = _response_safety.normalize_response_code(
            getattr(err, "code", None)
        )
        if normalized in (ERROR_DEVICE_BUSY, ERROR_DEVICE_BUSY_STR):
            return True

        message = str(err)
        if not message:
            return False
        lowered = message.lower()
        return "设备繁忙" in message or "device busy" in lowered

    async def record_change_state_busy(
        self,
        target_id: str,
        command: str,
    ) -> tuple[float, int]:
        """Increase adaptive pacing interval when CHANGE_STATE hits busy error."""
        return await record_change_state_busy(
            target_id=target_id,
            command=command,
            command_pacing_lock=self.command_pacing_lock,
            change_state_min_interval=self.change_state_min_interval,
            change_state_busy_count=self.change_state_busy_count,
            last_change_state_at=self.last_change_state_at,
            command_pacing_target_locks=self.command_pacing_target_locks,
        )

    async def record_change_state_success(self, target_id: str, command: str) -> None:
        """Recover adaptive pacing interval after successful CHANGE_STATE command."""
        await record_change_state_success(
            target_id=target_id,
            command=command,
            command_pacing_lock=self.command_pacing_lock,
            change_state_min_interval=self.change_state_min_interval,
            change_state_busy_count=self.change_state_busy_count,
            last_change_state_at=self.last_change_state_at,
            command_pacing_target_locks=self.command_pacing_target_locks,
        )

    async def throttle_change_state(self, target_id: str, command: str) -> None:
        """Pace high-frequency CHANGE_STATE sends for the same target."""
        await throttle_change_state(
            target_id=target_id,
            command=command,
            command_pacing_lock=self.command_pacing_lock,
            command_pacing_target_locks=self.command_pacing_target_locks,
            last_change_state_at=self.last_change_state_at,
            change_state_min_interval=self.change_state_min_interval,
            change_state_busy_count=self.change_state_busy_count,
            monotonic=monotonic,
            sleep=asyncio.sleep,
        )

    async def iot_request_with_busy_retry(
        self,
        path: str,
        body_data: dict[str, object],
        *,
        target_id: str,
        command: str,
        iot_request: Callable[[str, dict[str, object]], Awaitable[object]],
        logger: logging.Logger = _LOGGER,
    ) -> dict[str, object]:
        """Execute one IoT command request with explicit policy-owned pacing."""
        iot_busy_retry_service = _get_iot_busy_retry_service()

        return await iot_busy_retry_service(
            path=path,
            body_data=body_data,
            target_id=target_id,
            command=command,
            attempt_limit=COMMAND_BUSY_RETRY_MAX_ATTEMPTS,
            base_delay_seconds=COMMAND_BUSY_RETRY_BASE_DELAY_SECONDS,
            iot_request=iot_request,
            throttle_change_state=self.throttle_change_state,
            record_change_state_success=self.record_change_state_success,
            is_command_busy_error=self.is_command_busy_error,
            lipro_api_error=LiproApiError,
            record_change_state_busy=self.record_change_state_busy,
            sleep=asyncio.sleep,
            logger=logger,
        )


__all__ = [
    "COMMAND_BUSY_RETRY_BASE_DELAY_SECONDS",
    "COMMAND_BUSY_RETRY_MAX_ATTEMPTS",
    "COMMAND_PACING_CACHE_MAX_SIZE",
    "RequestPolicy",
    "compute_exponential_retry_wait_time",
    "compute_rate_limit_wait_time",
    "enforce_command_pacing_cache_limit",
    "is_change_state_command",
    "normalize_pacing_target",
    "parse_retry_after",
    "record_change_state_busy",
    "record_change_state_success",
    "throttle_change_state",
]
