---
phase: 73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization
plan: "03"
subsystem: runtime-platform
tags: [schedule, runtime-surface, entities, platforms, typing]
requires:
  - phase: 73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization
    provides: diagnostics/helper convergence baseline
provides:
  - formal schedule runtime service contract
  - tighter entity/platform runtime lookup contracts
  - focused runtime/platform regressions around schedule and entity behavior
affects: [phase-73-04, schedule-surface, platform-runtime-contract]
tech-stack:
  added: []
  patterns: [runtime-owned schedule service, explicit platform runtime contract]
key-files:
  created:
    - .planning/phases/73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization/73-03-SUMMARY.md
  modified:
    - custom_components/lipro/core/coordinator/services/schedule_service.py
    - custom_components/lipro/core/coordinator/services/__init__.py
    - custom_components/lipro/core/coordinator/runtime_wiring.py
    - custom_components/lipro/core/coordinator/coordinator.py
    - custom_components/lipro/runtime_types.py
    - custom_components/lipro/services/schedule.py
    - custom_components/lipro/helpers/platform.py
    - custom_components/lipro/entities/base.py
    - tests/core/coordinator/services/test_schedule_service.py
    - tests/core/test_init_service_handlers_schedules.py
    - tests/services/test_services_schedule.py
    - tests/platforms/test_entity_base.py
    - tests/platforms/test_platform_entities_behavior.py
key-decisions:
  - "Keep schedule writes on the runtime-owned service chain instead of letting services/platforms improvise side routes."
  - "Entity/platform layers consume explicit runtime contracts and stop treating raw device stores as fallback truth."
requirements-completed: [ARC-19, HOT-33, TYP-21]
completed: 2026-03-25
---

# Phase 73 Plan 03 Summary

**schedule runtime surface 已 formalize，entity/platform runtime lookup contract 也被继续收紧。**

## Accomplishments
- 让 `services/schedule.py` 继续只经过 runtime-owned schedule service，而不是回流到临时 glue 或 raw protocol side route。
- 压缩 `helpers/platform.py` 与 `entities/base.py` 的 runtime lookup 口径，保持 platform/entity 只消费显式 contract。
- runtime/platform focused 回归全绿，证明 schedule、entity base 与平台行为没有退化。

## Proof
- `uv run pytest -q tests/core/coordinator/test_runtime_root.py tests/core/test_init_service_handlers_schedules.py tests/services/test_services_schedule.py tests/platforms/test_entity_base.py tests/platforms/test_platform_entities_behavior.py tests/platforms/test_fan_entity_behavior.py tests/platforms/test_light_entity_behavior.py tests/platforms/test_select_behavior.py` → `136 passed`.
