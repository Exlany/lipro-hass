"""Focused no-regrowth guards for Phase 92 redaction convergence and thin-shell topicization."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_REDACTION = _ROOT / "custom_components" / "lipro" / "core" / "utils" / "redaction.py"
_CONTROL_REDACTION = _ROOT / "custom_components" / "lipro" / "control" / "redaction.py"
_SANITIZE = _ROOT / "custom_components" / "lipro" / "core" / "anonymous_share" / "sanitize.py"
_TELEMETRY_JSON = _ROOT / "custom_components" / "lipro" / "core" / "telemetry" / "json_payloads.py"
_EXPORTER = _ROOT / "custom_components" / "lipro" / "core" / "telemetry" / "exporter.py"
_STATUS_ROOT = _ROOT / "tests" / "core" / "api" / "test_api_status_service.py"
_COMMAND_ROOT = _ROOT / "tests" / "core" / "api" / "test_api_command_surface_responses.py"
_LIGHT_ROOT = _ROOT / "tests" / "platforms" / "test_light_entity_behavior.py"
_DIAGNOSTICS_ROOT = _ROOT / "tests" / "services" / "test_services_diagnostics.py"
_DIAGNOSTICS_SUPPORT = _ROOT / "tests" / "services" / "test_services_diagnostics_support.py"
_DIAGNOSTICS_FEEDBACK = _ROOT / "tests" / "services" / "test_services_diagnostics_feedback.py"
_DIAGNOSTICS_CAPABILITIES = _ROOT / "tests" / "services" / "test_services_diagnostics_capabilities.py"
_DIAGNOSTICS_PAYLOADS = _ROOT / "tests" / "services" / "test_services_diagnostics_payloads.py"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_VERIFICATION = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase92_shared_redaction_truth_stays_canonical() -> None:
    redaction_text = _read_text(_REDACTION)
    control_text = _read_text(_CONTROL_REDACTION)
    sanitize_text = _read_text(_SANITIZE)
    telemetry_json_text = _read_text(_TELEMETRY_JSON)
    exporter_text = _read_text(_EXPORTER)

    for needle in (
        "SHARED_SENSITIVE_KEY_NAMES",
        "TELEMETRY_REFERENCE_ALIASES",
        "normalize_redaction_key",
        "redact_sensitive_literal",
        "redact_sensitive_text",
    ):
        assert needle in redaction_text

    assert "from ..core.utils.redaction import (" in control_text
    assert "looks_sensitive_value" in sanitize_text
    assert "SHARED_SENSITIVE_KEY_NAMES" in telemetry_json_text
    assert "redact_sensitive_text" in exporter_text
    assert "_summarize_redacted_string" in exporter_text


def test_phase92_touched_root_suites_stay_thin_and_topicized() -> None:
    assert "Thin shell for topicized API status service suites." in _read_text(_STATUS_ROOT)
    assert "Thin shell for topicized command-surface response suites." in _read_text(_COMMAND_ROOT)
    assert "Thin shell for topicized light entity behavior suites." in _read_text(_LIGHT_ROOT)
    assert "Thin shell for topicized services.diagnostics suites." in _read_text(_DIAGNOSTICS_ROOT)
    assert _DIAGNOSTICS_SUPPORT.exists()
    assert _DIAGNOSTICS_FEEDBACK.exists()
    assert _DIAGNOSTICS_CAPABILITIES.exists()
    assert _DIAGNOSTICS_PAYLOADS.exists()


def test_phase92_governance_truth_registers_closeout() -> None:
    verification_text = _read_text(_VERIFICATION)
    file_matrix_text = _read_text(_FILE_MATRIX)

    assert "## Phase 92 Control/Entity Thin-Boundary and Redaction Convergence" in verification_text
    assert "tests/meta/test_phase92_redaction_convergence_guards.py" in verification_text
    for needle in (
        "diagnostics-facing redaction adapter on shared redaction contract",
        "structure-preserving anonymous-share sanitizer on shared redaction contract",
        "shared-policy telemetry exporter with pseudonymous alias + marker summary budget contract",
        "thin shell after diagnostics-services topicization",
    ):
        assert needle in file_matrix_text
