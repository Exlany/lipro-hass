"""MQTT setup retry backoff state helpers."""

from __future__ import annotations

from collections.abc import Callable

from ..api.request_policy import compute_exponential_retry_wait_time


def _zero_jitter() -> float:
    """Default jitter provider for deterministic retry timing."""
    return 0.0


class MqttSetupBackoff:
    """Track bounded exponential retry backoff state for MQTT setup."""

    __slots__ = (
        "_failure_count",
        "_jitter",
        "_next_attempt_at",
        "base_delay",
        "max_delay",
    )

    def __init__(
        self,
        *,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: Callable[[], float] = _zero_jitter,
    ) -> None:
        """Initialize backoff policy with injectable jitter for tests."""
        if base_delay <= 0:
            msg = "base_delay must be > 0"
            raise ValueError(msg)
        if max_delay <= 0:
            msg = "max_delay must be > 0"
            raise ValueError(msg)
        if max_delay < base_delay:
            msg = "max_delay must be >= base_delay"
            raise ValueError(msg)

        self.base_delay: float = base_delay
        self.max_delay: float = max_delay
        self._jitter: Callable[[], float] = jitter
        self._failure_count: int = 0
        self._next_attempt_at: float = 0.0

    def should_attempt(self, now: float) -> bool:
        """Return whether MQTT setup should be attempted at current time."""
        return now >= self._next_attempt_at

    def on_failure(self, now: float) -> None:
        """Record failed attempt and schedule the next allowed retry time."""
        self._failure_count += 1
        bounded_delay = compute_exponential_retry_wait_time(
            retry_count=self._failure_count - 1,
            base_delay_seconds=self.base_delay,
            max_delay_seconds=self.max_delay,
            min_delay_seconds=0.0,
        )
        jitter_delay = self._jitter()
        wait_seconds = min(max(bounded_delay + jitter_delay, 0.0), self.max_delay)
        anchor = max(now, self._next_attempt_at)
        self._next_attempt_at = anchor + wait_seconds

    def on_success(self) -> None:
        """Reset backoff state after a successful MQTT setup."""
        self._failure_count = 0
        self._next_attempt_at = 0.0
