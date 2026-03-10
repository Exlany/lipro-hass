"""Coordinator command service owning the public dispatch entrypoint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..types import CommandTrace

if TYPE_CHECKING:
    from ...device import LiproDevice
    from ..coordinator import Coordinator


@dataclass(slots=True)
class CoordinatorCommandService:
    """Expose command dispatch through a composition-friendly service."""

    coordinator: Coordinator

    @property
    def last_failure(self) -> CommandTrace | None:
        """Return the latest command failure payload, if any."""
        return self.coordinator._command_runtime.last_command_failure

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
        fallback_device_id: str | None = None,
    ) -> bool:
        """Dispatch one command through the wrapped coordinator pipeline."""
        success, _route = await self.coordinator._command_runtime.send_device_command(
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
        )
        return success
