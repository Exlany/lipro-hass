---
phase: 66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening
plan: "02"
status: completed
completed_at: "2026-03-23T00:00:00Z"
verification:
  - uv run pytest -q tests/core/test_init.py tests/core/test_init_runtime_setup_entry.py tests/platforms/test_sensor.py tests/platforms/test_select_models.py
  - uv run pytest -q tests/platforms/select_setup_behavior_cases.py
---

# Phase 66 Plan 02 Summary

## Objective

Keep HA root adapters on one thin explicit story by removing duplicated stub folklore from `__init__.py` and replacing runtime-only dynamic imports in `sensor.py` / `select.py` with the formal `entities.base.LiproEntity` home.

## Completed Work

- `custom_components/lipro/__init__.py` now keeps one authoritative Protocol/stub block while preserving the lazy patchable constructor aliases required by runtime wiring and tests.
- `custom_components/lipro/sensor.py` now directly imports `LiproEntity` from the formal entity-base home instead of resolving it through runtime `__import__` folklore.
- `custom_components/lipro/select.py` now directly imports `LiproEntity` from the same formal home and no longer carries runtime-only import indirection.
- Existing HA root / platform regression suites continue to prove that patchable top-level aliases and setup behavior remain stable.

## Files Modified

- `custom_components/lipro/__init__.py`
- `custom_components/lipro/sensor.py`
- `custom_components/lipro/select.py`

## Verification

- `uv run pytest -q tests/core/test_init.py tests/core/test_init_runtime_setup_entry.py tests/platforms/test_sensor.py tests/platforms/test_select_models.py` → `109 passed in 1.59s`
- `uv run pytest -q tests/platforms/select_setup_behavior_cases.py` → `2 passed in 0.07s`

## Scope Notes

- This plan intentionally preserved the lazy top-level constructor aliases in `__init__.py`; it only removed duplicated stub truth and platform-level dynamic import folklore.
