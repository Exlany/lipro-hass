"""Phase 111 runtime-boundary regression guards."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_ENTITY_BASE = _ROOT / "custom_components" / "lipro" / "entities" / "base.py"
_FIRMWARE_UPDATE = _ROOT / "custom_components" / "lipro" / "entities" / "firmware_update.py"
_RUNTIME_ACCESS = _ROOT / "custom_components" / "lipro" / "control" / "runtime_access.py"
_RUNTIME_ACCESS_SUPPORT_VIEWS = (
    _ROOT / "custom_components" / "lipro" / "control" / "runtime_access_support_views.py"
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase111_entity_bridge_stays_off_concrete_runtime_root() -> None:
    entity_text = _read_text(_ENTITY_BASE)

    assert "_EntityCoordinatorBridge" in entity_text
    assert "runtime_coordinator" in entity_text
    assert "DataUpdateCoordinator" in entity_text
    assert "from ..core.coordinator.coordinator import Coordinator" not in entity_text
    assert "cast(Coordinator, coordinator)" not in entity_text
    assert "CoordinatorEntity[Coordinator]" not in entity_text


def test_phase111_firmware_entity_uses_runtime_coordinator_surface() -> None:
    firmware_text = _read_text(_FIRMWARE_UPDATE)

    assert "self.runtime_coordinator.async_send_command(" in firmware_text
    assert "self.runtime_coordinator.async_request_refresh()" in firmware_text
    assert "self.runtime_coordinator.async_query_device_ota_info(" in firmware_text
    assert "self.coordinator.async_send_command(" not in firmware_text
    assert "self.coordinator.async_request_refresh()" not in firmware_text
    assert "self.coordinator.async_query_device_ota_info(" not in firmware_text


def test_phase111_runtime_access_keeps_runtime_data_narrowing_support_local() -> None:
    runtime_access_text = _read_text(_RUNTIME_ACCESS)
    support_views_text = _read_text(_RUNTIME_ACCESS_SUPPORT_VIEWS)

    assert "_build_runtime_entry_view_support" in runtime_access_text
    assert "_iter_runtime_entry_views_support" in runtime_access_text
    assert "runtime_data" not in runtime_access_text
    assert "_get_explicit_member(" not in runtime_access_text

    assert '_has_explicit_runtime_member(entry, "runtime_data")' in support_views_text
    assert "_coerce_runtime_entry_port(" in support_views_text
    assert '_get_explicit_member(entry, "entry_id")' in support_views_text
    assert '_get_explicit_member(coordinator, "protocol")' in support_views_text
    assert "type(entry).__getattribute__" not in support_views_text
    assert "type(coordinator).__getattribute__" not in support_views_text
    assert "entry.runtime_data" not in support_views_text
