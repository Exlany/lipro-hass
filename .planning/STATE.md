---
gsd_state_version: 1.0
milestone: v1.30
milestone_name: Protocol Hotspot Convergence, Transport De-friendization & Snapshot Surface Slimming
current_phase: '107'
status: active
last_updated: "2026-03-30T00:00:00.000Z"
progress:
  total_phases: 4
  completed_phases: 1
  total_plans: 3
  completed_plans: 3
---

# Project State

## Project Reference

See: `.planning/PROJECT.md`

**Current milestone:** `v1.30 Protocol Hotspot Convergence, Transport De-friendization & Snapshot Surface Slimming`
**Active milestone:** `v1.30`
**Core value:** `以 v1.29 latest archived baseline 为唯一 north-star 起点，把 Phase 106 evidence-only audit 点名的 remaining hotspots 转正为正式 active route，并持续在 formal homes 内 inward split。`
**Current mode:** `v1.30 active route / Phase 107 complete / latest archived baseline = v1.29`

## Current Position

- `v1.29` 已完成 `Phase 103 -> 105` 全部计划、focused closeout proof、repo-wide quality gates 与 milestone audit，现已升级为 latest archived baseline。
- `Phase 107` 已把 REST child-façade init composition、binary-split fallback support 与 request-policy pacing caches 的热点继续压回更局部 collaborator / helper homes。
- 当前 active route 已进入 `Phase 107 complete / continuation-ready`；`Phase 108` 尚未启动，但已作为下一条有 owner 的 continuation phase 写入 roadmap / requirements / governance truth。
- maintainer/delegate continuity 仍是组织层高风险；本里程碑只负责把技术与治理入口写清楚，不伪装成可被单次代码提交解决。
- 历史 terminal audit artifact `.planning/reviews/V1_23_TERMINAL_AUDIT.md` 继续作为早期 residual-routing / coverage-column truth 的 pull-only 审计输入，被 `.planning/baseline/VERIFICATION_MATRIX.md` 与 residual ledgers 引用，但不参与当前 `v1.30` route 决策。

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
active_milestone:
  version: v1.30
  name: Protocol Hotspot Convergence, Transport De-friendization & Snapshot Surface Slimming
  status: active / Phase 107 complete / continuation-ready (2026-03-30)
  phase: '107'
  phase_title: REST/auth/status hotspot convergence and support-surface slimming
  phase_dir: 107-rest-auth-status-hotspot-convergence-and-support-surface-slimming
  route_mode: v1.30 active route / Phase 107 complete / latest archived baseline = v1.29
latest_archived:
  version: v1.29
  name: Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization
  status: archived / evidence-ready (2026-03-30)
  phase: '105'
  phase_title: Governance rule datafication and milestone freeze
  phase_dir: 105-governance-rule-datafication-and-milestone-freeze
  audit_path: .planning/v1.29-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_29_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.28
  name: Governance Portability, Verification Stratification & Open-Source Continuity Hardening
  evidence_path: .planning/reviews/V1_28_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.30 active route / Phase 107 complete / latest archived baseline = v1.29
  default_next_command: $gsd-discuss-phase 108
  latest_archived_evidence_pointer: .planning/reviews/V1_29_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->

## Current Milestone (v1.30)
- **Milestone:** `v1.30 Protocol Hotspot Convergence, Transport De-friendization & Snapshot Surface Slimming`
- **Phase range:** `107 -> 110`
- **Current phase:** `Phase 107`
- **Milestone status:** `active / Phase 107 complete / continuation-ready (2026-03-30)`
- **Requirements basket:** `HOT-46`, `ARC-27`, `TST-37`, `QLT-45`, `RUN-10`, `HOT-47`, `RUN-11`, `GOV-70`
- **Milestone starting evidence:** `.planning/v1.29-MILESTONE-AUDIT.md`, `.planning/reviews/V1_29_EVIDENCE_INDEX.md`, `.planning/milestones/v1.29-ROADMAP.md`, `.planning/milestones/v1.29-REQUIREMENTS.md`
- **Latest archived baseline:** `v1.29`
- **Default next command:** `$gsd-discuss-phase 108`
- **Current follow-up target:** discuss `Phase 108` and continue v1.30 without regressing `Phase 107` or `v1.29` archived truth

## Latest Archived Milestone (v1.29)
- **Milestone:** `v1.29 Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization`
- **Phase range:** `103 -> 105`
- **Latest archived phase:** `Phase 105`
- **Milestone status:** `archived / evidence-ready (2026-03-30)`
- **Requirements basket:** `ARC-26`, `TST-35`, `DOC-09`, `QLT-43`, `HOT-44`, `HOT-45`, `TST-36`, `GOV-69`, `QLT-44`
- **Milestone closeout assets:** `.planning/v1.29-MILESTONE-AUDIT.md`, `.planning/reviews/V1_29_EVIDENCE_INDEX.md`, `.planning/milestones/v1.29-ROADMAP.md`, `.planning/milestones/v1.29-REQUIREMENTS.md`
- **Current audit artifact:** `.planning/v1.29-MILESTONE-AUDIT.md`
- **Default next command:** `$gsd-new-milestone`（historical closeout command）
- **Current follow-up target:** active `v1.30` route / Phase 107 complete / continuation-ready

