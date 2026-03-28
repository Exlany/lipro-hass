---
gsd_state_version: 1.0
milestone: v1.29
milestone_name: Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization
current_phase: '104'
status: active
last_updated: "2026-03-28T23:55:00.000Z"
progress:
  total_phases: 3
  completed_phases: 2
  total_plans: 3
  completed_plans: 3
---

# Project State

## Project Reference

See: `.planning/PROJECT.md`

**Current milestone:** `v1.29 Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization`
**Active milestone:** `v1.29`
**Core value:** `以 v1.28 latest archived baseline 为唯一 north-star 起点，把 HA 根入口 / pytest topology / 术语 contract 的残留热点回收到诚实 formal homes，并为 Phase 105 的治理数据化与里程碑冻结留出清晰 continuation path。`
**Current mode:** `v1.29 active route / Phase 104 complete / latest archived baseline = v1.28`

## Current Position

- `v1.28` 已完成 `Phase 102` 全部计划、focused closeout proof、repo-wide quality gates 与 milestone audit，现已升级为 latest archived baseline。
- `Phase 103` 已把 `custom_components/lipro/__init__.py` 的 lazy-load / entry-auth / service-registry adapter 支撑抽回 `custom_components/lipro/control/entry_root_support.py`，HA 根入口继续只保留 thin adapter 职责。
- `tests/conftest.py` 已把 topicized collection hooks 与 `_CoordinatorDouble` 下沉到 `tests/topicized_collection.py` / `tests/coordinator_double.py`，fixture giant-root 风险已开始收口。
- `docs/adr/0005-entry-surface-terminology-contract.md` 已明确 `support / surface / wiring / handlers / facade` 的术语裁决，供已完成的 `Phase 104` split 与后续 `Phase 105` 治理数据化复用。
- `Phase 104` 已把 `service_router_handlers.py` 收窄为 family index，并把 schedule/share/diagnostics/maintenance handler homes 显式化。
- `Phase 104` 已把 `CommandRuntime` 的 outcome bookkeeping / reauth handling 抽到 `command_runtime_outcome_support.py`，formal orchestration root 仍留在 `command_runtime.py`。
- `Phase 104` 已完成；service-router family density 与 command-runtime second pass 已不再是假性 residual，剩余未完成项只保留在 `Phase 105` governance rule datafication / milestone freeze。
- maintainer/delegate continuity 仍是组织层高风险；本里程碑继续只负责技术与治理入口写清楚。

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
active_milestone:
  version: v1.29
  name: Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization
  status: active / Phase 104 complete / continuation-ready (2026-03-28)
  phase: '104'
  phase_title: Service-router family split and command-runtime second-pass decomposition
  phase_dir: 104-service-router-family-split-and-command-runtime-second-pass-decomposition
  route_mode: v1.29 active route / Phase 104 complete / latest archived baseline = v1.28
latest_archived:
  version: v1.28
  name: Governance Portability, Verification Stratification & Open-Source Continuity Hardening
  status: archived / evidence-ready (2026-03-28)
  phase: '102'
  phase_title: Governance portability, verification stratification, and open-source continuity hardening
  phase_dir: 102-governance-portability-verification-stratification-and-open-source-continuity-hardening
  audit_path: .planning/v1.28-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_28_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.27
  name: Final Carry-Forward Eradication & Route Reactivation
  evidence_path: .planning/reviews/V1_27_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.29 active route / Phase 104 complete / latest archived baseline = v1.28
  default_next_command: $gsd-discuss-phase 105
  latest_archived_evidence_pointer: .planning/reviews/V1_28_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->

## Current Milestone (v1.29)
- **Milestone:** `v1.29 Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization`
- **Phase range:** `103 -> 105`
- **Current phase:** `Phase 104`
- **Milestone status:** `active / Phase 104 complete / continuation-ready (2026-03-28)`
- **Requirements basket:** `ARC-26`, `TST-35`, `DOC-09`, `QLT-43`, `HOT-44`, `HOT-45`, `TST-36`, `GOV-69`, `QLT-44`
- **Milestone starting evidence:** `.planning/v1.28-MILESTONE-AUDIT.md`, `.planning/reviews/V1_28_EVIDENCE_INDEX.md`, `.planning/milestones/v1.28-ROADMAP.md`, `.planning/milestones/v1.28-REQUIREMENTS.md`
- **Latest archived baseline:** `v1.28`
- **Default next command:** `$gsd-discuss-phase 105`
- **Current follow-up target:** `Phase 105` governance rule datafication / milestone freeze while preserving `v1.28` archived truth

