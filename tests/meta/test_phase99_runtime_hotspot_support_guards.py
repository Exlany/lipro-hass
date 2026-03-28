"""Focused predecessor guards for Phase 99 runtime hotspot support extraction freeze."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot
from .governance_current_truth import CURRENT_PHASE, CURRENT_ROUTE

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
_STATUS_FALLBACK = _ROOT / "custom_components" / "lipro" / "core" / "api" / "status_fallback.py"
_STATUS_FALLBACK_SUPPORT = _ROOT / "custom_components" / "lipro" / "core" / "api" / "status_fallback_support.py"
_COMMAND_RUNTIME = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "runtime" / "command_runtime.py"
_COMMAND_RUNTIME_SUPPORT = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "runtime" / "command_runtime_support.py"
_PHASE99_DIR = (
    _ROOT
    / ".planning"
    / "phases"
    / "99-runtime-hotspot-support-extraction-and-terminal-audit-freeze"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase99_bundle_stays_visible_as_completed_predecessor() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_ARCHIVED_V127_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    dev_arch_text = _read(_DEV_ARCH)
    phase99_verification = _read(_PHASE99_DIR / "99-VERIFICATION.md")
    phase99_validation = _read(_PHASE99_DIR / "99-VALIDATION.md")

    assert CURRENT_ROUTE in project_text
    assert "### Phase 99: Runtime hotspot support extraction and terminal audit freeze" in roadmap_text
    assert "| HOT-41 | Phase 99 | Completed |" in requirements_text
    assert f"Phase {CURRENT_PHASE}" in state_text
    assert "`Phase 99`: runtime hotspot support extraction and terminal audit freeze ✅" in milestones_text
    assert "Phase 99 Runtime Hotspot Support Extraction / Predecessor Freeze Note" in dev_arch_text
    assert "# Phase 99 Verification" in phase99_verification
    assert "# Phase 99 Validation Contract" in phase99_validation


def test_phase99_maps_keep_predecessor_guard_footprint() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)
    concerns_text = _read(_CONCERNS)

    assert "custom_components/lipro/core/api/status_fallback_support.py" in file_matrix_text
    assert "custom_components/lipro/core/coordinator/runtime/command_runtime_support.py" in file_matrix_text
    assert "tests/meta/test_phase99_runtime_hotspot_support_guards.py" in file_matrix_text
    assert "focused predecessor guard home for Phase 99 runtime hotspot support extraction / governance freeze" in file_matrix_text
    assert_testing_inventory_snapshot(testing_text)
    assert "tests/meta/test_phase99_runtime_hotspot_support_guards.py" in verification_text
    assert "## Phase 99 Runtime Hotspot Support Extraction / Terminal Audit Freeze" in verification_text
    assert "## Phase 102 Governance Portability / Verification Stratification / Open-Source Continuity Hardening" in verification_text
    assert "Phase 101 已把 `anonymous_share/manager.py` 收窄到 435 行 formal manager home" in concerns_text


def test_phase99_support_seams_preserve_formal_homes() -> None:
    status_fallback_text = _read(_STATUS_FALLBACK)
    status_support_text = _read(_STATUS_FALLBACK_SUPPORT)
    command_runtime_text = _read(_COMMAND_RUNTIME)
    command_support_text = _read(_COMMAND_RUNTIME_SUPPORT)

    assert "from .status_fallback_support import (" in status_fallback_text
    assert "def _build_query_payload(body_key: str, ids: list[str]) -> QueryPayload:" in status_fallback_text
    assert "_SMALL_SUBSET_BATCH_QUERY_THRESHOLD = 4" in status_fallback_text
    assert "async def query_items_by_binary_split_impl(" in status_support_text
    assert "async def query_with_fallback_impl(" in status_support_text
    assert "from .command_runtime_support import (" in command_runtime_text
    assert "class CommandRuntime:" in command_runtime_text
    assert "class _CommandRequest:" in command_support_text
    assert "def _build_failure_summary(" in command_support_text
