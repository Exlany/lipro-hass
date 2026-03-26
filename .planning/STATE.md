---
gsd_state_version: 1.0
milestone: v1.21
milestone_name: Governance Bootstrap Truth Hardening & Planning Route Automation
status: active
last_updated: "2026-03-26T00:00:00Z"
progress:
  total_phases: 3
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
---

# Project State

## Project Reference

See: `.planning/PROJECT.md`

**Current milestone:** `v1.21 Governance Bootstrap Truth Hardening & Planning Route Automation`
**Core value:** 以 `v1.20` archived baseline 与 `.planning/reviews/V1_20_EVIDENCE_INDEX.md` latest archived evidence index 作为 active route 的稳定 seed，把 `v1.21` 的下一步工作收束到 `Phase 76` planning，而不是继续依赖 archive-closeout 后的一次性修补。
**Current mode:** `Phase 76 planning-ready`

## Current Position

- `v1.21` 已于 `2026-03-26` 显式开立为 active milestone；当前 phase queue `76 -> 78` 已进入 planning-ready，下一步是 `$gsd-plan-phase 76`。
- latest archived baseline 固定为 `v1.20`；latest archived evidence index 继续是 `.planning/reviews/V1_20_EVIDENCE_INDEX.md`；`v1.19` 继续承担 previous archived baseline。
- recent bootstrap drift 已通过 machine-readable contract 修正；后续重点是把这类 current-route / latest-archive truth 固化为长期维护友好的 planning/bootstrap contract。

## Current Milestone (v1.21)

- **Milestone:** `v1.21 Governance Bootstrap Truth Hardening & Planning Route Automation`
- **Phase range:** `76 -> 78`
- **Milestone status:** `planning-ready (2026-03-26)`
- **Seed input:** `.planning/v1.20-MILESTONE-AUDIT.md`, `.planning/reviews/V1_20_EVIDENCE_INDEX.md`, `.planning/MILESTONES.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `tests/meta/governance_current_truth.py`, `tests/meta/test_governance_milestone_archives.py`
- **Default next command:** `$gsd-plan-phase 76`

## Latest Archived Baseline (v1.20)

- **Milestone:** `v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement`
- **Phase range:** `72 -> 75`
- **Milestone status:** `archived / evidence-ready (2026-03-25)`
- **Route seed:** `.planning/reviews/V1_19_TERMINAL_AUDIT.md`
- **Starting baseline:** `.planning/v1.19-MILESTONE-AUDIT.md`, `.planning/reviews/V1_19_EVIDENCE_INDEX.md`, `.planning/milestones/v1.19-ROADMAP.md`, `.planning/milestones/v1.19-REQUIREMENTS.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-SUMMARY.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VERIFICATION.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VALIDATION.md`
- **Milestone audit:** `.planning/v1.20-MILESTONE-AUDIT.md`
- **Evidence index:** `.planning/reviews/V1_20_EVIDENCE_INDEX.md`
- **Archived snapshots:** `.planning/milestones/v1.20-ROADMAP.md`, `.planning/milestones/v1.20-REQUIREMENTS.md`

## Previous Archived Baseline (v1.19)

- **Milestone:** `v1.19 Audit-Driven Final Hotspot Decomposition & Governance Truth Projection`
- **Phase range:** `71`
- **Archive status:** `archived / evidence-ready (2026-03-25)`
- **Archive assets:** `.planning/v1.19-MILESTONE-AUDIT.md`, `.planning/reviews/V1_19_EVIDENCE_INDEX.md`, `.planning/milestones/v1.19-ROADMAP.md`, `.planning/milestones/v1.19-REQUIREMENTS.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-SUMMARY.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VERIFICATION.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VALIDATION.md`

## Historical Archived Baseline (v1.18)

- **Milestone:** `v1.18 Support-Seam Slimming, OTA Resolver Consolidation & Governance Test Topicization`
- **Phase range:** `70`
- **Archive status:** `archived / evidence-ready (2026-03-24)`
- **Archive assets:** `.planning/v1.18-MILESTONE-AUDIT.md`, `.planning/reviews/V1_18_EVIDENCE_INDEX.md`, `.planning/milestones/v1.18-ROADMAP.md`, `.planning/milestones/v1.18-REQUIREMENTS.md`, `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-SUMMARY.md`, `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-VERIFICATION.md`, `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-VALIDATION.md`

## Recommended Next Command

1. `$gsd-plan-phase 76` —— 先把 `v1.21 / Phase 76` 详细计划落盘
2. `$gsd-execute-phase 76` —— 在 Phase 76 计划确认后执行 current-route/bootstrap truth 收口
3. `$gsd-next` —— 让 GSD 继续在 `v1.21` active route 内自动推进
4. `$gsd-progress` —— 查看当前 active route / latest archived baseline / next command 是否保持一致
5. `uv run python scripts/check_file_matrix.py --check` —— 复核 planning / baseline / review / archive assets 契约
6. `uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_phase75_governance_closeout_guards.py tests/meta/test_version_sync.py` —— 复核 active-route / latest-archive / promoted evidence guards

## Session Continuity

If resuming, read in this order:

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/reviews/V1_20_EVIDENCE_INDEX.md`
7. `.planning/v1.20-MILESTONE-AUDIT.md`
8. `.planning/milestones/v1.20-ROADMAP.md`
9. `.planning/milestones/v1.20-REQUIREMENTS.md`
10. `.planning/reviews/V1_19_TERMINAL_AUDIT.md`
11. `.planning/reviews/V1_19_EVIDENCE_INDEX.md`
12. `.planning/milestones/v1.19-REQUIREMENTS.md`
13. `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-SUMMARY.md`
14. `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VERIFICATION.md`
15. `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VALIDATION.md`
16. `.planning/v1.18-MILESTONE-AUDIT.md`
17. `.planning/reviews/V1_18_EVIDENCE_INDEX.md`

