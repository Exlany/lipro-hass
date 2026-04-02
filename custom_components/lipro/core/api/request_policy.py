"""Request pacing and retry policy helpers for Lipro REST protocol."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
import logging
from time import monotonic
from typing import Final

from ...const.api import (
    ERROR_DEVICE_BUSY,
    ERROR_DEVICE_BUSY_STR,
    MAX_RATE_LIMIT_RETRIES,
    MAX_RETRY_AFTER,
)
from ..utils.backoff import (
    compute_exponential_retry_wait_time as _compute_exponential_retry_wait_time,
)
from ..utils.retry_after import parse_retry_after as _parse_retry_after_util
from . import response_safety as _response_safety
from .errors import LiproApiError, LiproRateLimitError
from .request_policy_support import (
    _build_command_pacing_caches,
    _CommandPacingCaches,
    compute_rate_limit_wait_time as _support_compute_rate_limit_wait_time,
    enforce_command_pacing_cache_limit as _support_enforce_command_pacing_cache_limit,
    is_change_state_command as _support_is_change_state_command,
    normalize_pacing_target as _support_normalize_pacing_target,
    reached_max_rate_limit_retries,
    record_change_state_busy as _support_record_change_state_busy,
    record_change_state_success as _support_record_change_state_success,
    throttle_change_state as _support_throttle_change_state,
)
from .types import JsonObject, JsonValue

_LOGGER = logging.getLogger('custom_components.lipro.core.api')

COMMAND_BUSY_RETRY_MAX_ATTEMPTS: Final = 3
COMMAND_BUSY_RETRY_BASE_DELAY_SECONDS: Final = 0.25
CHANGE_STATE_MIN_INTERVAL_SECONDS: Final = 0.2
CHANGE_STATE_MAX_INTERVAL_SECONDS: Final = 1.2
CHANGE_STATE_BUSY_MULTIPLIER: Final = 1.6
CHANGE_STATE_RECOVERY_MULTIPLIER: Final = 0.8
COMMAND_PACING_CACHE_MAX_SIZE: Final = 256

type SleepFn = Callable[[float], Awaitable[None]]


def _new_command_pacing_caches() -> _CommandPacingCaches:
    return _build_command_pacing_caches(
        last_change_state_at={},
        change_state_min_interval={},
        change_state_busy_count={},
        command_pacing_target_users={},
        command_pacing_target_locks={},
        command_pacing_cache_max_size=COMMAND_PACING_CACHE_MAX_SIZE,
    )


@dataclass(slots=True)
class _RequestPolicyPacingState:
    """Explicit pacing-state owner for request-policy caches and locks."""

    command_pacing_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    caches: _CommandPacingCaches = field(default_factory=_new_command_pacing_caches)


def is_change_state_command(command: str) -> bool:
    """Return True when command is CHANGE_STATE."""
    return _support_is_change_state_command(command)


def normalize_pacing_target(target_id: str) -> str:
    """Normalize command target ID for per-target pacing caches."""
    return _support_normalize_pacing_target(target_id)


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
    return _support_compute_rate_limit_wait_time(
        retry_after=retry_after,
        retry_count=retry_count,
        max_retry_after=max_retry_after,
    )


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
        self._pacing_state = _RequestPolicyPacingState()

    @property
    def command_pacing_lock(self) -> asyncio.Lock:
        """Expose the pacing lock for focused compatibility tests."""
        return self._pacing_state.command_pacing_lock

    @property
    def command_pacing_target_locks(self) -> dict[str, asyncio.Lock]:
        """Expose per-target pacing locks for focused compatibility tests."""
        return self._pacing_state.caches.command_pacing_target_locks

    @property
    def command_pacing_target_users(self) -> dict[str, int]:
        """Expose per-target pacing user counters for focused compatibility tests."""
        return self._pacing_state.caches.command_pacing_target_users

    @property
    def last_change_state_at(self) -> dict[str, float]:
        """Expose last-send timestamps for focused compatibility tests."""
        return self._pacing_state.caches.last_change_state_at

    @property
    def change_state_min_interval(self) -> dict[str, float]:
        """Expose adaptive pacing intervals for focused compatibility tests."""
        return self._pacing_state.caches.change_state_min_interval

    @property
    def change_state_busy_count(self) -> dict[str, int]:
        """Expose busy counters for focused compatibility tests."""
        return self._pacing_state.caches.change_state_busy_count

    def enforce_command_pacing_cache_limit(self) -> None:
        """Trim per-target pacing caches to the configured maximum size."""
        _support_enforce_command_pacing_cache_limit(caches=self._pacing_state.caches)

    def _enforce_command_pacing_cache_limit(self) -> None:
        self.enforce_command_pacing_cache_limit()

    async def handle_rate_limit(
        self,
        path: str,
        headers: dict[str, str],
        retry_count: int,
        *,
        logger: logging.Logger = _LOGGER,
        sleep: SleepFn | None = None,
    ) -> float:
        """Handle 429 retry/backoff as an explicit policy decision."""
        retry_after = parse_retry_after(headers)
        if reached_max_rate_limit_retries(retry_count):
            logger.warning(
                'Rate limited on %s after %d retries (retry_after=%s)',
                path,
                MAX_RATE_LIMIT_RETRIES,
                retry_after,
            )
            msg = f'Rate limited after {MAX_RATE_LIMIT_RETRIES} retries'
            raise LiproRateLimitError(msg, retry_after)

        wait_time = compute_rate_limit_wait_time(
            retry_after=retry_after,
            retry_count=retry_count,
            max_retry_after=MAX_RETRY_AFTER,
        )
        logger.debug(
            'Rate limited on %s, waiting %.1fs before retry %d/%d',
            path,
            wait_time,
            retry_count + 1,
            MAX_RATE_LIMIT_RETRIES,
        )
        wait = asyncio.sleep if sleep is None else sleep
        await wait(wait_time)
        return wait_time

    @staticmethod
    def is_command_busy_error(err: Exception) -> bool:
        """Check whether an API error is a transient command-busy response."""
        normalized = _response_safety.normalize_response_code(
            getattr(err, 'code', None)
        )
        if normalized in (ERROR_DEVICE_BUSY, ERROR_DEVICE_BUSY_STR):
            return True

        message = str(err)
        if not message:
            return False
        lowered = message.lower()
        return '设备繁忙' in message or 'device busy' in lowered

    async def record_change_state_busy(
        self,
        target_id: str,
        command: str,
    ) -> tuple[float, int]:
        """Increase adaptive pacing interval when CHANGE_STATE hits busy error."""
        return await _support_record_change_state_busy(
            target_id=target_id,
            command=command,
            command_pacing_lock=self.command_pacing_lock,
            caches=self._pacing_state.caches,
            change_state_min_interval_seconds=CHANGE_STATE_MIN_INTERVAL_SECONDS,
            change_state_max_interval_seconds=CHANGE_STATE_MAX_INTERVAL_SECONDS,
            change_state_busy_multiplier=CHANGE_STATE_BUSY_MULTIPLIER,
        )

    async def record_change_state_success(self, target_id: str, command: str) -> None:
        """Recover adaptive pacing interval after successful CHANGE_STATE command."""
        await _support_record_change_state_success(
            target_id=target_id,
            command=command,
            command_pacing_lock=self.command_pacing_lock,
            caches=self._pacing_state.caches,
            change_state_min_interval_seconds=CHANGE_STATE_MIN_INTERVAL_SECONDS,
            change_state_recovery_multiplier=CHANGE_STATE_RECOVERY_MULTIPLIER,
        )

    async def throttle_change_state(self, target_id: str, command: str) -> None:
        """Pace high-frequency CHANGE_STATE sends for the same target."""
        await _support_throttle_change_state(
            target_id=target_id,
            command=command,
            command_pacing_lock=self.command_pacing_lock,
            caches=self._pacing_state.caches,
            monotonic=monotonic,
            sleep=asyncio.sleep,
            change_state_min_interval_seconds=CHANGE_STATE_MIN_INTERVAL_SECONDS,
        )

    async def iot_request_with_busy_retry(
        self,
        path: str,
        body_data: JsonObject,
        *,
        target_id: str,
        command: str,
        iot_request: Callable[[str, JsonObject], Awaitable[JsonValue]],
        logger: logging.Logger = _LOGGER,
    ) -> JsonObject:
        """Execute one IoT command request with explicit policy-owned pacing."""
        for attempt in range(COMMAND_BUSY_RETRY_MAX_ATTEMPTS + 1):
            await self.throttle_change_state(target_id, command)
            try:
                result = await iot_request(path, body_data)
                await self.record_change_state_success(target_id, command)
                if isinstance(result, dict):
                    return result
                return {}
            except LiproApiError as err:
                if not self.is_command_busy_error(err):
                    raise

                adaptive_interval, busy_count = await self.record_change_state_busy(
                    target_id,
                    command,
                )
                if attempt >= COMMAND_BUSY_RETRY_MAX_ATTEMPTS:
                    raise

                wait_time = _compute_exponential_retry_wait_time(
                    retry_count=attempt,
                    base_delay_seconds=COMMAND_BUSY_RETRY_BASE_DELAY_SECONDS,
                )
                logger.debug(
                    (
                        'Command %s to %s busy (code=%s), retrying in %.2fs '
                        '(%d/%d), adaptive_interval=%.2fs busy_count=%d'
                    ),
                    command,
                    target_id,
                    getattr(err, 'code', None),
                    wait_time,
                    attempt + 1,
                    COMMAND_BUSY_RETRY_MAX_ATTEMPTS,
                    adaptive_interval,
                    busy_count,
                )
                await asyncio.sleep(wait_time)

        return {}


__all__ = [
    'COMMAND_BUSY_RETRY_BASE_DELAY_SECONDS',
    'COMMAND_BUSY_RETRY_MAX_ATTEMPTS',
    'COMMAND_PACING_CACHE_MAX_SIZE',
    'RequestPolicy',
    'compute_rate_limit_wait_time',
    'is_change_state_command',
    'normalize_pacing_target',
    'parse_retry_after',
]
