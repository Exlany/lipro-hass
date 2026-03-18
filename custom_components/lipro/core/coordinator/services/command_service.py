"""Coordinator command service - stable write-side runtime surface."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

from ..types import CommandTrace

if TYPE_CHECKING:
    from ...device import LiproDevice
    from ..runtime.command_runtime import CommandRuntime
    from ..runtime.tuning_runtime import TuningRuntime

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class CoordinatorCommandService:
    """Expose command dispatch through a stable coordinator-owned service."""

    command_runtime: CommandRuntime
    tuning_runtime: TuningRuntime

    @property
    def last_failure(self) -> CommandTrace | None:
        """Return the latest command failure payload, if any."""
        return self.command_runtime.last_command_failure

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
        fallback_device_id: str | None = None,
    ) -> bool:
        """Dispatch command and record post-send tuning signals on success."""
        success, _route = await self.command_runtime.send_device_command(
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
        )

        if success and properties:
            try:
                self.tuning_runtime.record_user_action(
                    device_serial=device.serial,
                    command=command,
                )
            except (RuntimeError, TypeError, ValueError) as err:
                _LOGGER.debug(
                    "Failed to record user action for %s (%s)",
                    device.serial,
                    type(err).__name__,
                )

        return success

    async def async_shutdown(self) -> None:
        """Release service-owned resources.

        Refresh fallback tasks are owned by runtime/background-task collaborators,
        so this surface intentionally remains lightweight.
        """
