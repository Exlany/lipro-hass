---
phase: 72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement
plan: "02"
subsystem: control-runtime
tags: [runtime-access, runtime-infra, diagnostics, system-health, typing]
requires:
  - phase: 72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement
    provides: thinner coordinator bootstrap and runtime-root seams
provides:
  - runtime-access read model without probe-style folklore
  - slimmer runtime-infra listener orchestration
  - focused regressions for diagnostics/system-health/runtime-access consumers
affects: [phase-72-03, control-plane, runtime-access]
tech-stack:
  added: []
  patterns: [typed runtime projection, focused listener hotspot split]
key-files:
  created:
    - .planning/phases/72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement/72-02-SUMMARY.md
  modified:
    - custom_components/lipro/control/runtime_access.py
    - custom_components/lipro/control/runtime_access_types.py
    - custom_components/lipro/control/runtime_access_support.py
    - custom_components/lipro/control/runtime_access_support_views.py
    - custom_components/lipro/control/runtime_access_support_members.py
    - custom_components/lipro/runtime_infra.py
    - tests/core/test_runtime_access.py
    - tests/core/test_runtime_infra.py
    - tests/core/test_diagnostics.py
    - tests/core/test_system_health.py
    - tests/services/test_maintenance.py
key-decisions:
  - "Keep `runtime_access.py` as the single outward read home and move probe-like branching back behind typed helpers."
  - "Treat runtime-infra listener wiring as a local hotspot to split, not a reason to add another runtime facade."
requirements-completed: [ARC-19, HOT-32, TYP-21, TST-22, QLT-30]
completed: 2026-03-25
---

# Phase 72 Plan 02 Summary

**`runtime_access` probing folklore 已被退役，`runtime_infra` listener 热点也被压回更窄的 typed helper 链。**

## Accomplishments
- 收紧 `runtime_access` 读模型与 support/views/members typing，让 control-plane 继续只消费单一 outward runtime truth。
- 切薄 `runtime_infra.py` 的 listener/lookup 热点，避免 runtime listener glue 再次长成隐式第二故事线。
- diagnostics、system health、maintenance 与 runtime-access focused suites 保持稳定，通过本地回归锁住收口结果。

## Proof
- `uv run pytest -q tests/core/test_runtime_access.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_runtime_infra.py tests/services/test_maintenance.py` → `30 passed`.
