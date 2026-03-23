"""Typed read-model ports used by the control-plane runtime access surface."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from ..runtime_types import LiproCoordinator, ProtocolTelemetryFacadeLike

if TYPE_CHECKING:
    from ..core.device import LiproDevice


class RuntimeEntryPort(Protocol):
    """Minimal config-entry surface consumed by control runtime access."""

    entry_id: str
    runtime_data: LiproCoordinator | None
    options: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class RuntimeCoordinatorView:
    """Typed read-model of the runtime-facing coordinator facts."""

    coordinator: LiproCoordinator
    update_interval: str | None
    last_update_success: bool
    mqtt_connected: bool | None
    protocol: ProtocolTelemetryFacadeLike | None
    runtime_telemetry_snapshot: Mapping[str, object]
    devices: Mapping[str, LiproDevice] | None


@dataclass(frozen=True, slots=True)
class RuntimeEntryView:
    """Typed read-model of one live config entry plus its runtime coordinator."""

    entry: RuntimeEntryPort
    entry_id: str
    options: Mapping[str, object]
    coordinator: RuntimeCoordinatorView | None
