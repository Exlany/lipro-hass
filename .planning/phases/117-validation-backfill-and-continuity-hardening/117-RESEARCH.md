# Phase 117 Research

**Phase:** `117-validation-backfill-and-continuity-hardening`
**Date:** `2026-03-31`
**Requirements:** `TST-39`, `GOV-73`

## Objective

把 `Phase 112 -> 114` 留下的 validation / changed-surface / continuity 缺口一次补齐，并把 `v1.32 active route / latest archived baseline = v1.31` 的 selector、runbook、evidence chain 重新压回单一 machine-checkable truth。该工作不是新功能开发，也不是下一轮热点瘦身，而是把已经完成的历史成果补成“对人和对机器都一致”的正式治理链。

## Inputs Reviewed

- `.planning/phases/117-validation-backfill-and-continuity-hardening/117-CONTEXT.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `.planning/reviews/V1_31_EVIDENCE_INDEX.md`
- `.planning/v1.31-MILESTONE-AUDIT.md`
- `docs/developer_architecture.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `.planning/phases/112-formal-home-discoverability-and-governance-anchor-normalization/{112-SUMMARY.md,112-VERIFICATION.md}`
- `.planning/phases/113-hotspot-burn-down-and-changed-surface-assurance-hardening/{113-SUMMARY.md,113-VERIFICATION.md,113-AUDIT.md}`
- `.planning/phases/114-open-source-reachability-honesty-and-security-surface-normalization/{114-SUMMARY.md,114-VERIFICATION.md,114-AUDIT.md}`
- `tests/meta/governance_current_truth.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_phase113_hotspot_assurance_guards.py`
- `tests/meta/test_governance_release_continuity.py`
- `tests/meta/test_governance_release_docs.py`
- `tests/meta/test_version_sync.py`

## Findings

1. 当前最大的治理裂缝不是“缺文档”，而是**同一事实在不同权威层发生漂移**：
   - `.planning/ROADMAP.md` 的 Phase 117 概览仍是 planned，但 detail block 被误写成 complete，且 evidence 错挂到 `Phase 116`；
   - `tests/meta/governance_followup_route_current_milestones.py` 仍停留在 `v1.31 archived / no active milestone` 的旧世界，而 `tests/meta/governance_current_truth.py` 已切到 `v1.32 active / phase 116 complete / phase 117 discuss-ready`。
   **结论**：本 phase 必须先修 route truth / test truth 漂移，再谈 closeout。

2. `v1.31` 的 archived evidence chain 现在确实是“verification-ready 但 validation 不完整”：
   - `.planning/v1.31-MILESTONE-AUDIT.md` 明确记录 `112 -> 114` 缺 `VALIDATION.md`；
   - `.planning/reviews/V1_31_EVIDENCE_INDEX.md` 与 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 也只提升了 summary/verification/audit，未提升 validation。
   **结论**：需要补 `112/113/114-VALIDATION.md`，并同步 evidence index / promoted allowlist / milestone audit。

3. `Phase 113` 的 hotspot guard 已落后于 `Phase 116` 真实代码尺寸：
   - `rest_facade.py` 和 `anonymous_share/manager.py` 已瘦身到 ~361 / ~360 行；
   - `tests/meta/test_phase113_hotspot_assurance_guards.py` 仍冻结在 `431 / 430`。
   **结论**：budget guard 必须跟着最新 formal-home reality 收紧，否则 no-growth truth 形同虚设。

4. `.planning/baseline/VERIFICATION_MATRIX.md` 尚未登记 `115 -> 117` 的 active-route contract，尾部仍停在 `113 / 114` closeout 语义。
   **结论**：本 phase 至少要把 `115/116/117` 的 verification contract 补齐，并确保 default next command、route truth、focused proof 都切到当前 active milestone。

5. `.planning/MILESTONES.md` 当前仍混合了 chronology 与 current selector 信息；`docs/MAINTAINER_RELEASE_RUNBOOK.md` 已强调 selector family 应以 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md` 为准。
   **结论**：本 phase 需保持 `MILESTONES.md` 的 human-readable chronology 身份，不让它再次成为第二套 live selector。

## Execution Shape

建议拆为 **3 个 plans**：

- **117-01 Archived evidence/validation backfill**
  - 补 `112-VALIDATION.md`、`113-VALIDATION.md`、`114-VALIDATION.md`
  - 同步 `V1_31_EVIDENCE_INDEX.md`、`PROMOTED_PHASE_ASSETS.md`、`v1.31-MILESTONE-AUDIT.md`
  - 新增或扩展针对 `v1.31` archived bundle 的 meta proof

- **117-02 Active-route continuity repair and stale guard tightening**
  - 修正 `ROADMAP` phase detail / progress drift
  - 更新 `governance_followup_route_current_milestones.py` 到当前 `v1.32` active story
  - 收紧 `Phase 113` hotspot no-growth budgets
  - 补齐 `VERIFICATION_MATRIX` 的 `115 -> 117` 合同块

- **117-03 Phase closeout and next-step freeze**
  - 生成 `117-01/02/03-SUMMARY.md`、`117-VERIFICATION.md`、`117-SUMMARY.md`
  - 把 current route 前推到 `Phase 117 complete; closeout-ready`
  - 让 `$gsd-next` 下一跳自然切到 `$gsd-complete-milestone v1.32`

## Risks

- 若只回写 prose 而不补 meta guards，route drift 会再次在后续 closeout 时复发。
- 若只补 `VALIDATION.md` 而不提升进 evidence index / promoted assets，archived chain 依旧不完整。
- 若直接把 `Phase 117` 改成 complete，却不先修 `governance_followup_route_current_milestones.py` 与 `ROADMAP` detail drift，测试与 selector truth 仍会继续打架。
- 若借此 phase 顺手大范围重构 `status_fallback_support.py` / command family，会让 validation backfill 失焦，违背本 phase 边界。
