"""Background task tracking utilities for coordinator workflows."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
import logging
from typing import Any


class BackgroundTaskManager:
    """Track and safely finalize coordinator-owned background tasks."""

    def __init__(
        self,
        create_task: Callable[[Coroutine[Any, Any, Any]], asyncio.Task[Any]],
        logger: logging.Logger,
    ) -> None:
        """Initialize manager with task factory and logger."""
        self._create_task = create_task
        self._logger = logger
        self._tasks: set[asyncio.Task[Any]] = set()

    @property
    def tasks(self) -> set[asyncio.Task[Any]]:
        """Expose tracked tasks for coordinator compatibility."""
        return self._tasks

    def create(
        self,
        coro: Coroutine[Any, Any, Any],
        *,
        create_task: (
            Callable[[Coroutine[Any, Any, Any]], asyncio.Task[Any]] | None
        ) = None,
    ) -> asyncio.Task[Any]:
        """Create and track a background task."""
        task_factory = create_task or self._create_task
        task = task_factory(coro)
        self._tasks.add(task)
        add_done_callback = getattr(task, "add_done_callback", None)
        if callable(add_done_callback):
            add_done_callback(self.on_done)
        return task

    def on_done(self, task: asyncio.Task[Any]) -> None:
        """Finalize tracked task and consume terminal exceptions."""
        self._tasks.discard(task)
        try:
            task.result()
        except asyncio.CancelledError:
            return
        except Exception as err:  # noqa: BLE001
            self._logger.debug(
                "Background task failed (%s)",
                type(err).__name__,
            )

    async def cancel_all(self) -> None:
        """Cancel and await all tracked tasks."""
        if not self._tasks:
            return

        tasks_to_cancel = [task for task in self._tasks if not task.done()]
        for task in tasks_to_cancel:
            task.cancel()

        if tasks_to_cancel:
            await asyncio.gather(*tasks_to_cancel, return_exceptions=True)

        self._tasks.clear()
