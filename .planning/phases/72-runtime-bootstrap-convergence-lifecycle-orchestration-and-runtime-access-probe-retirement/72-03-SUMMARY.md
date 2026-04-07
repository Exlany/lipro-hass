---
phase: 72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement
plan: "03"
subsystem: lifecycle
tags: [entry-root, lifecycle, wiring, typing, home-assistant]
requires:
  - phase: 72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement
    provides: runtime-access convergence baseline
provides:
  - typed entry root wiring without kwargs-bag folklore
  - slimmer lifecycle controller/support seam
  - focused HA entry lifecycle regressions
affects: [phase-72-04, init-wiring, entry-lifecycle]
tech-stack:
  added: []
  patterns: [typed root wiring, slimmer controller-support contract]
key-files:
  created:
    - .planning/phases/72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement/72-03-SUMMARY.md
  modified:
    - custom_components/lipro/control/entry_root_wiring.py
    - custom_components/lipro/control/entry_lifecycle_controller.py
    - custom_components/lipro/control/entry_lifecycle_support.py
    - custom_components/lipro/__init__.py
    - tests/core/test_entry_root_wiring.py
    - tests/core/test_entry_lifecycle_controller.py
    - tests/core/test_init_runtime_setup_entry.py
    - tests/core/test_init_runtime_unload_reload.py
key-decisions:
  - "Keep HA root modules as thin adapters and move lifecycle collaboration into named typed seams."
  - "Do not reintroduce a giant kwargs bag; root wiring must stay explicit and patchable."
requirements-completed: [ARC-19, HOT-32, TYP-21, TST-22, QLT-30]
completed: 2026-03-25
---

# Phase 72 Plan 03 Summary

**entry root wiring 与 lifecycle orchestration 已收口到更显式、更可 patch 的 typed collaborator seams。**

## Accomplishments
- 压缩 `entry_root_wiring.py`、`EntryLifecycleController` 与 support seam 的参数袋式装配，让 `__init__.py` 继续保持 thin adapter。
- 保留现有 Home Assistant 入口行为，不让 lifecycle 细节反向定义新的 runtime root 或 wiring folklore。
- focused entry/lifecycle 回归套件稳定通过，验证 setup/unload/reload 主链未回退。

## Proof
- `uv run pytest -q tests/core/test_entry_root_wiring.py tests/core/test_entry_lifecycle_controller.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_unload_reload.py` → `23 passed`.