## Latest Archived Milestone (v1.28)
- **Milestone:** `v1.28 Governance Portability, Verification Stratification & Open-Source Continuity Hardening`
- **Phase range:** `102 -> 102`
- **Latest archived phase:** `Phase 102`
- **Milestone status:** `archived / evidence-ready (2026-03-28)`
- **Requirements basket:** `GOV-68`, `TST-34`, `OSS-13`, `QLT-42`
- **Milestone starting evidence:** `.planning/v1.27-MILESTONE-AUDIT.md`, `.planning/reviews/V1_27_EVIDENCE_INDEX.md`, `.planning/milestones/v1.27-ROADMAP.md`, `.planning/milestones/v1.27-REQUIREMENTS.md`
- **Milestone closeout assets:** `.planning/v1.28-MILESTONE-AUDIT.md`, `.planning/reviews/V1_28_EVIDENCE_INDEX.md`, `.planning/milestones/v1.28-ROADMAP.md`, `.planning/milestones/v1.28-REQUIREMENTS.md`
- **Current audit artifact:** `.planning/v1.28-MILESTONE-AUDIT.md`
- **Default next command:** `$gsd-new-milestone`（historical closeout command）
- **Current follow-up target:** serve as latest archived baseline for `v1.29`

## Previous Archived Milestone (v1.27)
- **Milestone:** `v1.27 Final Carry-Forward Eradication & Route Reactivation`
- **Phase range:** `98 -> 101`
- **Latest archived phase:** `Phase 101`
- **Milestone status:** `archived / evidence-ready (2026-03-28)`
- **Requirements basket:** `RES-15`, `HOT-41`, `GOV-65`, `TST-31`, `QLT-39`, `HOT-42`, `GOV-66`, `TST-32`, `QLT-40`, `HOT-43`, `GOV-67`, `TST-33`, `QLT-41`
- **Milestone closeout assets:** `.planning/v1.27-MILESTONE-AUDIT.md`, `.planning/reviews/V1_27_EVIDENCE_INDEX.md`, `.planning/milestones/v1.27-ROADMAP.md`, `.planning/milestones/v1.27-REQUIREMENTS.md`
- **Current audit artifact:** `.planning/v1.27-MILESTONE-AUDIT.md`
- **Default next command:** `$gsd-new-milestone`（historical closeout command）
- **Current follow-up target:** serve as previous archived baseline for `v1.29`

## Historical Archived Milestone (v1.26)
- **Milestone:** `v1.26 Terminal Architecture Audit Follow-through, Typed Mapping Retirement & Hotspot Decomposition`
- **Phase range:** `94 -> 97`
- **Latest archived phase:** `Phase 97`
- **Milestone status:** `archived / evidence-ready (2026-03-28)`
- **Requirements basket:** `TYP-24`, `HOT-41`, `SEC-02`, `ARC-25`, `TST-30`, `QLT-38`
- **Milestone closeout assets:** `.planning/v1.26-MILESTONE-AUDIT.md`, `.planning/reviews/V1_26_EVIDENCE_INDEX.md`, `.planning/milestones/v1.26-ROADMAP.md`, `.planning/milestones/v1.26-REQUIREMENTS.md`
- **Current audit artifact:** `.planning/v1.26-MILESTONE-AUDIT.md`
- **Default next command:** `$gsd-new-milestone`（historical closeout command）
- **Current follow-up target:** serve as historical archived baseline after `v1.28`

