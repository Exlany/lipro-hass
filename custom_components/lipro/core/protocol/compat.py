"""Explicit compat markers for protocol-root migration."""

from __future__ import annotations

TRANSITIONAL_PROTOCOL_PUBLIC_SURFACES = (
    "LiproClient",
    "LiproMqttClient",
)


def is_transitional_protocol_surface(name: str) -> bool:
    """Return whether one symbol is an explicitly transitional protocol surface."""
    return name in TRANSITIONAL_PROTOCOL_PUBLIC_SURFACES


__all__ = [
    "TRANSITIONAL_PROTOCOL_PUBLIC_SURFACES",
    "is_transitional_protocol_surface",
]
