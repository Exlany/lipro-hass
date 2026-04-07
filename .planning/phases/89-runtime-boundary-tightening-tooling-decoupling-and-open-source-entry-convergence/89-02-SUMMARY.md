---
phase: 89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence
plan: "02"
subsystem: runtime
tags: [runtime, bootstrap, wiring, coordinator]
requires:
  - phase: 89-01
    provides: entity-facing runtime verbs
provides:
  - single bootstrap artifact wiring
  - named support-services bundle
  - focused runtime-wiring regression guards
affects: [custom_components/lipro/core/coordinator, tests/core/coordinator, tests/meta]
tech-stack:
  added: []
  patterns:
    - coordinator consumes one bootstrap artifact instead of building parallel service roots
key-files:
  created:
    - tests/meta/test_phase89_runtime_wiring_guards.py
  modified:
    - custom_components/lipro/core/coordinator/coordinator.py
    - custom_components/lipro/core/coordinator/orchestrator.py
    - custom_components/lipro/core/coordinator/runtime_wiring.py
    - custom_components/lipro/core/coordinator/factory.py
    - tests/core/coordinator/test_runtime_root.py
    - tests/core/test_init_runtime_bootstrap.py
    - tests/core/test_coordinator.py
key-decisions:
  - "Move support-service construction into bootstrap/orchestrator-owned assembly so Coordinator only binds artifact outputs."
patterns-established:
  - "`CoordinatorSupportServices` is the single source for auth/protocol/signal support wiring."
requirements-completed:
  - RUN-09
  - HOT-39
  - TST-28
  - QLT-36
duration: session-carried
completed: 2026-03-27
---

# Summary 89-02

**Coordinator bootstrap now tells one runtime-wiring story: support services are assembled once upstream and bound from a single bootstrap artifact.**

## Outcome

- `custom_components/lipro/core/coordinator/runtime_wiring.py` introduces the named support-service bundle that owns auth / protocol / signal assembly.
- `custom_components/lipro/core/coordinator/orchestrator.py` and `factory.py` now build and pass that bundle as part of one bootstrap artifact.
- `custom_components/lipro/core/coordinator/coordinator.py` no longer hand-constructs support services in parallel before asking the orchestrator for bootstrap state.
- Runtime-root tests were aligned so regressions fail if constructor-local pre-bootstrap service construction returns.
- `tests/meta/test_phase89_runtime_wiring_guards.py` freezes the single-wiring contract.

## Verification

- `uv run pytest -q tests/core/coordinator/test_runtime_root.py tests/core/test_init_runtime_bootstrap.py tests/core/test_coordinator.py tests/meta/test_phase89_runtime_wiring_guards.py`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- None — runtime/service assembly was fully centralized without introducing a compat wrapper.

## Next Readiness

- `89-04` can document runtime single-wiring truth as an implemented fact instead of a planned convergence.
