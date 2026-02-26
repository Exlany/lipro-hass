"""Runtime planning helpers for coordinator update orchestration."""

from __future__ import annotations


def should_refresh_device_list(
    *,
    has_devices: bool,
    force_device_refresh: bool,
    last_device_refresh_at: float,
    now: float,
    refresh_interval_seconds: float,
) -> bool:
    """Return True when a full device-list refresh should run."""
    if not has_devices or force_device_refresh:
        return True
    return now - last_device_refresh_at >= refresh_interval_seconds


def should_schedule_mqtt_setup(
    *,
    mqtt_enabled: bool,
    has_mqtt_client: bool,
    mqtt_setup_in_progress: bool,
    has_devices: bool,
) -> bool:
    """Return True when coordinator should schedule MQTT setup task."""
    return (
        mqtt_enabled
        and not has_mqtt_client
        and not mqtt_setup_in_progress
        and has_devices
    )