## Previous Archived Milestone (v1.28)
- **Milestone:** `v1.28 Governance Portability, Verification Stratification & Open-Source Continuity Hardening`
- **Phase range:** `102 -> 102`
- **Latest archived phase:** `Phase 102`
- **Milestone status:** `archived / evidence-ready (2026-03-28)`
- **Requirements basket:** `GOV-68`, `TST-34`, `OSS-13`, `QLT-42`
- **Milestone closeout assets:** `.planning/v1.28-MILESTONE-AUDIT.md`, `.planning/reviews/V1_28_EVIDENCE_INDEX.md`, `.planning/milestones/v1.28-ROADMAP.md`, `.planning/milestones/v1.28-REQUIREMENTS.md`
- **Current audit artifact:** `.planning/v1.28-MILESTONE-AUDIT.md`
- **Default next command:** `$gsd-new-milestone`（historical closeout command）
- **Current follow-up target:** serve as previous archived baseline for `v1.30`

## Recommended Next Command

1. `$gsd-discuss-phase 108` —— 进入 transport/runtime private-state reach-through 的正式 phase discussion 与边界确认。
2. `$gsd-next` —— 复核自动路由是否稳定前推到 `Phase 108` 的下一步工作。
3. `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` —— 复核 parser-stable `milestone = v1.30` 与 `status = active`。
4. `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` —— 复核 `Phase 107` complete、`next_phase = 108` 与 `has_work_in_progress = false`。
5. `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 107` —— 复核 `Phase 107` 三个 plans 全部归档可见。
6. `uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase105_governance_freeze_guards.py tests/meta/test_phase107_rest_status_hotspot_guards.py` —— 复核 current-route / latest-archived / focused-guard 一致性。
7. `uv run ruff check .` —— 复核 repo-wide lint gate。
8. `uv run mypy` —— 复核 repo-wide typing gate。

## Session Continuity

If resuming, read in this order:

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/phases/107-rest-auth-status-hotspot-convergence-and-support-surface-slimming/107-CONTEXT.md`
7. `.planning/phases/107-rest-auth-status-hotspot-convergence-and-support-surface-slimming/107-RESEARCH.md`
8. `.planning/phases/107-rest-auth-status-hotspot-convergence-and-support-surface-slimming/107-VERIFICATION.md`
9. `.planning/phases/107-rest-auth-status-hotspot-convergence-and-support-surface-slimming/107-VALIDATION.md`
10. `.planning/v1.29-MILESTONE-AUDIT.md`
11. `.planning/reviews/V1_29_EVIDENCE_INDEX.md`
12. `.planning/milestones/v1.29-ROADMAP.md`
13. `.planning/milestones/v1.29-REQUIREMENTS.md`

## Historical Continuity Anchors

`v1.1` 已完成全部计划执行：`15 phases / 58 plans` 全绿落表

- `Phase 17` 已完成：最终残留退役 / 类型契约收紧 / 里程碑收官。
- `Phase 24` 已完成并于 2026-03-17 重新验证。
- `Phase 46` 已于 `2026-03-20` 执行完成；follow-up route source = `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md`。
- `v1.21` archive anchors: `.planning/v1.21-MILESTONE-AUDIT.md`, `.planning/reviews/V1_21_EVIDENCE_INDEX.md`, `.planning/milestones/v1.21-ROADMAP.md`, `.planning/milestones/v1.21-REQUIREMENTS.md`
- `v1.20` archive anchors: `.planning/v1.20-MILESTONE-AUDIT.md`, `.planning/reviews/V1_20_EVIDENCE_INDEX.md`, `.planning/milestones/v1.20-ROADMAP.md`, `.planning/milestones/v1.20-REQUIREMENTS.md`
- `v1.19` archive anchors: `.planning/v1.19-MILESTONE-AUDIT.md`, `.planning/reviews/V1_19_EVIDENCE_INDEX.md`, `.planning/milestones/v1.19-ROADMAP.md`, `.planning/milestones/v1.19-REQUIREMENTS.md`
- `v1.16` archive anchors: `.planning/v1.16-MILESTONE-AUDIT.md`, `.planning/reviews/V1_16_EVIDENCE_INDEX.md`, `.planning/milestones/v1.16-ROADMAP.md`, `.planning/milestones/v1.16-REQUIREMENTS.md`
- `v1.13` archive anchors: `.planning/v1.13-MILESTONE-AUDIT.md`, `.planning/reviews/V1_13_EVIDENCE_INDEX.md`, `.planning/milestones/v1.13-ROADMAP.md`, `.planning/milestones/v1.13-REQUIREMENTS.md`
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
