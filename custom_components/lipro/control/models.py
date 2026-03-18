"""Control-plane data models."""

from __future__ import annotations

from dataclasses import dataclass

type FailureSummary = dict[str, str | None]


def empty_failure_summary() -> FailureSummary:
    """Return the stable empty failure-summary shape."""
    return {
        "failure_category": None,
        "failure_origin": None,
        "handling_policy": None,
        "error_type": None,
    }


@dataclass(frozen=True, slots=True)
class RuntimeCoordinatorSnapshot:
    """Read-model snapshot exposed from control plane to support surfaces."""

    entry_id: str
    entry_ref: str | None
    device_count: int
    last_update_success: bool
    mqtt_connected: bool | None
    failure_summary: FailureSummary
