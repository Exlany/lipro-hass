# Phase 117: Validation backfill and continuity hardening - Context

**Gathered:** 2026-03-31
**Status:** Draft planning workspace

<domain>
## Phase Boundary

本 phase 处理 `TST-39` 与 `GOV-73`：补齐 `Phase 112 -> 114` 的 validation / changed-surface / continuity 资产，并把 active route 与 latest archived baseline 之间的 selector、runbook、evidence chain 重新压回单一 machine-checkable truth。

本 phase 的核心不是再开新功能，也不是顺手重构所有剩余热点，而是：
- 回补 `Phase 112 -> 114` 已完成成果对应的 validation / changed-surface / continuity proof，使 promoted evidence、runbook 与 current-route selector 不再脱节；
- 让 `docs/developer_architecture.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、planning selector family 与 meta guards 对 `v1.32 active route / v1.31 latest archived baseline` 给出同一条故事线；
- 修复当前 continuity truth 中已经出现的复制残留 / stale guard / archived-vs-active 漂移，避免 route truth 退回成“只有对话知道、文件彼此不一致”的状态。

本 phase **不**处理：
- 新 public API、新 outward root、新 compat shell；
- 伪造 maintainer continuity、delegate identity、non-GitHub fallback 或任何仓外事实；
- 把 `v1.31` archived baseline 重新写成 active route；
- 借题发挥把 `status_fallback_support.py`、`services/command.py`、`dispatch.py` 等下一轮热点一次性全部重构完；这些可作为 follow-up，但不是本 phase 的主目标。
</domain>

<decisions>
## Implementation Decisions

- **D-01:** archived truth 继续以 `v1.31` 为 latest archived baseline；active selector 继续以 `v1.32 / Phase 117` 为当前路线，不允许通过改写 archived verdict 来掩盖 current-route continuity 缺口。
- **D-02:** Phase 117 应优先修复 machine-checkable truth 漂移，例如 `.planning/ROADMAP.md` 中 `Phase 117` 误写为 complete、evidence 误指向 `Phase 116`，以及 `tests/meta/test_phase113_hotspot_assurance_guards.py` 中对 `rest_facade.py` / `anonymous_share/manager.py` 的 stale hotspot budgets。
- **D-03:** validation backfill 只围绕 `Phase 112 -> 114` 已交付的正式成果展开：`112` 的 discoverability / governance anchors、`113` 的 hotspot assurance / changed-surface gate、`114` 的 open-source reachability / release continuity truth；不新增另一条“补证专用故事线”。
- **D-04:** `docs/developer_architecture.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 必须和 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md` 保持相同的 active/archive selector 叙事；`.planning/MILESTONES.md` 继续只做 chronology / human-readable archive，不晋升为 selector authority。
- **D-05:** 本 phase 的测试/守卫优先补 focused continuity proof：route handoff、phase-history continuity、release docs continuity、changed-surface hotspot budgets 与 promoted-evidence discoverability，而不是依赖仓库全量回归“碰巧发现”治理漂移。
- **D-06:** 发现的下一批生产热点（`custom_components/lipro/core/api/status_fallback_support.py`、`custom_components/lipro/services/command.py`、`custom_components/lipro/core/command/{dispatch.py,result_policy.py}`、`custom_components/lipro/core/auth/manager.py`、`custom_components/lipro/entities/firmware_update.py`）仅作为后续 phase 候选；除非直接关系到 validation truth，否则本 phase 不扩大为新一轮 hotspot burn-down。
</decisions>

<canonical_refs>
## Canonical References

- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `docs/developer_architecture.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `.planning/phases/112-formal-home-discoverability-and-governance-anchor-normalization/112-SUMMARY.md`
- `.planning/phases/112-formal-home-discoverability-and-governance-anchor-normalization/112-VERIFICATION.md`
- `.planning/phases/113-hotspot-burn-down-and-changed-surface-assurance-hardening/113-SUMMARY.md`
- `.planning/phases/113-hotspot-burn-down-and-changed-surface-assurance-hardening/113-VERIFICATION.md`
- `.planning/phases/114-open-source-reachability-honesty-and-security-surface-normalization/114-SUMMARY.md`
- `.planning/phases/114-open-source-reachability-honesty-and-security-surface-normalization/114-VERIFICATION.md`
- `tests/meta/governance_current_truth.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/test_phase112_formal_home_governance_guards.py`
- `tests/meta/test_phase113_hotspot_assurance_guards.py`
- `tests/meta/test_governance_release_continuity.py`
- `tests/meta/test_governance_release_docs.py`
- `tests/meta/test_version_sync.py`
- `tests/meta/governance_followup_route_current_milestones.py`
</canonical_refs>

<specifics>
## Specific Ideas

- 当前 selector truth 已统一承认 `Phase 117 discuss-ready`，但 `.planning/ROADMAP.md` 的 `Phase 117` 详情段落仍误写成 `Complete (2026-03-31)` 且 evidence 指向 `Phase 116`；这类复制残留正是本 phase 要消除的 continuity drift。
- `tests/meta/test_phase113_hotspot_assurance_guards.py` 仍冻结 `rest_facade.py=431`、`anonymous_share/manager.py=430`，而 `Phase 116` 已将它们实际收窄到约 `361/360` 行；guard truth 已落后于当前代码与 route summary。
- `Phase 112 -> 114` 的 summary / verification 已存在，但 changed-surface / promoted-evidence / selector continuity 仍未完全形成“从 archived baseline 到 active route 的一条可机器追踪链”。
- 当前最大的生产热点已经前移到 `status_fallback_support.py` 与 command family；Phase 117 可以记录这些 follow-up targets，但不要让 validation backfill 被新的代码重构吞掉。
</specifics>

<risks>
## Risks

- 如果只更新 prose、不补 focused tests 与 guard rails，`$gsd-next` 与 route continuity 很容易再次漂移。
- 如果把 `Phase 117` 扩张成“顺便重构所有热点”，validation backfill 将再次延期，active-route truth 继续处于半同步状态。
- 如果通过修改 archived evidence 来掩盖 continuity 缺口，会模糊 `latest archived baseline` 与 `current active route` 的 authority boundary。
- 如果新的守卫仍然依赖宽松字符串匹配而非明确 contract，下一次 closeout 仍会留下 stale budget / stale pointer / stale route 文案。
</risks>
