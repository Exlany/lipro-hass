"""Unit tests for command dispatch helpers."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.lipro.core.api import LiproApiError
from custom_components.lipro.core.command.dispatch import (
    CommandDispatchPlan,
    execute_command_dispatch,
    normalize_group_power_command,
    resolve_group_fallback_member_id,
)
from custom_components.lipro.core.device import LiproDevice


def _make_device(
    serial: str = "03ab5ccd7c000001",
    is_group: bool = False,
    *,
    extra_data: dict[str, Any] | None = None,
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
    properties: list[dict[str, object]] = [{"key": 1, "value": "1"}]
    command, resolved_properties = normalize_group_power_command(
        "CHANGE_STATE",
        cast(list[dict[str, str]] | None, properties),
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


@pytest.mark.asyncio
async def test_execute_command_dispatch_device_direct_route() -> None:
    """Non-group devices should call send_command directly."""
    device = _make_device(is_group=False)
    client = AsyncMock()
    client.send_command = AsyncMock(return_value={"pushSuccess": True})

    result, route = await execute_command_dispatch(
        client,
        device=device,
        plan=CommandDispatchPlan(
            route="device_direct",
            command="POWER_ON",
            properties=None,
            member_fallback_id=None,
        ),
    )

    assert result == {"pushSuccess": True}
    assert route == "device_direct"
    client.send_command.assert_awaited_once()
    client.send_group_command.assert_not_called()


@pytest.mark.asyncio
async def test_execute_command_dispatch_group_error_fallback_to_member() -> None:
    """Group API errors should fallback to member when fallback id is present."""
    device = _make_device(serial="mesh_group_10001", is_group=True)
    client = AsyncMock()
    client.send_group_command = AsyncMock(side_effect=LiproApiError("boom", 500))
    client.send_command = AsyncMock(return_value={"pushSuccess": True, "source": "m"})

    result, route = await execute_command_dispatch(
        client,
        device=device,
        plan=CommandDispatchPlan(
            route="group_direct",
            command="POWER_ON",
            properties=None,
            member_fallback_id="03ab111111111111",
        ),
    )

    assert result == {"pushSuccess": True, "source": "m"}
    assert route == "group_error_fallback_member"
    client.send_group_command.assert_awaited_once()
    client.send_command.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("push_success", [False, 0, "0", "false"])
async def test_execute_command_dispatch_group_push_fail_fallback_to_member(
    push_success: object,
) -> None:
    """Bool-like push failure values should fallback to member when configured."""
    device = _make_device(serial="mesh_group_10001", is_group=True)
    client = AsyncMock()
    client.send_group_command = AsyncMock(return_value={"pushSuccess": push_success})
    client.send_command = AsyncMock(return_value={"pushSuccess": True, "source": "m"})

    result, route = await execute_command_dispatch(
        client,
        device=device,
        plan=CommandDispatchPlan(
            route="group_direct",
            command="POWER_ON",
            properties=None,
            member_fallback_id="03ab111111111111",
        ),
    )

    assert result == {"pushSuccess": True, "source": "m"}
    assert route == "group_push_fail_fallback_member"
    client.send_group_command.assert_awaited_once()
    client.send_command.assert_awaited_once()


@pytest.mark.asyncio
async def test_execute_command_dispatch_fallback_guard_allows_early_return() -> None:
    """Defensive branch: if fallback predicate forces True but member id is None."""
    device = _make_device(serial="mesh_group_10001", is_group=True)
    client = AsyncMock()
    client.send_group_command = AsyncMock(return_value={"pushSuccess": False})
    client.send_command = AsyncMock()

    with patch(
        "custom_components.lipro.core.command.dispatch._should_fallback_after_group_result",
        return_value=True,
    ):
        result, route = await execute_command_dispatch(
            client,
            device=device,
            plan=CommandDispatchPlan(
                route="group_direct",
                command="POWER_ON",
                properties=None,
                member_fallback_id=None,
            ),
        )

    assert result == {"pushSuccess": False}
    assert route == "group_direct"
    client.send_group_command.assert_awaited_once()
    client.send_command.assert_not_called()


@pytest.mark.asyncio
async def test_execute_command_dispatch_group_error_without_fallback_raises() -> None:
    """Group API error should bubble up when fallback id is absent."""
    device = _make_device(serial="mesh_group_10001", is_group=True)
    client = AsyncMock()
    client.send_group_command = AsyncMock(side_effect=LiproApiError("boom", 500))
    client.send_command = AsyncMock()

    with pytest.raises(LiproApiError, match="boom"):
        await execute_command_dispatch(
            client,
            device=device,
            plan=CommandDispatchPlan(
                route="group_direct",
                command="POWER_ON",
                properties=None,
                member_fallback_id=None,
            ),
        )

    client.send_command.assert_not_called()
