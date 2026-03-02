"""Tests for device identity index behavior."""

from __future__ import annotations

from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.device.device_identity_index import (
    DeviceIdentityIndex,
)


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


def test_get_compatible_with_direct_mapping_mutation() -> None:
    index = DeviceIdentityIndex()
    device = _make_device("dev1")

    # Simulate legacy direct writes to the public mapping.
    index.mapping["GW_Legacy"] = device

    assert index.get("gw_legacy") is device
    # Alias should be backfilled after first lookup.
    assert index.mapping["gw_legacy"] is device


def test_direct_mapping_mutation_scan_is_bounded() -> None:
    index = DeviceIdentityIndex()
    device = _make_device("dev1")
    index.mapping["GW_Target"] = device

    # Grow mapping beyond the scan limit to ensure get() stays bounded.
    for i in range(index._MAX_DIRECT_MUTATION_SCAN + 10):
        index.mapping[f"junk_{i}"] = device

    assert index.get("gw_target") is None
