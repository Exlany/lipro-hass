"""Focused predecessor guards for Phase 100 runtime/schedule support extraction freeze."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot

_ROOT = repo_root(Path(__file__))
_PROJECT = _ROOT / ".planning" / "PROJECT.md"
_ROADMAP = _ROOT / ".planning" / "ROADMAP.md"
_ARCHIVED_V127_REQUIREMENTS = _ROOT / ".planning" / "milestones" / "v1.27-REQUIREMENTS.md"
_STATE = _ROOT / ".planning" / "STATE.md"
_MILESTONES = _ROOT / ".planning" / "MILESTONES.md"
_VERIFICATION_MATRIX = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_TESTING = _ROOT / ".planning" / "codebase" / "TESTING.md"
_CONCERNS = _ROOT / ".planning" / "codebase" / "CONCERNS.md"
_DEV_ARCH = _ROOT / "docs" / "developer_architecture.md"
_SCHEDULE_SERVICE = _ROOT / "custom_components" / "lipro" / "core" / "api" / "schedule_service.py"
_SCHEDULE_SUPPORT = _ROOT / "custom_components" / "lipro" / "core" / "api" / "schedule_service_support.py"
_MQTT_RUNTIME = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "runtime" / "mqtt_runtime.py"
_MQTT_RUNTIME_SUPPORT = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "runtime" / "mqtt_runtime_support.py"
_PHASE100_DIR = (
    _ROOT
    / ".planning"
    / "phases"
    / "100-mqtt-runtime-and-schedule-service-support-extraction-freeze"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase100_bundle_stays_visible_as_completed_predecessor() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_ARCHIVED_V127_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    dev_arch_text = _read(_DEV_ARCH)
    phase100_verification = _read(_PHASE100_DIR / "100-VERIFICATION.md")
    phase100_validation = _read(_PHASE100_DIR / "100-VALIDATION.md")

    assert "no active milestone route / latest archived baseline = v1.28" in project_text
    assert "### Phase 100: MQTT runtime and schedule service support extraction freeze" in roadmap_text
    assert "| HOT-42 | Phase 100 | Completed |" in requirements_text
    assert "Phase 102" in state_text
    assert "`Phase 100`: MQTT runtime and schedule service support extraction freeze ✅" in milestones_text
    assert "Phase 100 MQTT Runtime / Schedule Service Support Extraction / Predecessor Freeze Note" in dev_arch_text
    assert "# Phase 100 Verification" in phase100_verification
    assert "# Phase 100 Validation Contract" in phase100_validation


def test_phase100_maps_keep_predecessor_guard_footprint() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)
    concerns_text = _read(_CONCERNS)

    assert "custom_components/lipro/core/api/schedule_service_support.py" in file_matrix_text
    assert "custom_components/lipro/core/coordinator/runtime/mqtt_runtime_support.py" in file_matrix_text
    assert "tests/meta/test_phase100_runtime_schedule_support_guards.py" in file_matrix_text
    assert "focused predecessor guard home for Phase 100 MQTT/runtime schedule support extraction / governance freeze" in file_matrix_text
    assert_testing_inventory_snapshot(testing_text)
    assert "tests/meta/test_phase100_runtime_schedule_support_guards.py" in verification_text
    assert "## Phase 100 MQTT Runtime / Schedule Service Support Extraction Freeze" in verification_text
    assert "## Phase 102 Governance Portability / Verification Stratification / Open-Source Continuity Hardening" in verification_text
    assert "Phase 101 已把 `anonymous_share/manager.py` 收窄到 435 行 formal manager home" in concerns_text


def test_phase100_support_seams_preserve_formal_homes() -> None:
    schedule_service_text = _read(_SCHEDULE_SERVICE)
    schedule_support_text = _read(_SCHEDULE_SUPPORT)
    mqtt_runtime_text = _read(_MQTT_RUNTIME)
    mqtt_support_text = _read(_MQTT_RUNTIME_SUPPORT)

    assert "from .schedule_service_support import (" in schedule_service_text
    assert "def _next_mesh_schedule_id(rows: ScheduleRows) -> int:" in schedule_service_text
    assert "async def collect_schedule_rows_from_batch(" in schedule_support_text
    assert "async def add_mesh_schedule_for_candidate(" in schedule_support_text
    assert "from .mqtt_runtime_support import (" in mqtt_runtime_text
    assert "class MqttRuntime:" in mqtt_runtime_text
    assert "def require_transport(" in mqtt_support_text
    assert "def build_runtime_metrics(" in mqtt_support_text
