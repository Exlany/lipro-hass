---
phase: 02-api-client-de-mixin
plan: "02-01"
subsystem: api
tags: [docs, governance, architecture, verification]
requires:
  - phase: 01.5
    provides: baseline asset pack and formal acceptance truth
provides:
  - Phase 2 slice file-level governance matrix for `core/api`、`tests/core/api`、direct consumer tests
  - Residual/Kill registration for compat wrappers、mixin inheritance、legacy public names
  - Executable responsibility boundaries for `LiproRestFacade` and collaborators
  - Clarified Phase 2 exit contract in `VERIFICATION_MATRIX.md`
affects: [02-02, 02-03, 02-04, 02.5]
completed: 2026-03-12
---

# Phase 02 Plan 02-01 执行总结

## 本次完成

- 补齐 `.planning/reviews/FILE_MATRIX.md` 的 file-level 治理矩阵，覆盖 `custom_components/lipro/core/api/**/*.py`、`tests/core/api/**/*.py`、direct consumer tests，以及高风险 legacy public-name / compat support consumers。
- 回写 `.planning/reviews/RESIDUAL_LEDGER.md` 与 `.planning/reviews/KILL_LIST.md`，把 compat wrappers、mixin inheritance、legacy public names 升级为具名 residual / kill targets，并写清 owner 与删除门槛。
- 强化 `.planning/phases/02-api-client-de-mixin/02-ARCHITECTURE.md`，把 `LiproRestFacade`、`ClientSessionState`、`TransportExecutor`、`RequestPolicy`、`AuthRecoveryCoordinator`、endpoint collaborators、payload normalizers、compat shell 的职责边界写成可执行裁决。
- 回写 `.planning/baseline/VERIFICATION_MATRIX.md`，把 Phase 2 exit contract 从抽象表述收紧为可引用、可检查、可交接的 acceptance truth。
- 运行最小回归护栏：`uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/snapshots/test_api_snapshots.py -q`。

## 修改文件

- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/phases/02-api-client-de-mixin/02-ARCHITECTURE.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/phases/02-api-client-de-mixin/02-01-SUMMARY.md`

## 关键裁决

- `LiproRestFacade` 被再次明确为 **Phase 2 唯一正式 REST root**；`LiproClient` 只允许作为 transitional compat shell 存在，且必须可计数、可删除。
- `ClientSessionState` 成为唯一 session/auth state owner；transport 只读状态，auth recovery 才能改 token / refresh state。
- `TransportExecutor`、`RequestPolicy`、`AuthRecoveryCoordinator`、endpoint collaborators、payload normalizers 被拆成显式协作者，禁止继续借由 mixin inheritance 隐式耦合。
- compat wrappers、mixin spine、legacy public names 不再只是“后续会处理”的口头债务，而是进入正式 `RESIDUAL_LEDGER` / `KILL_LIST` 的文件级治理对象。
- direct consumer tests 被分成 **正式 contract/错误面护栏** 与 **迁移适配消费者** 两类，避免 Phase 2 把 error-surface guards 与 compat consumers 混成一团。
- `tests/test_coordinator_runtime.py`、`tests/platforms/test_update_task_callback.py` 明确不再被误标为 `02-01` direct consumer tests；它们仍是 Phase 2 邻接验证，但不进入本计划的 file-level direct-consumer 名册。

## 验证结果

- 命令：`uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/snapshots/test_api_snapshots.py -q`
- 结果：`6 passed`，`2 snapshots passed`。
- 说明：本次只验证 Phase 1 canonical truth 没被 `02-01` 文档治理工作破坏；未越界运行 `02-02+` 的实现级回归。

## 边界确认

- 本计划 **未修改任何业务代码**，只改治理文档、架构文档、phase exit contract 与执行总结。
- 本计划 **未进入 `02-02`**，没有开始 façade / session / transport / auth recovery 的实现改写。
- 本计划 **未提交 commit**。
- 本计划 **停在主代理复核点**；后续若继续，只应从 `02-02` 进入实现阶段。
