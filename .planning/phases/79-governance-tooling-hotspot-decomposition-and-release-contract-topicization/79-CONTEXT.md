# Phase 79: Governance tooling hotspot decomposition and release-contract topicization - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning
**Source:** PRD Express Path (`79-PRD.md`)

<domain>
## Phase Boundary

This phase only targets governance/tooling/test maintainability hotspots that still impose unnecessary long-term cost after `Phase 78`:

- the monolithic classifier logic in `scripts/check_file_matrix_registry.py`;
- the over-concentrated release/docs/continuity assertions in `tests/meta/test_governance_release_contract.py`;
- the live governance route truth needed to carry one extra maintainability phase without reopening a second story.

Out of scope: new production features, protocol/runtime behavior changes, milestone archive promotion.
</domain>

<decisions>
## Implementation Decisions

### Governance route honesty
- `v1.21` must honestly acknowledge `Phase 79` during this pass and return to `closeout-ready` only after the phase is complete.
- The final next command must return to `$gsd-complete-milestone v1.21`.

### Tooling hotspot decomposition
- `scripts/check_file_matrix_registry.py` should become a thin root or at least a materially slimmer classifier home.
- Exact-path and prefix-based classification rules should become easier to scan than the current nested `if` chain.
- Any new registry/helper modules must remain inside the same governed checker story; do not create a second truth chain.

### Release-contract topicization
- `tests/meta/test_governance_release_contract.py` should stop being the only large carrier of CI/release/docs/continuity concerns.
- New concern-oriented suites may be added, but current live governance docs should not lose a stable release-contract anchor.
- File-matrix ownership must be explicit for any new suites.

### Validation discipline
- Quality proof must include a complexity-focused lint check for the registry hotspot, file-matrix validation, architecture policy, and focused governance pytest bundles.

### the agent's Discretion
- Choose the exact split shape (table-driven rules, helper modules, concern splits) based on the smallest change that clearly improves maintainability.
- Keep naming aligned with existing governance/tooling vocabulary.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Governance truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — north-star arbitration rules
- `lipro-hass/AGENTS.md` — repo-level execution contract
- `.planning/PROJECT.md` — current route + milestone framing
- `.planning/ROADMAP.md` — active phase list and route structure
- `.planning/REQUIREMENTS.md` — live requirement traceability
- `.planning/STATE.md` — machine-readable active state
- `.planning/MILESTONES.md` — bootstrap contract mirror

### Baseline and review assets
- `.planning/baseline/VERIFICATION_MATRIX.md` — active acceptance contract
- `.planning/reviews/FILE_MATRIX.md` — file-governance truth surface
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` — promoted phase evidence allowlist
- `.planning/reviews/RESIDUAL_LEDGER.md` — residual honesty ledger
- `.planning/reviews/KILL_LIST.md` — delete-gate ledger

### Hotspot files
- `scripts/check_file_matrix_registry.py` — current monolithic registry hotspot
- `scripts/check_file_matrix_validation.py` — registry maintainability checks
- `tests/meta/test_governance_release_contract.py` — current giant release-contract suite
- `tests/meta/governance_current_truth.py` — active route constants
- `tests/test_refactor_tools.py` — existing script-focused unit-test home
</canonical_refs>

<specifics>
## Specific Ideas

- Keep `test_governance_release_contract.py` as a stable anchor only if doing so still meaningfully improves failure localization; otherwise document the new split clearly in live governance assets.
- Prefer targeted new tests over mega-suite growth.
- Prefer companion modules over deeper branching inside `check_file_matrix_registry.py`.
</specifics>

<deferred>
## Deferred Ideas

- Production-code hotspots such as `custom_components/lipro/core/api/auth_recovery.py` and `custom_components/lipro/core/api/schedule_service.py` were identified as non-blocking maintainability candidates, but they are lower ROI than the governance/tooling hotspots in this phase.
</deferred>
