---
phase: 74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout
plan: "01"
subsystem: cleanup
tags: [auth, residual, cleanup, service-registry, governance]
requires:
  - phase: 73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization
    provides: converged service/runtime formal homes
provides:
  - retired `services/registrations.py` compat shell
  - truthful auth/service residual ledger updates
  - focused cleanup guards for dead shell retirement
affects: [phase-74-02, control-service-registry, residual-ledger]
tech-stack:
  added: []
  patterns: [physical residual retirement, cleanup guard freeze]
key-files:
  created:
    - .planning/phases/74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout/74-01-SUMMARY.md
  modified:
    - tests/services/test_services_registry.py
    - tests/core/test_init_runtime_unload_reload.py
    - tests/meta/test_dependency_guards.py
    - docs/developer_architecture.md
    - .planning/baseline/PUBLIC_SURFACES.md
    - .planning/baseline/ARCHITECTURE_POLICY.md
    - .planning/reviews/KILL_LIST.md
    - .planning/reviews/RESIDUAL_LEDGER.md
  deleted:
    - custom_components/lipro/services/registrations.py
key-decisions:
  - "Delete the dead compat shell physically instead of letting it linger as pseudo-public surface folklore."
  - "Treat auth/service residual cleanup as governance truth work too, not only code deletion."
requirements-completed: [HOT-34, QLT-30]
completed: 2026-03-25
---

# Phase 74 Plan 01 Summary

**最后一层 service-registration compat shell 已物理退场，auth/service residual 账本也同步讲回真话。**

## Accomplishments
- 删除 `custom_components/lipro/services/registrations.py`，把 service registration 正式 owner 固定回 `control/service_registry.py`。
- 修正相关导入、dependency guards、developer architecture 与 residual/kill truth，避免“代码删了但治理仍承认它存在”。
- focused cleanup 套件通过，证明退休的 compat shell 不会悄悄回流。

## Proof
- `uv run pytest -q tests/services/test_services_registry.py tests/core/test_init_runtime_unload_reload.py tests/meta/test_dependency_guards.py tests/meta/test_phase74_cleanup_closeout_guards.py` → `41 passed`.
