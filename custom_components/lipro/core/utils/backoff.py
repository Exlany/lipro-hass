"""Neutral shared exponential backoff helpers."""

from __future__ import annotations


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


__all__ = ["compute_exponential_retry_wait_time"]
