"""Phase 89 runtime-boundary regression guards."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_ENTITY_BASE = _ROOT / "custom_components" / "lipro" / "entities" / "base.py"
_FIRMWARE_UPDATE = _ROOT / "custom_components" / "lipro" / "entities" / "firmware_update.py"
_RUNTIME_TYPES = _ROOT / "custom_components" / "lipro" / "runtime_types.py"
_COORDINATOR = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "coordinator.py"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase89_entities_use_named_runtime_verbs_only() -> None:
    entity_text = _read_text(_ENTITY_BASE)
    firmware_text = _read_text(_FIRMWARE_UPDATE)

    assert "coordinator.command_service" not in entity_text
    assert "coordinator.protocol_service" not in entity_text
    assert "coordinator.get_device_lock" not in entity_text
    assert "coordinator.async_send_command(" in entity_text
    assert "coordinator.async_apply_optimistic_state(" in entity_text
    assert "coordinator.async_query_device_ota_info(" in firmware_text


def test_phase89_runtime_types_hide_service_handles_from_entity_protocol() -> None:
    runtime_types_text = _read_text(_RUNTIME_TYPES)
    runtime_protocol_block = runtime_types_text.split(
        "class LiproRuntimeCoordinator(Protocol):",
        maxsplit=1,
    )[1].split(
        "class LiproCoordinator(LiproRuntimeCoordinator, Protocol):",
        maxsplit=1,
    )[0]

    assert "async_send_command(" in runtime_protocol_block
    assert "async_apply_optimistic_state(" in runtime_protocol_block
    assert "async_query_device_ota_info(" in runtime_protocol_block
    assert "command_service" not in runtime_protocol_block
    assert "protocol_service" not in runtime_protocol_block
    assert "get_device_lock" not in runtime_protocol_block


def test_phase89_coordinator_removes_entity_lock_backdoor() -> None:
    coordinator_text = _read_text(_COORDINATOR)

    assert "def get_device_lock(" not in coordinator_text
    assert "async_apply_optimistic_state(" in coordinator_text
    assert "async_query_device_ota_info(" in coordinator_text