## Historical Archived Milestone (v1.25)
- **Milestone:** `v1.25 Hotspot Inward Decomposition, Typed Boundary Hardening & Redaction Convergence`
- **Phase range:** `90 -> 93`
- **Latest archived phase:** `Phase 93`
- **Milestone status:** `archived / evidence-ready (2026-03-28)`
- **Requirements basket:** `HOT-40`, `ARC-24`, `TYP-23`, `SEC-01`, `TST-29`, `QLT-37`
- **Milestone closeout assets:** `.planning/v1.25-MILESTONE-AUDIT.md`, `.planning/reviews/V1_25_EVIDENCE_INDEX.md`, `.planning/milestones/v1.25-ROADMAP.md`, `.planning/milestones/v1.25-REQUIREMENTS.md`
- **Current audit artifact:** `.planning/v1.25-MILESTONE-AUDIT.md`
- **Default next command:** `$gsd-new-milestone`
- **Current follow-up target:** serve as historical archived baseline after `v1.28`

## Historical Archived Milestone (v1.24)

- **Milestone:** `v1.24 Runtime Boundary Tightening, Tooling Kernel Decoupling & Open-Source Entry Convergence`
- **Phase range:** `89 -> 89`
- **Latest archived phase:** `Phase 89`
- **Milestone status:** `archived / evidence-ready (2026-03-27)`
- **Phase 89 closeout summaries:** `.planning/phases/89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence/{89-01-SUMMARY.md,89-02-SUMMARY.md,89-03-SUMMARY.md,89-04-SUMMARY.md}`
- **Phase 89 phase evidence:** `.planning/phases/89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence/{89-VERIFICATION.md,89-VALIDATION.md}`
- **Latest archived baseline:** `v1.24`
- **Milestone starting evidence:** `.planning/v1.23-MILESTONE-AUDIT.md`, `.planning/reviews/V1_23_EVIDENCE_INDEX.md`, `.planning/milestones/v1.23-ROADMAP.md`, `.planning/milestones/v1.23-REQUIREMENTS.md`
- **Milestone closeout assets:** `.planning/v1.24-MILESTONE-AUDIT.md`, `.planning/reviews/V1_24_EVIDENCE_INDEX.md`, `.planning/milestones/v1.24-ROADMAP.md`, `.planning/milestones/v1.24-REQUIREMENTS.md`
- **Current audit artifact:** `.planning/v1.24-MILESTONE-AUDIT.md`
- **Default next command:** `$gsd-new-milestone`
- **Current follow-up target:** next milestone bootstrap / fresh requirements routing

## Previous Archived Baseline (v1.23)

- **Milestone:** `v1.23 Repository-Wide Terminal Code Audit, Residual Eradication & Closeout Truth Freeze`
- **Phase range:** `85 -> 88`
- **Latest archived phase:** `Phase 88`
- **Milestone status:** `archived / evidence-ready (2026-03-27)`
- **Phase 85 closeout summaries:** `.planning/phases/85-terminal-audit-refresh-and-residual-routing/{85-01-SUMMARY.md,85-02-SUMMARY.md,85-03-SUMMARY.md}`
- **Phase 86 closeout summaries:** `.planning/phases/86-production-residual-eradication-and-boundary-re-tightening/{86-01-SUMMARY.md,86-02-SUMMARY.md,86-03-SUMMARY.md,86-04-SUMMARY.md,86-VALIDATION.md}`
- **Phase 87 closeout summaries:** `.planning/phases/87-assurance-hotspot-decomposition-and-no-regrowth-guards/{87-01-SUMMARY.md,87-02-SUMMARY.md,87-03-SUMMARY.md,87-04-SUMMARY.md}`
- **Phase 88 phase evidence:** `.planning/phases/88-governance-sync-quality-proof-and-milestone-freeze/{88-01-SUMMARY.md,88-02-SUMMARY.md,88-03-SUMMARY.md,88-SUMMARY.md,88-VERIFICATION.md,88-VALIDATION.md}`
- **Latest archived baseline:** `v1.23`
- **Milestone starting evidence:** `.planning/v1.22-MILESTONE-AUDIT.md`, `.planning/reviews/V1_22_EVIDENCE_INDEX.md`, `.planning/milestones/v1.22-ROADMAP.md`, `.planning/milestones/v1.22-REQUIREMENTS.md`
- **Milestone closeout assets:** `.planning/v1.23-MILESTONE-AUDIT.md`, `.planning/reviews/V1_23_EVIDENCE_INDEX.md`, `.planning/milestones/v1.23-ROADMAP.md`, `.planning/milestones/v1.23-REQUIREMENTS.md`
- **Current audit artifact:** `.planning/reviews/V1_23_TERMINAL_AUDIT.md`
- **Default next command:** `$gsd-new-milestone`
- **Current follow-up target:** next milestone bootstrap / fresh requirements routing

