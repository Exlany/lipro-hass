"""Coordinator data containers and utilities.

This module provides:
- CoordinatorStateContainers: Mutable state containers owned by the coordinator
- CoordinatorRuntimes: Immutable registry of runtime components
- normalize_device_key: Device ID normalization utility

Runtime assembly is handled by RuntimeOrchestrator (orchestrator.py).
MQTT transport binding is handled by mqtt_lifecycle.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..command.confirmation_tracker import CommandConfirmationTracker
from ..device.identity_index import DeviceIdentityIndex
from ..utils.background_task_manager import BackgroundTaskManager
from .runtime.command_runtime import CommandRuntime
from .runtime.device_runtime import DeviceRuntime
from .runtime.mqtt_runtime import MqttRuntime
from .runtime.state_runtime import StateRuntime
from .runtime.status_runtime import StatusRuntime
from .runtime.tuning_runtime import TuningRuntime

if TYPE_CHECKING:
    from ..device import LiproDevice
    from .entity_protocol import LiproEntityProtocol
    from .lifecycle import CoordinatorUpdateCycle
    from .runtime_wiring import CoordinatorServiceLayer


def normalize_device_key(device_id: str) -> str:
    """Normalize device identifier for indexing."""
    return device_id.lower().strip()


@dataclass(slots=True)
class CoordinatorStateContainers:
    """Mutable state containers owned by the coordinator."""

    devices: dict[str, LiproDevice]
    entities: dict[str, LiproEntityProtocol]
    entities_by_device: dict[str, list[LiproEntityProtocol]]
    device_identity_index: DeviceIdentityIndex
    background_task_manager: BackgroundTaskManager
    confirmation_tracker: CommandConfirmationTracker


@dataclass(frozen=True, slots=True)
class CoordinatorRuntimes:
    """Immutable runtime component registry owned by the coordinator."""

    tuning: TuningRuntime
    state: StateRuntime
    device: DeviceRuntime
    status: StatusRuntime
    mqtt: MqttRuntime
    command: CommandRuntime


@dataclass(frozen=True, slots=True)
class CoordinatorBootstrapArtifact:
    """Named bootstrap contract returned to the coordinator runtime root."""

    state: CoordinatorStateContainers
    runtimes: CoordinatorRuntimes
    service_layer: CoordinatorServiceLayer
    update_cycle: CoordinatorUpdateCycle
