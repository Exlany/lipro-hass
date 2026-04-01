"""Formal control-plane public surfaces."""

from .diagnostics_surface import (
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
    build_device_diagnostics,
    extract_device_serial,
)
from .entry_lifecycle_controller import EntryLifecycleController
from .service_registry import ServiceRegistry
from .system_health_surface import async_register, system_health_info

__all__ = [
    "EntryLifecycleController",
    "ServiceRegistry",
    "async_get_config_entry_diagnostics",
    "async_get_device_diagnostics",
    "async_register",
    "build_device_diagnostics",
    "extract_device_serial",
    "system_health_info",
]
