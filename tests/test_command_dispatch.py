"""Unit tests for command dispatch helpers."""

from __future__ import annotations

from custom_components.lipro.core.command_dispatch import (
    normalize_group_power_command,
    resolve_group_fallback_member_id,
)
from custom_components.lipro.core.device import LiproDevice


def _make_device(
    serial: str = "03ab5ccd7c000001",
    is_group: bool = False,
    *,
    extra_data: dict | None = None,
) -> LiproDevice:
    """Create a minimal LiproDevice instance for helper tests."""
    return LiproDevice(
        device_number=1,
        serial=serial,
        name="Test Device",
        device_type=1,
        iot_name="lipro_led",
        physical_model="light",
        is_group=is_group,
        extra_data=extra_data or {},
    )


def test_normalize_group_power_command_non_string_key_keeps_original() -> None:
    """Non-string property keys should preserve CHANGE_STATE payload."""
    properties = [{"key": 1, "value": "1"}]
    command, resolved_properties = normalize_group_power_command(
        "CHANGE_STATE",
        properties,
    )

    assert command == "CHANGE_STATE"
    assert resolved_properties == properties


def test_normalize_group_power_command_unknown_power_value_keeps_original() -> None:
    """Unknown power values should not collapse to POWER_ON/OFF."""
    properties = [{"key": "powerState", "value": "unexpected"}]
    command, resolved_properties = normalize_group_power_command(
        "CHANGE_STATE",
        properties,
    )

    assert command == "CHANGE_STATE"
    assert resolved_properties == properties


def test_resolve_group_fallback_member_id_non_string_member_returns_none() -> None:
    """Fallback is invalid when the single member id is not a string."""
    device = _make_device(
        serial="mesh_group_10001",
        is_group=True,
        extra_data={"group_member_ids": [123]},
    )

    result = resolve_group_fallback_member_id(device, "03ab111111111111")

    assert result is None


def test_resolve_group_fallback_member_id_invalid_member_format_returns_none() -> None:
    """Fallback is rejected when group member id is not a valid IoT id."""
    device = _make_device(
        serial="mesh_group_10001",
        is_group=True,
        extra_data={"group_member_ids": ["mesh_group_20001"]},
    )

    result = resolve_group_fallback_member_id(device, "03ab111111111111")

    assert result is None
