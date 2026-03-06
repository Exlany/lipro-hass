"""Tests for coordinator runtime helper functions."""

from __future__ import annotations

import inspect
from typing import Any

from custom_components.lipro.core.coordinator.runtime.coordinator_runtime import (
    should_refresh_device_list,
    should_schedule_mqtt_setup,
)


def _call_should_schedule_mqtt_setup(**overrides: Any) -> bool:
    """Call helper with signature-aware kwargs for refactor compatibility."""
    defaults: dict[str, Any] = {
        "mqtt_enabled": True,
        "has_mqtt_client": False,
        "mqtt_setup_in_progress": False,
        "has_devices": True,
        "now": 100.0,
    }
    defaults.update(overrides)

    kwargs: dict[str, Any] = {}
    for name in inspect.signature(should_schedule_mqtt_setup).parameters:
        if name in defaults:
            kwargs[name] = defaults[name]
            continue
        if name.endswith(("_at", "_time", "_until")):
            kwargs[name] = 0.0
            continue
        if "cooldown" in name or "backoff" in name or "retry" in name:
            kwargs[name] = 0.0
            continue
        if name.startswith(("has_", "is_")) or name.endswith("_enabled"):
            kwargs[name] = False
            continue
        msg = f"Unhandled should_schedule_mqtt_setup argument: {name}"
        raise AssertionError(msg)

    return should_schedule_mqtt_setup(**kwargs)


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
    assert _call_should_schedule_mqtt_setup() is True


def test_should_schedule_mqtt_setup_when_any_condition_missing() -> None:
    assert _call_should_schedule_mqtt_setup(mqtt_enabled=False) is False
    assert _call_should_schedule_mqtt_setup(has_mqtt_client=True) is False
    assert _call_should_schedule_mqtt_setup(mqtt_setup_in_progress=True) is False
    assert _call_should_schedule_mqtt_setup(has_devices=False) is False


def test_should_schedule_mqtt_setup_honors_runtime_backoff_when_exposed() -> None:
    params = inspect.signature(should_schedule_mqtt_setup).parameters
    backoff_param = next(
        (
            name
            for name in params
            if name != "mqtt_setup_in_progress"
            and (
                "cooldown" in name
                or "backoff" in name
                or "retry" in name
                or name.endswith("_until")
            )
        ),
        None,
    )
    if backoff_param is None:
        return

    override: object
    if backoff_param.endswith("_seconds"):
        override = 30.0
    elif backoff_param.endswith(("_until", "_at")):
        override = 130.0
    else:
        override = True

    assert (
        _call_should_schedule_mqtt_setup(now=100.0, **{backoff_param: override})
        is False
    )
