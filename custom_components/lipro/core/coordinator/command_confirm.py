"""Command confirmation and post-refresh scheduling for the coordinator.

This module contains the command-confirmation side of the coordinator command
pipeline. It is kept separate from command sending to make responsibilities
clear and keep runtime helpers smaller.
"""

from __future__ import annotations

import logging
from typing import Any, Final

from ..command.post_refresh import schedule_post_command_refresh
from ..command.result import run_delayed_refresh
from .base import _CoordinatorBase

_LOGGER = logging.getLogger(__name__)

# API status may lag after command push; schedule one delayed refresh fallback.
_POST_COMMAND_REFRESH_DELAY_SECONDS: Final[float] = 3.0

# Adaptive post-command reconciliation tuning.
_MIN_POST_COMMAND_REFRESH_DELAY_SECONDS: Final[float] = 1.5
_MAX_POST_COMMAND_REFRESH_DELAY_SECONDS: Final[float] = 8.0
_STATE_LATENCY_MARGIN_SECONDS: Final[float] = 0.6
_STATE_LATENCY_EWMA_ALPHA: Final[float] = 0.35
_STATE_CONFIRM_TIMEOUT_SECONDS: Final[float] = 20.0


class CoordinatorCommandConfirmationRuntime(_CoordinatorBase):
    """Command confirmation and post-refresh scheduling runtime methods."""

    def _filter_pending_command_mismatches(
        self,
        device_serial: str,
        properties: dict[str, Any],
    ) -> dict[str, Any]:
        """Filter stale values while waiting for command confirmation.

        If we recently sent CHANGE_STATE to a device, transient polls may still
        return old values. Keep optimistic keys stable by dropping mismatched
        values for pending keys until confirmed or timeout.
        """
        filtered, blocked_keys = (
            self._command_confirmation_tracker.filter_pending_command_mismatches(
                pending_expectations=self._pending_command_expectations,
                device_serial=device_serial,
                properties=properties,
            )
        )
        if not blocked_keys:
            return filtered

        _LOGGER.debug(
            "Skipping stale keys for device %s while command pending: %s",
            device_serial[:8] + "...",
            blocked_keys,
        )
        return filtered

    def _track_command_expectation(
        self,
        device_serial: str,
        command: str,
        properties: list[dict[str, str]] | None,
    ) -> None:
        """Track expected CHANGE_STATE values for adaptive confirmation."""
        self._command_confirmation_tracker.track_command_expectation(
            pending_expectations=self._pending_command_expectations,
            device_serial=device_serial,
            command=command,
            properties=properties,
        )

    def _update_state_latency(
        self,
        device_serial: str,
        observed_latency: float,
    ) -> None:
        """Update per-device command->state latency EWMA."""
        self._command_confirmation_tracker.update_state_latency(
            device_state_latency_seconds=self._device_state_latency_seconds,
            device_serial=device_serial,
            observed_latency=observed_latency,
        )

    def _observe_command_confirmation(
        self,
        device_serial: str,
        properties: dict[str, Any],
    ) -> None:
        """Observe property updates and confirm pending command expectations."""
        latency = self._command_confirmation_tracker.observe_command_confirmation(
            pending_expectations=self._pending_command_expectations,
            device_state_latency_seconds=self._device_state_latency_seconds,
            device_serial=device_serial,
            properties=properties,
        )
        if latency is None:
            return

        _LOGGER.debug(
            "Device %s: confirmed command state in %.2fs (adaptive delay=%.2fs)",
            device_serial[:8] + "...",
            latency,
            self._get_adaptive_post_refresh_delay(device_serial),
        )

    def _get_adaptive_post_refresh_delay(self, device_serial: str | None) -> float:
        """Get adaptive delayed-refresh value for a device."""
        return self._command_confirmation_tracker.get_adaptive_post_refresh_delay(
            device_state_latency_seconds=self._device_state_latency_seconds,
            device_serial=device_serial,
        )

    def _prune_runtime_state_for_devices(self, active_serials: set[str]) -> None:
        """Prune per-device runtime caches for removed devices."""
        self._command_confirmation_tracker.prune_runtime_state_for_devices(
            pending_expectations=self._pending_command_expectations,
            device_state_latency_seconds=self._device_state_latency_seconds,
            active_serials=active_serials,
        )

        active_normalized = {
            self._normalize_device_key(serial)
            for serial in active_serials
            if isinstance(serial, str) and serial.strip()
        }
        stale_mqtt_connect = set(self._last_mqtt_connect_state_at) - active_normalized
        for serial in stale_mqtt_connect:
            self._last_mqtt_connect_state_at.pop(serial, None)

        stale_connect_priority = (
            set(self._connect_status_priority_ids) - active_normalized
        )
        for serial in stale_connect_priority:
            self._connect_status_priority_ids.discard(serial)

    def _schedule_post_command_refresh(
        self,
        *,
        skip_immediate: bool = False,
        device_serial: str | None = None,
    ) -> None:
        """Schedule immediate refresh and optional delayed refresh after a command."""
        schedule_post_command_refresh(
            track_background_task=self._track_background_task,
            request_refresh=self.async_request_refresh,
            post_command_refresh_tasks=self._post_command_refresh_tasks,
            mqtt_connected=self._mqtt_connected,
            device_serial=device_serial,
            pending_expectations=self._pending_command_expectations,
            get_adaptive_post_refresh_delay=self._get_adaptive_post_refresh_delay,
            skip_immediate=skip_immediate,
        )

    async def _async_delayed_command_refresh(self, delay_seconds: float) -> None:
        """Run one delayed refresh after command to absorb API status lag."""
        await run_delayed_refresh(
            delay_seconds=delay_seconds,
            request_refresh=self.async_request_refresh,
        )


__all__ = [
    "_MAX_POST_COMMAND_REFRESH_DELAY_SECONDS",
    "_MIN_POST_COMMAND_REFRESH_DELAY_SECONDS",
    "_POST_COMMAND_REFRESH_DELAY_SECONDS",
    "_STATE_CONFIRM_TIMEOUT_SECONDS",
    "_STATE_LATENCY_EWMA_ALPHA",
    "_STATE_LATENCY_MARGIN_SECONDS",
    "CoordinatorCommandConfirmationRuntime",
]
