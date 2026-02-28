"""Tests for OTA refresh background task callbacks."""

from __future__ import annotations

import asyncio

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
