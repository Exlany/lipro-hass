"""Control-plane data models."""

from __future__ import annotations

from dataclasses import dataclass

from ..core.telemetry.models import FailureSummary, empty_failure_summary


@dataclass(frozen=True, slots=True)
class RuntimeCoordinatorSnapshot:
    """Read-model snapshot exposed from control plane to support surfaces."""

    entry_id: str
    entry_ref: str | None
    device_count: int
    last_update_success: bool
    mqtt_connected: bool | None
    failure_summary: FailureSummary


@dataclass(frozen=True, slots=True)
class RuntimeDiagnosticsProjection:
    """Typed diagnostics projection derived from one runtime snapshot."""

    snapshot: RuntimeCoordinatorSnapshot
    update_interval: str
    degraded_fields: tuple[str, ...] = ()


__all__ = [
    "FailureSummary",
    "RuntimeCoordinatorSnapshot",
    "RuntimeDiagnosticsProjection",
    "empty_failure_summary",
]
