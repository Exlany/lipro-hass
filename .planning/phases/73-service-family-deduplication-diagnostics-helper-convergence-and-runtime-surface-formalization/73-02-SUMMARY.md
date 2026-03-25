---
phase: 73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization
plan: "02"
subsystem: diagnostics-runtime
tags: [diagnostics, system-health, telemetry, runtime-access, control-plane]
requires:
  - phase: 73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization
    provides: thinner service-router callback bundles
provides:
  - converged diagnostics/system-health helper families
  - flatter runtime-access projections without facade regrowth
  - focused diagnostics/runtime-access regressions
affects: [phase-73-03, diagnostics-surface, system-health]
tech-stack:
  added: []
  patterns: [surface convergence, runtime projection flattening]
key-files:
  created:
    - .planning/phases/73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization/73-02-SUMMARY.md
  modified:
    - custom_components/lipro/diagnostics.py
    - custom_components/lipro/system_health.py
    - custom_components/lipro/control/diagnostics_surface.py
    - custom_components/lipro/control/telemetry_surface.py
    - custom_components/lipro/control/system_health_surface.py
    - custom_components/lipro/control/runtime_access.py
    - custom_components/lipro/control/runtime_access_support.py
    - custom_components/lipro/control/runtime_access_support_views.py
    - custom_components/lipro/control/runtime_access_support_telemetry.py
    - tests/core/test_runtime_access.py
    - tests/core/test_diagnostics.py
    - tests/core/test_system_health.py
    - tests/services/test_services_diagnostics.py
key-decisions:
  - "Do not add a new diagnostics facade root; converge existing helper families inside current control-plane surfaces."
  - "Keep runtime_access outward and typed, while pushing projection details inward into support helpers."
requirements-completed: [ARC-19, HOT-33, TYP-21]
completed: 2026-03-25
---

# Phase 73 Plan 02 Summary

**diagnostics/helper families 与 runtime-access projection 已继续收薄，没有长出新的 facade root。**

## Accomplishments
- 统一 diagnostics、system health、telemetry 与 runtime-access 相关 helper 家族，减少 duplicated helper choreography。
- `runtime_access` outward home 保持不变，但投影与 support 细节被压回更窄的内部协作者。
- diagnostics/system-health/runtime-access focused suites 保持稳定，证明 control-plane outward story 没有漂移。

## Proof
- `uv run pytest -q tests/core/test_runtime_access.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/services/test_services_diagnostics.py` → `41 passed`.
