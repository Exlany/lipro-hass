"""Focused no-regrowth guards for Phase 94 typed payload contraction."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_PHASE_DIR = (
    _ROOT
    / ".planning"
    / "phases"
    / "94-typed-payload-contraction-and-domain-bag-narrowing"
)
_PHASE_VERIFICATION = _PHASE_DIR / "94-VERIFICATION.md"
_PHASE_VALIDATION = _PHASE_DIR / "94-VALIDATION.md"
_VERIFICATION_MATRIX = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
_TRANSPORT_TEST = _ROOT / "tests" / "core" / "api" / "test_api_transport_executor.py"

_FORBIDDEN_LITERALS = {
    "custom_components/lipro/domain_data.py": (
        "dict[str, Any]",
    ),
    "custom_components/lipro/entities/base.py": (
        "CoordinatorEntity[Any]",
    ),
    "custom_components/lipro/core/utils/property_normalization.py": (
        "from typing import Any",
        "Mapping[str, Any]",
        "dict[str, Any]",
    ),
    "custom_components/lipro/control/diagnostics_surface.py": (
        "type DiagnosticsPayload = dict[str, Any]",
        "Callable[[Mapping[str, object], set[str]], Any]",
        "Callable[..., str | None]",
    ),
    "custom_components/lipro/core/api/command_api_service.py": (
        "type MappingPayload = dict[str, Any]",
    ),
    "custom_components/lipro/core/api/status_fallback.py": (
        "logger: Any",
        "dict[str, Any]",
        "Awaitable[Any]",
        "Callable[[Any], str | int | None]",
    ),
    "custom_components/lipro/core/api/status_service.py": (
        "logger: Any",
        "result: Any",
    ),
    "custom_components/lipro/core/api/transport_core.py": (
        "-> tuple[int, dict[str, Any], dict[str, str]]",
        "def require_mapping_response(path: str, result: Any)",
    ),
}


def _read(relative_path: str) -> str:
    return (_ROOT / relative_path).read_text(encoding="utf-8")


def test_phase94_typed_seams_do_not_regrow_broad_contract_literals() -> None:
    for relative_path, forbidden_literals in _FORBIDDEN_LITERALS.items():
        text = _read(relative_path)
        for forbidden in forbidden_literals:
            assert forbidden not in text, f"{relative_path} regrew forbidden literal: {forbidden}"


def test_phase94_transport_and_diagnostics_guards_keep_the_new_contract_visible() -> None:
    diagnostics_text = _read("custom_components/lipro/control/diagnostics_surface.py")
    status_fallback_text = _read("custom_components/lipro/core/api/status_fallback.py")
    transport_text = _read("custom_components/lipro/core/api/transport_core.py")
    transport_test_text = _TRANSPORT_TEST.read_text(encoding="utf-8")

    assert "type DiagnosticsPayload = dict[str, DiagnosticsValue]" in diagnostics_text
    assert "type RedactDataFn = Callable[[Mapping[str, object], set[str]], DiagnosticsValue]" in diagnostics_text
    assert "type ExtractDeviceSerialFn = Callable[[DeviceEntry], str | None]" in diagnostics_text
    assert "type MappingPayload = JsonObject" in _read("custom_components/lipro/core/api/command_api_service.py")
    assert "type QueryPayload = JsonObject" in status_fallback_text
    assert "def _build_query_payload(body_key: str, ids: list[str]) -> QueryPayload:" in status_fallback_text
    assert "mapping_result = self.require_mapping_response(path, result)" in transport_text
    assert "test_execute_request_rejects_non_mapping_json_payload" in transport_test_text


def test_phase94_governance_truth_registers_the_no_growth_guard() -> None:
    verification_text = _PHASE_VERIFICATION.read_text(encoding="utf-8")
    validation_text = _PHASE_VALIDATION.read_text(encoding="utf-8")
    verification_matrix_text = _VERIFICATION_MATRIX.read_text(encoding="utf-8")
    file_matrix_text = _FILE_MATRIX.read_text(encoding="utf-8")

    assert "# Phase 94 Verification" in verification_text
    assert "v1.26 active route / Phase 95 execution-ready / latest archived baseline = v1.25" in verification_text
    assert "tests/meta/test_phase94_typed_boundary_guards.py" in verification_text
    assert "# Phase 94 Validation Contract" in validation_text
    assert "$gsd-execute-phase 95" in validation_text
    assert "## Phase 94 Typed Payload Contraction and Domain-Bag Narrowing" in verification_matrix_text
    assert "tests/meta/test_phase94_typed_boundary_guards.py" in verification_matrix_text
    assert "focused no-regrowth guard home for Phase 94 typed payload contraction" in file_matrix_text
