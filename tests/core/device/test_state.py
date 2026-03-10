"""Compatibility coverage for the extracted device state helper."""

from __future__ import annotations

from tests.core import test_device_state as legacy_state


def test_device_state_reads_common_properties() -> None:
    """Keep common state accessors aligned with the pre-split tests."""
    legacy_state.test_device_state_reads_common_properties()


def test_device_state_color_temp_uses_device_range() -> None:
    """Keep device-specific color-temperature conversion behavior covered."""
    legacy_state.test_device_state_color_temp_uses_device_range()


def test_device_state_fan_gear_is_clamped() -> None:
    """Keep fan gear clamping covered close to the extracted helper."""
    legacy_state.test_device_state_fan_gear_is_clamped()


def test_device_state_position_is_clamped() -> None:
    """Keep curtain position clamping covered in the new module layout."""
    legacy_state.test_device_state_position_is_clamped()
