"""Compatibility import home for control-owned service registrations."""

from __future__ import annotations

from ..control.service_registry import (
    DEVELOPER_SERVICE_REGISTRATIONS,
    PUBLIC_SERVICE_REGISTRATIONS,
    SERVICE_REGISTRATIONS,
    has_debug_mode_runtime_entry,
    is_debug_mode_enabled_for_entry,
)

__all__ = [
    "DEVELOPER_SERVICE_REGISTRATIONS",
    "PUBLIC_SERVICE_REGISTRATIONS",
    "SERVICE_REGISTRATIONS",
    "has_debug_mode_runtime_entry",
    "is_debug_mode_enabled_for_entry",
]
