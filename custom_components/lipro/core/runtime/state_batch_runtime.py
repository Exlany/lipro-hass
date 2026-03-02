"""Runtime helpers for state-batch metric normalization and reporting."""

from __future__ import annotations

from .status_strategy import StateBatchMetric


def normalize_state_batch_metric(
    batch_size: int,
    duration_seconds: float,
    fallback_depth: int,
) -> StateBatchMetric:
    """Normalize one coordinator state-batch metric sample."""
    return (
        batch_size,
        max(0.0, duration_seconds),
        max(0, fallback_depth),
    )


def summarize_recent_state_batch_metrics(
    metrics: list[StateBatchMetric] | tuple[StateBatchMetric, ...],
    *,
    sample_size: int,
) -> tuple[float, int, int]:
    """Compute (avg_latency_seconds, max_fallback_depth, sample_count)."""
    if not metrics:
        return (0.0, 0, 0)

    capped_sample_size = max(1, sample_size)
    sample_count = min(capped_sample_size, len(metrics))
    latency_sum = 0.0
    max_depth = 0
    for idx, (_, duration_seconds, depth) in enumerate(reversed(metrics), start=1):
        latency_sum += max(0.0, duration_seconds)
        max_depth = max(max_depth, depth, 0)
        if idx >= sample_count:
            break

    return (latency_sum / sample_count, max_depth, sample_count)
