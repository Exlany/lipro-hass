"""Phase 112 formal-home discoverability and governance-anchor guards."""

from __future__ import annotations

from pathlib import Path

from scripts.check_file_matrix import repo_root

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


def test_phase112_developer_architecture_uses_active_route_and_sanctioned_root_homes() -> None:
    text = _DEVELOPER.read_text(encoding="utf-8")

    assert "v1.31 active milestone route / starting from latest archived baseline = v1.30" not in text
    assert "no active milestone route / latest archived baseline = v1.31" in text
    assert "默认下一步保持为 `$gsd-new-milestone`" in text
    for token in (
        "custom_components/lipro/runtime_infra.py",
        "custom_components/lipro/runtime_types.py",
        "custom_components/lipro/entry_auth.py",
        "Sanctioned Root-level Homes",
    ):
        assert token in text


def test_phase112_runbook_points_at_v130_archived_assets() -> None:
    text = _RUNBOOK.read_text(encoding="utf-8")

    assert ".planning/reviews/V1_31_EVIDENCE_INDEX.md" in text
    assert ".planning/v1.31-MILESTONE-AUDIT.md" in text
    assert "V1_28" not in text
    assert "v1.28-MILESTONE-AUDIT.md" not in text


def test_phase112_authority_matrix_separates_live_selectors_from_archive_chronology() -> None:
    text = _AUTHORITY.read_text(encoding="utf-8")

    assert "`.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`" in text
    assert "`.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`" not in text
    assert ".planning/reviews/V1_31_EVIDENCE_INDEX.md" in text


def test_phase112_file_matrix_registers_sanctioned_root_home_wording() -> None:
    text = _FILE_MATRIX.read_text(encoding="utf-8")

    assert "config-entry auth/bootstrap formal home" in text
    assert "shared runtime infra formal home" in text
    assert "`custom_components/lipro/runtime_types.py`" in text


def test_phase112_targeted_helpers_drop_double_coordinator_wording() -> None:
    for path in _TARGETED_HELPERS:
        text = path.read_text(encoding="utf-8")
        assert ".coordinator.coordinator" not in text, path.as_posix()
        assert ".coordinator.runtime_coordinator" in text, path.as_posix()
