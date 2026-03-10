"""Compatibility coverage for the extracted device identity model."""

from __future__ import annotations

from tests.core import test_device_identity as legacy_identity


def test_device_identity_from_api_data_extracts_expected_fields() -> None:
    """Keep the extracted identity parser aligned with legacy expectations."""
    legacy_identity.test_device_identity_from_api_data_extracts_expected_fields()


def test_device_identity_is_frozen() -> None:
    """Keep the immutable identity contract explicit in the new layout."""
    legacy_identity.test_device_identity_is_frozen()


def test_lipro_device_identity_property_matches_device_fields() -> None:
    """Keep the facade-to-identity mapping covered under the new directory."""
    legacy_identity.test_lipro_device_identity_property_matches_device_fields()
