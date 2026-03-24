"""Shared helpers for governance contract tests."""

from __future__ import annotations

from pathlib import Path


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
