"""Tests for MQTT polling helper functions."""

from __future__ import annotations

import logging
from typing import Any

import pytest

from custom_components.lipro.core.coordinator.mqtt.polling import (
    resolve_base_scan_interval_seconds,
    resolve_polling_interval_seconds_on_mqtt_connect,
    resolve_polling_interval_seconds_on_mqtt_disconnect,
)


class TestResolveBaseScanIntervalSeconds:
    """Test resolve_base_scan_interval_seconds."""

    def test_returns_default_when_options_none(self) -> None:
        """Test returns default when options is None."""
        result = resolve_base_scan_interval_seconds(
            options=None,
            option_name="scan_interval",
            default=30,
            min_value=10,
            max_value=300,
            logger=logging.getLogger(__name__),
        )
        assert result == 30

    def test_returns_value_from_options(self) -> None:
        """Test returns value from options."""
        result = resolve_base_scan_interval_seconds(
            options={"scan_interval": 60},
            option_name="scan_interval",
            default=30,
            min_value=10,
            max_value=300,
            logger=logging.getLogger(__name__),
        )
        assert result == 60

    def test_returns_default_when_option_missing(self) -> None:
        """Test returns default when option key missing."""
        result = resolve_base_scan_interval_seconds(
            options={"other_option": 100},
            option_name="scan_interval",
            default=30,
            min_value=10,
            max_value=300,
            logger=logging.getLogger(__name__),
        )
        assert result == 30

    def test_coerces_string_to_int(self) -> None:
        """Test coerces string value to int."""
        result = resolve_base_scan_interval_seconds(
            options={"scan_interval": "45"},
            option_name="scan_interval",
            default=30,
            min_value=10,
            max_value=300,
            logger=logging.getLogger(__name__),
        )
        assert result == 45

    def test_clamps_to_min_value(self) -> None:
        """Test clamps value to minimum."""
        result = resolve_base_scan_interval_seconds(
            options={"scan_interval": 5},
            option_name="scan_interval",
            default=30,
            min_value=10,
            max_value=300,
            logger=logging.getLogger(__name__),
        )
        assert result == 10

    def test_clamps_to_max_value(self) -> None:
        """Test clamps value to maximum."""
        result = resolve_base_scan_interval_seconds(
            options={"scan_interval": 500},
            option_name="scan_interval",
            default=30,
            min_value=10,
            max_value=300,
            logger=logging.getLogger(__name__),
        )
        assert result == 300

    def test_handles_invalid_value(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handles invalid value and returns default."""
        result = resolve_base_scan_interval_seconds(
            options={"scan_interval": "invalid"},
            option_name="scan_interval",
            default=30,
            min_value=10,
            max_value=300,
            logger=logging.getLogger(__name__),
        )
        assert result == 30


class TestResolvePollingIntervalOnMqttConnect:
    """Test resolve_polling_interval_seconds_on_mqtt_connect."""

    def test_applies_multiplier(self) -> None:
        """Test applies multiplier to base seconds."""
        result = resolve_polling_interval_seconds_on_mqtt_connect(
            base_seconds=30,
            multiplier=4,
        )
        # compute_relaxed_polling_seconds(30, 4) = 30 * 4 = 120
        assert result == 120

    def test_multiplier_one(self) -> None:
        """Test multiplier of 1 returns base."""
        result = resolve_polling_interval_seconds_on_mqtt_connect(
            base_seconds=30,
            multiplier=1,
        )
        assert result == 30

    def test_large_multiplier(self) -> None:
        """Test large multiplier."""
        result = resolve_polling_interval_seconds_on_mqtt_connect(
            base_seconds=60,
            multiplier=10,
        )
        assert result == 600


class TestResolvePollingIntervalOnMqttDisconnect:
    """Test resolve_polling_interval_seconds_on_mqtt_disconnect."""

    def test_returns_base_seconds(self) -> None:
        """Test returns base seconds unchanged."""
        result = resolve_polling_interval_seconds_on_mqtt_disconnect(base_seconds=30)
        assert result == 30

    def test_various_base_values(self) -> None:
        """Test various base values."""
        assert resolve_polling_interval_seconds_on_mqtt_disconnect(base_seconds=10) == 10
        assert resolve_polling_interval_seconds_on_mqtt_disconnect(base_seconds=60) == 60
        assert (
            resolve_polling_interval_seconds_on_mqtt_disconnect(base_seconds=300) == 300
        )
