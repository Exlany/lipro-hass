"""Unified protocol-root package for Lipro integration."""

from __future__ import annotations

from .compat import (
    TRANSITIONAL_PROTOCOL_PUBLIC_SURFACES,
    is_transitional_protocol_surface,
)
from .contracts import (
    CanonicalMqttConfig,
    CanonicalProtocolContracts,
    MqttTransportFacade,
)
from .diagnostics_context import ProtocolDiagnosticsContext
from .facade import LiproMqttFacade, LiproProtocolFacade
from .session import ProtocolSessionState
from .telemetry import ProtocolTelemetry

__all__ = [
    "TRANSITIONAL_PROTOCOL_PUBLIC_SURFACES",
    "CanonicalMqttConfig",
    "CanonicalProtocolContracts",
    "LiproMqttFacade",
    "LiproProtocolFacade",
    "MqttTransportFacade",
    "ProtocolDiagnosticsContext",
    "ProtocolSessionState",
    "ProtocolTelemetry",
    "is_transitional_protocol_surface",
]
