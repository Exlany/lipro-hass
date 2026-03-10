"""Tests for MQTT polling helper functions."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.lipro.core.coordinator.mqtt.polling import (
    resolve_base_scan_interval_seconds,
    resolve_polling_interval_seconds_on_mqtt_connect,
    resolve_polling_interval_seconds_on_mqtt_disconnect,
)


def test_resolve_base_scan_interval_uses_default_when_options_missing() -> None:
    """Absent options should leave the configured default untouched."""
    assert (
        resolve_base_scan_interval_seconds(
            options=None,
            option_name="scan_interval",
            default=30,
            min_value=10,
            max_value=300,
            logger=MagicMock(),
        )
        == 30
    )


def test_resolve_base_scan_interval_coerces_and_clamps_values() -> None:
    """Option coercion should handle strings and hard min/max bounds."""
    logger = MagicMock()

    assert (
        resolve_base_scan_interval_seconds(
            options={"scan_interval": "45"},
            option_name="scan_interval",
            default=30,
            min_value=10,
            max_value=300,
            logger=logger,
        )
        == 45
    )
    assert (
        resolve_base_scan_interval_seconds(
            options={"scan_interval": 5},
            option_name="scan_interval",
            default=30,
            min_value=10,
            max_value=300,
            logger=logger,
        )
        == 10
    )
    assert (
        resolve_base_scan_interval_seconds(
            options={"scan_interval": 500},
            option_name="scan_interval",
            default=30,
            min_value=10,
            max_value=300,
            logger=logger,
        )
        == 300
    )


def test_resolve_base_scan_interval_logs_and_falls_back_for_invalid_values() -> None:
    """Invalid scan interval values should log once and return the default."""
    logger = MagicMock()

    assert (
        resolve_base_scan_interval_seconds(
            options={"scan_interval": "invalid"},
            option_name="scan_interval",
            default=30,
            min_value=10,
            max_value=300,
            logger=logger,
        )
        == 30
    )
    logger.warning.assert_called_once_with(
        "Invalid option %s=%r, using default %d",
        "scan_interval",
        "invalid",
        30,
    )


def test_polling_interval_resolution_distinguishes_connect_and_disconnect() -> None:
    """MQTT connect should relax polling while disconnect should keep base."""
    assert (
        resolve_polling_interval_seconds_on_mqtt_connect(base_seconds=30, multiplier=4)
        == 120
    )
    assert resolve_polling_interval_seconds_on_mqtt_connect(
        base_seconds=30,
        multiplier=1,
    ) == 30
    assert resolve_polling_interval_seconds_on_mqtt_disconnect(base_seconds=30) == 30
