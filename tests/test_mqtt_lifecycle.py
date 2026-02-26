"""Tests for MQTT lifecycle helper functions."""

from __future__ import annotations

from custom_components.lipro.core.mqtt_lifecycle import (
    compute_relaxed_polling_seconds,
    resolve_disconnect_notification_minutes,
    resolve_disconnect_started_at,
)


def test_compute_relaxed_polling_seconds() -> None:
    assert compute_relaxed_polling_seconds(30, 2) == 60


def test_resolve_disconnect_started_at_keeps_existing_timestamp() -> None:
    assert resolve_disconnect_started_at(123.0, now=999.0) == 123.0


def test_resolve_disconnect_started_at_sets_initial_timestamp() -> None:
    assert resolve_disconnect_started_at(None, now=999.0) == 999.0


def test_resolve_disconnect_notification_minutes_returns_none_when_not_ready() -> None:
    assert (
        resolve_disconnect_notification_minutes(
            mqtt_enabled=False,
            mqtt_connected=False,
            disconnect_started_at=10.0,
            disconnect_notified=False,
            now=100.0,
            threshold_seconds=30.0,
        )
        is None
    )
    assert (
        resolve_disconnect_notification_minutes(
            mqtt_enabled=True,
            mqtt_connected=True,
            disconnect_started_at=10.0,
            disconnect_notified=False,
            now=100.0,
            threshold_seconds=30.0,
        )
        is None
    )
    assert (
        resolve_disconnect_notification_minutes(
            mqtt_enabled=True,
            mqtt_connected=False,
            disconnect_started_at=None,
            disconnect_notified=False,
            now=100.0,
            threshold_seconds=30.0,
        )
        is None
    )
    assert (
        resolve_disconnect_notification_minutes(
            mqtt_enabled=True,
            mqtt_connected=False,
            disconnect_started_at=10.0,
            disconnect_notified=True,
            now=100.0,
            threshold_seconds=30.0,
        )
        is None
    )


def test_resolve_disconnect_notification_minutes_returns_none_below_threshold() -> None:
    assert (
        resolve_disconnect_notification_minutes(
            mqtt_enabled=True,
            mqtt_connected=False,
            disconnect_started_at=80.0,
            disconnect_notified=False,
            now=100.0,
            threshold_seconds=30.0,
        )
        is None
    )


def test_resolve_disconnect_notification_minutes_returns_elapsed_minutes() -> None:
    assert (
        resolve_disconnect_notification_minutes(
            mqtt_enabled=True,
            mqtt_connected=False,
            disconnect_started_at=10.0,
            disconnect_notified=False,
            now=190.0,
            threshold_seconds=30.0,
        )
        == 3
    )
