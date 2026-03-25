---
gsd_state_version: 1.0
milestone: v1.20
milestone_name: Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement
status: active
last_updated: "2026-03-25T05:45:35Z"
progress:
  total_phases: 3
  completed_phases: 3
  total_plans: 12
  completed_plans: 12
---

# Project State

## Project Reference

See: `.planning/PROJECT.md`

**Current milestone:** `v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement`
**Core value:** 基于 `v1.19` archived baseline 与 `.planning/reviews/V1_19_TERMINAL_AUDIT.md` 已登记 seeds，把 bootstrap / lifecycle / runtime-access / service-family / auth-legacy residual 沿单一 north-star 主链继续 inward convergence，同时保持 `v1.19` 作为 latest archived baseline。
**Current mode:** `Phase 74 complete`

## Current Position

- `v1.20` 已于 `2026-03-25` 开立为 active milestone route：当前 phase queue = `72 -> 74`，`Phase 72`、`Phase 73` 与 `Phase 74` 已执行完成，下一步是 `$gsd-complete-milestone v1.20`。
- latest archived closeout pointer 继续固定为 `.planning/reviews/V1_19_EVIDENCE_INDEX.md`；它只承担 pull-only archived evidence 入口身份。
- `v1.19` 继续作为 latest archived baseline；`v1.18` 继续作为 previous archived baseline；`v1.17` 保留为 historical archived baseline。
- 当前 active route 来自 `.planning/reviews/V1_19_TERMINAL_AUDIT.md`；所有 non-blocking residual 已显式编排到 `Phase 72 -> 74`，不再保持 ownerless carry-forward。

## Active Milestone (v1.20)

- **Milestone:** `v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement`
- **Phase range:** `72 -> 74`
- **Milestone status:** `active / Phase 74 complete (2026-03-25)`
- **Route seed:** `.planning/reviews/V1_19_TERMINAL_AUDIT.md`
- **Starting baseline:** `.planning/v1.19-MILESTONE-AUDIT.md`, `.planning/reviews/V1_19_EVIDENCE_INDEX.md`, `.planning/milestones/v1.19-ROADMAP.md`, `.planning/milestones/v1.19-REQUIREMENTS.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-SUMMARY.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VERIFICATION.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VALIDATION.md`

## Latest Archived Baseline (v1.19)

- **Milestone:** `v1.19 Audit-Driven Final Hotspot Decomposition & Governance Truth Projection`
- **Phase range:** `71`
- **Archive status:** `archived / evidence-ready (2026-03-25)`
- **Archive assets:** `.planning/v1.19-MILESTONE-AUDIT.md`, `.planning/reviews/V1_19_EVIDENCE_INDEX.md`, `.planning/milestones/v1.19-ROADMAP.md`, `.planning/milestones/v1.19-REQUIREMENTS.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-SUMMARY.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VERIFICATION.md`, `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VALIDATION.md`

## Previous Archived Baseline (v1.18)

- **Milestone:** `v1.18 Support-Seam Slimming, OTA Resolver Consolidation & Governance Test Topicization`
- **Phase range:** `70`
- **Archive status:** `archived / evidence-ready (2026-03-24)`
- **Archive assets:** `.planning/v1.18-MILESTONE-AUDIT.md`, `.planning/reviews/V1_18_EVIDENCE_INDEX.md`, `.planning/milestones/v1.18-ROADMAP.md`, `.planning/milestones/v1.18-REQUIREMENTS.md`, `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-SUMMARY.md`, `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-VERIFICATION.md`, `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-VALIDATION.md`

## Historical Archived Baseline (v1.17)

- **Milestone:** `v1.17 Residual Formalization, Quality-Balance Hardening & Open-Source Contract Closure`
- **Phase range:** `69`
- **Archive status:** `archived / evidence-ready (2026-03-24)`
- **Archive assets:** `.planning/v1.17-MILESTONE-AUDIT.md`, `.planning/reviews/V1_17_EVIDENCE_INDEX.md`, `.planning/milestones/v1.17-ROADMAP.md`, `.planning/milestones/v1.17-REQUIREMENTS.md`, `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-SUMMARY.md`, `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-VERIFICATION.md`, `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-VALIDATION.md`

## Recommended Next Command

1. `$gsd-complete-milestone v1.20` —— 基于已完成的 `Phase 74` gates 执行里程碑 closeout / archive-ready 裁决
2. `$gsd-next` —— 按当前 `STATE.md` 自动路由到 `v1.20` 的 milestone closeout
3. `$gsd-progress` —— 查看 `v1.20 / Phase 74 complete` 的 closeout-ready 状态与归档基线
4. `uv run python scripts/check_file_matrix.py --check` —— 复核 planning / baseline / promoted assets 与 file-matrix 契约
5. `uv run pytest -q tests/meta/test_phase74_cleanup_closeout_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_milestone_archives.py tests/meta/test_version_sync.py tests/meta/governance_followup_route_current_milestones.py` —— 复核 active-route / latest-archive / cleanup closeout guards


## Session Continuity

If resuming, read in this order:

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/reviews/V1_19_TERMINAL_AUDIT.md`
7. `.planning/phases/73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization/73-CONTEXT.md`
8. `.planning/phases/73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization/73-VALIDATION.md`
9. `.planning/v1.19-MILESTONE-AUDIT.md`
10. `.planning/reviews/V1_19_EVIDENCE_INDEX.md`
11. `.planning/milestones/v1.19-REQUIREMENTS.md`
12. `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-SUMMARY.md`
13. `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VERIFICATION.md`
14. `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VALIDATION.md`
15. `.planning/v1.18-MILESTONE-AUDIT.md`
16. `.planning/reviews/V1_18_EVIDENCE_INDEX.md`

## Historical Continuity Anchors

`v1.1` 已完成全部计划执行：`15 phases / 58 plans` 全绿落表

- `Phase 17` 已完成：最终残留退役 / 类型契约收紧 / 里程碑收官。
- `Phase 24` 已完成并于 2026-03-17 重新验证。
- `Phase 46` 已于 `2026-03-20` 执行完成；follow-up route source = `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md`。
- `v1.13` archive anchors: `.planning/v1.13-MILESTONE-AUDIT.md`, `.planning/reviews/V1_13_EVIDENCE_INDEX.md`, `.planning/milestones/v1.13-ROADMAP.md`, `.planning/milestones/v1.13-REQUIREMENTS.md`
- `v1.12` archive anchors: `.planning/v1.12-MILESTONE-AUDIT.md`, `.planning/reviews/V1_12_EVIDENCE_INDEX.md`, `.planning/milestones/v1.12-ROADMAP.md`, `.planning/milestones/v1.12-REQUIREMENTS.md`
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
- 未列入 allowlist 的 phase `PLAN / CONTEXT / RESEARCH / PRD` 与临时 closeout 文件默认保持执行痕迹身份，不作为长期治理 / CI 证据。
