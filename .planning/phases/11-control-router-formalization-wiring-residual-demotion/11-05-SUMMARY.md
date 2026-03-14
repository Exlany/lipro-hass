---
phase: 11-control-router-formalization-wiring-residual-demotion
plan: "05"
status: completed
completed: 2026-03-14
requirements:
  - CTRL-04
  - RUN-01
---

# Summary 11-05

## Outcome

- `custom_components/lipro/control/runtime_access.py` 已成为 runtime locator、debug-mode policy 与 safe device mapping 的正式 home。
- `custom_components/lipro/control/diagnostics_surface.py` 在 malformed runtime、缺失 device mapping 与异常 anonymous-share 状态下已可退化而非崩溃。
- `custom_components/lipro/core/coordinator/runtime/status/executor.py` 已分离 query 失败与单设备 apply 失败，`custom_components/lipro/runtime_types.py` 也已收窄为 public protocols。

## Verification

- 见 `11-VERIFICATION.md` 的 Phase 11 closeout suite。
- 关键切片：`tests/core/test_control_plane.py`、`tests/core/test_diagnostics.py`、`tests/core/test_system_health.py`、`tests/core/coordinator/runtime/test_status_runtime.py`、`tests/meta/test_dependency_guards.py`。

## Governance Notes

- control/services 不再多点复制 `runtime_data` 探测与 debug gating；formal runtime-access story 已收口。
