"""Tests for OTA refresh background task callbacks."""

from __future__ import annotations

import asyncio
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro.entities.firmware_update import LiproFirmwareUpdateEntity
from custom_components.lipro.entities.firmware_update_support import (
    resolve_refresh_task_outcome,
)


@pytest.mark.asyncio
async def test_resolve_refresh_task_outcome_ignores_cancelled_error() -> None:
    async def _pending() -> None:
        await asyncio.sleep(1)

    task = asyncio.create_task(_pending())
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

    outcome = resolve_refresh_task_outcome(
        active_task=task,
        completed_task=task,
        logger=MagicMock(),
    )
    assert outcome.active_task is None
    assert outcome.error is None


@pytest.mark.asyncio
async def test_async_will_remove_from_hass_awaits_ota_refresh_cancel(
    mock_coordinator, make_device
) -> None:
    """Entity removal should await the cancelled OTA refresh task."""
    device = make_device("light", serial="03ab5ccd7c111111")
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)

    async def _pending() -> None:
        await asyncio.sleep(10)

    task = asyncio.create_task(_pending())
    entity._ota_refresh_task = cast(asyncio.Task[None] | None, task)

    with patch(
        "custom_components.lipro.entities.base.LiproEntity.async_will_remove_from_hass",
        new=AsyncMock(),
    ):
        await entity.async_will_remove_from_hass()

    assert entity._ota_refresh_task is None
    assert task.done()
    assert task.cancelled()


@pytest.mark.asyncio
async def test_handle_refresh_task_done_sets_last_error_and_calls_hook(
    mock_coordinator, make_device
) -> None:
    """Background OTA task failures should become observable via state and hook."""
    on_error = MagicMock()
    device = make_device("light", serial="03ab5ccd7c111111")
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device, on_error=on_error)
    patch.object(entity, "async_write_ha_state", new=MagicMock()).start()

    async def _boom() -> None:
        raise RuntimeError("ota boom")

    task = asyncio.create_task(_boom())
    await asyncio.gather(task, return_exceptions=True)
    entity._ota_refresh_task = cast(asyncio.Task[None] | None, task)

    entity._handle_refresh_task_done(task)

    assert entity._ota_refresh_task is None
    assert isinstance(entity.last_error, RuntimeError)
    assert entity.extra_state_attributes["last_error_type"] == "RuntimeError"
    on_error.assert_called_once()


@pytest.mark.asyncio
async def test_handle_refresh_task_done_ignores_error_hook_exception(
    mock_coordinator, make_device
) -> None:
    """Hook failures should be swallowed while preserving original task error."""
    on_error = MagicMock(side_effect=RuntimeError("hook boom"))
    device = make_device("light", serial="03ab5ccd7c222222")
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device, on_error=on_error)
    patch.object(entity, "async_write_ha_state", new=MagicMock()).start()

    async def _boom() -> None:
        raise ValueError("ota failed")

    task = asyncio.create_task(_boom())
    await asyncio.gather(task, return_exceptions=True)

    entity._handle_refresh_task_done(task)

    assert isinstance(entity.last_error, ValueError)
    on_error.assert_called_once()


@pytest.mark.asyncio
async def test_async_update_success_clears_last_error(
    mock_coordinator, make_device
) -> None:
    """Successful refresh should clear previous OTA error state."""
    device = make_device(
        "light",
        serial="03ab5ccd7c333333",
        properties={"version": "1.0.0"},
    )
    mock_coordinator.protocol = MagicMock()
    mock_coordinator.protocol.query_ota_info = AsyncMock(
        return_value=[
            {
                "deviceType": device.device_type_hex,
                "latestVersion": "1.1.0",
                "certified": True,
            }
        ]
    )
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    patch.object(entity, "async_write_ha_state", new=MagicMock()).start()
    entity._last_error = RuntimeError("stale error")

    await entity.async_update()

    assert entity.last_error is None
    assert "last_error" not in entity.extra_state_attributes