## Archived Baseline (v1.22)

- **Milestone:** `v1.22 Maintainer Entry Contracts, Release Operations Closure & Contributor Routing`
- **Phase range:** `81 -> 84`
- **Milestone status:** `archived / evidence-ready (2026-03-27)`
- **Milestone audit:** `.planning/v1.22-MILESTONE-AUDIT.md`
- **Evidence index:** `.planning/reviews/V1_22_EVIDENCE_INDEX.md`
- **Archived snapshots:** `.planning/milestones/v1.22-ROADMAP.md`, `.planning/milestones/v1.22-REQUIREMENTS.md`


## Recommended Next Command

1. `$gsd-discuss-phase 105` —— 进入 `Phase 104` 的下一跳，围绕 service-router family split 与 command-runtime second pass 开始上下文收集
2. `$gsd-next` —— 复核自动路由是否已稳定前推到 `Phase 104`
3. `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` —— 复核 parser-stable `current_phase = 103` 与 `status = active`
4. `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 103` —— 复核 `Phase 103` 的 3/3 plans 已完成
5. `uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase103_root_thinning_guards.py` —— 复核 active route / phase103 focused guards
6. `uv run ruff check .` —— 复核 repo-wide lint gate
7. `uv run mypy` —— 复核 repo-wide typing gate

## Session Continuity

If resuming, read in this order:

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/phases/104-service-router-family-split-and-command-runtime-second-pass-decomposition/104-CONTEXT.md`
7. `.planning/phases/104-service-router-family-split-and-command-runtime-second-pass-decomposition/104-RESEARCH.md`
8. `.planning/phases/104-service-router-family-split-and-command-runtime-second-pass-decomposition/104-VERIFICATION.md`
9. `.planning/phases/104-service-router-family-split-and-command-runtime-second-pass-decomposition/104-VALIDATION.md`
10. `.planning/v1.28-MILESTONE-AUDIT.md`
11. `.planning/reviews/V1_28_EVIDENCE_INDEX.md`
12. `.planning/milestones/v1.28-ROADMAP.md`
13. `.planning/milestones/v1.28-REQUIREMENTS.md`



If resuming, read in this order:

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/v1.28-MILESTONE-AUDIT.md`
7. `.planning/reviews/V1_28_EVIDENCE_INDEX.md`
8. `.planning/milestones/v1.28-ROADMAP.md`
9. `.planning/milestones/v1.28-REQUIREMENTS.md`
10. `.planning/phases/102-governance-portability-verification-stratification-and-open-source-continuity-hardening/102-VERIFICATION.md`
11. `.planning/phases/102-governance-portability-verification-stratification-and-open-source-continuity-hardening/102-VALIDATION.md`
12. `.planning/phases/100-mqtt-runtime-and-schedule-service-support-extraction-freeze/100-VERIFICATION.md`
13. `.planning/phases/100-mqtt-runtime-and-schedule-service-support-extraction-freeze/100-VALIDATION.md`
14. `.planning/phases/99-runtime-hotspot-support-extraction-and-terminal-audit-freeze/99-VERIFICATION.md`
15. `.planning/phases/99-runtime-hotspot-support-extraction-and-terminal-audit-freeze/99-VALIDATION.md`
16. `.planning/phases/98-carry-forward-eradication-route-reactivation-and-closeout-proof/98-VERIFICATION.md`
17. `.planning/phases/98-carry-forward-eradication-route-reactivation-and-closeout-proof/98-VALIDATION.md`
18. `.planning/v1.26-MILESTONE-AUDIT.md`
19. `.planning/reviews/V1_26_EVIDENCE_INDEX.md`

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
