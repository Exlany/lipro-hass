"""Phase 140 governance source freshness guards."""

from __future__ import annotations

import json
from pathlib import Path
import re

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot

_ROOT = repo_root(Path(__file__))
_CHANGELOG = _ROOT / "CHANGELOG.md"
_RUNBOOK = _ROOT / "docs" / "MAINTAINER_RELEASE_RUNBOOK.md"
_DEVELOPER_ARCHITECTURE = _ROOT / "docs" / "developer_architecture.md"
_VERIFICATION = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
_GOVERNANCE_REGISTRY = _ROOT / ".planning" / "baseline" / "GOVERNANCE_REGISTRY.json"
_TESTING = _ROOT / ".planning" / "codebase" / "TESTING.md"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_RESIDUAL = _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
_REMEDIATION = _ROOT / ".planning" / "reviews" / "V1_41_REMEDIATION_CHARTER.md"

_STALE_VERIFICATION_TOKENS = (
    "tests/meta/test_governance_bootstrap_smoke.py",
    "tests/meta/test_governance_route_handoff_smoke.py",
)
_CURRENT_ROUTE = "v1.44 active milestone route / Phase 143 planned / execution-ready / latest archived baseline = v1.43"
_PHASE140_GUARD = "tests/meta/test_phase140_governance_source_freshness_guards.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_section(text: str, start: str, end: str) -> str:
    match = re.search(
        rf"{re.escape(start)}\n(?P<body>.*?)(?:\n{re.escape(end)}|\Z)",
        text,
        flags=re.DOTALL,
    )
    assert match is not None
    return match.group("body")


def test_phase140_release_governance_proof_lanes_drop_stale_paths() -> None:
    verification_text = _read(_VERIFICATION)
    remediation_text = _read(_REMEDIATION)
    verification_scope = _extract_section(
        verification_text,
        "## Phase 140 Exit Contract",
        "## Phase 141 Exit Contract",
    )
    remediation_scope = _extract_section(
        remediation_text,
        "### WS-05 Governance Derivation Cost Reduction",
        "### WS-06 Observability & Log-Safety Follow-Up",
    )

    for text in (verification_scope, remediation_scope):
        for token in _STALE_VERIFICATION_TOKENS:
            assert token not in text

    for token in (
        "tests/meta/test_governance_release_docs.py",
        "tests/meta/test_governance_release_continuity.py",
        "tests/meta/test_governance_release_contract.py",
        _PHASE140_GUARD,
    ):
        assert token in verification_scope
        assert token in remediation_scope


def test_phase140_changelog_keeps_public_release_summary_scope() -> None:
    changelog_text = _read(_CHANGELOG)
    match = re.search(
        r"## \[Unreleased\]（未发布）\n(?P<body>.*?)(?:\n## \[1\.0\.0\] - 2026-02-08)",
        changelog_text,
        flags=re.DOTALL,
    )
    assert match is not None
    body = match.group("body")
    for token in (
        ".planning/",
        "GOVERNANCE_REGISTRY.json",
        "$gsd-",
        "Phase 124",
        "Phase 125",
    ):
        assert token not in body


def test_phase140_runbook_keeps_access_mode_honesty() -> None:
    runbook_text = _read(_RUNBOOK)
    assert "reachable in the current access mode" in runbook_text


def test_phase140_ledgers_registry_and_guides_register_predecessor_guard_chain() -> None:
    verification_text = _read(_VERIFICATION)
    testing_text = _read(_TESTING)
    file_matrix_text = _read(_FILE_MATRIX)
    residual_text = _read(_RESIDUAL)
    developer_text = _read(_DEVELOPER_ARCHITECTURE)

    assert_testing_inventory_snapshot(testing_text)

    registry = json.loads(_read(_GOVERNANCE_REGISTRY))
    planning_route = registry["planning_route"]
    active_milestone = planning_route["active_milestone"]
    latest_archived = planning_route["latest_archived"]
    bootstrap = planning_route["bootstrap"]

    assert active_milestone is not None
    assert active_milestone["version"] == "v1.44"
    assert active_milestone["phase"] == "143"
    assert latest_archived["version"] == "v1.43"
    assert latest_archived["phase"] == "141"
    assert (
        latest_archived["phase_title"]
        == "control/runtime hotspot narrowing and device aggregate hardening"
    )
    assert bootstrap["current_route"] == _CURRENT_ROUTE
    assert bootstrap["default_next_command"] == "$gsd-execute-phase 143"

    for text in (verification_text, testing_text, file_matrix_text, residual_text):
        assert "Phase 140" in text
        assert _PHASE140_GUARD in text

    assert _CURRENT_ROUTE in developer_text
    assert "Phase 140" not in developer_text
