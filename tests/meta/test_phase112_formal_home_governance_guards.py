"""Phase 112 formal-home discoverability and governance-anchor guards."""

from __future__ import annotations

from pathlib import Path

from scripts.check_file_matrix import repo_root

from .governance_current_truth import (
    LATEST_ARCHIVED_AUDIT_PATH,
    LATEST_ARCHIVED_EVIDENCE_PATH,
)

_ROOT = repo_root(Path(__file__))
_DEVELOPER = _ROOT / "docs" / "developer_architecture.md"
_RUNBOOK = _ROOT / "docs" / "MAINTAINER_RELEASE_RUNBOOK.md"
_AUTHORITY = _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_TARGETED_HELPERS = (
    _ROOT / "custom_components" / "lipro" / "control" / "runtime_access_support_views.py",
    _ROOT / "custom_components" / "lipro" / "control" / "runtime_access_support_devices.py",
    _ROOT / "custom_components" / "lipro" / "control" / "developer_router_support.py",
)


def test_phase112_developer_architecture_uses_current_route_and_sanctioned_root_homes() -> None:
    text = _DEVELOPER.read_text(encoding="utf-8")

    assert "no active milestone route / latest archived baseline = v1.34" in text
    assert "docs/architecture_archive.md" in text
    for token in (
        "custom_components/lipro/runtime_infra.py",
        "custom_components/lipro/runtime_types.py",
        "custom_components/lipro/entry_auth.py",
        "Sanctioned Root-level Homes",
    ):
        assert token in text


def test_phase112_runbook_points_at_latest_archived_assets() -> None:
    text = _RUNBOOK.read_text(encoding="utf-8")

    assert LATEST_ARCHIVED_EVIDENCE_PATH in text
    assert LATEST_ARCHIVED_AUDIT_PATH in text
    assert "V1_28" not in text
    assert "v1.28-MILESTONE-AUDIT.md" not in text


def test_phase112_authority_matrix_separates_live_selectors_from_archive_chronology() -> None:
    text = _AUTHORITY.read_text(encoding="utf-8")

    assert "`.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`" in text
    assert "`.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`" not in text
    assert ".planning/reviews/V1_34_EVIDENCE_INDEX.md" in text


def test_phase112_file_matrix_registers_sanctioned_root_home_wording() -> None:
    text = _FILE_MATRIX.read_text(encoding="utf-8")

    assert "config-entry auth/bootstrap formal home" in text
    assert "shared runtime infra formal home" in text
    assert "`custom_components/lipro/runtime_types.py`" in text


def test_phase112_targeted_helpers_route_raw_coordinator_access_through_helpers() -> None:
    helper_texts = [path.read_text(encoding="utf-8") for path in _TARGETED_HELPERS]
    for path, text in zip(_TARGETED_HELPERS, helper_texts, strict=True):
        assert ".coordinator.coordinator" not in text, path.as_posix()
        assert ".coordinator.runtime_coordinator" not in text, path.as_posix()

    views_text, devices_text, developer_text = helper_texts
    assert "_get_entry_runtime_coordinator_support(" in views_text
    assert "_get_entry_runtime_coordinator_support(" in devices_text
    assert "iter_developer_runtime_coordinators as _iter_developer_runtime_coordinators" in developer_text
