"""Focused no-regrowth guards for Phase 87 assurance hotspot topicization."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))

_DIAGNOSTICS_ROOT = _ROOT / "tests" / "core" / "api" / "test_api_diagnostics_service.py"
_PROTOCOL_ROOT = _ROOT / "tests" / "core" / "api" / "test_protocol_contract_matrix.py"
_MQTT_ROOT = _ROOT / "tests" / "core" / "coordinator" / "runtime" / "test_mqtt_runtime.py"

_EXPECTED_DIAGNOSTICS_TOPICS = {
    "tests/core/api/test_api_diagnostics_service_cloud.py",
    "tests/core/api/test_api_diagnostics_service_history.py",
    "tests/core/api/test_api_diagnostics_service_ota.py",
    "tests/core/api/test_api_diagnostics_service_support.py",
}
_EXPECTED_PROTOCOL_TOPICS = {
    "tests/core/api/test_protocol_contract_boundary_decoders.py",
    "tests/core/api/test_protocol_contract_facade_runtime.py",
    "tests/core/api/test_protocol_contract_fixture_authority.py",
}
_EXPECTED_MQTT_TOPICS = {
    "tests/core/coordinator/runtime/test_mqtt_runtime_connection.py",
    "tests/core/coordinator/runtime/test_mqtt_runtime_init.py",
    "tests/core/coordinator/runtime/test_mqtt_runtime_messages.py",
    "tests/core/coordinator/runtime/test_mqtt_runtime_notifications.py",
    "tests/core/coordinator/runtime/test_mqtt_runtime_support.py",
}


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def _test_function_names(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    ]


def test_phase87_roots_stay_thin_and_honest() -> None:
    diagnostics_text = _DIAGNOSTICS_ROOT.read_text(encoding="utf-8")
    protocol_text = _PROTOCOL_ROOT.read_text(encoding="utf-8")
    mqtt_text = _MQTT_ROOT.read_text(encoding="utf-8")

    assert _line_count(_DIAGNOSTICS_ROOT) <= 5
    assert _test_function_names(_DIAGNOSTICS_ROOT) == []
    assert "Thin anchor" in diagnostics_text

    assert _line_count(_PROTOCOL_ROOT) <= 15
    assert _test_function_names(_PROTOCOL_ROOT) == [
        "test_lipro_protocol_facade_is_available_as_unified_protocol_root"
    ]
    assert "Thin anchor" in protocol_text

    assert _line_count(_MQTT_ROOT) <= 12
    assert _test_function_names(_MQTT_ROOT) == []
    for token in (
        "from .test_mqtt_runtime_connection import *",
        "from .test_mqtt_runtime_init import *",
        "from .test_mqtt_runtime_messages import *",
        "from .test_mqtt_runtime_notifications import *",
    ):
        assert token in mqtt_text


def test_phase87_topicized_suite_inventory_exists() -> None:
    for relative_path in (
        *_EXPECTED_DIAGNOSTICS_TOPICS,
        *_EXPECTED_PROTOCOL_TOPICS,
        *_EXPECTED_MQTT_TOPICS,
    ):
        assert (_ROOT / relative_path).exists(), f"missing Phase 87 topical suite: {relative_path}"


def test_phase87_file_matrix_freezes_topicized_suite_homes() -> None:
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )

    assert "**Python files total:** 682" in file_matrix_text
    for token in (
        "| `tests/core/api/test_api_diagnostics_service.py` | Protocol | Phase 2 / 85 / 87 | 保留 | thin anchor after diagnostics API hotspot topicization |",
        "| `tests/core/api/test_protocol_contract_matrix.py` | Protocol | Phase 2 / 85 / 87 | 保留 | thin anchor after protocol-contract hotspot topicization |",
        "| `tests/core/coordinator/runtime/test_mqtt_runtime.py` | Runtime | Phase 5 / 6 / 85 / 87 | 保留 | thin shell after MQTT runtime hotspot topicization |",
        "| `tests/core/api/test_api_diagnostics_service_support.py` | Protocol | Phase 87 | 保留 | local inward helper home for diagnostics API topical suites |",
        "| `tests/core/coordinator/runtime/test_mqtt_runtime_support.py` | Runtime | Phase 87 | 保留 | local support helper home for topicized MQTT runtime suites |",
        "| `tests/meta/test_phase87_assurance_hotspot_guards.py` | Assurance | Phase 87 | 保留 | focused no-regrowth guard home for Phase 87 assurance hotspot topicization |",
    ):
        assert token in file_matrix_text

    for relative_path in (
        *_EXPECTED_DIAGNOSTICS_TOPICS,
        *_EXPECTED_PROTOCOL_TOPICS,
        *_EXPECTED_MQTT_TOPICS,
    ):
        assert f"| `{relative_path}` |" in file_matrix_text


def test_phase87_verification_and_residual_truth_match_closeout() -> None:
    verification_text = (_ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 87 Assurance Hotspot Decomposition / No-Regrowth Guards" in verification_text
    for command in (
        "uv run pytest -q tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_diagnostics_service_*.py",
        "uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_contract_*.py",
        "uv run pytest -q tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/runtime/test_mqtt_runtime_*.py",
        "uv run pytest -q tests/meta/test_phase85_terminal_audit_route_guards.py tests/meta/test_phase70_governance_hotspot_guards.py tests/meta/test_phase87_assurance_hotspot_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py",
    ):
        assert command in verification_text

    assert "| giant assurance carriers (`test_api_diagnostics_service.py`, `test_protocol_contract_matrix.py`, `test_mqtt_runtime.py`) | Assurance | closed in Phase 87 | Phase 87 |" in residual_text
    assert "## Phase 87 Residual Delta" in residual_text
    assert "route next | Phase 87" not in residual_text
