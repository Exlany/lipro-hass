"""Compatibility coverage for the extracted device network-info helper."""

from __future__ import annotations

from tests.core import test_device_network_info as legacy_network_info


def test_device_network_info_from_properties_extracts_expected_fields() -> None:
    """Keep network diagnostics extraction aligned with legacy assertions."""
    legacy_network_info.test_device_network_info_from_properties_extracts_expected_fields()


def test_lipro_device_network_info_property_matches_existing_accessors() -> None:
    """Keep the LiproDevice facade mapped to DeviceNetworkInfo accessors."""
    legacy_network_info.test_lipro_device_network_info_property_matches_existing_accessors()
