"""Tests for the coordinator command service entrypoint."""

from __future__ import annotations

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api import LiproApiError
from custom_components.lipro.core.coordinator.services.command_service import (
    CoordinatorCommandService,
)
from custom_components.lipro.core.utils.background_task_manager import (
    BackgroundTaskManager,
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
    coordinator.background_task_manager.create.assert_called_once()


@pytest.mark.asyncio
async def test_command_service_triggers_refresh_after_confirmation_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    coordinator = MagicMock()
    coordinator.command_runtime = MagicMock()
    coordinator.command_runtime.send_device_command = AsyncMock(
        return_value=(True, "device_direct")
    )
    coordinator.background_task_manager = BackgroundTaskManager(
        asyncio.create_task,
        logging.getLogger(__name__),
    )
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

    original_sleep = asyncio.sleep

    async def _fast_sleep(_delay: float) -> None:
        await original_sleep(0)

    monkeypatch.setattr(
        "custom_components.lipro.core.coordinator.services.command_service.asyncio.sleep",
        _fast_sleep,
    )

    result = await service.async_send_command(
        device,
        "POWER_ON",
        [{"key": "powerState", "value": "1"}],
    )

    await asyncio.gather(
        *tuple(coordinator.background_task_manager.tasks),
        return_exceptions=True,
    )

    assert result is True
    coordinator.tuning_runtime.record_user_action.assert_called_once_with(
        device_serial=device.serial,
        command="POWER_ON",
    )
    coordinator.async_request_refresh.assert_awaited_once()
    assert service._pending_confirmations == {}
    assert not coordinator.background_task_manager.tasks


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
async def test_command_service_shutdown_cancels_pending_confirmations() -> None:
    coordinator = MagicMock()
    coordinator.background_task_manager = BackgroundTaskManager(
        asyncio.create_task,
        logging.getLogger(__name__),
    )
    service = CoordinatorCommandService(coordinator)
    device = MagicMock(serial="03ab5ccd7caaaaaa")

    service._schedule_confirmation_fallback(device)
    pending_task = service._pending_confirmations[device.serial]

    await service.async_shutdown()

    assert pending_task.cancelled()
    assert service._pending_confirmations == {}


def test_command_service_exposes_last_failure_trace() -> None:
    coordinator = MagicMock()
    trace = MagicMock()
    coordinator.command_runtime.last_command_failure = trace

    service = CoordinatorCommandService(coordinator)

    assert service.last_failure is trace
