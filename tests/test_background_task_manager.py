"""Tests for coordinator background task manager helper."""

from __future__ import annotations

import asyncio
import logging

import pytest

from custom_components.lipro.core.utils.background_task_manager import (
    BackgroundTaskManager,
)


@pytest.mark.asyncio
async def test_create_tracks_and_removes_completed_task() -> None:
    manager = BackgroundTaskManager(asyncio.create_task, logging.getLogger(__name__))

    async def _work() -> None:
        await asyncio.sleep(0)

    task = manager.create(_work())
    assert task in manager.tasks

    await task
    assert task not in manager.tasks


@pytest.mark.asyncio
async def test_create_consumes_task_exception(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("tests.background_task_manager")
    manager = BackgroundTaskManager(asyncio.create_task, logger)

    async def _raise_later() -> None:
        await asyncio.sleep(0)
        raise RuntimeError("boom")

    with caplog.at_level(logging.DEBUG, logger=logger.name):
        task = manager.create(_raise_later())
        await asyncio.sleep(0.05)

    assert task.done()
    assert task not in manager.tasks
    assert "Background task failed (RuntimeError)" in caplog.text


@pytest.mark.asyncio
async def test_cancel_all_cancels_pending_tasks() -> None:
    manager = BackgroundTaskManager(asyncio.create_task, logging.getLogger(__name__))

    async def _sleep_forever() -> None:
        await asyncio.sleep(3600)

    task = manager.create(_sleep_forever())
    assert task in manager.tasks

    await manager.cancel_all()

    assert task.cancelled()
    assert not manager.tasks


def test_create_without_done_callback_support() -> None:
    class _TaskWithoutDoneCallback:
        def done(self) -> bool:
            return True

        def cancel(self) -> None:
            return None

        def result(self) -> None:
            return None

    def _create_task(coro):
        coro.close()
        return _TaskWithoutDoneCallback()

    manager = BackgroundTaskManager(_create_task, logging.getLogger(__name__))
    task = manager.create(asyncio.sleep(0))

    assert task in manager.tasks
