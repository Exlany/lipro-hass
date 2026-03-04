"""Request pacing and command throttling for LiproClient."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from ...const.api import (
    ERROR_DEVICE_BUSY,
    ERROR_DEVICE_BUSY_STR,
    MAX_RATE_LIMIT_RETRIES,
    MAX_RETRY_AFTER,
)
from . import response_safety as _response_safety
from .client_base import _ClientBase
from .command_service import (
    iot_request_with_busy_retry as iot_request_with_busy_retry_service,
)
from .errors import LiproApiError, LiproRateLimitError
from .request_policy import (
    COMMAND_BUSY_RETRY_BASE_DELAY_SECONDS as _COMMAND_BUSY_RETRY_BASE_DELAY_SECONDS,
    COMMAND_BUSY_RETRY_MAX_ATTEMPTS as _COMMAND_BUSY_RETRY_MAX_ATTEMPTS,
    compute_rate_limit_wait_time as _compute_rate_limit_wait_time,
    enforce_command_pacing_cache_limit as _enforce_command_pacing_cache_limit_policy,
    is_change_state_command as _is_change_state_command_policy,
    normalize_pacing_target as _normalize_pacing_target_policy,
    parse_retry_after as _parse_retry_after_policy,
    record_change_state_busy as _record_change_state_busy_policy,
    record_change_state_success as _record_change_state_success_policy,
    throttle_change_state as _throttle_change_state_policy,
)

# Use the same logger instance as custom_components.lipro.core.api.client._LOGGER
# so tests patching client._LOGGER.* still intercept logs here.
_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")


class _ClientPacingMixin(_ClientBase):
    """Mixin implementing request pacing and adaptive throttling."""

    def _init_pacing(self) -> None:
        """Initialize pacing/adaptive throttling state containers."""
        self._command_pacing_lock = asyncio.Lock()
        self._command_pacing_target_locks = {}
        self._last_change_state_at = {}
        self._change_state_min_interval = {}
        self._change_state_busy_count = {}

    async def _handle_rate_limit(
        self,
        path: str,
        headers: dict[str, str],
        retry_count: int,
    ) -> float:
        """Handle 429 rate limit with exponential backoff.

        Args:
            path: API path (for logging).
            headers: Response headers (may contain Retry-After).
            retry_count: Current retry attempt (0-based).

        Returns:
            Wait time in seconds.

        Raises:
            LiproRateLimitError: If max retries exceeded.

        """
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

    @staticmethod
    def _is_command_busy_error(err: Exception) -> bool:
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

    @staticmethod
    def _is_change_state_command(command: str) -> bool:
        """Return True when command is CHANGE_STATE."""
        return _is_change_state_command_policy(command)

    @staticmethod
    def _normalize_pacing_target(target_id: str) -> str:
        """Normalize command target ID for per-target pacing caches."""
        return _normalize_pacing_target_policy(target_id)

    def _enforce_command_pacing_cache_limit(self) -> None:
        """Keep per-target pacing caches bounded."""
        _enforce_command_pacing_cache_limit_policy(
            last_change_state_at=self._last_change_state_at,
            change_state_min_interval=self._change_state_min_interval,
            change_state_busy_count=self._change_state_busy_count,
            command_pacing_target_locks=self._command_pacing_target_locks,
        )

    async def _record_change_state_busy(
        self,
        target_id: str,
        command: str,
    ) -> tuple[float, int]:
        """Increase adaptive pacing interval when CHANGE_STATE hits busy error."""
        return await _record_change_state_busy_policy(
            target_id=target_id,
            command=command,
            command_pacing_lock=self._command_pacing_lock,
            change_state_min_interval=self._change_state_min_interval,
            change_state_busy_count=self._change_state_busy_count,
            last_change_state_at=self._last_change_state_at,
            command_pacing_target_locks=self._command_pacing_target_locks,
        )

    async def _record_change_state_success(self, target_id: str, command: str) -> None:
        """Recover adaptive pacing interval after successful CHANGE_STATE command."""
        await _record_change_state_success_policy(
            target_id=target_id,
            command=command,
            command_pacing_lock=self._command_pacing_lock,
            change_state_min_interval=self._change_state_min_interval,
            change_state_busy_count=self._change_state_busy_count,
            last_change_state_at=self._last_change_state_at,
            command_pacing_target_locks=self._command_pacing_target_locks,
        )

    async def _iot_request_with_busy_retry(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        target_id: str,
        command: str,
    ) -> dict[str, Any]:
        """Send IoT command request with retry for transient busy errors."""
        return await iot_request_with_busy_retry_service(
            path=path,
            body_data=body_data,
            target_id=target_id,
            command=command,
            attempt_limit=_COMMAND_BUSY_RETRY_MAX_ATTEMPTS,
            base_delay_seconds=_COMMAND_BUSY_RETRY_BASE_DELAY_SECONDS,
            iot_request=self._iot_request,
            throttle_change_state=self._throttle_change_state,
            record_change_state_success=self._record_change_state_success,
            is_command_busy_error=self._is_command_busy_error,
            lipro_api_error=LiproApiError,
            record_change_state_busy=self._record_change_state_busy,
            sleep=asyncio.sleep,
            logger=_LOGGER,
        )

    async def _throttle_change_state(self, target_id: str, command: str) -> None:
        """Pace high-frequency CHANGE_STATE sends for the same target."""
        await _throttle_change_state_policy(
            target_id=target_id,
            command=command,
            command_pacing_lock=self._command_pacing_lock,
            command_pacing_target_locks=self._command_pacing_target_locks,
            last_change_state_at=self._last_change_state_at,
            change_state_min_interval=self._change_state_min_interval,
            change_state_busy_count=self._change_state_busy_count,
            monotonic=time.monotonic,
            sleep=asyncio.sleep,
        )

    @staticmethod
    def _parse_retry_after(headers: dict[str, str]) -> float | None:
        """Parse Retry-After header value."""
        return _parse_retry_after_policy(headers)
