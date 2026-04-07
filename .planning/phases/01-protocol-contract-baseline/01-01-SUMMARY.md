---
phase: 01-protocol-contract-baseline
plan: "01-01"
subsystem: api
tags: [mqtt, diagnostics, fixtures, pytest, protocol-contract]
requires: []
provides:
  - MQTT direct/wrapped golden fixtures bound to one canonical payload
  - Targeted protocol contract tests for MQTT, city, and user-cloud helpers
  - Adjacent regression proof covering helper modules, diagnostics helpers, and snapshots
affects: [01-02, 01.5, 02, 02.5]
tech-stack:
  added: []
  patterns: [golden-fixture canonicalization, helper-level protocol contract tests]
key-files:
  created:
    - .planning/phases/01-protocol-contract-baseline/01-01-SUMMARY.md
  modified:
    - tests/fixtures/api_contracts/README.md
    - tests/fixtures/api_contracts/get_mqtt_config.wrapped.json
    - tests/core/api/test_protocol_contract_matrix.py
key-decisions:
  - "Use one canonical MQTT payload across direct and wrapped fixtures so envelope variance is not treated as a second contract truth."
  - "Keep get_city and query_user_cloud assertions at helper/service seams instead of coupling them to LiproClient inheritance shape."
patterns-established:
  - "Golden fixtures encode canonical payloads, not transport noise or mixin structure."
  - "Protocol contract tests assert behavior through extraction/helper seams that survive future facade refactors."
requirements-completed: [PROT-01, PROT-02, ASSR-01]
duration: 3min
completed: 2026-03-12
---

# Phase 01 Plan 01-01: Protocol Contract Baseline Summary

**Golden MQTT direct/wrapped fixtures now share one canonical payload, with city and user-cloud helper contracts locked by targeted regression tests**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-12T14:05:28Z
- **Completed:** 2026-03-12T14:07:46Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- Tightened the MQTT golden fixture pair so direct and wrapped shapes represent one canonical contract truth instead of two payload variants.
- Reworked targeted protocol contract coverage to assert both MQTT shapes normalize to the same canonical payload while keeping `get_city` and `query_user_cloud` independent from `LiproClient` inheritance.
- Proved the baseline against adjacent regression guards with helper-module, diagnostics-service, and snapshot suites.

## Task Commits

Each task was committed atomically when code changed:

1. **Task 1: 建立 contract matrix 与 fixture 目录** - `393e799` (`feat`)
2. **Task 2: 新增 targeted protocol contract tests** - `54907d0` (`test`)
3. **Task 3: 用现有 helper/snapshot tests 做回归护栏** - verification only (no file changes)

## Files Created/Modified
- `.planning/phases/01-protocol-contract-baseline/01-01-SUMMARY.md` - Records the executed scope, decisions, commits, and verification evidence for `01-01`.
- `tests/fixtures/api_contracts/README.md` - Clarifies that MQTT direct/wrapped fixtures are two input shapes of one canonical contract.
- `tests/fixtures/api_contracts/get_mqtt_config.wrapped.json` - Reuses the canonical MQTT payload while preserving the wrapped transport envelope.
- `tests/core/api/test_protocol_contract_matrix.py` - Parametrizes MQTT fixture coverage and locks both shapes to the same canonical output.

## Decisions Made
- Reused the same MQTT sample payload across direct and wrapped fixtures to make “input shape difference, single contract truth” executable instead of implicit.
- Left `get_city` and `query_user_cloud` assertions on helper/service boundaries, matching the phase requirement that contract truth must not depend on current `LiproClient` mixin structure.

## Deviations from Plan

None - plan executed exactly as written. The repo already contained most `01-01` assets; execution focused on tightening the remaining ambiguity in the MQTT canonical contract truth and validating the full targeted regression envelope.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `01-02` can now build snapshots and governance closeout on top of an explicit MQTT single-truth contract baseline.
- No blocking issues were found within the `01-01` scope.

## Self-Check: PASSED
