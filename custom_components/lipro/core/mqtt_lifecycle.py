"""MQTT lifecycle helper functions for coordinator state transitions."""

from __future__ import annotations


def compute_relaxed_polling_seconds(base_seconds: int, multiplier: int) -> int:
    """Return polling interval when MQTT real-time updates are available."""
    return base_seconds * multiplier


def resolve_disconnect_started_at(
    disconnect_started_at: float | None,
    *,
    now: float,
) -> float:
    """Keep the first disconnect timestamp and ignore repeated disconnect events."""
    if disconnect_started_at is not None:
        return disconnect_started_at
    return now


def resolve_disconnect_notification_minutes(
    *,
    mqtt_enabled: bool,
    mqtt_connected: bool,
    disconnect_started_at: float | None,
    disconnect_notified: bool,
    now: float,
    threshold_seconds: float,
) -> int | None:
    """Return disconnect duration in minutes when a notification should fire."""
    if (
        not mqtt_enabled
        or mqtt_connected
        or disconnect_started_at is None
        or disconnect_notified
    ):
        return None

    elapsed = now - disconnect_started_at
    if elapsed < threshold_seconds:
        return None
    return int(elapsed // 60)
