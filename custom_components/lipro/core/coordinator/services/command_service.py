"""Coordinator command service owning the public dispatch entrypoint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ...api import LiproApiError
from ...command.trace import build_command_trace
from ...utils.redaction import redact_identifier as _redact_identifier

if TYPE_CHECKING:
    from ...device import LiproDevice
    from ..command_send import CoordinatorCommandRuntime


@dataclass(slots=True)
class CoordinatorCommandService:
    """Expose command dispatch through a composition-friendly service."""

    coordinator: CoordinatorCommandRuntime

    @property
    def last_failure(self) -> dict[str, Any] | None:
        """Return the latest command failure payload, if any."""
        return self.coordinator.last_command_failure

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
        fallback_device_id: str | None = None,
    ) -> bool:
        """Dispatch one command through the wrapped coordinator pipeline."""
        trace = build_command_trace(
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
            redact_identifier=_redact_identifier,
        )
        route = "device_direct"

        try:
            await self.coordinator.async_ensure_authenticated()
            success, route = await self.coordinator.async_execute_command_flow(
                device=device,
                command=command,
                properties=properties,
                fallback_device_id=fallback_device_id,
                trace=trace,
            )
            return success
        except LiproApiError as err:
            return await self.coordinator.async_handle_command_api_error(
                device=device,
                trace=trace,
                route=route,
                err=err,
            )
