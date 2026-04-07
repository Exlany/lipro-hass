"""Focused no-regrowth guards for Phase 96 sanitizer burndown."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_REDACTION = _ROOT / "custom_components" / "lipro" / "control" / "redaction.py"
_EXPORTER = _ROOT / "custom_components" / "lipro" / "core" / "telemetry" / "exporter.py"
_MANAGER_SUPPORT = _ROOT / "custom_components" / "lipro" / "core" / "anonymous_share" / "manager_support.py"
_SANITIZE = _ROOT / "custom_components" / "lipro" / "core" / "anonymous_share" / "sanitize.py"
_PHASE_DIR = _ROOT / ".planning" / "phases" / "96-redaction-telemetry-and-anonymous-share-sanitizer-burndown"
_PHASE_VERIFICATION = _PHASE_DIR / "96-VERIFICATION.md"
_PHASE_VALIDATION = _PHASE_DIR / "96-VALIDATION.md"
_VERIFICATION_MATRIX = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
_DEPENDENCY_MATRIX = _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase96_redaction_and_sanitizer_helpers_stay_localized() -> None:
    redaction_text = _read(_REDACTION)
    exporter_text = _read(_EXPORTER)
    manager_support_text = _read(_MANAGER_SUPPORT)
    sanitize_text = _read(_SANITIZE)

    for needle in (
        "def _should_redact_nested_key(",
        "def _redact_mapping_value(",
        "def _redact_sequence_value(",
        "def _redact_json_container_string(",
        "def _redact_scalar_string(",
    ):
        assert needle in redaction_text

    for needle in (
        "def _extract_entry_id(",
        "def _sanitize_mapping_entry(",
        "def _sanitize_sequence(",
        "def _sanitize_string_value(",
    ):
        assert needle in exporter_text

    for needle in (
        "def configure_scope_state(",
        "def aggregate_pending_count(",
        "def clear_scope_collectors(",
    ):
        assert needle in manager_support_text

    for needle in (
        "def _sanitize_container_string(",
        "def _sanitize_scalar_value(",
    ):
        assert needle in sanitize_text


def test_phase96_governance_truth_registers_sanitizer_closeout() -> None:
    verification_text = _read(_PHASE_VERIFICATION)
    validation_text = _read(_PHASE_VALIDATION)
    verification_matrix_text = _read(_VERIFICATION_MATRIX)
    dependency_matrix_text = _read(_DEPENDENCY_MATRIX)
    file_matrix_text = _read(_FILE_MATRIX)

    assert "# Phase 96 Verification" in verification_text
    assert "v1.26 active route / Phase 97 planning-ready / latest archived baseline = v1.25" in verification_text
    assert "tests/meta/test_phase96_sanitizer_burndown_guards.py" in verification_text
    assert "# Phase 96 Validation Contract" in validation_text
    assert "$gsd-plan-phase 97" in validation_text
    assert "## Phase 96 Redaction/Telemetry/Anonymous-Share Sanitizer Burndown" in verification_matrix_text
    assert "tests/meta/test_phase96_sanitizer_burndown_guards.py" in verification_matrix_text

    for needle in (
        "control/redaction.py` 继续是 diagnostics-facing redaction adapter on shared redaction truth",
        "core/telemetry/exporter.py` 继续是唯一 formal runtime telemetry exporter root",
        "anonymous_share/manager.py` 继续是 formal anonymous-share aggregate manager home",
    ):
        assert needle in dependency_matrix_text

    for needle in (
        "diagnostics-facing redaction adapter on shared redaction contract with inward recursion helpers",
        "shared-policy telemetry exporter with localized sanitize helper split",
        "formal anonymous-share aggregate manager home with scope-state support collaborators",
        "anonymous-share scope-state / pending aggregation helper home",
        "structure-preserving anonymous-share sanitizer with container/scalar helper split",
        "focused no-regrowth guard home for Phase 96 sanitizer burn-down",
    ):
        assert needle in file_matrix_text
