"""Tests for coordinator runtime helper functions."""

from __future__ import annotations

from custom_components.lipro.core.coordinator_runtime import (
    should_refresh_device_list,
    should_schedule_mqtt_setup,
)


def test_should_refresh_device_list_when_no_devices() -> None:
    assert (
        should_refresh_device_list(
            has_devices=False,
            force_device_refresh=False,
            last_device_refresh_at=100.0,
            now=150.0,
            refresh_interval_seconds=60.0,
        )
        is True
    )


def test_should_refresh_device_list_when_force_refresh_enabled() -> None:
    assert (
        should_refresh_device_list(
            has_devices=True,
            force_device_refresh=True,
            last_device_refresh_at=100.0,
            now=101.0,
            refresh_interval_seconds=60.0,
        )
        is True
    )


def test_should_refresh_device_list_within_interval() -> None:
    assert (
        should_refresh_device_list(
            has_devices=True,
            force_device_refresh=False,
            last_device_refresh_at=100.0,
            now=120.0,
            refresh_interval_seconds=60.0,
        )
        is False
    )


def test_should_refresh_device_list_after_interval() -> None:
    assert (
        should_refresh_device_list(
            has_devices=True,
            force_device_refresh=False,
            last_device_refresh_at=100.0,
            now=160.0,
            refresh_interval_seconds=60.0,
        )
        is True
    )


def test_should_schedule_mqtt_setup_when_all_conditions_met() -> None:
    assert (
        should_schedule_mqtt_setup(
            mqtt_enabled=True,
            has_mqtt_client=False,
            mqtt_setup_in_progress=False,
            has_devices=True,
        )
        is True
    )


def test_should_schedule_mqtt_setup_when_any_condition_missing() -> None:
    assert (
        should_schedule_mqtt_setup(
            mqtt_enabled=False,
            has_mqtt_client=False,
            mqtt_setup_in_progress=False,
            has_devices=True,
        )
        is False
    )
    assert (
        should_schedule_mqtt_setup(
            mqtt_enabled=True,
            has_mqtt_client=True,
            mqtt_setup_in_progress=False,
            has_devices=True,
        )
        is False
    )
    assert (
        should_schedule_mqtt_setup(
            mqtt_enabled=True,
            has_mqtt_client=False,
            mqtt_setup_in_progress=True,
            has_devices=True,
        )
        is False
    )
    assert (
        should_schedule_mqtt_setup(
            mqtt_enabled=True,
            has_mqtt_client=False,
            mqtt_setup_in_progress=False,
            has_devices=False,
        )
        is False
    )
