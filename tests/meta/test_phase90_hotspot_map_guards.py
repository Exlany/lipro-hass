"""Focused no-regrowth guards for the Phase 90 hotspot formal-home freeze."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_RESIDUAL_LEDGER = _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
_KILL_LIST = _ROOT / ".planning" / "reviews" / "KILL_LIST.md"
_VERIFICATION = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
_PROJECT = _ROOT / ".planning" / "PROJECT.md"
_ROADMAP = _ROOT / ".planning" / "ROADMAP.md"
_REQUIREMENTS = _ROOT / ".planning" / "REQUIREMENTS.md"
_STATE = _ROOT / ".planning" / "STATE.md"
_DEV_ARCH = _ROOT / "docs" / "developer_architecture.md"
_CODEBASE_ARCH = _ROOT / ".planning" / "codebase" / "ARCHITECTURE.md"
_CODEBASE_STRUCTURE = _ROOT / ".planning" / "codebase" / "STRUCTURE.md"
_CODEBASE_CONCERNS = _ROOT / ".planning" / "codebase" / "CONCERNS.md"
_CODEBASE_CONVENTIONS = _ROOT / ".planning" / "codebase" / "CONVENTIONS.md"

_FORMAL_HOME_ROWS = {
    "custom_components/lipro/core/coordinator/runtime/command_runtime.py": "formal command-runtime orchestration home",
    "custom_components/lipro/core/api/rest_facade.py": "canonical REST child-façade composition home",
    "custom_components/lipro/core/api/request_policy.py": "formal 429 / busy / pacing policy home",
    "custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py": "formal MQTT-runtime orchestration home",
    "custom_components/lipro/core/anonymous_share/manager.py": "formal anonymous-share aggregate manager home",
    "custom_components/lipro/core/api/client.py": "stable REST façade import shell / home",
}

_PROTECTED_SHELL_ROWS = {
    "custom_components/lipro/__init__.py": "protected thin HA root adapter / lazy wiring shell",
    "custom_components/lipro/control/runtime_access.py": "protected thin runtime read-model / typed access home",
    "custom_components/lipro/entities/base.py": "protected thin entity command / state projection shell",
    "custom_components/lipro/entities/firmware_update.py": "protected thin OTA projection shell after runtime-boundary tightening",
}


def _row_for(path: str) -> str:
    for line in _FILE_MATRIX.read_text(encoding="utf-8").splitlines():
        if f"| `{path}` |" in line:
            return line
    message = f"missing file-matrix row: {path}"
    raise AssertionError(message)


def test_phase90_file_matrix_freezes_formal_homes_and_protected_shells() -> None:
    for path, phrase in {**_FORMAL_HOME_ROWS, **_PROTECTED_SHELL_ROWS}.items():
        line = _row_for(path)
        assert phrase in line
        assert "delete target" not in line.lower()


def test_phase90_ledgers_keep_delete_gate_explicit_and_zero_growth() -> None:
    residual_text = _RESIDUAL_LEDGER.read_text(encoding="utf-8")
    kill_list_text = _KILL_LIST.read_text(encoding="utf-8")

    assert "## Phase 90 Residual Delta" in residual_text
    assert "无新增 active residual family" in residual_text
    assert "owner + target phase + delete gate + evidence pointer" in residual_text
    assert "## Phase 90 Status Update" in kill_list_text
    assert "无新增 active kill target" in kill_list_text
    assert "不得再被写成 future kill target" in kill_list_text


def test_phase90_closeout_docs_and_derived_maps_keep_the_freeze_visible() -> None:
    verification_text = _VERIFICATION.read_text(encoding="utf-8")
    assert "## Phase 90 Hotspot Routing Freeze / Formal-Home Decomposition Map" in verification_text
    assert "tests/meta/test_phase90_hotspot_map_guards.py" in verification_text
    assert "phase-plan-index 90" in verification_text

    project_text = _PROJECT.read_text(encoding="utf-8")
    roadmap_text = _ROADMAP.read_text(encoding="utf-8")
    requirements_text = _REQUIREMENTS.read_text(encoding="utf-8")
    state_text = _STATE.read_text(encoding="utf-8")
    dev_arch_text = _DEV_ARCH.read_text(encoding="utf-8")

    assert ".planning/phases/90-hotspot-routing-freeze-and-formal-home-decomposition-map/" in project_text
    assert "### Phase 90: Hotspot routing freeze and formal-home decomposition map" in roadmap_text
    assert "| HOT-40 | Phase 90 | Complete |" in requirements_text
    assert "no active milestone route / latest archived baseline = v1.25" in state_text
    assert "$gsd-new-milestone" in state_text
    assert "## Phase 90 Freeze Notes" in dev_arch_text

    for path in (_CODEBASE_ARCH, _CODEBASE_STRUCTURE, _CODEBASE_CONCERNS, _CODEBASE_CONVENTIONS):
        assert "Phase 90" in path.read_text(encoding="utf-8")
