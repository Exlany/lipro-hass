"""Tests for the canonical capability registry."""

from __future__ import annotations

from custom_components.lipro.const.categories import DeviceCategory
from custom_components.lipro.core.capability import (
    CapabilityRegistry,
    CapabilitySnapshot,
)
from custom_components.lipro.core.device import device_views


def test_capability_registry_builds_light_snapshot_from_profile() -> None:
    """Profile metadata should map to one canonical capability snapshot."""
    snapshot = CapabilityRegistry().from_device_profile(
        device_type_hex="FF000001",
        min_color_temp_kelvin=2700,
        max_color_temp_kelvin=6500,
        max_fan_gear=6,
    )

    assert isinstance(snapshot, CapabilitySnapshot)
    assert snapshot.device_type_hex == "ff000001"
    assert snapshot.category == DeviceCategory.LIGHT
    assert snapshot.platforms == ("light",)
    assert snapshot.supports_color_temp is True
    assert snapshot.max_fan_gear == 6


def test_capability_registry_builds_snapshot_from_device(make_device) -> None:
    """Device aggregates should project through the registry without drift."""
    device = make_device(
        "fanLight",
        serial="03ab5ccd7c444444",
        max_fan_gear=8,
        min_color_temp_kelvin=3000,
        max_color_temp_kelvin=6500,
    )

    snapshot = CapabilityRegistry().from_device(device)

    assert snapshot.device_type_hex == device.device_type_hex
    assert snapshot.category == device.category
    assert snapshot.platforms == tuple(device.platforms)
    assert snapshot.max_fan_gear == 8
    assert snapshot.supports_color_temp is True
    assert snapshot.is_fan_light is True


def test_capability_snapshot_supports_platform_and_panel() -> None:
    """Capability snapshots should expose platform and panel projections."""
    switch_snapshot = CapabilityRegistry().from_device_type("ff000003")
    outlet_snapshot = CapabilityRegistry().from_device_type("ff000006")

    assert switch_snapshot.is_panel is True
    assert switch_snapshot.supports_platform("switch") is True
    assert switch_snapshot.supports_platform("light") is False
    assert outlet_snapshot.is_panel is False
    assert outlet_snapshot.is_outlet is True


def test_device_views_follow_capability_snapshot(monkeypatch, make_device) -> None:
    """Device views should derive category/platforms from capability truth."""
    device = make_device("light", serial="03ab5ccd7c555555")
    snapshot = CapabilitySnapshot(
        device_type_hex="ff000006",
        category=DeviceCategory.OUTLET,
        platforms=("switch",),
        supports_color_temp=False,
        max_fan_gear=3,
    )

    monkeypatch.setattr(device_views, "build_capabilities_snapshot", lambda _: snapshot)

    assert device_views.capabilities(device) == snapshot
    assert device_views.category(device) == DeviceCategory.OUTLET
    assert device_views.platforms(device) == ["switch"]
    assert device_views.fan_speed_range(device) == (1, 3)
