"""Milestone-archive snapshot ordering and historical-route guards."""
from __future__ import annotations

import re

from .governance_contract_helpers import _ROOT
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_ROUTE_MODE,
    HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH,
    HISTORICAL_CLOSEOUT_ROUTE_TRUTH,
    LATEST_ARCHIVED_MILESTONE,
    LATEST_ARCHIVED_MILESTONE_NAME,
)


def test_milestone_archive_snapshots_exist_and_are_referenced() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")

    archive_paths = (
        _ROOT / ".planning" / "milestones" / "v1.1-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.1-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.2-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.2-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.4-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.4-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.5-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.5-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.6-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.6-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.12-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.12-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.13-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.13-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.14-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.14-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.15-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.15-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.16-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.16-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.17-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.17-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.21-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.21-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.22-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.22-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.23-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.23-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.24-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.24-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.25-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.25-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.26-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.26-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.27-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.27-REQUIREMENTS.md",
        _ROOT / ".planning" / "milestones" / "v1.28-ROADMAP.md",
        _ROOT / ".planning" / "milestones" / "v1.28-REQUIREMENTS.md",
    )

    for path in archive_paths:
        assert path.exists()

    for needle in (
        "v1.1-ROADMAP.md",
        "v1.1-REQUIREMENTS.md",
        "v1.2-ROADMAP.md",
        "v1.2-REQUIREMENTS.md",
        "v1.4-ROADMAP.md",
        "v1.4-REQUIREMENTS.md",
        "v1.5-ROADMAP.md",
        "v1.5-REQUIREMENTS.md",
        "v1.6-ROADMAP.md",
        "v1.6-REQUIREMENTS.md",
        "v1.12-ROADMAP.md",
        "v1.12-REQUIREMENTS.md",
        "v1.13-ROADMAP.md",
        "v1.13-REQUIREMENTS.md",
        "v1.14-ROADMAP.md",
        "v1.14-REQUIREMENTS.md",
        "v1.15-ROADMAP.md",
        "v1.15-REQUIREMENTS.md",
        "v1.16-ROADMAP.md",
        "v1.16-REQUIREMENTS.md",
        "v1.17-ROADMAP.md",
        "v1.17-REQUIREMENTS.md",
        "v1.21-ROADMAP.md",
        "v1.21-REQUIREMENTS.md",
        "v1.22-ROADMAP.md",
        "v1.22-REQUIREMENTS.md",
        "v1.23-ROADMAP.md",
        "v1.23-REQUIREMENTS.md",
        "v1.24-ROADMAP.md",
        "v1.24-REQUIREMENTS.md",
        "v1.25-ROADMAP.md",
        "v1.25-REQUIREMENTS.md",
        "v1.26-ROADMAP.md",
        "v1.26-REQUIREMENTS.md",
        "v1.27-ROADMAP.md",
        "v1.27-REQUIREMENTS.md",
        "v1.28-ROADMAP.md",
        "v1.28-REQUIREMENTS.md",
    ):
        assert needle in roadmap_text
        assert needle in requirements_text or needle in project_text or needle in milestones_text

    assert "v1.16-MILESTONE-AUDIT.md" in state_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in state_text
    assert f"**Current mode:** `{CURRENT_ROUTE_MODE}`" in state_text
    assert "archived / evidence-ready" in milestones_text
    assert "archived snapshots created / handoff-ready" in milestones_text
    assert "revalidated 2026-03-17" in milestones_text
    assert ".planning/v1.4-MILESTONE-AUDIT.md" in milestones_text
    assert ".planning/v1.5-MILESTONE-AUDIT.md" in milestones_text
    assert "V1_4_EVIDENCE_INDEX.md" in milestones_text
    assert "V1_5_EVIDENCE_INDEX.md" in milestones_text
    assert ".planning/v1.5-MILESTONE-AUDIT.md" in milestones_text
    assert "V1_5_EVIDENCE_INDEX.md" in milestones_text

    v1_1_archive_text = (
        _ROOT / ".planning" / "milestones" / "v1.1-ROADMAP.md"
    ).read_text(encoding="utf-8")

    assert "待执行 milestone archival" not in v1_1_archive_text
    assert "当当前里程碑完成时，应能同时回答以下问题：" in project_text

def test_machine_readable_roadmap_latest_archived_entry_comes_first() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    archived_match = re.search(r"^-\s+✅\s+\*\*v(\d+(?:\.\d+)+)\s+([^*]+)\*\*", roadmap_text, re.MULTILINE)
    assert archived_match is not None
    assert archived_match.group(1) == LATEST_ARCHIVED_MILESTONE.removeprefix("v")
    assert archived_match.group(2).strip() == LATEST_ARCHIVED_MILESTONE_NAME

def test_machine_readable_milestones_latest_archived_baseline_comes_first() -> None:
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(encoding="utf-8")

    shipped_match = re.search(
        r"^##\s+(v[\d.]+)\s+(.+?)\s+\(Shipped:",
        milestones_text,
        re.MULTILINE,
    )
    assert shipped_match is not None
    assert shipped_match.group(1) == LATEST_ARCHIVED_MILESTONE
    assert shipped_match.group(2).strip() == LATEST_ARCHIVED_MILESTONE_NAME

def test_historical_route_truth_is_demoted_to_archive_context() -> None:
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(
        encoding="utf-8"
    )
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )

    for text in (milestones_text, roadmap_text, requirements_text):
        assert "current governance state =" not in text
        assert "当前治理状态已切换为" not in text
        assert "当前治理状态现已切换为" not in text
        assert "live governance state" not in text

    assert HISTORICAL_CLOSEOUT_ROUTE_TRUTH in milestones_text
    assert HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH in milestones_text
    assert HISTORICAL_CLOSEOUT_ROUTE_TRUTH in roadmap_text
    assert HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH in roadmap_text
    assert HISTORICAL_CLOSEOUT_ROUTE_TRUTH in requirements_text
    assert HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH in requirements_text
