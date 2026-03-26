# Phase 80: Governance typing closure and final meta-suite hotspot topicization - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning
**Source:** post-Phase-79 repository audit

<domain>
## Phase Boundary

This phase only targets governance/tooling/test quality closure that still gives better ROI than reopening production hotspots:

- mypy regressions introduced around Phase 79 registry/topicization work;
- oversized remaining governance test bodies that still hurt failure localization;
- live route/evidence truth that must honestly carry one more maintainability pass before milestone closeout.

Out of scope: production feature work, protocol/runtime behavior redesign, milestone archive promotion.
</domain>

<decisions>
## Implementation Decisions

### Typing closure first
- Fix explicit export and typed JSON access instead of silencing errors.
- Prefer local typed helpers or narrow casts over spreading `Any`.

### Hotspot decomposition standard
- Only split or re-shape tests where it clearly improves failure localization and future edits.
- Prefer smaller tests in the same file over creating new files unless a new concern home is truly justified.

### Governance truth honesty
- Once complete, `v1.21` must move to `Phase 80 complete / closeout-ready` and next step must return to `$gsd-complete-milestone v1.21`.

### Quality discipline
- Phase proof must explicitly include `mypy` in addition to the existing ruff/file-matrix/architecture/pytest/GSD gates.
</decisions>

<canonical_refs>
## Canonical References

- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `scripts/check_file_matrix.py`
- `scripts/check_file_matrix_registry.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_governance_release_contract.py`
</canonical_refs>

<specifics>
## Specific Ideas

- Add an explicit re-export contract for `FileGovernanceRow` instead of relying on transitive imports.
- Collapse JSON parsing in GSD smoke tests behind typed helper functions so route assertions stay readable and `mypy`-clean.
- Break giant governance assertions into smaller tests grouped by one concern family at a time.
</specifics>

<deferred>
## Deferred Ideas

- Production-file hotspots like `core/coordinator/runtime/command_runtime.py`, `runtime_infra.py`, and `core/api/status_service.py` remain measurable but lower-ROI than the governance/tooling residuals above because they are currently green under repo quality gates and no new architecture drift has been observed.
</deferred>
