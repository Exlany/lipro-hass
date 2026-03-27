---
phase: 87-assurance-hotspot-decomposition-and-no-regrowth-guards
plan: "01"
subsystem: testing
tags: [pytest, diagnostics, topicization, assurance]
requires: []
provides:
  - diagnostics API assurance now routes OTA, history/command-result, and cloud stories through concern-local suites
  - original diagnostics hotspot file is reduced to a thin anchor instead of a giant truth-carrier
  - local diagnostics support helpers centralize shared mapping/error utilities without copying fixture authority
affects: [Phase 87 Plan 04, diagnostics assurance topology, hotspot guards]
tech-stack:
  added: []
  patterns: [thin anchor test root, concern-local topical suites, local inward test support helper]
key-files:
  created:
    - tests/core/api/test_api_diagnostics_service_ota.py
    - tests/core/api/test_api_diagnostics_service_history.py
    - tests/core/api/test_api_diagnostics_service_cloud.py
    - tests/core/api/test_api_diagnostics_service_support.py
  modified:
    - tests/core/api/test_api_diagnostics_service.py
key-decisions:
  - "Kept tests/core/api/test_api_diagnostics_service.py as a thin anchor so the giant hotspot no longer carries bulk assertions."
  - "Extracted only DummyApiError and mapping-row helpers into a local support module to avoid creating a second truth root."
patterns-established:
  - "Diagnostics API topicization: split suites by OTA, history/command-result, and cloud concern families."
  - "Local test helpers live beside topical suites and do not duplicate external-boundary fixture authority."
requirements-completed: [HOT-38, TST-27]
duration: 7min
completed: 2026-03-27
---

# Phase 87 Plan 01: topicize diagnostics API assurance hotspot into concern-local suites Summary

**Diagnostics API assurance now isolates OTA fallback, sensor history/command-result, and raw cloud-body contracts into concern-local suites with a thin root anchor.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-27T09:36:41Z
- **Completed:** 2026-03-27T09:43:37Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Split the former `tests/core/api/test_api_diagnostics_service.py` giant hotspot into `OTA`, `history`, and `cloud` topical suites.
- Reduced `tests/core/api/test_api_diagnostics_service.py` to a thin anchor so failure locality comes from the topical filenames.
- Added `tests/core/api/test_api_diagnostics_service_support.py` as a strictly local helper home for shared row/mapping utilities and `DummyApiError`.

## Task Commits

Each task was committed atomically:

1. **Task 1: split diagnostics API assertions by concrete concern family** - `59f3816` (test)
2. **Task 2: add the smallest necessary support helper without creating a second truth root** - `141ac0b` (refactor)

## Files Created/Modified
- `tests/core/api/test_api_diagnostics_service.py` - thin anchor file for the topicized diagnostics API suites
- `tests/core/api/test_api_diagnostics_service_ota.py` - OTA/info fallback and degraded-outcome assertions
- `tests/core/api/test_api_diagnostics_service_history.py` - sensor history and command-result assertions
- `tests/core/api/test_api_diagnostics_service_cloud.py` - raw-body cloud query contract assertion
- `tests/core/api/test_api_diagnostics_service_support.py` - local shared helper home for diagnostics topical suites

## Decisions Made
- Kept the original hotspot path as a thin anchor instead of an aggregator import shell so the verify command does not double-collect tests.
- Shared only `DummyApiError`, `_extract_rows`, and `_require_mapping_response` in the support module; all fixture authority remains in existing external-boundary helpers.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The workspace already contained unrelated changes in other `Phase 87` hotspot files; they were left untouched and excluded from task commits.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Diagnostics API hotspot is topicized and ready for any later `87-04` governance/file-matrix sync.
- OTA/history/cloud failures now localize by file name without reopening production surfaces.

## Self-Check: PASSED

- Confirmed summary and all five diagnostics API files exist on disk.
- Confirmed task commits `59f3816` and `141ac0b` are present in git history.

---
*Phase: 87-assurance-hotspot-decomposition-and-no-regrowth-guards*
*Completed: 2026-03-27*
