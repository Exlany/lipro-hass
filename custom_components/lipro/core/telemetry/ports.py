"""Formal source/sink ports for telemetry exporting."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from .models import TelemetrySnapshot


class ProtocolTelemetrySource(Protocol):
    """Protocol-plane source consumed by the exporter."""

    def get_protocol_telemetry_snapshot(self) -> Mapping[str, Any]:
        """Return a protocol-owned snapshot."""
        ...


class RuntimeTelemetrySource(Protocol):
    """Runtime-plane source consumed by the exporter."""

    def get_runtime_telemetry_snapshot(self) -> Mapping[str, Any]:
        """Return a runtime-owned snapshot."""
        ...


class TelemetrySink(Protocol):
    """Exporter sink contract for stable projections."""

    name: str

    def build_view(self, snapshot: TelemetrySnapshot) -> Mapping[str, Any]:
        """Build one projection from the shared snapshot."""
        ...


__all__ = [
    "ProtocolTelemetrySource",
    "RuntimeTelemetrySource",
    "TelemetrySink",
]
