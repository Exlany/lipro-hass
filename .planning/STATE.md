---
gsd_state_version: 1.0
milestone: v1.20
milestone_name: Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement
status: archived
last_updated: "2026-03-25T19:30:00Z"
progress:
  total_phases: 4
  completed_phases: 4
  total_plans: 16
  completed_plans: 16
---

# Project State

## Project Reference

See: `.planning/PROJECT.md`

**Current milestone:** `No active milestone route`
**Core value:** 以 `v1.20` archived baseline 与 `.planning/reviews/V1_20_EVIDENCE_INDEX.md` latest pull-only closeout pointer 作为下一条正式路线的唯一 seed；任何后续 work 都必须显式开立新 milestone，不得隐式延续 `Phase 75` closeout truth。
**Current mode:** `no active milestone route / latest archived baseline = v1.20`

## Current Position

- `v1.20` 已于 `2026-03-25` 完成 milestone archive promotion：当前 phase queue `72 -> 75` 全部完成，仓库已无 active milestone route；下一步是 `$gsd-new-milestone`。
- latest archived closeout pointer 已固定为 `.planning/reviews/V1_20_EVIDENCE_INDEX.md`；它只承担 pull-only archived evidence 入口身份。
- `v1.20` 现为 latest archived baseline；`v1.19` 退为 previous archived baseline；`v1.18` 保留为 historical archived baseline。
- 当前 archived baseline 由 `.planning/reviews/V1_19_TERMINAL_AUDIT.md` seed 路线收口而成，并通过 `.planning/v1.20-MILESTONE-AUDIT.md` 与 `.planning/reviews/V1_20_EVIDENCE_INDEX.md` 冻结归档真相。

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

1. `$gsd-new-milestone` —— 以 `v1.20` archived baseline 为起点，显式开立下一条正式路线
2. `$gsd-next` —— 让 GSD 自动路由到 archive-closeout 之后的下一步工作流
3. `$gsd-progress` —— 查看 `no active milestone route / latest archived baseline = v1.20` 的当前状态
4. `uv run python scripts/check_file_matrix.py --check` —— 复核 planning / baseline / review / archive assets 契约
5. `uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_phase75_governance_closeout_guards.py tests/meta/test_version_sync.py` —— 复核 archive pointer / no-active-route / promoted evidence guards

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
