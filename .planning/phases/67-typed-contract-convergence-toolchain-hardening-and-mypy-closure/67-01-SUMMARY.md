---
phase: 67-typed-contract-convergence-toolchain-hardening-and-mypy-closure
plan: "01"
status: completed
completed_at: "2026-03-23T18:00:00Z"

requirements_completed:
  - TYP-19
verification:
  - uv run pytest -q tests/core/telemetry/test_models.py tests/core/telemetry/test_sinks.py tests/core/telemetry/test_exporter.py
---

# Phase 67 Plan 01 Summary

## Objective

Converge telemetry models, exporter views, and control-plane bridges onto one honest JSON-safe typed contract story.

## Completed Work

- `custom_components/lipro/core/telemetry/models.py`, `sinks.py`, and `exporter.py` now keep `FailureSummary`, `TelemetryJsonValue`, snapshot payloads, and view payloads as the only formal truth.
- `custom_components/lipro/control/runtime_access_support.py` and `custom_components/lipro/control/telemetry_surface.py` now project telemetry through explicit typed payloads instead of broad `Mapping[str, object]` seams.
- Telemetry-focused tests and replay harness helpers were tightened to use explicit narrowing helpers instead of partial TypedDict folklore.

## Files Modified

- `custom_components/lipro/control/runtime_access_support.py`
- `custom_components/lipro/control/telemetry_surface.py`
- `custom_components/lipro/core/telemetry/exporter.py`
- `custom_components/lipro/core/telemetry/models.py`
- `custom_components/lipro/core/telemetry/sinks.py`
- `tests/core/telemetry/test_exporter.py`
- `tests/core/telemetry/test_models.py`
- `tests/core/telemetry/test_sinks.py`
- `tests/harness/protocol/replay_assertions.py`
- `tests/harness/protocol/replay_report.py`

## Verification

- `uv run pytest -q tests/core/telemetry/test_models.py tests/core/telemetry/test_sinks.py tests/core/telemetry/test_exporter.py`

## Scope Notes

- This plan only tightened telemetry contracts and their assurance surfaces; it did not widen public surfaces or reopen runtime/control roots.
