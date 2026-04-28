"""Tests for MqttSetupBackoff validation and edge cases."""

from __future__ import annotations

import pytest

from custom_components.lipro.core.mqtt.setup_backoff import MqttSetupBackoff


def test_backoff_rejects_nonpositive_base_delay() -> None:
    with pytest.raises(ValueError, match="base_delay must be > 0"):
        MqttSetupBackoff(base_delay=0.0)


def test_backoff_rejects_nonpositive_max_delay() -> None:
    with pytest.raises(ValueError, match="max_delay must be > 0"):
        MqttSetupBackoff(base_delay=1.0, max_delay=0.0)


def test_backoff_rejects_max_less_than_base() -> None:
    with pytest.raises(ValueError, match="max_delay must be >= base_delay"):
        MqttSetupBackoff(base_delay=10.0, max_delay=5.0)


def test_backoff_failure_sequence_uses_exponential_schedule_and_cap() -> None:
    backoff = MqttSetupBackoff(base_delay=0.05, max_delay=0.2)

    backoff.on_failure(10.0)
    assert backoff.should_attempt(10.049) is False
    assert backoff.should_attempt(10.05) is True

    backoff.on_failure(10.05)
    assert backoff.should_attempt(10.149) is False
    assert backoff.should_attempt(10.15) is True

    backoff.on_failure(10.15)
    assert backoff.should_attempt(10.349) is False
    assert backoff.should_attempt(10.35) is True


def test_backoff_failure_inside_window_extends_from_existing_deadline() -> None:
    backoff = MqttSetupBackoff(base_delay=1.0, max_delay=60.0)

    backoff.on_failure(100.0)
    backoff.on_failure(100.5)

    assert backoff.should_attempt(102.999) is False
    assert backoff.should_attempt(103.0) is True


def test_backoff_success_resets_gate_immediately() -> None:
    backoff = MqttSetupBackoff(base_delay=1.0, max_delay=60.0)

    backoff.on_failure(100.0)
    assert backoff.should_attempt(100.5) is False

    backoff.on_success()

    assert backoff.should_attempt(100.5) is True
