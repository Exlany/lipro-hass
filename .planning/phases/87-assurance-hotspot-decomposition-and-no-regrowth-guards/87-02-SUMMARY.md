---
phase: 87-assurance-hotspot-decomposition-and-no-regrowth-guards
plan: "02"
subsystem: testing
tags: [protocol-contracts, boundary-decoders, fixture-authority, facade-runtime, pytest]
requires:
  - phase: 87-assurance-hotspot-decomposition-and-no-regrowth-guards
    provides: context/research truth routing for hotspot topicization
provides:
  - boundary decoder topical suite for protocol canonicalization
  - facade/runtime topical suite for unified root and child-facade smoke
  - fixture authority topical suite for replay and authority-path coverage
  - thin anchor root at tests/core/api/test_protocol_contract_matrix.py
affects: [HOT-38, TST-27, assurance, protocol-contracts]
tech-stack:
  added: []
  patterns: [thin-anchor-shell, concern-local-assurance-suites]
key-files:
  created:
    - tests/core/api/test_protocol_contract_boundary_decoders.py
    - tests/core/api/test_protocol_contract_facade_runtime.py
    - tests/core/api/test_protocol_contract_fixture_authority.py
  modified:
    - tests/core/api/test_protocol_contract_matrix.py
key-decisions:
  - "Kept test_protocol_contract_matrix.py as a one-test anchor so existing matrix path contracts stay stable without re-aggregating bulk assertions."
  - "Split decoder canonicalization, facade/runtime smoke, and fixture/replay authority into separate suites so failures land on the actual contract family."
patterns-established:
  - "Thin anchor shell: legacy root paths keep only discoverable smoke coverage."
  - "Fixture authority stays bound to existing replay manifests and authority paths instead of duplicating assets."
requirements-completed: [HOT-38, TST-27]
duration: 15min
completed: 2026-03-27
---

# Phase 87 Plan 02: topicize protocol contract matrix into boundary, facade, and authority suites Summary

**Protocol contract hotspot now fails by boundary decoder, facade/runtime, or fixture authority concern while `test_protocol_contract_matrix.py` remains only a unified-root anchor.**

## Performance

- **Duration:** 15 min
- **Started:** 2026-03-27T09:31:43Z
- **Completed:** 2026-03-27T09:46:43Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Moved decoder canonicalization and boundary metadata assertions into `tests/core/api/test_protocol_contract_boundary_decoders.py`.
- Moved replay-manifest and fixture authority assertions into `tests/core/api/test_protocol_contract_fixture_authority.py` without copying fixture truth.
- Moved unified root / facade runtime smoke into `tests/core/api/test_protocol_contract_facade_runtime.py` and reduced `tests/core/api/test_protocol_contract_matrix.py` to a thin anchor.

## Task Commits

Each task was committed atomically:

1. **Task 1: split the protocol matrix by contract family rather than by historical file gravity** - `d23774b` (test)
2. **Task 2: preserve stable anchor paths without legalizing a second contract story** - `93375f9` (test)

## Files Created/Modified

- `tests/core/api/test_protocol_contract_boundary_decoders.py` - boundary decoder canonicalization and metadata truth.
- `tests/core/api/test_protocol_contract_facade_runtime.py` - unified root and child-facade runtime smoke coverage.
- `tests/core/api/test_protocol_contract_fixture_authority.py` - replay manifest and authority-path assertions.
- `tests/core/api/test_protocol_contract_matrix.py` - single unified-root anchor shell.

## Decisions Made

- Kept the matrix path alive as a thin shell instead of an umbrella importer so existing anchors remain valid without hiding topical homes.
- Left fixture/replay truth on the existing authority paths and only moved assertions, avoiding a second contract story.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected device-status authority assertion after first split pass**
- **Found during:** Task 1 (split the protocol matrix by contract family rather than by historical file gravity)
- **Issue:** The moved `rest.device-status` metadata assertion was copied with a concrete fixture path instead of the decoder's wildcard authority path.
- **Fix:** Updated the assertion to `tests/fixtures/api_contracts/query_device_status.*.json` in the new boundary suite.
- **Files modified:** `tests/core/api/test_protocol_contract_boundary_decoders.py`
- **Verification:** `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_contract_*.py`
- **Committed in:** `d23774b` (part of task commit)

---

**Total deviations:** 1 auto-fixed (1 Rule 1 bug)
**Impact on plan:** The fix kept the split aligned with the existing authority contract. No scope creep.

## Issues Encountered

- The plan context referenced `tests/harness/protocol.py`, but the live authority helpers are provided by the package at `tests/harness/protocol/__init__.py`; execution continued against the real import home already used by the suite.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Protocol contract hotspot decomposition is complete and verification-clean.
- The remaining Phase 87 plans can build on concern-local protocol assurance without reusing a giant matrix carrier.

## Self-Check: PASSED

- Found `tests/core/api/test_protocol_contract_matrix.py`.
- Found `tests/core/api/test_protocol_contract_boundary_decoders.py`.
- Found `tests/core/api/test_protocol_contract_facade_runtime.py`.
- Found `tests/core/api/test_protocol_contract_fixture_authority.py`.
- Found commit `d23774b`.
- Found commit `93375f9`.

---
*Phase: 87-assurance-hotspot-decomposition-and-no-regrowth-guards*
*Completed: 2026-03-27*
