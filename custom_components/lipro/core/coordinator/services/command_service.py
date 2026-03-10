"""Coordinator command service owning the public dispatch entrypoint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ...api import LiproApiError
from ...command.trace import build_command_trace
from ...utils.redaction import redact_identifier as _redact_identifier

if TYPE_CHECKING:
    from ...device import LiproDevice
    from ..coordinator import Coordinator


@dataclass(slots=True)
class CoordinatorCommandService:
    """Expose command dispatch through a composition-friendly service."""

    coordinator: Coordinator

    @property
    def last_failure(self) -> dict[str, Any] | None:
        """Return the latest command failure payload, if any."""
        # TODO: Implement command failure tracking
        return None

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
        fallback_device_id: str | None = None,
    ) -> bool:
        """Dispatch one command through the wrapped coordinator pipeline."""
        # TODO: Implement command dispatch via CommandRuntime
        return False
