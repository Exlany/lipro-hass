"""Governance closeout helper home and promoted-asset manifest guards."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re

from scripts.check_file_matrix import repo_root

from .conftest import _load_frontmatter


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


_ROOT = repo_root(Path(__file__))

_PROMOTED_PHASE_ASSETS = _ROOT / ".planning" / "reviews" / "PROMOTED_PHASE_ASSETS.md"


@lru_cache(maxsize=1)
def _load_promoted_phase_assets() -> dict[str, frozenset[str]]:
    manifest = _load_frontmatter(_PROMOTED_PHASE_ASSETS)
    phases = manifest["phases"]
    assert isinstance(phases, dict)

    promoted_assets: dict[str, frozenset[str]] = {}
    for phase_dir_name, filenames in phases.items():
        assert isinstance(phase_dir_name, str)
        assert isinstance(filenames, list)
        assert filenames
        promoted_assets[phase_dir_name] = frozenset(filenames)

    return promoted_assets


def _assert_promoted_phase_assets(phase_dir_name: str, *filenames: str) -> None:
    promoted_assets = _load_promoted_phase_assets()
    assert phase_dir_name in promoted_assets

    phase_root = _ROOT / ".planning" / "phases" / phase_dir_name
    for filename in filenames:
        assert filename in promoted_assets[phase_dir_name]
        assert (phase_root / filename).exists()


def _assert_promoted_closeout_package(roadmap_text: str, *filenames: str) -> None:
    package_listing = ", ".join(f"`{filename}`" for filename in filenames)
    assert f"**Promoted closeout package**: {package_listing}" in roadmap_text


def _assert_exact_promoted_phase_assets(phase_dir_name: str, *filenames: str) -> None:
    promoted_assets = _load_promoted_phase_assets()
    assert phase_dir_name in promoted_assets
    assert promoted_assets[phase_dir_name] == frozenset(filenames)

    phase_root = _ROOT / ".planning" / "phases" / phase_dir_name
    for filename in filenames:
        assert (phase_root / filename).exists()


def _assert_phase_assets_not_promoted(phase_dir_name: str, *filenames: str) -> None:
    promoted_assets = _load_promoted_phase_assets().get(phase_dir_name, frozenset())

    for filename in filenames:
        assert filename not in promoted_assets


def test_promoted_phase_assets_manifest_enforces_explicit_ci_evidence() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")
    manifest_text = _PROMOTED_PHASE_ASSETS.read_text(encoding="utf-8")
    manifest = _load_frontmatter(_PROMOTED_PHASE_ASSETS)
    policy = manifest["policy"]

    assert isinstance(policy, dict)
    assert policy["default_identity"] == "execution-trace"
    assert ".planning/ROADMAP.md" in policy["promotion_sources"]
    assert ".planning/baseline/VERIFICATION_MATRIX.md" in policy["promotion_sources"]
    assert ".planning/milestones/*.md" in policy["promotion_sources"]
    assert ".planning/reviews/*.md" in policy["promotion_sources"]
    assert ".planning/reviews/PROMOTED_PHASE_ASSETS.md" in roadmap_text
    assert ".planning/reviews/PROMOTED_PHASE_ASSETS.md" in state_text
    assert "promoted phase evidence allowlist" in authority_text
    assert ".planning/reviews/PROMOTED_PHASE_ASSETS.md" in verification_text
    assert "未被 allowlist 显式列出的 `*-SUMMARY.md`、`*-VERIFICATION.md`、`*-VALIDATION.md`" in manifest_text

    for phase_dir_name, filenames in _load_promoted_phase_assets().items():
        for filename in filenames:
            assert not filename.endswith(
                (
                    "-PLAN.md",
                    "-CONTEXT.md",
                    "-RESEARCH.md",
                    "-PRD.md",
                    "-ARCHITECTURE.md",
                    "-UAT.md",
                )
            )
            assert (
                _ROOT / ".planning" / "phases" / phase_dir_name / filename
            ).exists()

    _assert_phase_assets_not_promoted(
        "15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through",
        "15-CONTEXT.md",
        "15-01-PLAN.md",
    )
    _assert_phase_assets_not_promoted(
        "24-final-milestone-audit-archive-readiness-and-v1-3-handoff-prep",
        "24-CONTEXT.md",
        "24-03-PLAN.md",
    )
    _assert_phase_assets_not_promoted(
        "30-protocol-control-typed-contract-tightening",
        "30-VALIDATION.md",
        "30-01-SUMMARY.md",
    )
    _assert_phase_assets_not_promoted(
        "32-truth-convergence-gate-honesty-and-quality-10-closeout",
        "32-CONTEXT.md",
        "32-RESEARCH.md",
        "32-01-PLAN.md",
        "32-VALIDATION.md",
    )
    _assert_phase_assets_not_promoted(
        "34-continuity-and-hard-release-gates",
        "34-01-PLAN.md",
        "34-VALIDATION.md",
    )
    _assert_phase_assets_not_promoted(
        "39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition",
        "39-PRD.md",
        "39-CONTEXT.md",
        "39-01-PLAN.md",
        "39-02-PLAN.md",
        "39-03-PLAN.md",
        "39-04-PLAN.md",
        "39-05-PLAN.md",
        "39-06-PLAN.md",
        "39-VALIDATION.md",
    )
    _assert_phase_assets_not_promoted(
        "40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification",
        "40-CONTEXT.md",
        "40-01-PLAN.md",
        "40-02-PLAN.md",
        "40-03-PLAN.md",
        "40-04-PLAN.md",
        "40-05-PLAN.md",
        "40-06-PLAN.md",
        "40-07-PLAN.md",
        "40-VALIDATION.md",
    )
    _assert_phase_assets_not_promoted(
        "43-control-services-boundary-decoupling-and-typed-runtime-access",
        "43-CONTEXT.md",
        "43-RESEARCH.md",
        "43-01-PLAN.md",
        "43-02-PLAN.md",
        "43-03-PLAN.md",
        "43-04-PLAN.md",
        "43-01-SUMMARY.md",
        "43-02-SUMMARY.md",
        "43-03-SUMMARY.md",
        "43-04-SUMMARY.md",
    )


def test_v1_20_promoted_allowlist_exactly_matches_audited_closeout_bundles() -> None:
    _assert_exact_promoted_phase_assets(
        "72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement",
        "72-01-SUMMARY.md",
        "72-02-SUMMARY.md",
        "72-03-SUMMARY.md",
        "72-04-SUMMARY.md",
        "72-VERIFICATION.md",
        "72-VALIDATION.md",
    )
    _assert_exact_promoted_phase_assets(
        "73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization",
        "73-01-SUMMARY.md",
        "73-02-SUMMARY.md",
        "73-03-SUMMARY.md",
        "73-04-SUMMARY.md",
        "73-VERIFICATION.md",
        "73-VALIDATION.md",
    )
    _assert_exact_promoted_phase_assets(
        "74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout",
        "74-01-SUMMARY.md",
        "74-02-SUMMARY.md",
        "74-03-SUMMARY.md",
        "74-04-SUMMARY.md",
        "74-VERIFICATION.md",
        "74-VALIDATION.md",
    )


def test_v1_20_promoted_allowlist_does_not_widen_into_execution_traces() -> None:
    for phase_dir_name, prefix in (
        ("72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement", "72"),
        ("73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization", "73"),
        ("74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout", "74"),
    ):
        _assert_phase_assets_not_promoted(phase_dir_name, f"{prefix}-CONTEXT.md", f"{prefix}-RESEARCH.md", f"{prefix}-01-PLAN.md")

    _assert_phase_assets_not_promoted(
        "75-access-mode-truth-closure-evidence-promotion-formalization-and-thin-adapter-typing-hardening",
        "75-CONTEXT.md",
        "75-RESEARCH.md",
        "75-01-PLAN.md",
        "75-01-SUMMARY.md",
        "75-VERIFICATION.md",
        "75-VALIDATION.md",
    )
