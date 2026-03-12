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

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

from ..types import CommandTrace

if TYPE_CHECKING:
    from ...device import LiproDevice
    from ..coordinator import Coordinator

_LOGGER = logging.getLogger(__name__)

_CONFIRMATION_TIMEOUT_SECONDS = 5.0


@dataclass(slots=True)
class CoordinatorCommandService:
    """Saga-lite orchestrator for command dispatch.

    Coordinates CommandRuntime + TuningRuntime while delegating refresh timing
    to the command runtime's confirmation manager.
    """

    coordinator: Coordinator

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
        3. Let CommandRuntime own post-command refresh/confirmation policy
        """
        success, _route = await self.coordinator.command_runtime.send_device_command(
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
        )

        if success:
            if properties:
                try:
                    self.coordinator.tuning_runtime.record_user_action(
                        device_serial=device.serial,
                        command=command,
                    )
                except Exception:  # noqa: BLE001
                    _LOGGER.debug(
                        "Failed to record user action for %s", device.serial
                    )


        return success  # type: ignore[no-any-return]

    async def async_shutdown(self) -> None:
        """Release service-owned resources.

        Post-command refresh tasks are owned by the coordinator background task
        manager and command confirmation manager, so this service remains
        intentionally lightweight.
        """
