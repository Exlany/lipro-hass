# Phase 80 PRD

## Title
Governance typing closure and final meta-suite hotspot topicization

## Why now

A fresh repository-wide audit after `Phase 79` shows production code is still on a healthy single north-star chain, but governance/tooling quality closure is not fully complete:

1. `uv run mypy --follow-imports=silent .` now reports governance/tooling regressions introduced by the recent topicization and registry split:
   - `scripts/check_file_matrix.py` imports `FileGovernanceRow` from `scripts.check_file_matrix_registry`, but the registry root does not explicitly export it;
   - `tests/meta/test_governance_route_handoff_smoke.py` and `tests/meta/governance_followup_route_current_milestones.py` still rely on weak `object`-typed JSON payload access.
2. Two governance test hotspots still carry oversized single-test bodies even after Phase 79:
   - `tests/meta/governance_followup_route_current_milestones.py`
   - `tests/meta/test_governance_release_contract.py`
3. The next maintainability pass should close these quality gaps without reopening production architecture work that currently shows lower ROI than the governance/tooling residuals above.

## Scope

This phase is limited to governance/tooling/test quality closure with direct maintenance payoff:

- restore touched-scope mypy cleanliness for governance/tooling roots and fast-path tests;
- reduce the remaining giant governance test bodies into smaller, clearer concern slices;
- freeze the resulting `Phase 80` truth so GSD routing returns to milestone closeout with no hidden quality debt.

## Non-goals

- No production behavior changes in `custom_components/` unless a touched typing seam absolutely requires it.
- No cosmetic splitting that does not materially improve failure localization or type honesty.
- No new second governance chain, no milestone archive promotion in this phase.

## Locked requirements

- **GOV-59**: live planning/governance truth must honestly record that `v1.21` now includes `Phase 80`, and after execution the route must resolve to `Phase 80 complete` with next step `$gsd-complete-milestone v1.21`.
- **TYP-22**: governance/tooling roots touched by Phase 79 must return to `mypy`-clean state using explicit exports and typed JSON/route helpers instead of `object` indexing.
- **HOT-36**: the remaining giant governance test bodies must stop being single giant carriers for workflow/follow-up truth; failure localization and edit ergonomics must improve measurably.
- **TST-25**: focused governance tests must preserve current route, archived baseline, release workflow, and follow-up truth after hotspot decomposition.
- **QLT-33**: touched scope must pass `mypy`, `ruff`, `check_file_matrix`, `check_architecture_policy`, focused pytest, and GSD fast-path proof.

## Acceptance criteria

1. `uv run mypy --follow-imports=silent .` passes with no Phase 79 regressions left.
2. `tests/meta/governance_followup_route_current_milestones.py` and `tests/meta/test_governance_release_contract.py` no longer depend on one oversized single-test body for their main concern.
3. `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/MILESTONES.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/{FILE_MATRIX,PROMOTED_PHASE_ASSETS,RESIDUAL_LEDGER,KILL_LIST}.md`, and `tests/meta/governance_current_truth.py` all tell the same `Phase 80` story.
4. Validation proves the new test topology and typing closure did not regress governance truth or file-matrix integrity.

## Suggested proof bundle

- `uv run mypy --follow-imports=silent .`
- `uv run ruff check tests/meta scripts`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run pytest -q tests/test_refactor_tools.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_version_sync.py`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 80`
