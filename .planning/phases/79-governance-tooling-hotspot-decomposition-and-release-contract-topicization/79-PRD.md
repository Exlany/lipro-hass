# Phase 79 PRD

## Title
Governance tooling hotspot decomposition and release-contract topicization

## Why now

A repository-wide audit shows that production code is currently on a healthy single north-star chain with no newly registered active residual family. The highest remaining maintenance cost now sits in governance/tooling hotspots that are still correct but too dense:

1. `scripts/check_file_matrix_registry.py` is the largest non-test Python file in the repository and still carries the only active `C901` hit in the local complexity sweep.
2. `tests/meta/test_governance_release_contract.py` concentrates multiple concerns (CI/release workflow, docs, support/security/continuity, release identity) into one giant suite, which hurts failure localization and future editing ergonomics.
3. Current route truth must remain honest after this extra maintainability pass: once the phase is complete, `v1.21` should return to milestone closeout-ready with the next step fixed to `$gsd-complete-milestone v1.21`.

## Scope

This phase is intentionally limited to governance/tooling/test maintainability work with direct long-term payoff:

- decompose file-matrix registry classification logic into smaller, explicit, table-driven or helper-backed pieces;
- topicize release-contract regression coverage into clearer concern-oriented homes;
- update live governance docs/tests/review assets so the new phase becomes the formal current story rather than an undocumented afterthought.

## Non-goals

- No production behavior changes in `custom_components/` unless strictly required by touched tooling/tests.
- No new public surfaces, no new second governance chain, no milestone archive promotion in this phase.
- No cosmetic splitting without measurable maintainability gain.

## Locked requirements

- **GOV-58**: live planning/governance truth must honestly record that `v1.21` now includes `Phase 79`, and after execution the route must resolve to `Phase 79 complete` with the next step `$gsd-complete-milestone v1.21`.
- **HOT-35**: `scripts/check_file_matrix_registry.py` must stop being a monolithic hotspot; classifier logic should be decomposed into smaller explicit units with clearer ownership.
- **TST-24**: release-contract governance coverage must be topicized into smaller, concern-oriented test homes without losing contract coverage.
- **QLT-32**: touched scope must pass focused quality gates, including file-matrix checks and a complexity guard proving the registry hotspot has been reduced.

## Acceptance criteria

1. `scripts/check_file_matrix_registry.py` no longer triggers `uv run ruff check scripts/check_file_matrix_registry.py --select C901`, and the classification logic is materially easier to navigate than the pre-phase monolith.
2. `tests/meta/test_governance_release_contract.py` is no longer the single carrier for all release/docs/continuity assertions; concern-oriented suites or helper-backed split files exist, and the file-governance registry truth is updated for any new files.
3. `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/MILESTONES.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/FILE_MATRIX.md`, `.planning/reviews/PROMOTED_PHASE_ASSETS.md`, `.planning/reviews/RESIDUAL_LEDGER.md`, `.planning/reviews/KILL_LIST.md`, and `tests/meta/governance_current_truth.py` all tell the same `Phase 79` story.
4. Validation proves the maintainability pass did not regress governance truth, release-contract coverage, or file-matrix/tooling integrity.

## Suggested proof bundle

- `uv run ruff check scripts/check_file_matrix_registry.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_*.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run pytest -q tests/test_refactor_tools.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_*.py tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_version_sync.py`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 79`

## Canonical references

- `lipro-hass/AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `scripts/check_file_matrix_registry.py`
- `scripts/check_file_matrix_validation.py`
- `tests/meta/test_governance_release_contract.py`
- `tests/meta/governance_current_truth.py`
- `tests/test_refactor_tools.py`
