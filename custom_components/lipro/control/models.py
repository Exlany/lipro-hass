"""Control-plane data models."""

from __future__ import annotations

from dataclasses import dataclass

from ..runtime_types import LiproCoordinator


@dataclass(frozen=True, slots=True)
class RuntimeCoordinatorSnapshot:
    """Read-model snapshot exposed from control plane to support surfaces."""

    entry_id: str
    coordinator: LiproCoordinator
    device_count: int
    last_update_success: bool
    mqtt_connected: bool | None
