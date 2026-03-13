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
    command_runtime = MagicMock()
    command_runtime.send_device_command = AsyncMock(return_value=(True, "device_direct"))
    tuning_runtime = MagicMock()
    service = CoordinatorCommandService(
        command_runtime=command_runtime,
        tuning_runtime=tuning_runtime,
    )
    device = MagicMock(serial="03ab5ccd7caaaaaa")

    result = await service.async_send_command(
        device,
        "POWER_ON",
        [{"key": "powerState", "value": "1"}],
    )

    assert result is True
    command_runtime.send_device_command.assert_awaited_once_with(
        device=device,
        command="POWER_ON",
        properties=[{"key": "powerState", "value": "1"}],
        fallback_device_id=None,
    )
    tuning_runtime.record_user_action.assert_called_once_with(
        device_serial=device.serial,
        command="POWER_ON",
    )


@pytest.mark.asyncio
async def test_command_service_skips_follow_up_side_effects_on_failure() -> None:
    command_runtime = MagicMock()
    command_runtime.send_device_command = AsyncMock(return_value=(False, "device_direct"))
    tuning_runtime = MagicMock()
    service = CoordinatorCommandService(
        command_runtime=command_runtime,
        tuning_runtime=tuning_runtime,
    )
    device = MagicMock(serial="03ab5ccd7caaaaaa")

    result = await service.async_send_command(
        device,
        "POWER_ON",
        [{"key": "powerState", "value": "1"}],
    )

    assert result is False
    tuning_runtime.record_user_action.assert_not_called()


@pytest.mark.asyncio
async def test_command_service_handles_api_error_via_runtime() -> None:
    command_runtime = MagicMock()
    command_runtime.send_device_command = AsyncMock(side_effect=LiproApiError("boom", code="500"))
    service = CoordinatorCommandService(
        command_runtime=command_runtime,
        tuning_runtime=MagicMock(),
    )
    device = MagicMock(serial="03ab5ccd7caaaaaa", name="Desk Light")

    with pytest.raises(LiproApiError):
        await service.async_send_command(device, "POWER_ON")

    command_runtime.send_device_command.assert_awaited_once()


@pytest.mark.asyncio
async def test_command_service_shutdown_is_idempotent() -> None:
    service = CoordinatorCommandService(
        command_runtime=MagicMock(),
        tuning_runtime=MagicMock(),
    )

    await service.async_shutdown()


def test_command_service_exposes_last_failure_trace() -> None:
    command_runtime = MagicMock()
    trace = MagicMock()
    command_runtime.last_command_failure = trace

    service = CoordinatorCommandService(
        command_runtime=command_runtime,
        tuning_runtime=MagicMock(),
    )

    assert service.last_failure is trace
