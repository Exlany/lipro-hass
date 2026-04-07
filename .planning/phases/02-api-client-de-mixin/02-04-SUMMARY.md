---
phase: 02-api-client-de-mixin
plan: "04"
subsystem: api
tags: [refactor, compat, governance, public-surface, handoff]
requires:
  - phase: 02-03
    provides: explicit endpoint collaborators, façade composition root, protected helper compat surface
provides:
  - `LiproClient` 的 formal-root 语义完成降级，`LiproRestFacade` 成为 Phase 2 唯一正式 REST root
  - internal direct-consumer type hints / public-surface 叙事开始切向 `LiproRestFacade`
  - `FILE_MATRIX` / `RESIDUAL_LEDGER` / `KILL_LIST` / `VERIFICATION_MATRIX` 与当前代码真相重新对齐
  - Phase 2 对 Phase 2.5 的 unified protocol root handoff 具备正式文档与 runnable proof
affects: [02.5, 02.6, 03]
completed: 2026-03-12
---

# Phase 02 Plan 02-04 执行总结

## 本次完成

- 更新 `custom_components/lipro/core/api/__init__.py` 与 `custom_components/lipro/core/__init__.py`，把 `LiproRestFacade` 明确为 canonical export / canonical public-root 叙事；`LiproClient` 保留为 transitional compat shell。
- 将 `entry_auth.py`、`core/auth/manager.py`、`core/coordinator/**`、`core/command/dispatch.py` 等 direct-consumer 邻接模块的类型依赖转向 `LiproRestFacade`，避免旧 public name 继续充当“正式根”。
- 回写 `FILE_MATRIX.md`，纠正 `session_state.py` / `auth_recovery.py` / `transport_executor.py` / `endpoints/__init__.py` 等文件的真实定位：保留正式组件、仅把残余 compat spine 视为删除对象。
- 回写 `RESIDUAL_LEDGER.md`，把 `API mixin inheritance` 与 `Legacy public names` 的残留范围收缩到 helper-test / patch seam / typing anchor / factory alias，并明确 handoff 给 `Phase 2.5+`。
- 回写 `KILL_LIST.md` 与 `VERIFICATION_MATRIX.md`，明确 `LiproClient` formal-root demotion 已完成，而真正删除动作仍受 top-level factory / unified protocol root 迁移门槛约束。
- 回写 `ROADMAP.md`、`STATE.md`、`REQUIREMENTS.md`，将 `Phase 1 / 1.5 / 2` 标记为完成，正式解锁 `Phase 2.5`。

## 关键裁决

- **public-root 裁决**：`LiproRestFacade` 是 Phase 2 唯一正式 REST root；`LiproClient` 不能再被描述为 canonical public surface。
- **compat 裁决**：`LiproClient` 与若干 compat wrappers 继续存在，但其合法性仅来自迁移期桥接职责，而不是架构主链地位。
- **文件级裁决**：`session_state.py` / `transport_executor.py` / `auth_recovery.py` / `endpoints/__init__.py` 这些文件本身不删除；真正待删除的是其中的 legacy mixin / compat spine。
- **handoff 裁决**：Phase 2 在 closeout 时允许残留 compat shell，但必须把残留范围、删除门槛、consumer 迁移责任写入治理真源，交给 `Phase 2.5` 继续推进。

## 验证结果

- `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/snapshots/test_api_snapshots.py tests/flows/test_config_flow.py tests/test_coordinator_runtime.py tests/platforms/test_update_task_callback.py tests/meta/test_public_surface_guards.py -q`
  - 结果：`50 passed`
- `uv run pytest tests/core/api/test_api.py tests/core/api/test_api_command_service.py tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_status_service.py tests/core/api/test_protocol_contract_matrix.py tests/snapshots/test_api_snapshots.py tests/flows/test_config_flow.py tests/test_coordinator_runtime.py tests/platforms/test_update_task_callback.py tests/meta/test_public_surface_guards.py -q`
  - 结果：`327 passed`

## 修改文件

- `custom_components/lipro/core/api/__init__.py`
- `custom_components/lipro/core/__init__.py`
- `custom_components/lipro/entry_auth.py`
- `custom_components/lipro/core/auth/manager.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/core/coordinator/orchestrator.py`
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`
- `custom_components/lipro/core/coordinator/runtime/device_runtime.py`
- `custom_components/lipro/core/coordinator/runtime/command/sender.py`
- `custom_components/lipro/core/coordinator/mqtt_lifecycle.py`
- `custom_components/lipro/core/command/dispatch.py`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/REQUIREMENTS.md`
- `.planning/phases/02-api-client-de-mixin/02-04-SUMMARY.md`

## Phase 2 Exit 结论

- `LiproRestFacade` 已形成清晰的 façade + collaborator 正式主链。
- `_ClientEndpointsMixin` 与 endpoint mixin family 已退出生产 façade 根，只剩受控 compat / helper-test 角色。
- `LiproClient` 已完成 formal-root demotion，但 factory alias 与 legacy wrappers 仍在 residual ledger / kill list 中受控存在。
- `Phase 2.5` 现在可基于清晰的 REST child façade 与治理台账，继续统一 `REST / MQTT` 为单一 protocol plane root。
