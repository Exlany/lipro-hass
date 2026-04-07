# Phase 63: Governance truth realignment, typed runtime access, and hidden-root closure - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning
**Source:** Post-v1.13 audit refresh + active governance truth

<domain>
## Phase Boundary

本 phase 只处理 fresh audit 仍明确指出、且可由仓库代码/文档/测试真实解决的尾债：

- governance latest-pointer / archive route / `MILESTONES` current-story drift
- `RuntimeAccess` 的 typed read-model 收口与 `__init__.py` thin-adapter follow-through
- `scripts/check_file_matrix_registry.py`、API/meta topic suites 的 hidden-root / second-truth 收口
- command failure / anonymous-share follow-through 的 stringly / `Any` typed tightening

不做：
- 新增第二 formal root
- conversation-only “建议式”修补
- 无真实制度支撑的人事承诺（如虚构 co-maintainer / SLA）
- 与当前审阅问题无直接关系的大规模换栈

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- 所有改动必须继续沿单一正式主链 inward split，不新增长期 compat shell、public wrapper 或 helper-owned second story。
- 先修治理真相指针、archive route 与 anti-drift guards，再做热点内拆；documentation truth 不得落后于代码与测试。
- `RuntimeAccess` 只能继续收口到 typed read-model / explicit port；不得扩大 `inspect.getattr_static`、MagicMock probing 或 `object` 形态读取的权威范围。
- `custom_components/lipro/__init__.py` 只允许继续变薄；wiring/context factory 应下沉到 `control/` formal homes。
- tooling/test topicization 的目标是消除 hidden-root 与 second-truth，同一 concern 只能保留一个共享 helper home。
- command failure / anonymous-share 只做 inward typed tightening；不得改变 outward behavior 或引入新 public surface。
- 任何新发现 residual 若无法在本 phase 关闭，必须显式登记到 `RESIDUAL_LEDGER.md` / `KILL_LIST.md`，不能只留在对话里。

### Claude's Discretion
- plan 拆分粒度（如治理/运行/工具/测试/typed follow-through 是否分 4 还是 5 个 plans）可按 verification / dependency 最优切分。
- 若 `MILESTONES.md` 需要补齐 `v1.7` ~ `v1.12` 才能消除 stale truth，可在不编造资产的前提下一并修复。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture & Governance Truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 北极星正式架构裁决
- `.planning/PROJECT.md` — 当前 active milestone / archived baseline truth
- `.planning/ROADMAP.md` — `Phase 63` 正式目标、requirements 与 success criteria
- `.planning/REQUIREMENTS.md` — `GOV-46` / `GOV-47` / `HOT-16` / `HOT-17` / `TST-13` / `TYP-16` / `QLT-21`
- `.planning/STATE.md` — 当前 active route 与 recommended commands
- `.planning/MILESTONES.md` — 归档里程碑索引真相
- `.planning/reviews/RESIDUAL_LEDGER.md` — residual 登记规则
- `.planning/reviews/KILL_LIST.md` — delete gate / keep-vs-drop 规则
- `.planning/baseline/PUBLIC_SURFACES.md` — formal home / no-second-root 约束
- `.planning/baseline/AUTHORITY_MATRIX.md` — latest closeout pointer / authority wording

### Current Archive Baseline
- `.planning/v1.13-MILESTONE-AUDIT.md` — 最近 archive-ready 里程碑审计结论
- `.planning/reviews/V1_13_EVIDENCE_INDEX.md` — 最近 archive-ready evidence pointer
- `.planning/milestones/v1.13-ROADMAP.md` — `v1.13` 归档 roadmap 快照
- `.planning/milestones/v1.13-REQUIREMENTS.md` — `v1.13` 归档 requirements 快照
- `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-REMEDIATION-ROADMAP.md` — refreshed audit route baseline

### Touched Code / Tests / Docs
- `custom_components/lipro/control/runtime_access.py` — formal runtime-access import home
- `custom_components/lipro/control/runtime_access_support.py` — typed read-model / introspection follow-through hotspot
- `custom_components/lipro/__init__.py` — HA root adapter slimming hotspot
- `custom_components/lipro/core/coordinator/coordinator.py` — command failure consumer hotspot
- `custom_components/lipro/core/coordinator/runtime/command_runtime.py` — command failure producer hotspot
- `custom_components/lipro/core/anonymous_share/manager.py` — anonymous-share manager hotspot
- `custom_components/lipro/core/anonymous_share/share_client_flows.py` — typed submit/refresh follow-through hotspot
- `scripts/check_file_matrix_registry.py` — file-governance hidden-root hotspot
- `tests/core/api/test_api.py` — API suite implicit helper root
- `tests/meta/test_governance_guards.py` — governance suite implicit helper root
- `tests/meta/test_governance_milestone_archives.py` — archive truth guard
- `tests/meta/test_version_sync.py` — latest-pointer / version sync guard
- `docs/README.md` — public docs fast path / latest pointer consumer
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` — maintainer closeout pointer consumer

</canonical_refs>

<specifics>
## Specific Ideas

- 优先考虑把治理指针 / stale pointer / milestone archive drift 收口成第一 plan，这会降低后续执行时的真相噪音。
- `RuntimeAccess` 与 `__init__.py` 需要同一轮看待，避免 “typed port 已有但 HA root 仍动态拼装” 的半吊子状态。
- 对测试 topicization，倾向于提炼明确 `fixtures.py` / `helpers.py` home，而不是继续从旧 giant root 反向导入。
- `file-matrix` 收口应优先减少 second-truth 同步点，而不是只追求换文件名。

</specifics>

<deferred>
## Deferred Ideas

- bus-factor 的真实制度化（delegate / co-maintainer / SLA）需要现实维护者安排；若仓库层无法真实提供，只能文档诚实化，不能伪造制度。
- 若 protocol boundary `object` / `cast(dict(...))` 纯度缺口与本 phase 其他目标产生依赖冲突，可保留到后续独立 phase，但必须登记。

</deferred>

---

*Phase: 63-governance-truth-realignment-typed-runtime-access-and-hidden-root-closure*
*Context gathered: 2026-03-23 via post-v1.13 audit refresh*
