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
    CURRENT_ROUTE_FOCUSED_GUARDS,
    CURRENT_ROUTE_MODE,
    HAS_ACTIVE_MILESTONE,
    LATEST_ARCHIVED_AUDIT_PATH,
    LATEST_ARCHIVED_EVIDENCE_LABEL,
    LATEST_ARCHIVED_EVIDENCE_PATH,
    LATEST_ARCHIVED_PROJECT_HEADER,
    PREVIOUS_ARCHIVED_PROJECT_HEADER,
    TESTS_META_SUITE_COUNT,
    TESTS_PYTHON_FILE_COUNT,
    TESTS_RUNNABLE_FILE_COUNT,
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


def assert_current_route_focused_guards(text: str) -> None:
    """Assert one text mentions every current-route focused guard."""
    for guard in CURRENT_ROUTE_FOCUSED_GUARDS:
        assert guard in text


def assert_current_route_markers(*texts: str) -> None:
    """Assert each text carries the shared current-route and next-step markers."""
    for text in texts:
        assert CURRENT_ROUTE in text
        assert CURRENT_MILESTONE_DEFAULT_NEXT in text


def assert_testing_inventory_snapshot(testing_text: str) -> None:
    """Assert the derived testing map reflects the current repository inventory."""
    assert f"`{TESTS_PYTHON_FILE_COUNT}` Python files under `tests`" in testing_text
    assert f"`{TESTS_RUNNABLE_FILE_COUNT}` runnable `test_*.py` files" in testing_text
    assert f"`{TESTS_META_SUITE_COUNT}` meta suites" in testing_text


def _assert_state_keeps_forward_progress_commands(state_text: str) -> None:
    assert "## Recommended Next Command" in state_text
    assert "$gsd-progress" in state_text or CURRENT_MILESTONE_DEFAULT_NEXT in state_text
    assert (
        "$gsd-plan-milestone-gaps" in state_text
        or "$gsd-new-milestone" in state_text
        or re.search(r"\$gsd-discuss-phase \d+(?:\.\d+)?", state_text)
        or re.search(r"\$gsd-(?:plan|execute)-phase \d+(?:\.\d+)?", state_text)
        or re.search(r"\$gsd-complete-milestone v\d+\.\d+", state_text)
    )


def _assert_project_allows_post_v1_4_next_step(project_text: str) -> None:
    assert (
        "**Default next step:** `$gsd-new-milestone`" in project_text
        or re.search(
            r"\*\*Default next step:\*\* `\$gsd-discuss-phase \d+(?:\.\d+)?`",
            project_text,
        )
        is not None
        or re.search(
            r"\*\*Default next step:\*\* `\$gsd-discuss-phase \d+(?:\.\d+)?` → `\$gsd-plan-phase \d+(?:\.\d+)?`",
            project_text,
        )
        is not None
        or re.search(
            r"\*\*Default next step:\*\* `\$gsd-plan-phase \d+(?:\.\d+)?`", project_text
        )
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
    if HAS_ACTIVE_MILESTONE:
        assert LATEST_ARCHIVED_PROJECT_HEADER in project_text
    assert PREVIOUS_ARCHIVED_PROJECT_HEADER in project_text
    assert f"**Current status:** `{CURRENT_MILESTONE_STATUS}`" in project_text
    assert (
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`" in project_text
    )
    assert CURRENT_MILESTONE_ROADMAP_HEADER in roadmap_text
    assert f"**Milestone status:** `{CURRENT_MILESTONE_STATUS}`" in roadmap_text
    assert (
        f"**Default next command:** `{CURRENT_MILESTONE_DEFAULT_NEXT}`" in roadmap_text
    )
    if HAS_ACTIVE_MILESTONE:
        assert CURRENT_PHASE_HEADING in roadmap_text
    else:
        assert "## Phases" in roadmap_text
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


def assert_docs_readme_public_contract(docs_text: str) -> None:
    """Assert docs/README keeps the public-first-hop and community-health contract visible."""
    for token in (
        "## Public Fast Path",
        "README.md",
        "README_zh.md",
        "docs/README.md",
        "## Community-Health Contract",
        "CONTRIBUTING.md",
        "SUPPORT.md",
        "SECURITY.md",
        "Current access-mode truth",
        "conditional follow-up surfaces",
    ):
        assert token in docs_text


def assert_issue_docs_entry_contact_link(issue_config: dict[str, object]) -> None:
    """Assert issue contact links keep routing readers back to docs/README first."""
    contact_links = issue_config.get("contact_links")
    assert isinstance(contact_links, list)
    docs_link = next(
        link
        for link in contact_links
        if isinstance(link, dict)
        and isinstance(link.get("name"), str)
        and "Documentation" in link["name"]
    )
    assert isinstance(docs_link, dict)
    url = docs_link.get("url")
    about = docs_link.get("about")
    assert isinstance(url, str)
    assert isinstance(about, str)
    assert url.endswith("/docs/README.md")
    assert "docs-first route" in about
    assert "repository access" in about


__all__ = [
    "_ROOT",
    "_assert_current_route_truth",
    "_assert_latest_archived_route_truth",
    "_assert_project_allows_post_v1_4_next_step",
    "_assert_public_docs_hide_internal_route_story",
    "_assert_state_keeps_forward_progress_commands",
    "_assert_state_reflects_post_v1_4_continuation",
    "assert_current_route_focused_guards",
    "assert_current_route_markers",
    "assert_docs_readme_public_contract",
    "assert_issue_docs_entry_contact_link",
    "assert_pull_only_evidence_index",
    "assert_runbook_points_to_latest_evidence",
    "assert_testing_inventory_snapshot",
]
