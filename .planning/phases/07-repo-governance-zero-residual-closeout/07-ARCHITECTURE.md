# Phase 07: 全仓治理与零残留收尾 - Architecture

**Status:** Execution-aligned
**Updated:** 2026-03-13

## Architectural Goal

让仓库的“代码 / 测试 / planning / docs / governance / agent guide”全部围绕同一套北极星终态和同一套活跃真源运转，不再存在：
- 双权威文档；
- 无 owner 的 compat 残留；
- 未覆盖的 Python 文件；
- 已过期但仍在主叙事中的历史审计结论。

## Formal Components

### 1. File-level governance truth
- `FILE_MATRIX` 必须覆盖全部 404 个 `.py` 文件；
- 每个文件要有 owner phase、分类、状态与 residual link。

### 2. Residual closeout truth
- `RESIDUAL_LEDGER` 记录仍存在的过渡层；
- `KILL_LIST` 记录明确删除门槛与状态；
- 二者必须和代码现状、文档现状保持一致。

### 3. Active docs authority
- north-star / planning / developer docs 各司其职；
- 历史报告与 archive 只作历史参考，不参与当前仲裁。

### 4. Repository execution guide
- `AGENTS.md` 是正式执行契约；
- 若存在 `agent.md`，只能作为 pointer / 索引，不引入第二套规则。

## Canonical Direction

```text
Repository inventory
  -> FILE_MATRIX (file-level truth)
  -> RESIDUAL_LEDGER / KILL_LIST
  -> active docs authority alignment
  -> final closeout report + agent guide pointer
```

## Phase 7 Execution Shape

### `07-01` — file matrix finalization
- 统计全部 `.py` 文件；
- 生成 file-level matrix；
- 对齐 counts / owners / residual links。

### `07-02` — residual cleanup
- 删除或正式归档 compat/legacy/shadow/docs；
- 关闭可关闭的 residual ledger / kill items。

### `07-03` — docs & guide alignment
- 对齐 north-star / developer / planning / tests 文档；
- 产出 `agent.md` pointer，并更新 `AGENTS.md` 的 authority 说明。

### `07-04` — final closeout report
- 生成终态完整报告；
- 给出 remaining evolution opportunities，但不得回退 active authority。
