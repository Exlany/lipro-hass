"""Phase 73 service/runtime convergence guards."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.ast_guard_utils import find_forbidden_imports, iter_import_modules
from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_PRODUCTION_ROOT = _ROOT / "custom_components" / "lipro"
_PLATFORM_PATH = _PRODUCTION_ROOT / "helpers" / "platform.py"
_ENTITY_BASE_PATH = _PRODUCTION_ROOT / "entities" / "base.py"
_SCHEDULE_SERVICE_PATH = _PRODUCTION_ROOT / "services" / "schedule.py"
_DIAGNOSTICS_PATH = _PRODUCTION_ROOT / "diagnostics.py"
_SYSTEM_HEALTH_PATH = _PRODUCTION_ROOT / "system_health.py"
_SERVICE_ROUTER_PATH = _PRODUCTION_ROOT / "control" / "service_router.py"
_SERVICE_ROUTER_SUPPORT_PATH = _PRODUCTION_ROOT / "control" / "service_router_support.py"
_FORBIDDEN_RUNTIME_ACCESS_IMPORTS = (
    "custom_components.lipro.control.runtime_access",
    ".control.runtime_access",
    "..control.runtime_access",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase73_platform_and_entity_do_not_import_control_runtime_access() -> None:
    violations = find_forbidden_imports(
        [_PLATFORM_PATH, _ENTITY_BASE_PATH],
        _FORBIDDEN_RUNTIME_ACCESS_IMPORTS,
        root=_ROOT,
    )
    assert not violations, violations


def test_phase73_platform_helper_uses_formal_runtime_contract() -> None:
    platform_text = _read_text(_PLATFORM_PATH)
    entity_text = _read_text(_ENTITY_BASE_PATH)

    assert "coordinator.iter_devices()" in platform_text
    assert ".devices" not in platform_text
    assert platform_text.count("entry.runtime_data") == 1

    assert ".runtime_data" not in entity_text
    assert ".devices" not in entity_text
    assert "self.coordinator.get_device(self._device.serial)" in entity_text


def test_phase73_schedule_service_calls_use_coordinator_schedule_surface() -> None:
    schedule_text = _read_text(_SCHEDULE_SERVICE_PATH)

    assert "coordinator.protocol_service" not in schedule_text
    assert "coordinator.schedule_service.async_get_schedules" in schedule_text
    assert "coordinator.schedule_service.async_add_schedule" in schedule_text
    assert "coordinator.schedule_service.async_delete_schedules" in schedule_text


def test_phase73_diagnostics_and_system_health_stay_on_control_surfaces() -> None:
    diagnostics_imports = iter_import_modules(_DIAGNOSTICS_PATH)
    system_health_imports = iter_import_modules(_SYSTEM_HEALTH_PATH)
    diagnostics_text = _read_text(_DIAGNOSTICS_PATH)
    system_health_text = _read_text(_SYSTEM_HEALTH_PATH)

    assert ".control.diagnostics_surface" in diagnostics_imports
    assert ".control.system_health_surface" in system_health_imports
    assert "runtime_access" not in diagnostics_text
    assert "runtime_access" not in system_health_text
    assert ".runtime_data" not in diagnostics_text
    assert ".runtime_data" not in system_health_text


def test_phase73_service_router_keeps_runtime_lookup_localized_to_support() -> None:
    router_text = _read_text(_SERVICE_ROUTER_PATH)
    support_imports = iter_import_modules(_SERVICE_ROUTER_SUPPORT_PATH)

    assert "service_router_handlers as _handlers" in router_text
    assert "service_router_support as _support" in router_text
    assert ".runtime_access" not in router_text
    assert ".runtime_access" in support_imports
