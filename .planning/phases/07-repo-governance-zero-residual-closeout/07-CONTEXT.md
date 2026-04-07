# Phase 07: 全仓治理与零残留收尾 - Context

**Gathered:** 2026-03-13
**Status:** Execution-aligned
**Decision mode:** North-star arbitration by default
**Source:** `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/reviews/FILE_MATRIX.md`, `.planning/reviews/RESIDUAL_LEDGER.md`, `.planning/reviews/KILL_LIST.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `docs/developer_architecture.md`, `docs/archive/COMPREHENSIVE_AUDIT_2026-03-12.md`, `docs/adr/README.md`, repository-wide Python inventory

## Phase Boundary

本阶段唯一目标：

**以全仓视角完成 file-level 治理、compat/legacy/shadow 清理、活跃文档 authority 统一与最终复核闭环，使仓库只保留一套正式架构叙事与一套正式治理真源。**

本阶段必须完成：
- 将 `FILE_MATRIX` 升级为真正 file-level 权威视图；
- 修正 Python 文件总数与活跃文档 authority 漂移；
- 删除或归档 compat/legacy/shadow 残留与无效文档；
- 生成终态收尾报告与后续演进建议；
- 产出仓库执行说明入口，并避免形成第二份冲突 authority。

## Current Structural Tension

当前治理真相已经大体统一，但仍需把最后一批文档和收尾工件补齐：
- 真实 Python 文件总数已经稳定为 **404**，`FILE_MATRIX` 也已成为 file-level authority；
- dead/shadow 模块已从代码中删除，但旧 codebase map 与历史执行文档仍残留陈旧引用；
- 活跃 authority 顺序已经收紧到 north-star + `.planning/*` + `.planning/reviews/*`，但仍需在 `AGENTS.md` / `agent.md` / final report 中明确写死。

## Locked Decisions

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 是终态裁决真源；
- `.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 是当前 phase/status 真源；
- `docs/developer_architecture.md` 只承担开发者解释职责；
- 历史执行/审计文档必须降级为历史快照，不得继续冒充当前 authority；
- 若需要 `agent.md`，它只能是对 `AGENTS.md` 的 thin pointer / 索引，不得形成第二份执行契约。

## Downstream Output

Phase 7 完成后，仓库应留下：
- file-level `FILE_MATRIX`；
- 收口后的 `RESIDUAL_LEDGER / KILL_LIST`；
- 对齐后的 north-star / developer / planning / tests 文档；
- 最终审查报告；
- 单一执行契约入口（`AGENTS.md` + `agent.md` pointer）。
