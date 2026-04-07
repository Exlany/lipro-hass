# Phase 115: Status-fallback query-flow normalization - Context

**Gathered:** 2026-03-31
**Status:** Draft planning workspace (pre-bootstrap)

<domain>
## Phase Boundary

本草案处理 `HOT-48` 的第一刀，但定位为 **contract freeze + regression hardening**：在已局部修补空输入短路的基础上，把 `status_fallback` family 的空输入入口语义与最小 fallback 深度语义冻结为单一正式契约，避免后续再次出现 `query_with_fallback()` 与 binary-split helper 在空集场景下分叉。

本草案优先目标：
- 让 `custom_components/lipro/core/api/status_fallback_support.py` 的两个正式 support 入口对空 `ids` 继续保持一致行为，并明确这是后续重构不得回退的 contract；
- 保持 public home `custom_components/lipro/core/api/status_fallback.py` 不变；
- 用 focused regression test 冻结“空输入不触发无意义 I/O、depth 语义保持可预测”这一契约。

本草案**不**处理：
- 新增 public API；
- 改写 batch fallback / split recursion 的整体算法；
- 触碰 `v1.31` archived-only governance truth；
- 在未启动 `$gsd-new-milestone` 前伪造 active milestone route。
</domain>

<decisions>
## Implementation Decisions

- **D-01:** `query_with_fallback_impl()` 对空 `ids` 直接返回空结果，并记录 fallback depth = `0`，与“无 fallback 发生”的语义保持一致。
- **D-02:** binary-split helper 继续保留现有 `([], 0, {}, 0)` 契约，不扩展到新的返回结构。
- **D-03:** focused regression 只冻结入口语义与 side-effect contract，不把测试耦合到内部 setup 构建细节。
- **D-04:** 本目录下 `115-*` 资产仅作为 pre-bootstrap draft / execution workspace，不改变 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 当前 archived truth。
</decisions>

<canonical_refs>
## Canonical References

- `.planning/MILESTONE-CONTEXT.md`
- `custom_components/lipro/core/api/status_fallback.py`
- `custom_components/lipro/core/api/status_fallback_support.py`
- `tests/core/api/test_api_status_service_fallback.py`
- `.planning/PROJECT.md`
- `.planning/STATE.md`
- `tests/meta/governance_current_truth.py`
</canonical_refs>
