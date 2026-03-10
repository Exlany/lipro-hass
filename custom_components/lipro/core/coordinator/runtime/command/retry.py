"""Retry strategy for command result verification."""

from __future__ import annotations

from typing import Final

from ....api.request_policy import compute_exponential_retry_wait_time


class RetryStrategy:
    """Manage retry logic for command result verification."""

    DEFAULT_MAX_ATTEMPTS: Final[int] = 6
    DEFAULT_BASE_DELAY: Final[float] = 0.35

    def __init__(
        self,
        *,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        base_delay: float = DEFAULT_BASE_DELAY,
    ) -> None:
        """Initialize retry strategy.

        Args:
            max_attempts: Maximum number of verification attempts
            base_delay: Base delay in seconds for exponential backoff
        """
        self._max_attempts = max_attempts
        self._base_delay = base_delay

    @property
    def max_attempts(self) -> int:
        """Get maximum retry attempts."""
        return self._max_attempts

    def build_retry_delays(self) -> list[float]:
        """Build progressive retry delay schedule with exponential backoff.

        Returns:
            List of delay values in seconds for each retry attempt
        """
        delays: list[float] = []
        for attempt in range(1, self._max_attempts):
            delay = compute_exponential_retry_wait_time(
                retry_count=attempt,
                base_delay_seconds=self._base_delay,
            )
            delays.append(delay)
        return delays

    def should_retry(self, attempt: int) -> bool:
        """Check if another retry attempt should be made.

        Args:
            attempt: Current attempt number (1-indexed)

        Returns:
            True if retry should continue
        """
        return attempt < self._max_attempts


__all__ = ["RetryStrategy"]
