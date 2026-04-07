---
phase: 67-typed-contract-convergence-toolchain-hardening-and-mypy-closure
plan: "04"
status: completed
completed_at: "2026-03-23T20:00:00Z"

requirements_completed:
  - HOT-23
verification:
  - uv run pytest -q tests/core/test_control_plane.py tests/services/test_services_registry.py tests/platforms/test_update_background_tasks.py tests/core/test_init.py
---

# Phase 67 Plan 04 Summary

## Objective

Tighten runtime/control wiring callable annotations and focused adapter tests.

## Completed Work

- `custom_components/lipro/core/coordinator/runtime_context.py`, `runtime_wiring.py`, and `custom_components/lipro/core/command/post_refresh.py` now align callback and background-task signatures with actual awaitable/coroutine behavior.
- `custom_components/lipro/control/entry_root_wiring.py`, `service_router_support.py`, `custom_components/lipro/__init__.py`, and `custom_components/lipro/select.py` now use honest typed adapter returns and callable seams.
- Focused control/platform tests were updated to exercise the tightened contracts directly.

## Files Modified

- `custom_components/lipro/__init__.py`
- `custom_components/lipro/control/entry_root_wiring.py`
- `custom_components/lipro/control/service_router_support.py`
- `custom_components/lipro/core/command/post_refresh.py`
- `custom_components/lipro/core/coordinator/runtime_context.py`
- `custom_components/lipro/core/coordinator/runtime_wiring.py`
- `custom_components/lipro/select.py`
- `tests/core/test_control_plane.py`
- `tests/platforms/test_update_background_tasks.py`
- `tests/services/test_services_registry.py`

## Verification

- `uv run pytest -q tests/core/test_control_plane.py tests/services/test_services_registry.py tests/platforms/test_update_background_tasks.py tests/core/test_init.py`

## Scope Notes

- This plan tightened callable truth and adapter returns without reintroducing broad placeholders or hidden runtime backdoors.
