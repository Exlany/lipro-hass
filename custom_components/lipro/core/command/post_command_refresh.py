"""Post-command refresh scheduling helpers for the coordinator."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, Protocol

from .command_result import resolve_delayed_refresh_delay, run_delayed_refresh


class TrackBackgroundTask(Protocol):
    """Protocol for coordinator background-task tracking."""

    def __call__(self, coro: Coroutine[Any, Any, Any]) -> asyncio.Task[Any]:
        """Track and return a scheduled background task."""


def on_post_command_refresh_task_done(
    *,
    post_command_refresh_tasks: dict[str, asyncio.Task[Any]],
    refresh_key: str,
    finished_task: asyncio.Task[Any],
) -> None:
    """Clear per-device delayed-refresh handle when task completes."""
    if post_command_refresh_tasks.get(refresh_key) is finished_task:
        post_command_refresh_tasks.pop(refresh_key, None)


def schedule_post_command_refresh(
    *,
    track_background_task: TrackBackgroundTask,
    request_refresh: Callable[[], Coroutine[Any, Any, Any]],
    post_command_refresh_tasks: dict[str, asyncio.Task[Any]],
    mqtt_connected: bool,
    device_serial: str | None,
    pending_expectations: dict[str, Any],
    get_adaptive_post_refresh_delay: Callable[[str | None], float],
    skip_immediate: bool = False,
) -> None:
    """Schedule immediate refresh and optional delayed refresh after a command."""
    if not skip_immediate:
        track_background_task(request_refresh())

    delay_seconds = resolve_delayed_refresh_delay(
        mqtt_connected=mqtt_connected,
        device_serial=device_serial,
        pending_expectations=pending_expectations,
        get_adaptive_post_refresh_delay=get_adaptive_post_refresh_delay,
    )
    if delay_seconds is None:
        return

    refresh_key = device_serial or ""
    previous_task = post_command_refresh_tasks.get(refresh_key)
    if previous_task and not previous_task.done():
        previous_task.cancel()

    delayed_task = track_background_task(
        run_delayed_refresh(
            delay_seconds=delay_seconds,
            request_refresh=request_refresh,
        )
    )
    post_command_refresh_tasks[refresh_key] = delayed_task

    def _on_done(finished_task: asyncio.Task[Any]) -> None:
        on_post_command_refresh_task_done(
            post_command_refresh_tasks=post_command_refresh_tasks,
            refresh_key=refresh_key,
            finished_task=finished_task,
        )

    delayed_task.add_done_callback(_on_done)
