"""Tests for device identity index behavior."""

from __future__ import annotations

import pytest

from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex


def _make_device(serial: str) -> LiproDevice:
    """Create minimal test device."""
    return LiproDevice(
        device_number=1,
        serial=serial,
        name=serial,
        device_type=1,
        iot_name="lipro_led",
        physical_model="light",
        properties={},
    )


def test_register_and_get_with_case_aliases() -> None:
    index = DeviceIdentityIndex()
    device = _make_device("dev1")

    index.register("GW_Mixed_001", device)

    assert index.get("GW_Mixed_001") is device
    assert index.get("gw_mixed_001") is device
    assert index.get("  gw_mixed_001  ") is device


def test_unregister_respects_device_guard() -> None:
    index = DeviceIdentityIndex()
    device_a = _make_device("dev_a")
    device_b = _make_device("dev_b")

    index.register("gw_1", device_a)
    index.register("gw_2", device_b)
    index.unregister("gw_2", device=device_a)
    assert index.get("gw_2") is device_b

    index.unregister("gw_2", device=device_b)
    assert index.get("gw_2") is None


def test_mapping_is_read_only_view() -> None:
    index = DeviceIdentityIndex()
    device = _make_device("dev1")
    index.register("GW_Mixed_001", device)

    with pytest.raises(TypeError):
        index.mapping["GW_Mixed_001"] = device  # type: ignore[index]

    assert index.get("gw_mixed_001") is device


def test_replace_normalizes_aliases() -> None:
    index = DeviceIdentityIndex()
    device = _make_device("dev1")
    index.replace({" GW_Target ": device})

    assert index.get("GW_Target") is device
    assert index.get("gw_target") is device
