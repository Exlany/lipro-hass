"""Coordinator command service - Saga-lite orchestrator (Phase H4).

This service orchestrates cross-runtime transactions for command dispatch,
implementing the Saga-lite pattern from the refactor completion plan.

Architecture role:
- **Cross-Runtime Orchestration**: Coordinates CommandRuntime + TuningRuntime
- **Confirmation Fallback**: Schedules force-refresh if MQTT confirmation times out
- **API Stability**: Maintains stable interface for Entity layer

Transaction flow (e.g. "user adjusts color temperature"):
1. CommandRuntime dispatches the command to device
2. TuningRuntime records user action for learning curves (non-blocking)
3. Confirmation fallback schedules force-refresh after timeout

Design constraint: Linear ``do A → do B → schedule C``, no rollback semantics.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..types import CommandTrace

if TYPE_CHECKING:
    from ...device import LiproDevice
    from ..coordinator import Coordinator

_LOGGER = logging.getLogger(__name__)

_CONFIRMATION_TIMEOUT_SECONDS = 5.0


@dataclass(slots=True)
class CoordinatorCommandService:
    """Saga-lite orchestrator for command dispatch.

    Coordinates CommandRuntime + TuningRuntime + DeviceRefreshService
    for each command, with timeout-based confirmation fallback.
    """

    coordinator: Coordinator
    _pending_confirmations: dict[str, asyncio.Task[Any]] = field(
        default_factory=dict, init=False, repr=False
    )

    @property
    def last_failure(self) -> CommandTrace | None:
        """Return the latest command failure payload, if any."""
        return self.coordinator.command_runtime.last_command_failure  # type: ignore[no-any-return]

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
        fallback_device_id: str | None = None,
    ) -> bool:
        """Dispatch command with cross-runtime orchestration.

        Saga-lite flow:
        1. Send command via CommandRuntime
        2. Record user action in TuningRuntime (non-blocking)
        3. Schedule confirmation fallback (timeout → force refresh)
        """
        # Step 1: Dispatch command
        success, _route = await self.coordinator.command_runtime.send_device_command(
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
        )

        if success:
            # Step 2: Record user action for learning curves (non-blocking)
            if properties:
                try:
                    self.coordinator._runtimes.tuning.record_user_action(
                        device_serial=device.serial,
                        command=command,
                    )
                except Exception:  # noqa: BLE001
                    _LOGGER.debug(
                        "Failed to record user action for %s", device.serial
                    )

            # Step 3: Schedule confirmation fallback
            self._schedule_confirmation_fallback(device)

        return success  # type: ignore[no-any-return]

    def _schedule_confirmation_fallback(self, device: LiproDevice) -> None:
        """Schedule a force-refresh if MQTT confirmation doesn't arrive in time.

        If MQTT is connected, the device state should update via push within
        the timeout window. If not, this fallback triggers a REST poll to
        ensure state consistency.
        """
        serial = device.serial

        # Cancel any existing pending confirmation for this device
        existing = self._pending_confirmations.pop(serial, None)
        if existing is not None and not existing.done():
            existing.cancel()

        task = asyncio.create_task(
            self._async_confirmation_fallback(serial),
            name=f"lipro_confirm_{serial}",
        )
        self._pending_confirmations[serial] = task
        task.add_done_callback(lambda t: self._pending_confirmations.pop(serial, None))

    async def _async_confirmation_fallback(self, device_serial: str) -> None:
        """Wait for confirmation timeout, then force refresh if needed."""
        try:
            await asyncio.sleep(_CONFIRMATION_TIMEOUT_SECONDS)
            _LOGGER.debug(
                "Confirmation timeout for %s, triggering force refresh",
                device_serial,
            )
            await self.coordinator.async_request_refresh()
        except asyncio.CancelledError:
            pass
