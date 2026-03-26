"""Shared helpers for governance contract tests."""

from __future__ import annotations

from pathlib import Path
import re

from .conftest import _ROOT
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_MILESTONE_HEADER,
    CURRENT_MILESTONE_ROADMAP_HEADER,
    CURRENT_MILESTONE_STATE_LABEL,
    CURRENT_MILESTONE_STATUS,
    CURRENT_PHASE_HEADING,
    CURRENT_ROUTE,
    CURRENT_ROUTE_MODE,
    LATEST_ARCHIVED_AUDIT_PATH,
    LATEST_ARCHIVED_EVIDENCE_LABEL,
    LATEST_ARCHIVED_EVIDENCE_PATH,
    LATEST_ARCHIVED_MILESTONE_STATUS,
    LATEST_ARCHIVED_PROJECT_HEADER,
    PREVIOUS_ARCHIVED_PROJECT_HEADER,
    assert_machine_readable_route_contracts,
)


def assert_pull_only_evidence_index(evidence_index: Path, *tokens: str) -> str:
    """Assert one evidence index exists and contains the expected pull-only tokens."""
    assert evidence_index.exists()
    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    for token in tokens:
        assert token in evidence_text
    return evidence_text


def assert_runbook_points_to_latest_evidence(
    runbook_text: str,
    evidence_filename: str,
    *,
    deprecated: tuple[str, ...] = (),
) -> None:
    """Assert the runbook points at the latest archive evidence pointer only."""
    assert evidence_filename in runbook_text
    for stale in deprecated:
        assert stale not in runbook_text


def _assert_state_keeps_forward_progress_commands(state_text: str) -> None:
    assert "## Recommended Next Command" in state_text
    assert "$gsd-progress" in state_text
    assert (
        "$gsd-plan-milestone-gaps" in state_text
        or "$gsd-new-milestone" in state_text
        or re.search(r"\$gsd-(?:plan|execute)-phase \d+(?:\.\d+)?", state_text)
        or re.search(r"\$gsd-complete-milestone v\d+\.\d+", state_text)
    )


def _assert_project_allows_post_v1_4_next_step(project_text: str) -> None:
    assert (
        "**Default next step:** `$gsd-new-milestone`" in project_text
        or re.search(r"\*\*Default next step:\*\* `\$gsd-plan-phase \d+(?:\.\d+)?`", project_text)
        is not None
        or re.search(
            r"\*\*Default next step:\*\* `\$gsd-plan-phase \d+(?:\.\d+)?` → `\$gsd-execute-phase \d+(?:\.\d+)?`",
            project_text,
        )
        is not None
        or re.search(
            r"\*\*Default next step:\*\* `\$gsd-execute-phase \d+(?:\.\d+)?`",
            project_text,
        )
        is not None
        or re.search(
            r"\*\*Default next step:\*\* `\$gsd-complete-milestone v\d+\.\d+`",
            project_text,
        )
        is not None
    )


def _assert_state_reflects_post_v1_4_continuation(state_text: str) -> None:
    assert (
        "`Phase 39 complete`" in state_text
        or re.search(
            r"Phase \d+(?:\.\d+)? (?:execution-ready|complete|routing-ready|planning-ready)",
            state_text,
        )
        or re.search(r"v1\.\d+ archived", state_text)
        or re.search(r"\$gsd-(?:plan|execute)-phase \d+(?:\.\d+)?", state_text)
        or re.search(r"\$gsd-complete-milestone v\d+\.\d+", state_text)
        or "$gsd-new-milestone" in state_text
    )


def _assert_current_route_truth(
    project_text: str,
    roadmap_text: str,
    state_text: str,
) -> None:
    assert_machine_readable_route_contracts()
    assert (
        f"**Current route:** `{CURRENT_ROUTE}`；{LATEST_ARCHIVED_EVIDENCE_LABEL} = "
        f"`{LATEST_ARCHIVED_EVIDENCE_PATH}`."
    ) in project_text
    assert CURRENT_MILESTONE_HEADER in project_text
    assert LATEST_ARCHIVED_PROJECT_HEADER in project_text
    assert PREVIOUS_ARCHIVED_PROJECT_HEADER in project_text
    assert f"**Current status:** `{CURRENT_MILESTONE_STATUS}`" in project_text
    assert f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`" in project_text
    assert CURRENT_MILESTONE_ROADMAP_HEADER in roadmap_text
    assert f"**Milestone status:** `{CURRENT_MILESTONE_STATUS}`" in roadmap_text
    assert f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`" in roadmap_text
    assert CURRENT_PHASE_HEADING in roadmap_text
    assert f"**Current milestone:** `{CURRENT_MILESTONE_STATE_LABEL}`" in state_text
    assert f"**Current mode:** `{CURRENT_ROUTE_MODE}`" in state_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in state_text
    assert LATEST_ARCHIVED_AUDIT_PATH in state_text
    assert LATEST_ARCHIVED_EVIDENCE_PATH in project_text
    assert LATEST_ARCHIVED_EVIDENCE_PATH in state_text


def _assert_latest_archived_route_truth(
    project_text: str,
    roadmap_text: str,
    state_text: str,
) -> None:
    _assert_current_route_truth(project_text, roadmap_text, state_text)
    assert f"**Current status:** `{LATEST_ARCHIVED_MILESTONE_STATUS}`" in project_text
    assert LATEST_ARCHIVED_PROJECT_HEADER in project_text


def _assert_public_docs_hide_internal_route_story(
    docs_text: str,
    *extra_forbidden_tokens: str,
) -> None:
    for token in (
        CURRENT_ROUTE,
        LATEST_ARCHIVED_EVIDENCE_PATH,
        "Current governance status",
        "$gsd-plan-phase",
        *extra_forbidden_tokens,
    ):
        assert token not in docs_text


__all__ = [
    '_ROOT',
    '_assert_current_route_truth',
    '_assert_latest_archived_route_truth',
    '_assert_project_allows_post_v1_4_next_step',
    '_assert_public_docs_hide_internal_route_story',
    '_assert_state_keeps_forward_progress_commands',
    '_assert_state_reflects_post_v1_4_continuation',
    'assert_pull_only_evidence_index',
    'assert_runbook_points_to_latest_evidence',
]
