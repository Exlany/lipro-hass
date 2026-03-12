"""Protocol-owned diagnostics context, distinct from HA diagnostics surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .session import ProtocolSessionState
from .telemetry import ProtocolTelemetry


@dataclass(slots=True)
class ProtocolDiagnosticsContext:
    """Shared protocol diagnostics context for runtime/control consumers."""

    session_state: ProtocolSessionState
    telemetry: ProtocolTelemetry
    entry_id: str | None = None

    def snapshot(
        self,
        *,
        mqtt_connected: bool | None = None,
        subscribed_count: int | None = None,
    ) -> dict[str, Any]:
        """Return a stable protocol-owned diagnostics snapshot."""
        return {
            "entry_id": self.entry_id,
            "session": self.session_state.as_dict(),
            "telemetry": self.telemetry.snapshot(
                mqtt_connected=mqtt_connected,
                subscribed_count=subscribed_count,
            ),
        }


__all__ = ["ProtocolDiagnosticsContext"]
