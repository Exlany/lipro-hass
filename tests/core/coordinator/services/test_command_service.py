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
    coordinator.command_runtime = MagicMock()
    coordinator.command_runtime.send_device_command = AsyncMock(
        return_value=(True, "device_direct")
    )
    coordinator.background_task_manager = MagicMock()
    coordinator.tuning_runtime = MagicMock()

    def _track(coro, **kwargs):
        coro.close()
        task = MagicMock()
        task.add_done_callback = MagicMock()
        task.done.return_value = True
        return task

    coordinator.background_task_manager.create = MagicMock(side_effect=_track)
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
    coordinator.command_runtime.send_device_command.assert_awaited_once_with(
        device=device,
        command="POWER_ON",
        properties=[{"key": "powerState", "value": "1"}],
        fallback_device_id=None,
    )
    coordinator.tuning_runtime.record_user_action.assert_called_once_with(
        device_serial=device.serial,
        command="POWER_ON",
    )
    coordinator.background_task_manager.create.assert_not_called()


@pytest.mark.asyncio
async def test_command_service_does_not_schedule_duplicate_confirmation_fallback() -> None:
    coordinator = MagicMock()
    coordinator.command_runtime = MagicMock()
    coordinator.command_runtime.send_device_command = AsyncMock(
        return_value=(True, "device_direct")
    )
    coordinator.background_task_manager = MagicMock()
    coordinator.background_task_manager.create = MagicMock()
    coordinator.tuning_runtime = MagicMock()
    coordinator.async_request_refresh = AsyncMock()
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
    coordinator.tuning_runtime.record_user_action.assert_called_once_with(
        device_serial=device.serial,
        command="POWER_ON",
    )
    coordinator.async_request_refresh.assert_not_awaited()
    coordinator.background_task_manager.create.assert_not_called()


@pytest.mark.asyncio
async def test_command_service_skips_follow_up_side_effects_on_failure() -> None:
    coordinator = MagicMock()
    coordinator.command_runtime = MagicMock()
    coordinator.command_runtime.send_device_command = AsyncMock(
        return_value=(False, "device_direct")
    )
    coordinator.background_task_manager = MagicMock()
    coordinator.tuning_runtime = MagicMock()
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

    assert result is False
    coordinator.tuning_runtime.record_user_action.assert_not_called()
    coordinator.background_task_manager.create.assert_not_called()


@pytest.mark.asyncio
async def test_command_service_handles_api_error_via_coordinator_bridge() -> None:
    coordinator = MagicMock()
    coordinator.command_runtime = MagicMock()
    coordinator.command_runtime.send_device_command = AsyncMock(
        side_effect=LiproApiError("boom", code="500")
    )
    service = CoordinatorCommandService(coordinator)
    device = MagicMock(
        serial="03ab5ccd7caaaaaa",
        name="Desk Light",
        is_group=False,
        iot_name="lipro_led",
        device_type=1,
        physical_model="light",
    )

    with pytest.raises(LiproApiError):
        await service.async_send_command(device, "POWER_ON")

    coordinator.command_runtime.send_device_command.assert_awaited_once()


@pytest.mark.asyncio
async def test_command_service_shutdown_is_idempotent() -> None:
    coordinator = MagicMock()
    service = CoordinatorCommandService(coordinator)

    await service.async_shutdown()


def test_command_service_exposes_last_failure_trace() -> None:
    coordinator = MagicMock()
    trace = MagicMock()
    coordinator.command_runtime.last_command_failure = trace

    service = CoordinatorCommandService(coordinator)

    assert service.last_failure is trace
