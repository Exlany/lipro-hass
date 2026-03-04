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
