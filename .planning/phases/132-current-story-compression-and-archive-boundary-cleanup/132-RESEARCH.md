# Phase 132 Research

## Verdict

最适合单阶段彻收的不是继续扩张 production hotspot，而是治理/文档/测试 current-story compression：

- `docs/developer_architecture.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 首屏仍带 archived-only frozen wording / phase-log 气味。
- `tests/meta/governance_current_truth.py` 同时承载 canonical current-route、historical literals、forbidden prose 与 recent guard inventory，角色过载。
- `tests/meta/test_governance_route_handoff_smoke.py` 混合 docs sync、GSD fast-path smoke 与 recent promoted assets truth，职责不清。
- 多个 predecessor phase guard 仅为检查 `CURRENT_ROUTE` / `CURRENT_MILESTONE_DEFAULT_NEXT` 而重复相同 loop。

## Chosen Scope

1. 切回 `v1.38` active milestone route，并把 planning docs / current docs 压成单一 current story。
2. 在 `tests/meta/governance_contract_helpers.py` 新增 route-marker helper，回收 phase guard 重复断言。
3. 把 legacy archive-history markers 从 `governance_current_truth.py` 拆到更窄 helper home。
4. 收窄 `test_governance_route_handoff_smoke.py`，并把 recent promoted asset coverage 回流到 promoted-phase suite。

## Rejected Alternatives

- **直接处理 `runtime_types.py` / `core/auth/manager.py` / `dispatch.py`**：收益高，但不适合与 current-story compression 混做；guard 风险与 touched scope 都明显更高。
- **一次性 topicize 所有 archive/release mega-tests**：方向正确，但单阶段范围过大；本轮优先收当前 live route / smoke / helper 重复最重的簇。
