"""Typed models for protocol replay manifests and deterministic execution."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

ReplayChannel = Literal["rest", "mqtt"]
ReplayOperation = Literal[
    "protocol.contracts.normalize_mqtt_config",
    "protocol.boundary.decode_mqtt_properties",
]
AssertionFamily = Literal["canonical", "drift", "telemetry"]


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
    fingerprint: str | None = None
