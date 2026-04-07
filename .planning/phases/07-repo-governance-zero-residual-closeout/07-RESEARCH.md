# Phase 07: 全仓治理与零残留收尾 - Research

**Updated:** 2026-03-13
**Status:** Execution-aligned

## Verified Facts

- 仓库真实 Python 文件总数：**404**；
- 当前 `FILE_MATRIX` 已升级为 file-level governance authority；
- dead/shadow cleanup 已完成：`status_strategy.py`、`state_batch_runtime.py`、`group_lookup_runtime.py`、`room_sync_runtime.py`、`device_registry_sync.py` 已从生产代码中删除；
- active docs authority 已基本收紧，但 codebase map / 历史执行文档仍需更明确地降级为 snapshot。

## Required Closeout Order

1. **先冻结 current truth**
   - 没有 `ROADMAP / STATE / REQUIREMENTS / FILE_MATRIX` 的单一口径，就无法宣告 Phase 7 完成；
   - 所以 07-01 必须先锁住 file-level truth 与 counts。

2. **再执行 docs / guide cleanup**
   - 历史/快照文档必须明确降级；
   - `AGENTS.md` / `agent.md` 必须写死 authority order，避免代理再次走偏。

3. **最后生成终态报告**
   - 最终报告只引用活跃真源；
   - 历史报告只作背景，不再承载“当前问题与优先级”。

## Recommended Authority Order

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/ROADMAP.md`
3. `.planning/REQUIREMENTS.md`
4. `.planning/STATE.md`
5. `.planning/baseline/*.md`
6. `.planning/reviews/*.md`
7. `docs/developer_architecture.md`
8. `AGENTS.md` / `agent.md`（执行入口，不重新仲裁架构）
9. 历史执行/审计/归档文档

## Recommended Execution Shape

- `07-01`：冻结 file-level matrix 与最终 residual coverage；
- `07-02`：完成 dead/shadow/docs cleanup 与 remaining residual narration alignment；
- `07-03`：统一 north-star / developer / planning / AGENTS 叙事；
- `07-04`：生成终态完整报告与后续演进建议。
