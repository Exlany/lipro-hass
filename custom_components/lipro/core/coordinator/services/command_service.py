"""Coordinator command service - API stability layer.

This service provides a stable facade over the command runtime, implementing
the Stable Interface Pattern from Clean Architecture.

Design rationale:
- **API Stability**: Isolates Entity layer from Runtime implementation changes
- **Dependency Inversion**: Entity depends on Service interface, not Runtime
- **Single Responsibility**: Focused on command dispatch coordination

Architecture role:
- NOT a business logic layer (logic lives in CommandRuntime)
- NOT a Saga orchestrator (no cross-runtime transactions needed yet)
- IS a stable API boundary (protects Entity layer from Runtime refactoring)

This is intentional "thin proxy" design - the value is in API stability,
not in adding orchestration complexity.
"""

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
        return self.coordinator.command_runtime.last_command_failure  # type: ignore[no-any-return]

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
        fallback_device_id: str | None = None,
    ) -> bool:
        """Dispatch one command through the wrapped coordinator pipeline."""
        success, _route = await self.coordinator.command_runtime.send_device_command(
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
        )
        return success  # type: ignore[no-any-return]
