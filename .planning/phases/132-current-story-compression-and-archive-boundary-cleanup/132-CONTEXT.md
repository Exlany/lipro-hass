# Phase 132: current-story compression and archive-boundary cleanup - 背景

**Gathered:** 2026-04-02
**Status:** 规划就绪
**Source:** v1.37 archived baseline + repo-wide governance/docs/test audit

<domain>
## 阶段边界

本阶段承接 `AUD-07, GOV-88, DOC-17, OSS-19, QLT-54, TST-52`，目标不是继续扩张 production hotspot inward split，而是把 governance/docs/tests 当前真相压回更单一的 live-selector story：current docs 只讲当前路由与 latest archived pointer，archive/history 退回 pull-only 边界，route-marker 与 promoted-asset 断言不再在多处重复展开。

</domain>

<decisions>
## 实施决策

### Locked Decisions
- canonical current-route truth 继续只认 `.planning/baseline/GOVERNANCE_REGISTRY.json::planning_route` 与其投影，不新增第二份 selector authority。
- 本轮允许改动 planning docs、developer/runbook docs、`tests/meta` helpers 与 focused governance suites；除非遇到直接 blocker，不重开 production hotspot 拆分。
- `test_governance_route_handoff_smoke.py` 必须收窄到 docs/gsd fast-path smoke；recent promoted asset family 回归 promoted suites。
- historical archive literals 允许保留，但必须退出 `governance_current_truth.py` 当前真相 home。

### the agent's Discretion
- recent promoted-phase coverage 的数据化呈现方式。
- route-marker helper 的命名与是否顺手回收若干 phase guard 重复 loop。

</decisions>

<canonical_refs>
## 权威参考

### Route / Governance Truth
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

### Current Docs / Public Entry
- `docs/developer_architecture.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `docs/README.md`
- `CONTRIBUTING.md`
- `SUPPORT.md`
- `SECURITY.md`

### Governance Helpers / Suites
- `tests/meta/governance_current_truth.py`
- `tests/meta/governance_contract_helpers.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/test_governance_promoted_phase_assets.py`
- `tests/meta/governance_followup_route_current_milestones.py`

</canonical_refs>

<specifics>
## 具体关注点

- current selector / latest archived pointer / default next command 不再在 docs 与 tests 中重复手写近似文案。
- developer architecture / release runbook 首屏只讲 current route 与职责边界，不再混用 archived-only frozen wording 作为当前入口。
- recent promoted-phase asset coverage 集中到 promoted suites；handoff smoke 回归更窄职责。
- phase guard 中重复的 current-route markers 改为 shared helper 驱动。

</specifics>

<deferred>
## 延后事项

- `runtime_types.py` / coordinator service-contract family inward split。
- `core/auth/manager.py`、`request_policy.py`、`dispatch.py` 等 production hotspot 的下一轮减压。
- archive mega-tests（尤其 `governance_milestone_archives_assets.py`）进一步 manifest/topicization。

</deferred>
