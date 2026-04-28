"""Support-only helpers for request-policy pacing and retry mechanics."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from ...const.api import MAX_RATE_LIMIT_RETRIES
from ..utils.backoff import compute_exponential_retry_wait_time

SleepFn = Callable[[float], Awaitable[None]]


@dataclass(slots=True)
class _CommandPacingCaches:
    last_change_state_at: dict[str, float]
    change_state_min_interval: dict[str, float]
    change_state_busy_count: dict[str, int]
    command_pacing_target_users: dict[str, int]
    command_pacing_target_locks: dict[str, asyncio.Lock]
    command_pacing_cache_max_size: int

    def enforce_limit(self) -> None:
        """Keep per-target pacing caches bounded."""
        tracked_targets = (
            set(self.last_change_state_at)
            | set(self.change_state_min_interval)
            | set(self.change_state_busy_count)
        )
        while len(tracked_targets) > self.command_pacing_cache_max_size:
            if self.last_change_state_at:
                oldest_target = min(
                    self.last_change_state_at.items(),
                    key=lambda item: item[1],
                )[0]
            else:
                oldest_target = next(iter(tracked_targets))

            self.last_change_state_at.pop(oldest_target, None)
            self.change_state_min_interval.pop(oldest_target, None)
            self.change_state_busy_count.pop(oldest_target, None)
            active_users = self.command_pacing_target_users.get(oldest_target, 0)
            if active_users <= 0:
                self.command_pacing_target_users.pop(oldest_target, None)

            lock = self.command_pacing_target_locks.get(oldest_target)
            if active_users <= 0 and lock is not None and not lock.locked():
                self.command_pacing_target_locks.pop(oldest_target, None)
            tracked_targets.discard(oldest_target)

        for target in tuple(self.command_pacing_target_locks):
            if (
                target in self.last_change_state_at
                or target in self.change_state_min_interval
            ):
                continue
            if target in self.change_state_busy_count:
                continue
            if self.command_pacing_target_users.get(target, 0) > 0:
                continue
            self.command_pacing_target_users.pop(target, None)
            lock = self.command_pacing_target_locks.get(target)
            if lock is not None and not lock.locked():
                self.command_pacing_target_locks.pop(target, None)


def is_change_state_command(command: str) -> bool:
    """Return True when command is CHANGE_STATE."""
    return command.upper() == "CHANGE_STATE"


def normalize_pacing_target(target_id: str) -> str:
    """Normalize command target ID for per-target pacing caches."""
    return target_id.strip().lower()


def _build_command_pacing_caches(
    *,
    last_change_state_at: dict[str, float],
    change_state_min_interval: dict[str, float],
    change_state_busy_count: dict[str, int],
    command_pacing_target_users: dict[str, int],
    command_pacing_target_locks: dict[str, asyncio.Lock],
    command_pacing_cache_max_size: int,
) -> _CommandPacingCaches:
    return _CommandPacingCaches(
        last_change_state_at=last_change_state_at,
        change_state_min_interval=change_state_min_interval,
        change_state_busy_count=change_state_busy_count,
        command_pacing_target_users=command_pacing_target_users,
        command_pacing_target_locks=command_pacing_target_locks,
        command_pacing_cache_max_size=command_pacing_cache_max_size,
    )


def enforce_command_pacing_cache_limit(*, caches: _CommandPacingCaches) -> None:
    """Keep per-target pacing caches bounded."""
    caches.enforce_limit()


async def record_change_state_busy(
    *,
    target_id: str,
    command: str,
    command_pacing_lock: asyncio.Lock,
    caches: _CommandPacingCaches,
    change_state_min_interval_seconds: float,
    change_state_max_interval_seconds: float,
    change_state_busy_multiplier: float,
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
            caches.change_state_min_interval.get(
                normalized_target,
                change_state_min_interval_seconds,
            ),
        )
        next_interval = min(
            change_state_max_interval_seconds,
            current_interval * change_state_busy_multiplier,
        )
        busy_count = caches.change_state_busy_count.get(normalized_target, 0) + 1

        caches.change_state_min_interval[normalized_target] = next_interval
        caches.change_state_busy_count[normalized_target] = busy_count
        caches.enforce_limit()
        return next_interval, busy_count


async def record_change_state_success(
    *,
    target_id: str,
    command: str,
    command_pacing_lock: asyncio.Lock,
    caches: _CommandPacingCaches,
    change_state_min_interval_seconds: float,
    change_state_recovery_multiplier: float,
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
            caches.change_state_min_interval.get(
                normalized_target,
                change_state_min_interval_seconds,
            ),
        )
        recovered_interval = max(
            change_state_min_interval_seconds,
            current_interval * change_state_recovery_multiplier,
        )
        caches.change_state_min_interval[normalized_target] = recovered_interval
        caches.change_state_busy_count.pop(normalized_target, None)
        caches.enforce_limit()


async def _register_pacing_target(
    *,
    target_id: str,
    command: str,
    command_pacing_lock: asyncio.Lock,
    caches: _CommandPacingCaches,
) -> tuple[str, asyncio.Lock] | None:
    """Return the normalized pacing target and its lock when pacing applies."""
    if not is_change_state_command(command):
        return None

    normalized_target = normalize_pacing_target(target_id)
    if not normalized_target:
        return None

    async with command_pacing_lock:
        target_lock = caches.command_pacing_target_locks.get(normalized_target)
        if target_lock is None:
            target_lock = asyncio.Lock()
            caches.command_pacing_target_locks[normalized_target] = target_lock
        caches.command_pacing_target_users[normalized_target] = (
            caches.command_pacing_target_users.get(normalized_target, 0) + 1
        )
    return normalized_target, target_lock


def _resolve_change_state_wait_time(
    *,
    normalized_target: str,
    caches: _CommandPacingCaches,
    change_state_min_interval_seconds: float,
    monotonic: Callable[[], float],
) -> tuple[float, float]:
    """Return the current timestamp and pacing wait time for one target."""
    now = monotonic()
    last = caches.last_change_state_at.get(normalized_target)
    min_interval = max(
        change_state_min_interval_seconds,
        caches.change_state_min_interval.get(
            normalized_target,
            change_state_min_interval_seconds,
        ),
    )
    wait_time = 0.0 if last is None else min_interval - (now - last)
    return now, wait_time


def _record_change_state_send(
    *,
    normalized_target: str,
    timestamp: float,
    caches: _CommandPacingCaches,
) -> None:
    """Record one paced CHANGE_STATE send and trim caches."""
    caches.last_change_state_at[normalized_target] = timestamp
    caches.enforce_limit()


async def _release_pacing_target(
    *,
    normalized_target: str,
    command_pacing_lock: asyncio.Lock,
    caches: _CommandPacingCaches,
) -> None:
    """Release one pacing-target user and trim caches."""
    async with command_pacing_lock:
        active_users = caches.command_pacing_target_users.get(normalized_target, 0) - 1
        if active_users > 0:
            caches.command_pacing_target_users[normalized_target] = active_users
        else:
            caches.command_pacing_target_users.pop(normalized_target, None)
        caches.enforce_limit()


async def _async_record_or_wait_for_change_state_send(
    *,
    normalized_target: str,
    target_lock: asyncio.Lock,
    command_pacing_lock: asyncio.Lock,
    caches: _CommandPacingCaches,
    monotonic: Callable[[], float],
    sleep: SleepFn,
    change_state_min_interval_seconds: float,
) -> None:
    """Serialize one target's send and wait only when pacing still applies."""
    async with target_lock:
        async with command_pacing_lock:
            now, wait_time = _resolve_change_state_wait_time(
                normalized_target=normalized_target,
                caches=caches,
                change_state_min_interval_seconds=change_state_min_interval_seconds,
                monotonic=monotonic,
            )
            if wait_time <= 0:
                _record_change_state_send(
                    normalized_target=normalized_target,
                    timestamp=now,
                    caches=caches,
                )
                return

        await sleep(wait_time)
        async with command_pacing_lock:
            _record_change_state_send(
                normalized_target=normalized_target,
                timestamp=monotonic(),
                caches=caches,
            )


async def throttle_change_state(
    *,
    target_id: str,
    command: str,
    command_pacing_lock: asyncio.Lock,
    caches: _CommandPacingCaches,
    monotonic: Callable[[], float],
    sleep: SleepFn,
    change_state_min_interval_seconds: float,
) -> None:
    """Pace high-frequency CHANGE_STATE sends for the same target."""
    registered_target = await _register_pacing_target(
        target_id=target_id,
        command=command,
        command_pacing_lock=command_pacing_lock,
        caches=caches,
    )
    if registered_target is None:
        return

    normalized_target, target_lock = registered_target
    try:
        await _async_record_or_wait_for_change_state_send(
            normalized_target=normalized_target,
            target_lock=target_lock,
            command_pacing_lock=command_pacing_lock,
            caches=caches,
            monotonic=monotonic,
            sleep=sleep,
            change_state_min_interval_seconds=change_state_min_interval_seconds,
        )
    finally:
        await _release_pacing_target(
            normalized_target=normalized_target,
            command_pacing_lock=command_pacing_lock,
            caches=caches,
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
