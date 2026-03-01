"""Tests for OTA refresh background task callbacks."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.lipro.update import LiproFirmwareUpdateEntity


@pytest.mark.asyncio
async def test_async_clear_refresh_task_ignores_cancelled_error() -> None:
    async def _pending() -> None:
        await asyncio.sleep(1)

    task = asyncio.create_task(_pending())
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

    LiproFirmwareUpdateEntity._async_clear_refresh_task(task)


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
    entity._ota_refresh_task = task

    with patch(
        "custom_components.lipro.update.LiproEntity.async_will_remove_from_hass",
        new=AsyncMock(),
    ):
        await entity.async_will_remove_from_hass()

    assert entity._ota_refresh_task is None
    assert task.done()
    assert task.cancelled()
