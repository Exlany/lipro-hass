"""Confirmation manager for command state tracking and adaptive refresh."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any

from ....command.post_refresh import TrackBackgroundTask, schedule_post_command_refresh
from ....command.result import run_delayed_refresh

if TYPE_CHECKING:
    from ....command.confirmation_tracker import CommandConfirmationTracker
    from ....command.expectation import PendingCommandExpectation


class ConfirmationManager:
    """Manage command confirmation tracking and post-refresh scheduling."""

    def __init__(
        self,
        *,
        confirmation_tracker: CommandConfirmationTracker,
        pending_expectations: dict[str, PendingCommandExpectation],
        device_state_latency_seconds: dict[str, float],
        post_command_refresh_tasks: dict[str, asyncio.Task[Any]],
        track_background_task: TrackBackgroundTask,
        request_refresh: Callable[[], Coroutine[Any, Any, Any]],
        mqtt_connected_provider: Callable[[], bool],
    ) -> None:
        """Initialize confirmation manager."""
        self._confirmation_tracker = confirmation_tracker
        self._pending_expectations = pending_expectations
        self._device_state_latency_seconds = device_state_latency_seconds
        self._post_command_refresh_tasks = post_command_refresh_tasks
        self._track_background_task = track_background_task
        self._request_refresh = request_refresh
        self._mqtt_connected_provider = mqtt_connected_provider

    def track_command_expectation(
        self,
        *,
        device_serial: str,
        command: str,
        properties: list[dict[str, str]] | None,
    ) -> None:
        """Track expected command state for confirmation."""
        self._confirmation_tracker.track_command_expectation(
            pending_expectations=self._pending_expectations,
            device_serial=device_serial,
            command=command,
            properties=properties,
        )

    def get_adaptive_post_refresh_delay(self, device_serial: str | None) -> float:
        """Get adaptive delayed-refresh value for a device."""
        return self._confirmation_tracker.get_adaptive_post_refresh_delay(
            device_state_latency_seconds=self._device_state_latency_seconds,
            device_serial=device_serial,
        )

    def schedule_post_command_refresh(
        self,
        *,
        skip_immediate: bool = False,
        device_serial: str | None = None,
    ) -> None:
        """Schedule immediate and delayed refresh after command."""
        schedule_post_command_refresh(
            track_background_task=self._track_background_task,
            request_refresh=self._request_refresh,
            post_command_refresh_tasks=self._post_command_refresh_tasks,
            mqtt_connected=self._mqtt_connected_provider(),
            device_serial=device_serial,
            pending_expectations=self._pending_expectations,
            get_adaptive_post_refresh_delay=self.get_adaptive_post_refresh_delay,
            skip_immediate=skip_immediate,
        )

    async def run_delayed_refresh(self, delay_seconds: float) -> None:
        """Run delayed refresh after specified delay."""
        await run_delayed_refresh(
            delay_seconds=delay_seconds,
            request_refresh=self._request_refresh,
        )


__all__ = ["ConfirmationManager"]
