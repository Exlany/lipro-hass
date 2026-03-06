"""Tests for state-batch runtime helpers."""

from __future__ import annotations

from custom_components.lipro.core.coordinator.runtime.state_batch_runtime import (
    normalize_state_batch_metric,
    summarize_recent_state_batch_metrics,
)


def test_normalize_state_batch_metric_clamps_negative_values() -> None:
    assert normalize_state_batch_metric(3, -1.5, -2) == (3, 0.0, 0)


def test_summarize_recent_state_batch_metrics_empty_returns_zeros() -> None:
    assert summarize_recent_state_batch_metrics([], sample_size=5) == (0.0, 0, 0)


def test_summarize_recent_state_batch_metrics_handles_sample_and_clamping() -> None:
    metrics = [
        (1, 1.0, 1),
        (2, -3.0, -2),
        (3, 2.0, 4),
    ]

    assert summarize_recent_state_batch_metrics(metrics, sample_size=2) == (1.0, 4, 2)
    assert summarize_recent_state_batch_metrics(metrics, sample_size=0) == (2.0, 4, 1)
