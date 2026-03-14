# Phase 06: Assurance Plane 正式化 - Architecture

**Status:** Execution-aligned
**Updated:** 2026-03-13

## Architectural Goal

把“北极星文档 + baseline 资产 + runtime telemetry + meta tests + CI gates”收敛为一套正式 Assurance Plane，使任何未来改动都必须同时通过：
- 架构边界；
- 治理台账；
- 文档 authority；
- 关键 runtime telemetry / snapshot / integration evidence。

## Formal Components

### 1. Assurance taxonomy docs
- 描述什么是 architecture guard、governance guard、runtime assurance、validation artifact；
- 给出唯一 truth source 顺序与 phase 验收模板。

### 2. Governance checker
- 枚举真实 `.py` 文件；
- 校验 `FILE_MATRIX` / `RESIDUAL_LEDGER` / `KILL_LIST` / authority docs 与仓库现状一致；
- 本地与 CI 共用同一套检查逻辑。

### 3. Meta guards
- `tests/meta/` 是 assurance enforcement 的正式入口；
- dependency/public-surface/governance 三类 guard 必须协同阻断退化。

### 4. Runtime evidence
- `CoordinatorTelemetryService` 提供 runtime snapshot；
- snapshot/integration tests 负责证明新正式结构真实可运行，而不是只存在于文档。

### 5. CI / pre-commit gates
- 本地、pre-push、CI 三层 gate 口径一致；
- “结构未退化”必须先于“功能仍可跑”被验证。

## Phase 6 Execution Shape

### `06-01` — taxonomy + truth order
- 固化 assurance taxonomy、truth sources、authority order；
- 让 Phase 7 可以直接继承这套 closeout 模板。

### `06-02` — governance + meta guard
- 用 checker + tests 把 repo governance 变成正式 gate；
- 阻断 count drift、authority drift、residual drift。

### `06-03` — runtime evidence
- 把 runtime telemetry / snapshot / integration evidence 对齐到正式结构；
- 尽量把旧 private-field 断言迁移到 formal surface。

### `06-04` — CI / validation closeout
- 在 CI 与 pre-commit 中固化 assurance gates；
- 形成完整 phase validation package。
