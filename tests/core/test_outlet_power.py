"""Tests for outlet power helper functions."""

from __future__ import annotations

from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
)
from custom_components.lipro.core.coordinator.outlet_power import (
    apply_outlet_power_info,
    should_reraise_outlet_power_error,
)
from custom_components.lipro.core.device import LiproDevice


def _make_device(serial: str = "outlet_1") -> LiproDevice:
    return LiproDevice(
        device_number=1,
        serial=serial,
        name="Outlet",
        device_type=1,
        iot_name="lipro_outlet",
        physical_model="outlet",
        is_group=False,
        properties={"powerState": "1"},
    )


def test_should_reraise_outlet_power_error_for_auth_and_connection() -> None:
    assert should_reraise_outlet_power_error(LiproAuthError("unauthorized")) is True
    assert should_reraise_outlet_power_error(LiproConnectionError("timeout")) is True
    assert should_reraise_outlet_power_error(LiproApiError("invalid")) is False


def test_apply_outlet_power_info_updates_device_extra_data() -> None:
    device = _make_device()

    updated = apply_outlet_power_info(
        device,
        {"nowPower": 42.5, "energyList": [{"t": "20240101", "v": 1.2}]},
    )

    assert updated is True
    assert device.extra_data["power_info"]["nowPower"] == 42.5


def test_apply_outlet_power_info_with_missing_device_or_payload() -> None:
    device = _make_device()

    assert apply_outlet_power_info(None, {"nowPower": 1}) is False
    assert apply_outlet_power_info(device, {}) is False
