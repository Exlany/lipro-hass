---
phase: 89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence
plan: "01"
subsystem: runtime
tags: [runtime, entities, ota, boundary]
requires: []
provides:
  - entity-facing named runtime verbs
  - OTA query routed through coordinator verb
  - focused runtime-boundary regression guards
affects: [custom_components/lipro/runtime_types.py, custom_components/lipro/entities, tests/meta]
tech-stack:
  added: []
  patterns:
    - entity-facing runtime verbs instead of service/lock exposure
key-files:
  created:
    - tests/meta/test_phase89_runtime_boundary_guards.py
  modified:
    - custom_components/lipro/runtime_types.py
    - custom_components/lipro/core/coordinator/coordinator.py
    - custom_components/lipro/entities/base.py
    - custom_components/lipro/entities/firmware_update.py
    - tests/conftest.py
    - tests/platforms/test_entity_base.py
    - tests/meta/public_surface_runtime_contracts.py
key-decisions:
  - "Keep command/protocol/locking ownership inside coordinator and expose verb-shaped methods to entities."
  - "Preserve OTA cache/trust-root semantics while removing protocol_service leakage from update entity."
patterns-established:
  - "Entities call `async_send_command`, `async_apply_optimistic_state`, and `async_query_device_ota_info` only."
requirements-completed:
  - ARC-23
  - HOT-39
  - TST-28
  - QLT-36
duration: session-carried
completed: 2026-03-27
---

# Summary 89-01

**Entity-facing runtime access now flows through named coordinator verbs, with OTA lookups and optimistic state updates no longer reaching into service handles or device locks.**

## Outcome

- `custom_components/lipro/runtime_types.py` removes `command_service` / `protocol_service` / `get_device_lock` from `LiproRuntimeCoordinator` and replaces them with explicit verbs.
- `custom_components/lipro/entities/base.py` now routes command dispatch and optimistic state updates through coordinator-owned verbs.
- `custom_components/lipro/entities/firmware_update.py` now queries OTA data through `async_query_device_ota_info(...)` instead of touching protocol internals directly.
- `tests/conftest.py`, platform tests, and runtime public-surface tests were aligned to the narrowed contract.
- `tests/meta/test_phase89_runtime_boundary_guards.py` freezes the new boundary so entity/runtime leakage does not regrow.

## Verification

- `uv run pytest -q tests/core/coordinator/test_entity_protocol.py tests/meta/public_surface_runtime_contracts.py tests/platforms/test_entity_base.py tests/platforms/test_update_entity_refresh.py tests/platforms/test_firmware_update_entity_edges.py tests/meta/test_phase89_runtime_boundary_guards.py`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- None — executed the planned contract narrowing and added one extra guard to ensure the coordinator no longer keeps the entity lock backdoor alive.

## Next Readiness

- `89-02` can assume the runtime surface is verb-shaped and no longer needs to preserve entity-visible service seams.
