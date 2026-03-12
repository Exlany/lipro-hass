"""Formal control-plane public surfaces."""

from .diagnostics_surface import (
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
    build_device_diagnostics,
    extract_device_serial,
)
from .entry_lifecycle_controller import EntryLifecycleController
from .models import RuntimeCoordinatorSnapshot
from .runtime_access import (
    build_runtime_snapshot,
    build_runtime_snapshots,
    get_entry_runtime_coordinator,
    iter_runtime_coordinators,
    iter_runtime_entries,
)
from .service_registry import ServiceRegistry
from .system_health_surface import async_register, system_health_info

__all__ = [
    "EntryLifecycleController",
    "RuntimeCoordinatorSnapshot",
    "ServiceRegistry",
    "async_get_config_entry_diagnostics",
    "async_get_device_diagnostics",
    "async_register",
    "build_device_diagnostics",
    "build_runtime_snapshot",
    "build_runtime_snapshots",
    "extract_device_serial",
    "get_entry_runtime_coordinator",
    "iter_runtime_coordinators",
    "iter_runtime_entries",
    "system_health_info",
]
