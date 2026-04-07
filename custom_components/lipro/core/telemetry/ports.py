"""Formal source/sink ports for telemetry exporting."""

from __future__ import annotations

from typing import Protocol

from .models import TelemetrySinkPayload, TelemetrySnapshot, TelemetrySourcePayload


class ProtocolTelemetrySource(Protocol):
    """Protocol-plane source consumed by the exporter."""

    def get_protocol_telemetry_snapshot(self) -> TelemetrySourcePayload:
        """Return a protocol-owned snapshot."""
        ...


class RuntimeTelemetrySource(Protocol):
    """Runtime-plane source consumed by the exporter."""

    def get_runtime_telemetry_snapshot(self) -> TelemetrySourcePayload:
        """Return a runtime-owned snapshot."""
        ...


class TelemetrySink(Protocol):
    """Exporter sink contract for stable projections."""

    name: str

    def build_view(self, snapshot: TelemetrySnapshot) -> TelemetrySinkPayload:
        """Build one projection from the shared snapshot."""
        ...


__all__ = [
    "ProtocolTelemetrySource",
    "RuntimeTelemetrySource",
    "TelemetrySink",
]
