"""Temporary pacing adapter kept for legacy tests and compat shells."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import logging
import time

from ...const.api import MAX_RATE_LIMIT_RETRIES, MAX_RETRY_AFTER
from .errors import LiproRateLimitError
from .request_policy import (
    RequestPolicy,
    compute_rate_limit_wait_time as _compute_rate_limit_wait_time,
)

MONOTONIC = time.monotonic

# Use the same logger instance as custom_components.lipro.core.api.client._LOGGER
# so tests patching client._LOGGER.* still intercept logs here.
_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")


class _ClientPacingMixin:
    """Thin compatibility adapter over the explicit ``RequestPolicy`` collaborator."""

    _request_policy: RequestPolicy
    _iot_request: Callable[[str, dict[str, object]], Awaitable[object]]

    def _init_pacing(self) -> None:
        """Initialize the request policy collaborator and legacy aliases."""
        self._request_policy = RequestPolicy()
        self._command_pacing_lock = self._request_policy.command_pacing_lock
        self._command_pacing_target_locks = self._request_policy.command_pacing_target_locks
        self._last_change_state_at = self._request_policy.last_change_state_at
        self._change_state_min_interval = self._request_policy.change_state_min_interval
        self._change_state_busy_count = self._request_policy.change_state_busy_count

    async def _handle_rate_limit(
        self,
        path: str,
        headers: dict[str, str],
        retry_count: int,
    ) -> float:
        """Handle 429 rate limit with exponential backoff."""
        retry_after = self._parse_retry_after(headers)
        if retry_count >= MAX_RATE_LIMIT_RETRIES:
            _LOGGER.warning(
                "Rate limited on %s after %d retries (retry_after=%s)",
                path,
                MAX_RATE_LIMIT_RETRIES,
                retry_after,
            )
            msg = f"Rate limited after {MAX_RATE_LIMIT_RETRIES} retries"
            raise LiproRateLimitError(msg, retry_after)

        wait_time = _compute_rate_limit_wait_time(
            retry_after=retry_after,
            retry_count=retry_count,
            max_retry_after=MAX_RETRY_AFTER,
        )
        _LOGGER.debug(
            "Rate limited on %s, waiting %.1fs before retry %d/%d",
            path,
            wait_time,
            retry_count + 1,
            MAX_RATE_LIMIT_RETRIES,
        )
        await asyncio.sleep(wait_time)
        return wait_time

    def _enforce_command_pacing_cache_limit(self) -> None:
        self._request_policy.enforce_command_pacing_cache_limit()

    @staticmethod
    def _is_command_busy_error(err: Exception) -> bool:
        return RequestPolicy.is_command_busy_error(err)

    @staticmethod
    def _is_change_state_command(command: str) -> bool:
        return RequestPolicy.is_change_state_command(command)

    @staticmethod
    def _normalize_pacing_target(target_id: str) -> str:
        return RequestPolicy.normalize_pacing_target(target_id)

    async def _record_change_state_busy(
        self,
        target_id: str,
        command: str,
    ) -> tuple[float, int]:
        return await self._request_policy.record_change_state_busy(target_id, command)

    async def _record_change_state_success(self, target_id: str, command: str) -> None:
        await self._request_policy.record_change_state_success(target_id, command)

    async def _iot_request_with_busy_retry(
        self,
        path: str,
        body_data: dict[str, object],
        *,
        target_id: str,
        command: str,
    ) -> dict[str, object]:
        return await self._request_policy.iot_request_with_busy_retry(
            path,
            body_data,
            target_id=target_id,
            command=command,
            iot_request=self._iot_request,
            logger=_LOGGER,
        )

    async def _throttle_change_state(self, target_id: str, command: str) -> None:
        await self._request_policy.throttle_change_state(target_id, command)

    @staticmethod
    def _parse_retry_after(headers: dict[str, str]) -> float | None:
        return RequestPolicy.parse_retry_after(headers)


__all__ = ["MONOTONIC", "_ClientPacingMixin", "asyncio", "time"]
