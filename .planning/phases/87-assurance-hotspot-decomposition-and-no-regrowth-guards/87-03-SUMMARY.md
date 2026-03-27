---
phase: 87-assurance-hotspot-decomposition-and-no-regrowth-guards
plan: "03"
subsystem: testing
tags: [mqtt-runtime, runtime-facets, pytest, topicization, assurance]
requires:
  - phase: 87-assurance-hotspot-decomposition-and-no-regrowth-guards
    provides: context/research truth routing for assurance hotspot topicization
provides:
  - runtime-facet suites for mqtt runtime initialization, connection, messages, and notifications/reset coverage
  - local mqtt runtime support helper for shared runtime setup and typed helpers
  - thin anchor root at tests/core/coordinator/runtime/test_mqtt_runtime.py
affects: [HOT-38, TST-27, runtime assurance topology, Phase 87 Plan 04]
tech-stack:
  added: []
  patterns: [thin anchor shell, runtime-facet topical suites, local inward test support helper]
key-files:
  created:
    - tests/core/coordinator/runtime/test_mqtt_runtime_init.py
    - tests/core/coordinator/runtime/test_mqtt_runtime_connection.py
    - tests/core/coordinator/runtime/test_mqtt_runtime_messages.py
    - tests/core/coordinator/runtime/test_mqtt_runtime_notifications.py
    - tests/core/coordinator/runtime/test_mqtt_runtime_support.py
  modified:
    - tests/core/coordinator/runtime/test_mqtt_runtime.py
key-decisions:
  - "Kept test_mqtt_runtime.py as a thin anchor so the routed hotspot stops carrying bulk runtime assertions."
  - "Extracted only shared runtime setup and helper builders into test_mqtt_runtime_support.py to keep helper scope local to the runtime topical family."
patterns-established:
  - "MQTT runtime topicization: split init/DI, connection/reconnect, messages/dedup, and notifications/reset into sibling suites."
  - "Runtime support helpers live beside the topical suites and do not create a cross-tree utility root."
requirements-completed: [HOT-38, TST-27]
duration: 7min
completed: 2026-03-27
---

# Phase 87 Plan 03: topicize MQTT runtime assurance suite with inward support helper Summary

**MQTT runtime assurance now fails by init, connection/reconnect, messages/dedup, or notifications/reset concern while the legacy root remains only a thin anchor backed by one local support helper.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-27T09:42:00Z
- **Completed:** 2026-03-27T09:49:10Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Split the former `tests/core/coordinator/runtime/test_mqtt_runtime.py` hotspot into `init`, `connection`, `messages`, and `notifications` runtime-facet suites.
- Reduced `tests/core/coordinator/runtime/test_mqtt_runtime.py` to a thin anchor so failures localize by topical filename instead of a 600+ line carrier.
- Added `tests/core/coordinator/runtime/test_mqtt_runtime_support.py` as the single inward helper home for shared runtime setup, polling/failure helpers, and property payload builders.

## Task Commits

Each task was committed atomically:

1. **Task 1: split MQTT runtime tests by runtime facet and keep coverage honest** - `050c312` (test)
2. **Task 2: extract the minimum local support helper for repeated runtime setup** - `7d1e020` (test)

## Files Created/Modified

- `tests/core/coordinator/runtime/test_mqtt_runtime.py` - thin anchor for the topicized MQTT runtime suites.
- `tests/core/coordinator/runtime/test_mqtt_runtime_init.py` - initialization and dependency-injection coverage.
- `tests/core/coordinator/runtime/test_mqtt_runtime_connection.py` - connection, disconnect, transport callback, and reconnect coverage.
- `tests/core/coordinator/runtime/test_mqtt_runtime_messages.py` - message application, dedup, unknown-device, and group reconciliation coverage.
- `tests/core/coordinator/runtime/test_mqtt_runtime_notifications.py` - disconnect notification and reset coverage.
- `tests/core/coordinator/runtime/test_mqtt_runtime_support.py` - local shared runtime setup and helper home.

## Decisions Made

- Kept the original hotspot path as a thin anchor rather than an umbrella importer with local assertions, matching the repository's existing topicized runtime pattern.
- Moved only shared runtime construction and helper functions into the support module; no production code or cross-tree helper roots were introduced.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed leaked module-level asyncio marking from the message suite**
- **Found during:** Task 1 (split MQTT runtime tests by runtime facet and keep coverage honest)
- **Issue:** A module-level `pytestmark = pytest.mark.asyncio` leaked through the thin anchor's star imports and marked sync tests as async, producing warning noise.
- **Fix:** Replaced the module-level mark with per-test `@pytest.mark.asyncio` decorators in the message suite.
- **Files modified:** `tests/core/coordinator/runtime/test_mqtt_runtime_messages.py`
- **Verification:** `uv run pytest -q tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/runtime/test_mqtt_runtime_*.py`
- **Committed in:** `050c312` (part of Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 Rule 1 bug)
**Impact on plan:** The fix removed warning-only drift from the thin-anchor pattern without changing test coverage or scope.

## Issues Encountered

- The workspace already contained unrelated `Phase 87` planning artifacts and protocol-contract changes; they were left untouched and excluded from this plan's commits.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- MQTT runtime hotspot decomposition is complete and verification-clean.
- `Phase 87 Plan 04` can now add no-regrowth guards against the facet-local runtime topology without reusing a giant carrier file.

## Self-Check: PASSED

- Found `.planning/phases/87-assurance-hotspot-decomposition-and-no-regrowth-guards/87-03-SUMMARY.md`.
- Found all six touched MQTT runtime suite files on disk.
- Found task commits `050c312` and `7d1e020` in git history.

---
*Phase: 87-assurance-hotspot-decomposition-and-no-regrowth-guards*
*Completed: 2026-03-27*
