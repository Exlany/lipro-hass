"""Shared builders and cached snapshots for governance follow-up route tests."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from .conftest import _ROOT


@dataclass(frozen=True, slots=True)
class PlanningDocsSnapshot:
    """Cached planning/governance documents used by follow-up route suites."""

    milestones: str
    roadmap: str
    requirements: str
    project: str
    state: str
    residual: str | None = None
    kill: str | None = None


@dataclass(frozen=True, slots=True)
class RequirementTrace:
    """One requirement trace row reused across follow-up route guards."""

    requirement_id: str
    phase: str
    status: str = "Complete"
    checked: bool = True

    @property
    def checkbox_marker(self) -> str:
        mark = "x" if self.checked else " "
        return f"- [{mark}] **{self.requirement_id}**"

    @property
    def table_marker(self) -> str:
        return f"| {self.requirement_id} | Phase {self.phase} | {self.status} |"


@dataclass(frozen=True, slots=True)
class CoverageSnapshot:
    """Coverage arithmetic markers reused across milestone follow-up guards."""

    label: str
    total: int
    mapped: int | None = None
    complete: int | None = None
    pending: int | None = None

    def markers(self) -> tuple[str, ...]:
        markers = [f"- {self.label}: {self.total} total"]
        if self.mapped is not None:
            markers.append(f"- Current mapped: {self.mapped}")
        if self.complete is not None:
            markers.append(f"- Current complete: {self.complete}")
        if self.pending is not None:
            markers.append(f"- Current pending: {self.pending}")
        return tuple(markers)


@lru_cache(maxsize=2)
def load_planning_docs_snapshot(*, include_reviews: bool = False) -> PlanningDocsSnapshot:
    """Load the shared planning texts once for a test module."""
    planning_root = _ROOT / ".planning"
    snapshot = PlanningDocsSnapshot(
        milestones=(planning_root / "MILESTONES.md").read_text(encoding="utf-8"),
        roadmap=(planning_root / "ROADMAP.md").read_text(encoding="utf-8"),
        requirements=(planning_root / "REQUIREMENTS.md").read_text(encoding="utf-8"),
        project=(planning_root / "PROJECT.md").read_text(encoding="utf-8"),
        state=(planning_root / "STATE.md").read_text(encoding="utf-8"),
    )
    if not include_reviews:
        return snapshot
    reviews_root = planning_root / "reviews"
    return PlanningDocsSnapshot(
        milestones=snapshot.milestones,
        roadmap=snapshot.roadmap,
        requirements=snapshot.requirements,
        project=snapshot.project,
        state=snapshot.state,
        residual=(reviews_root / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8"),
        kill=(reviews_root / "KILL_LIST.md").read_text(encoding="utf-8"),
    )


def assert_contains_all(text: str, *needles: str) -> None:
    """Assert that one text contains every expected token."""
    for needle in needles:
        assert needle in text


def assert_not_contains_any(text: str, *needles: str) -> None:
    """Assert that one text does not contain any forbidden token."""
    for needle in needles:
        assert needle not in text


def requirement_checkbox_markers(*traces: RequirementTrace) -> tuple[str, ...]:
    """Return checkbox markers for the provided requirement traces."""
    return tuple(trace.checkbox_marker for trace in traces)


def requirement_table_markers(*traces: RequirementTrace) -> tuple[str, ...]:
    """Return table-row markers for the provided requirement traces."""
    return tuple(trace.table_marker for trace in traces)


__all__ = [
    "CoverageSnapshot",
    "PlanningDocsSnapshot",
    "RequirementTrace",
    "assert_contains_all",
    "assert_not_contains_any",
    "load_planning_docs_snapshot",
    "requirement_checkbox_markers",
    "requirement_table_markers",
]
