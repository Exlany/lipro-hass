"""Tests for the coordinator command service entrypoint."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api import LiproApiError
from custom_components.lipro.core.coordinator.services.command_service import (
    CoordinatorCommandService,
)


@pytest.mark.asyncio
async def test_command_service_runs_command_flow() -> None:
    coordinator = MagicMock()
    coordinator.async_ensure_authenticated = AsyncMock()
    coordinator.async_execute_command_flow = AsyncMock(return_value=(True, "device_direct"))
    coordinator.async_handle_command_api_error = AsyncMock()
    coordinator.last_command_failure = {"reason": "none"}
    service = CoordinatorCommandService(coordinator)
    device = MagicMock(
        serial="03ab5ccd7caaaaaa",
        is_group=False,
        iot_name="lipro_led",
        device_type=1,
        physical_model="light",
    )

    result = await service.async_send_command(
        device,
        "POWER_ON",
        [{"key": "powerState", "value": "1"}],
    )

    assert result is True
    coordinator.async_ensure_authenticated.assert_awaited_once_with()
    coordinator.async_execute_command_flow.assert_awaited_once()
    kwargs = coordinator.async_execute_command_flow.await_args.kwargs
    assert kwargs["device"] is device
    assert kwargs["command"] == "POWER_ON"
    assert kwargs["properties"] == [{"key": "powerState", "value": "1"}]
    assert kwargs["fallback_device_id"] is None
    assert kwargs["trace"]["requested_command"] == "POWER_ON"
    assert service.last_failure == {"reason": "none"}
    coordinator.async_handle_command_api_error.assert_not_awaited()


@pytest.mark.asyncio
async def test_command_service_handles_api_error_via_coordinator_bridge() -> None:
    coordinator = MagicMock()
    coordinator.async_ensure_authenticated = AsyncMock(
        side_effect=LiproApiError("boom", code="500")
    )
    coordinator.async_execute_command_flow = AsyncMock()
    coordinator.async_handle_command_api_error = AsyncMock(return_value=False)
    coordinator.last_command_failure = None
    service = CoordinatorCommandService(coordinator)
    device = MagicMock(
        serial="03ab5ccd7caaaaaa",
        name="Desk Light",
        is_group=False,
        iot_name="lipro_led",
        device_type=1,
        physical_model="light",
    )

    result = await service.async_send_command(device, "POWER_ON")

    assert result is False
    coordinator.async_execute_command_flow.assert_not_awaited()
    coordinator.async_handle_command_api_error.assert_awaited_once()
    kwargs = coordinator.async_handle_command_api_error.await_args.kwargs
    assert kwargs["device"] is device
    assert kwargs["route"] == "device_direct"
    assert isinstance(kwargs["err"], LiproApiError)
    assert kwargs["trace"]["device_id"] is not None
