---
phase: 65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure
plan: "01"
status: completed
completed_at: "2026-03-23T00:00:00Z"
verification:
  - uv run pytest -q tests/core/test_control_plane.py tests/core/test_system_health.py tests/core/test_diagnostics.py tests/core/test_diagnostics_config_entry.py
---

# Phase 65 Plan 01 Summary

## Objective

Remove MagicMock-aware reflection from `runtime_access_support.py` so control-plane runtime readers accept one explicit runtime-entry / coordinator read-model instead of mock-ghost-driven attribute probing.

## Completed Work

- `custom_components/lipro/control/runtime_access_support.py`
  now only accepts explicit instance/class members when materializing runtime entry and coordinator views; it no longer introspects mock children, `inspect.getattr_static(...)`, or instance `__dict__` as production truth.
- `tests/core/test_control_plane.py`
  now uses `SimpleNamespace` / explicit runtime stubs for runtime-access coverage, so tests stop relying on synthetic MagicMock attribute materialization.
- Formal lookup behavior remains stable: mapping-first device lookup, then explicit runtime helper methods (`get_device`, `get_device_by_id`) when the coordinator intentionally exposes them.

## Files Modified

- `custom_components/lipro/control/runtime_access_support.py`
- `tests/core/test_control_plane.py`

## Verification

- `uv run pytest -q tests/core/test_control_plane.py tests/core/test_system_health.py tests/core/test_diagnostics.py tests/core/test_diagnostics_config_entry.py` → `37 passed in 0.77s`

## Scope Notes

- This plan intentionally stopped at runtime-access de-reflection and did not modify device-extras or anonymous-share files.
