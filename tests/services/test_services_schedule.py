"""Tests for schedule service helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.core import (
    LiproApiError,
    LiproAuthError,
    LiproRefreshTokenExpiredError,
)
from custom_components.lipro.core.coordinator.services.auth_service import (
    CoordinatorAuthService,
)
from custom_components.lipro.core.coordinator.services.protocol_service import (
    build_schedule_mesh_context,
)
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.services.schedule import (
    async_execute_schedule_operation,
    normalize_schedule_row,
)
from tests.coordinator_double import _CoordinatorDouble


@dataclass
class _ScheduleDeviceDouble:
    """Schedule-facing device projection used only by helper tests."""

    serial: str = "03ab5ccd7c111111"
    iot_device_id: str = "03ab0000000000a1"
    device_type_hex: str = "0x1032"
    mesh_gateway_device_id: str | None = ""
    mesh_group_member_ids: list[str] | None = None
    ir_remote_gateway_device_id: str | None = None

    def __post_init__(self) -> None:
        self.mesh_group_member_ids = list(self.mesh_group_member_ids or [])


def _make_schedule_device(
    *,
    serial: str = "03ab5ccd7c111111",
    iot_device_id: str = "03ab0000000000a1",
    device_type_hex: str = "0x1032",
    mesh_gateway_device_id: str | None = "",
    mesh_group_member_ids: list[str] | None = None,
    ir_remote_gateway_device_id: str | None = None,
) -> LiproDevice:
    """Create one explicit LiproDevice double for schedule helper tests."""
    return cast(
        LiproDevice,
        _ScheduleDeviceDouble(
            serial=serial,
            iot_device_id=iot_device_id,
            device_type_hex=device_type_hex,
            mesh_gateway_device_id=mesh_gateway_device_id,
            mesh_group_member_ids=mesh_group_member_ids,
            ir_remote_gateway_device_id=ir_remote_gateway_device_id,
        ),
    )


class _ScheduleCoordinatorDouble(_CoordinatorDouble):
    """Coordinator double for schedule helper tests."""

    def __init__(self, *, auth_service: object | None = None) -> None:
        super().__init__()
        if auth_service is not None:
            self.auth_service = auth_service


def test_normalize_schedule_row_uses_empty_schedule_when_schedule_field_invalid() -> None:
    """Non-dict ``schedule`` values should fallback to an empty schedule."""
    result = normalize_schedule_row({"id": 10, "schedule": "invalid"})

    assert result == {
        "id": 10,
        "active": True,
        "days": [],
        "times": [],
        "events": [],
    }


def test_normalize_schedule_row_drops_unpaired_or_invalid_time_events() -> None:
    """Invalid or unpaired time/event values should be filtered together."""
    result = normalize_schedule_row(
        {
            "id": 11,
            "active": True,
            "schedule": {
                "days": [1, "bad"],
                "time": [3600, -1, 90000, "bad"],
                "evt": [1, "0", "bad"],
            },
        }
    )

    assert result == {
        "id": 11,
        "active": True,
        "days": [1],
        "times": ["01:00"],
        "events": [1],
    }


@pytest.mark.asyncio
async def test_async_execute_schedule_operation_maps_lipro_api_error() -> None:
    """LiproApiError should be logged and mapped via raise_service_error."""
    device = _make_schedule_device()
    api_error = LiproApiError("boom", 500)
    protocol_call = AsyncMock(side_effect=api_error)
    logger = MagicMock()
    raise_service_error = MagicMock(side_effect=RuntimeError("mapped"))

    with pytest.raises(RuntimeError, match="mapped"):
        await async_execute_schedule_operation(
            device,
            protocol_call,
            error_log="API error getting schedules: %s",
            error_translation_key="schedule_fetch_failed",
            logger=logger,
            raise_service_error=raise_service_error,
        )

    protocol_call.assert_awaited_once_with(device)
    logger.warning.assert_called_once_with("API error getting schedules: %s", api_error)
    raise_service_error.assert_called_once_with("schedule_fetch_failed", err=api_error)


@pytest.mark.asyncio
async def test_async_execute_schedule_operation_delegates_to_shared_executor() -> None:
    """Coordinator-backed schedule calls should delegate into the shared executor."""
    device = _make_schedule_device()
    coordinator = _ScheduleCoordinatorDouble()
    protocol_call = AsyncMock(return_value={"ok": True})
    logger = MagicMock()
    raise_service_error = MagicMock()

    async def _fake_execute(*_args, call, **_kwargs):
        return await call()

    with patch(
        "custom_components.lipro.services.schedule.async_execute_coordinator_call",
        AsyncMock(side_effect=_fake_execute),
    ) as shared_executor:
        result = await async_execute_schedule_operation(
            device,
            protocol_call,
            coordinator=coordinator,
            error_log="API error getting schedules: %s",
            error_translation_key="schedule_fetch_failed",
            logger=logger,
            raise_service_error=raise_service_error,
        )

    assert result == {"ok": True}
    shared_executor.assert_awaited_once()
    await_args = shared_executor.await_args
    if await_args is None:
        raise AssertionError("shared executor should capture await args")
    assert await_args.args == (coordinator,)
    assert callable(await_args.kwargs["call"])
    assert await_args.kwargs["raise_service_error"] is raise_service_error
    assert callable(await_args.kwargs["handle_api_error"])
    protocol_call.assert_awaited_once_with(device)


@pytest.mark.asyncio
async def test_async_execute_schedule_operation_with_real_auth_service_maps_auth_error(
    hass,
) -> None:
    """Coordinator auth flow should reauth first, then map schedule service errors."""
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    entry.async_start_reauth = MagicMock()
    coordinator = _ScheduleCoordinatorDouble(
        auth_service=CoordinatorAuthService(
            hass=hass,
            auth_manager=MagicMock(async_ensure_authenticated=AsyncMock()),
            config_entry=entry,
        )
    )
    device = _make_schedule_device()
    protocol_call = AsyncMock(side_effect=LiproAuthError("bad credentials"))
    logger = MagicMock()
    raise_service_error = MagicMock(side_effect=RuntimeError("mapped"))

    with pytest.raises(RuntimeError, match="mapped"):
        await async_execute_schedule_operation(
            device,
            protocol_call,
            coordinator=coordinator,
            error_log="API error getting schedules: %s",
            error_translation_key="schedule_fetch_failed",
            logger=logger,
            raise_service_error=raise_service_error,
        )

    entry.async_start_reauth.assert_called_once_with(hass)
    assert raise_service_error.call_args.args == ("auth_error",)
    assert "error" in raise_service_error.call_args.kwargs["translation_placeholders"]


@pytest.mark.asyncio
async def test_async_execute_schedule_operation_with_real_auth_service_maps_refresh_token_expired(
    hass,
) -> None:
    """Refresh-token expiry should reuse the shared executor translation path."""
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    entry.async_start_reauth = MagicMock()
    coordinator = _ScheduleCoordinatorDouble(
        auth_service=CoordinatorAuthService(
            hass=hass,
            auth_manager=MagicMock(async_ensure_authenticated=AsyncMock()),
            config_entry=entry,
        )
    )
    device = _make_schedule_device()
    protocol_call = AsyncMock(side_effect=LiproRefreshTokenExpiredError("expired"))
    logger = MagicMock()
    raise_service_error = MagicMock(side_effect=RuntimeError("mapped"))

    with pytest.raises(RuntimeError, match="mapped"):
        await async_execute_schedule_operation(
            device,
            protocol_call,
            coordinator=coordinator,
            error_log="API error getting schedules: %s",
            error_translation_key="schedule_fetch_failed",
            logger=logger,
            raise_service_error=raise_service_error,
        )

    entry.async_start_reauth.assert_called_once_with(hass)
    assert raise_service_error.call_args.args == ("auth_expired",)


def test_build_schedule_mesh_context_normalizes_member_ids_and_gateway() -> None:
    """Mesh context should canonicalize IDs before schedule calls."""
    device = _make_schedule_device(
        mesh_gateway_device_id=" 03AB0000000000A1 ",
        mesh_group_member_ids=["03ab0000000000a2", " 03AB0000000000A2 ", "bad"],
        ir_remote_gateway_device_id=None,
    )

    assert build_schedule_mesh_context(device) == (
        "03ab0000000000a1",
        ["03ab0000000000a2"],
    )


def test_build_schedule_mesh_context_falls_back_to_ir_remote_gateway_property() -> None:
    """IR remote devices should not require extra_data hand-filling."""
    device = _make_schedule_device(
        mesh_gateway_device_id=None,
        mesh_group_member_ids=[],
        ir_remote_gateway_device_id=" 03AB0000000000A9 ",
    )

    assert build_schedule_mesh_context(device) == ("03ab0000000000a9", [])


def test_build_schedule_mesh_context_preserves_blank_mesh_gateway_without_ir_override() -> None:
    """IR fallback should remain an explicit None-only branch."""
    device = _make_schedule_device(
        mesh_gateway_device_id="",
        mesh_group_member_ids=[],
        ir_remote_gateway_device_id=" 03AB0000000000A9 ",
    )

    assert build_schedule_mesh_context(device) == ("", [])
