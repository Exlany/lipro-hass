"""Compatibility coverage for the extracted device capabilities helper."""

from __future__ import annotations

from tests.core import test_device_capabilities as legacy_capabilities


def test_device_capabilities_from_device_profile() -> None:
    """Keep profile-derived category inference aligned with legacy tests."""
    legacy_capabilities.test_device_capabilities_from_device_profile()


def test_lipro_device_capabilities_property_matches_existing_flags() -> None:
    """Keep the LiproDevice facade flags aligned with DeviceCapabilities."""
    legacy_capabilities.test_lipro_device_capabilities_property_matches_existing_flags()
