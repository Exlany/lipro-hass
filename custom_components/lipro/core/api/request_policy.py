"""Request pacing and retry policy helpers for Lipro API client."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Final

COMMAND_BUSY_RETRY_MAX_ATTEMPTS: Final = 3
COMMAND_BUSY_RETRY_BASE_DELAY_SECONDS: Final = 0.25
CHANGE_STATE_MIN_INTERVAL_SECONDS: Final = 0.2
CHANGE_STATE_MAX_INTERVAL_SECONDS: Final = 1.2
CHANGE_STATE_BUSY_MULTIPLIER: Final = 1.6
CHANGE_STATE_RECOVERY_MULTIPLIER: Final = 0.8
COMMAND_PACING_CACHE_MAX_SIZE: Final = 256


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
        waiters = getattr(lock, "_waiters", None)
        has_waiters = bool(waiters) if waiters is not None else False
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

        await sleep(wait_time)

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
    retry_after = headers.get("Retry-After") or headers.get("retry-after")
    if not retry_after:
        return None

    try:
        return float(retry_after)
    except ValueError:
        pass

    try:
        retry_dt = parsedate_to_datetime(retry_after)
        delta = (retry_dt - datetime.now(tz=retry_dt.tzinfo)).total_seconds()
        return max(0.0, delta)
    except (ValueError, TypeError):
        return None


def compute_rate_limit_wait_time(
    *,
    retry_after: float | None,
    retry_count: int,
    max_retry_after: float,
) -> float:
    """Compute clamped wait time for rate-limit retries."""
    return min(max_retry_after, max(0.1, retry_after or (2**retry_count)))