## Historical Continuity Anchors

`v1.1` 已完成全部计划执行：`15 phases / 58 plans` 全绿落表

- `Phase 17` 已完成：最终残留退役 / 类型契约收紧 / 里程碑收官。
- `Phase 24` 已完成并于 2026-03-17 重新验证。
- `Phase 46` 已于 `2026-03-20` 执行完成；follow-up route source = `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md`。
- `v1.13` archive anchors: `.planning/v1.13-MILESTONE-AUDIT.md`, `.planning/reviews/V1_13_EVIDENCE_INDEX.md`, `.planning/milestones/v1.13-ROADMAP.md`, `.planning/milestones/v1.13-REQUIREMENTS.md`
- `v1.12` archive anchors: `.planning/v1.12-MILESTONE-AUDIT.md`, `.planning/reviews/V1_12_EVIDENCE_INDEX.md`, `.planning/milestones/v1.12-ROADMAP.md`, `.planning/milestones/v1.12-REQUIREMENTS.md`
- `v1.20` archive anchors: `.planning/v1.20-MILESTONE-AUDIT.md`, `.planning/reviews/V1_20_EVIDENCE_INDEX.md`, `.planning/milestones/v1.20-ROADMAP.md`, `.planning/milestones/v1.20-REQUIREMENTS.md`
- `v1.19` archive anchors: `.planning/v1.19-MILESTONE-AUDIT.md`, `.planning/reviews/V1_19_EVIDENCE_INDEX.md`, `.planning/milestones/v1.19-ROADMAP.md`, `.planning/milestones/v1.19-REQUIREMENTS.md`
- `v1.16` archive anchors: `.planning/v1.16-MILESTONE-AUDIT.md`, `.planning/reviews/V1_16_EVIDENCE_INDEX.md`, `.planning/milestones/v1.16-ROADMAP.md`, `.planning/milestones/v1.16-REQUIREMENTS.md`
- `v1.6` archive anchors: `.planning/v1.6-MILESTONE-AUDIT.md`, `.planning/reviews/V1_6_EVIDENCE_INDEX.md`, `.planning/milestones/v1.6-ROADMAP.md`, `.planning/milestones/v1.6-REQUIREMENTS.md`
- `v1.5` archive anchors: `.planning/v1.5-MILESTONE-AUDIT.md`, `.planning/reviews/V1_5_EVIDENCE_INDEX.md`, `.planning/milestones/v1.5-ROADMAP.md`, `.planning/milestones/v1.5-REQUIREMENTS.md`

## Governance Truth Sources

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/baseline/*.md` 与 `.planning/baseline/GOVERNANCE_REGISTRY.json`
7. `.planning/reviews/*.md`
8. `docs/developer_architecture.md`
9. `AGENTS.md`
10. `CLAUDE.md`（若使用 Claude Code）
11. 历史执行 / 审计 / 归档文档

## Phase Asset Promotion Contract

- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 是 `.planning/phases/**` 的显式 promoted allowlist。
- `Phase 72 / 73 / 74` 的 audited closeout bundles（`01..04-SUMMARY.md` + `VERIFICATION.md` + `VALIDATION.md`）现已正式提升为长期治理 / CI evidence。
- 未列入 allowlist 的 phase `PLAN / CONTEXT / RESEARCH / PRD` 与临时 closeout 文件默认保持执行痕迹身份；即使 `v1.20` 已归档，`Phase 75` 资产仍按 execution trace 处理，不作为长期治理 / CI 证据。
