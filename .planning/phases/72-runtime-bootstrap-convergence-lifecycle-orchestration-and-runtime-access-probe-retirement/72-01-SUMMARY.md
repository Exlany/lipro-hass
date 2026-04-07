---
phase: 72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement
plan: "01"
subsystem: runtime
tags: [home-assistant, coordinator, bootstrap, runtime-root, typing]
requires:
  - phase: 71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection
    provides: terminal-audit seeds for coordinator bootstrap inward convergence
provides:
  - named `CoordinatorBootstrapArtifact` contract in `core/coordinator`
  - thinner `Coordinator.__init__` that only consumes runtime bootstrap collaborators
  - focused runtime-root regression for bootstrap artifact consumption
affects: [phase-72-02, phase-72-03, coordinator-runtime-root]
tech-stack:
  added: []
  patterns: [named bootstrap artifact, focused runtime-root seam regression]
key-files:
  created:
    - .planning/phases/72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement/72-01-SUMMARY.md
  modified:
    - custom_components/lipro/core/coordinator/coordinator.py
    - custom_components/lipro/core/coordinator/factory.py
    - custom_components/lipro/core/coordinator/orchestrator.py
    - tests/core/coordinator/test_runtime_root.py
    - tests/core/coordinator/conftest.py
key-decisions:
  - "Keep `Coordinator` as the only runtime root; `RuntimeOrchestrator` only returns a named bootstrap artifact."
  - "Move state/runtime/service/update-cycle mechanics behind `CoordinatorBootstrapArtifact` instead of adding a new helper root."
  - "Lock the bootstrap seam with a focused constructor regression backed by a local `config_entry` fixture."
patterns-established:
  - "Named bootstrap artifact: runtime root consumes one explicit contract from formal homes."
  - "Focused seam test: patch `RuntimeOrchestrator.build_bootstrap_artifact` instead of widening coordinator mega-suites."
requirements-completed: [ARC-19, HOT-32, TYP-21, TST-22, QLT-30]
duration: 3min
completed: 2026-03-25
---

# Phase 72 Plan 01: Formalize coordinator bootstrap collaborators and trim runtime-root startup density Summary

**Coordinator now consumes a named bootstrap artifact for state, runtimes, service layer, and update-cycle without changing its outward constructor contract.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-25T04:24:09Z
- **Completed:** 2026-03-25T04:26:58Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Moved coordinator bootstrap mechanics behind `CoordinatorBootstrapArtifact` in existing `core/coordinator/` formal homes.
- Reduced `Coordinator.__init__` to root-owned binding plus bootstrap artifact consumption while keeping the runtime-root story unchanged.
- Added a focused runtime-root regression that proves constructor behavior and patch seam stability.

## Task Commits

Each task was committed atomically:

1. **Task 1: formalize bootstrap artifact assembly** - `4dbb02c` (refactor)
2. **Task 1 verification fix: align reauth callback typing** - `f0cc8ac` (fix)
3. **Task 2: cover runtime bootstrap artifact seam** - `fd9cf9a` (test)

**Plan metadata:** pending final docs commit

## Files Created/Modified
- `custom_components/lipro/core/coordinator/factory.py` - Adds `CoordinatorBootstrapArtifact` as the named bootstrap contract.
- `custom_components/lipro/core/coordinator/orchestrator.py` - Centralizes state/runtime/service/update-cycle assembly in `build_bootstrap_artifact`.
- `custom_components/lipro/core/coordinator/coordinator.py` - Consumes bootstrap artifact and keeps outward constructor semantics stable.
- `tests/core/coordinator/test_runtime_root.py` - Adds focused regression for named bootstrap artifact consumption.
- `tests/core/coordinator/conftest.py` - Reuses a local `config_entry` fixture for runtime-root seam tests.

## Decisions Made
- Kept `RuntimeOrchestrator` as an inward collaborator only; it does not become a second runtime root.
- Reused existing `runtime_wiring` service-layer helpers instead of introducing a new builder/helper carrier.
- Preserved the existing constructor and runtime-root patch seam so callers and current tests do not need new knowledge.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Aligned bootstrap reauth callback typing after extraction**
- **Found during:** Task 1 verification
- **Issue:** `build_bootstrap_artifact` initially typed `trigger_reauth` as a zero-arg callback, conflicting with `RuntimeContext`'s one-arg reauth protocol and blocking mypy.
- **Fix:** Changed the orchestrator bootstrap callback contract to `Callable[[str], Awaitable[None]]`.
- **Files modified:** `custom_components/lipro/core/coordinator/orchestrator.py`
- **Verification:** `uv run mypy --follow-imports=silent custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/core/coordinator/factory.py custom_components/lipro/core/coordinator/orchestrator.py`
- **Committed in:** `f0cc8ac`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The fix only restored the intended typed bootstrap contract and did not expand scope beyond 72-01.

## Issues Encountered
- The working tree already contained unrelated edits in `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/control/runtime_access_support_views.py`, `custom_components/lipro/control/runtime_access_types.py`, and `tests/core/test_runtime_access.py`; they were left untouched per scope boundary.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `Coordinator` bootstrap density is reduced behind a named artifact and focused runtime-root guards are green.
- Phase 72 follow-up plans can continue lifecycle/runtime-access convergence without reopening constructor or runtime-root surfaces.

## Known Stubs

None.

---
*Phase: 72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement*
*Completed: 2026-03-25*

## Self-Check: PASSED
