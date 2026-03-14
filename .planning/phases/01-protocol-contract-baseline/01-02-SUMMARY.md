---
phase: 01-protocol-contract-baseline
plan: "01-02"
subsystem: api
tags: [mqtt, snapshots, governance, protocol-contract, handoff]
requires:
  - phase: 01-01
    provides: targeted contract fixtures and canonical helper assertions for the Phase 01 baseline
provides:
  - Canonical protocol snapshots for `get_mqtt_config`, `get_city`, and `query_user_cloud`
  - Immutable protocol constraint ledger with sanitization rules and governance ownership
  - Phase 01 closeout notes for verification matrix, file matrix, residual ledger, and kill list
  - Explicit handoff conditions into Phase 1.5 baseline assetization and Phase 2 protocol refactor work
affects: [01.5, 02, 02.5]
tech-stack:
  added: []
  patterns: [canonical snapshot baseline, immutable-constraint governance, phase closeout handoff]
key-files:
  created:
    - .planning/phases/01-protocol-contract-baseline/01-IMMUTABLE-CONSTRAINTS.md
    - .planning/phases/01-protocol-contract-baseline/01-02-SUMMARY.md
  modified:
    - tests/snapshots/test_api_snapshots.py
    - tests/snapshots/snapshots/test_api_snapshots.ambr
    - .planning/baseline/VERIFICATION_MATRIX.md
    - .planning/reviews/FILE_MATRIX.md
    - .planning/reviews/RESIDUAL_LEDGER.md
    - .planning/reviews/KILL_LIST.md
key-decisions:
  - "Snapshot coverage records accepted input shapes plus canonical outputs instead of vendor payload noise."
  - "Immutable constraints are documented as governance facts and sanitization rules, not as sensitive implementation details."
  - "Phase 01 closeout requires governance outputs and handoff proof, not only passing tests."
patterns-established:
  - "Canonical protocol snapshots stay attached to normalized helper outputs so future facade refactors can detect drift without inheriting transport noise."
  - "Phase closeout docs must either update governance artifacts or explicitly state that they were checked and had no new changes."
requirements-completed: [PROT-01, PROT-02, ASSR-01]
duration: 11min
completed: 2026-03-12
---

# Phase 01 Plan 01-02: Protocol Contract Baseline Closeout Summary

**Canonical protocol snapshots, immutable-constraint governance, and Phase 01 closeout handoff now wrap the initial contract baseline into reusable input truth for Phase 1.5 and Phase 2**

## Performance

- **Duration:** 11 min
- **Started:** 2026-03-12T14:14:38Z
- **Completed:** 2026-03-12T14:21:22Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments
- Extended `tests/snapshots/test_api_snapshots.py` and its snapshot baseline so `get_mqtt_config`, `get_city`, and `query_user_cloud` are observed through canonical contract outputs instead of raw vendor payload samples.
- Added `01-IMMUTABLE-CONSTRAINTS.md` to record credential-field, envelope/request-form, algorithm, and path/topic constraint classes while keeping fixtures, snapshots, and docs sanitized.
- Closed Phase 01 governance outputs by checking `VERIFICATION_MATRIX`, `FILE_MATRIX`, `RESIDUAL_LEDGER`, and `KILL_LIST`, then documenting the handoff gate into Phase 1.5 and Phase 2.

## Task Commits

Each task was committed atomically when code changed:

1. **Task 1: 让 snapshot 层感知 canonical contract baseline** - `78170c8` (`test`)
2. **Task 2: 固化不可变约束与 Phase 1 治理收尾** - `05a4f4b` (`docs`)
3. **Task 3: 输出 plan summaries 与 handoff** - current closeout commit (`docs`)

## Verification Evidence

- `uv run pytest tests/snapshots/test_api_snapshots.py -q --snapshot-update`
- `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/snapshots/test_api_snapshots.py -q`
- Manual review confirmed immutable-constraint sanitization, governance closeout notes, and no-change explanations for residual / kill outputs.

## Files Created/Modified
- `tests/snapshots/test_api_snapshots.py` - Adds canonical snapshot coverage for the three locked protocol boundaries.
- `tests/snapshots/snapshots/test_api_snapshots.ambr` - Stores the canonical snapshot baseline for accepted input shapes and normalized outputs.
- `.planning/phases/01-protocol-contract-baseline/01-IMMUTABLE-CONSTRAINTS.md` - Records immutable constraint classes, sanitization rules, and downstream ownership.
- `.planning/baseline/VERIFICATION_MATRIX.md` - Confirms the Phase 01 exit contract now includes canonical snapshots and immutable constraints.
- `.planning/reviews/FILE_MATRIX.md` - Notes that `tests/snapshots` now carries the locked Phase 01 baseline surface.
- `.planning/reviews/RESIDUAL_LEDGER.md` - Records that no new residual family was introduced by the closeout work.
- `.planning/reviews/KILL_LIST.md` - Records that no new deletion candidates were introduced by the closeout work.
- `.planning/phases/01-protocol-contract-baseline/01-02-SUMMARY.md` - Captures the full closeout evidence and handoff conditions for the plan.

## Decisions Made
- Reused the existing fixture-driven helper seams in snapshot form so Phase 01 still locks contract truth without depending on `LiproClient` inheritance structure.
- Kept immutable-constraint documentation at the category/governance layer, preventing sensitive literals or algorithm details from leaking into `.planning` artifacts.
- Treated governance review outputs as part of the plan’s deliverable surface; residual and kill artifacts were checked and explicitly recorded as “no new change” where appropriate.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- **Phase 1.5** can now consume a complete Phase 01 baseline package: targeted fixtures/tests from `01-01`, canonical snapshots from `01-02`, and immutable/governance closeout artifacts.
- **Phase 2** should treat this baseline as a hard input boundary for demixin / REST façade work and preserve the accepted input shapes plus canonical outputs locked here.
- `RESIDUAL_LEDGER` and `KILL_LIST` remain unchanged in substance: mixin and compat-wrapper cleanup still belongs to later protocol refactor phases rather than Phase 01.
