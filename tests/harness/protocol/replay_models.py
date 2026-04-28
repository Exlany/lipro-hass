"""Typed models for protocol replay manifests and deterministic execution."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from custom_components.lipro.core.telemetry.models import (
    FailureSummary,
    empty_failure_summary,
)

ReplayChannel = Literal["rest", "mqtt"]
REPLAY_CHANNEL_VALUES: Mapping[str, ReplayChannel] = {
    "rest": "rest",
    "mqtt": "mqtt",
}

ReplayOperation = Literal[
    "protocol.contracts.normalize_mqtt_config",
    "protocol.contracts.normalize_list_envelope",
    "protocol.contracts.normalize_device_list_page",
    "protocol.contracts.normalize_device_status_rows",
    "protocol.contracts.normalize_mesh_group_status_rows",
    "protocol.contracts.normalize_schedule_json",
    "protocol.boundary.decode_mqtt_topic",
    "protocol.boundary.decode_mqtt_message_envelope",
    "protocol.boundary.decode_mqtt_properties",
]
REPLAY_OPERATION_VALUES: Mapping[str, ReplayOperation] = {
    "protocol.contracts.normalize_mqtt_config": "protocol.contracts.normalize_mqtt_config",
    "protocol.contracts.normalize_list_envelope": "protocol.contracts.normalize_list_envelope",
    "protocol.contracts.normalize_device_list_page": "protocol.contracts.normalize_device_list_page",
    "protocol.contracts.normalize_device_status_rows": "protocol.contracts.normalize_device_status_rows",
    "protocol.contracts.normalize_mesh_group_status_rows": "protocol.contracts.normalize_mesh_group_status_rows",
    "protocol.contracts.normalize_schedule_json": "protocol.contracts.normalize_schedule_json",
    "protocol.boundary.decode_mqtt_topic": "protocol.boundary.decode_mqtt_topic",
    "protocol.boundary.decode_mqtt_message_envelope": "protocol.boundary.decode_mqtt_message_envelope",
    "protocol.boundary.decode_mqtt_properties": "protocol.boundary.decode_mqtt_properties",
}

AssertionFamily = Literal["canonical", "drift", "telemetry"]
ASSERTION_FAMILY_VALUES: Mapping[str, AssertionFamily] = {
    "canonical": "canonical",
    "drift": "drift",
    "telemetry": "telemetry",
}


@dataclass(frozen=True, slots=True)
class DeterministicReplayControls:
    """Deterministic controls bound to one replay scenario."""

    seed: int
    clock_baseline: str

    def baseline_datetime(self) -> datetime:
        """Return the clock baseline parsed as an aware datetime."""
        return datetime.fromisoformat(self.clock_baseline)


@dataclass(frozen=True, slots=True)
class ReplayManifest:
    """Replay scenario manifest referencing one authority-owned fixture."""

    scenario_id: str
    channel: ReplayChannel
    family: str
    version: str
    operation: ReplayOperation
    authority_path: Path
    assertion_families: tuple[AssertionFamily, ...]
    controls: DeterministicReplayControls
    manifest_path: Path
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class LoadedReplayFixture:
    """Replay manifest plus the loaded authority payload it references."""

    manifest: ReplayManifest
    authority_payload: object
    authority_metadata: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ReplayExecutionResult:
    """Deterministic replay execution result produced by the driver."""

    manifest: ReplayManifest
    public_path: str
    started_at: str
    finished_at: str
    canonical: object | None
    drift_flags: tuple[str, ...]
    error_category: str | None
    error_type: str | None = None
    failure_summary: FailureSummary = field(default_factory=empty_failure_summary)
    fingerprint: str | None = None
