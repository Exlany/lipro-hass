"""Support-only helpers for request-policy pacing and retry mechanics."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from ...const.api import MAX_RATE_LIMIT_RETRIES
from ..utils.backoff import compute_exponential_retry_wait_time

SleepFn = Callable[[float], Awaitable[None]]


def is_change_state_command(command: str) -> bool:
    """Return True when command is CHANGE_STATE."""
    return command.upper() == "CHANGE_STATE"


def normalize_pacing_target(target_id: str) -> str:
    """Normalize command target ID for per-target pacing caches."""
    return target_id.strip().lower()


def enforce_command_pacing_cache_limit(
    *,
    command_pacing_cache_max_size: int,
    last_change_state_at: dict[str, float],
    change_state_min_interval: dict[str, float],
    change_state_busy_count: dict[str, int],
    command_pacing_target_locks: dict[str, asyncio.Lock],
) -> None:
    """Keep per-target pacing caches bounded."""
    tracked_targets = set(last_change_state_at) | set(change_state_min_interval)
    while len(tracked_targets) > command_pacing_cache_max_size:
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
    change_state_min_interval_seconds: float,
    change_state_max_interval_seconds: float,
    change_state_busy_multiplier: float,
    command_pacing_cache_max_size: int,
) -> tuple[float, int]:
    """Increase adaptive pacing interval when CHANGE_STATE hits busy error."""
    if not is_change_state_command(command):
        return change_state_min_interval_seconds, 0

    normalized_target = normalize_pacing_target(target_id)
    if not normalized_target:
        return change_state_min_interval_seconds, 0

    async with command_pacing_lock:
        current_interval = max(
            change_state_min_interval_seconds,
            change_state_min_interval.get(
                normalized_target,
                change_state_min_interval_seconds,
            ),
        )
        next_interval = min(
            change_state_max_interval_seconds,
            current_interval * change_state_busy_multiplier,
        )
        busy_count = change_state_busy_count.get(normalized_target, 0) + 1

        change_state_min_interval[normalized_target] = next_interval
        change_state_busy_count[normalized_target] = busy_count
        enforce_command_pacing_cache_limit(
            command_pacing_cache_max_size=command_pacing_cache_max_size,
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
    change_state_min_interval_seconds: float,
    change_state_recovery_multiplier: float,
    command_pacing_cache_max_size: int,
) -> None:
    """Recover adaptive pacing interval after successful CHANGE_STATE command."""
    if not is_change_state_command(command):
        return

    normalized_target = normalize_pacing_target(target_id)
    if not normalized_target:
        return

    async with command_pacing_lock:
        current_interval = max(
            change_state_min_interval_seconds,
            change_state_min_interval.get(
                normalized_target,
                change_state_min_interval_seconds,
            ),
        )
        recovered_interval = max(
            change_state_min_interval_seconds,
            current_interval * change_state_recovery_multiplier,
        )
        change_state_min_interval[normalized_target] = recovered_interval
        change_state_busy_count.pop(normalized_target, None)
        enforce_command_pacing_cache_limit(
            command_pacing_cache_max_size=command_pacing_cache_max_size,
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
    sleep: SleepFn,
    change_state_min_interval_seconds: float,
    command_pacing_cache_max_size: int,
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
                change_state_min_interval_seconds,
                change_state_min_interval.get(
                    normalized_target,
                    change_state_min_interval_seconds,
                ),
            )
            wait_time = 0.0
            if last is not None:
                wait_time = min_interval - (now - last)
            if wait_time <= 0:
                last_change_state_at[normalized_target] = now
                enforce_command_pacing_cache_limit(
                    command_pacing_cache_max_size=command_pacing_cache_max_size,
                    last_change_state_at=last_change_state_at,
                    change_state_min_interval=change_state_min_interval,
                    change_state_busy_count=change_state_busy_count,
                    command_pacing_target_locks=command_pacing_target_locks,
                )
                return

        sleep_fn = sleep if sleep is not None else asyncio.sleep
        await sleep_fn(wait_time)

        async with command_pacing_lock:
            last_change_state_at[normalized_target] = monotonic()
            enforce_command_pacing_cache_limit(
                command_pacing_cache_max_size=command_pacing_cache_max_size,
                last_change_state_at=last_change_state_at,
                change_state_min_interval=change_state_min_interval,
                change_state_busy_count=change_state_busy_count,
                command_pacing_target_locks=command_pacing_target_locks,
            )



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


def reached_max_rate_limit_retries(retry_count: int) -> bool:
    """Return whether retry count already exhausted the policy budget."""
    return retry_count >= MAX_RATE_LIMIT_RETRIES
