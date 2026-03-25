---
phase: 73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization
plan: "01"
subsystem: control-services
tags: [service-router, callbacks, control-plane, device-resolution]
requires:
  - phase: 72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement
    provides: runtime-access and lifecycle convergence baseline
provides:
  - thinner service-router callback bundles
  - explicit control-owned forwarding families for command/schedule/developer handlers
  - focused regression around service handler entrypoints
affects: [phase-73-02, phase-73-03, control-service-surface]
tech-stack:
  added: []
  patterns: [thin callback bundle, control-owned forwarding family]
key-files:
  created:
    - .planning/phases/73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization/73-01-SUMMARY.md
  modified:
    - custom_components/lipro/control/service_router.py
    - custom_components/lipro/control/service_router_handlers.py
    - custom_components/lipro/control/service_router_support.py
    - tests/core/test_init_service_handlers_commands.py
    - tests/core/test_init_service_handlers_device_resolution.py
    - tests/core/test_init_service_handlers_schedules.py
key-decisions:
  - "Keep `service_router.py` as the only outward callback home while shrinking its forwarding families into explicit bundles."
  - "Runtime/device lookup continues to flow through control -> runtime_access, never directly from handlers to runtime internals."
requirements-completed: [ARC-19, HOT-33, TYP-21]
completed: 2026-03-25
---

# Phase 73 Plan 01 Summary

**service-router forwarding families 已切回更薄的 control-owned callback bundles，外部入口仍保持单一。**

## Accomplishments
- 收紧 send-command、schedule 与 developer callback 的 forwarding glue，避免 `service_router.py` 再次堆积多条含混故事线。
- 保持 `service -> control -> runtime_access` 的单向桥接，不让 handler 直摸 runtime internals。
- focused service-handler 套件全绿，证明 callback outward behavior 稳定。

## Proof
- `uv run pytest -q tests/core/test_init_service_handlers.py tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py tests/services/test_services_registry.py` → `27 passed`.
