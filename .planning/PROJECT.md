# Project: Lipro-HASS North Star Evolution

**Status:** `active / phase 133 complete; closeout-ready (2026-04-02)`
**Current route:** `v1.39 active milestone route / starting from latest archived baseline = v1.38`；latest archived evidence index = `.planning/reviews/V1_38_EVIDENCE_INDEX.md`.
**Goal:** `完成 v1.39 / Phase 133 的治理恢复、runtime consistency 修补与 public contract correction，并把当前路线推进到 milestone closeout-ready。`
**Default next step:** `$gsd-complete-milestone v1.39`
**Archived baseline chain:** latest archived baseline = `v1.38`；previous archived baseline = `v1.37`.

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
projection_targets:
- .planning/PROJECT.md
- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- .planning/STATE.md
- .planning/MILESTONES.md
active_milestone:
  version: v1.39
  name: Governance Recovery, Runtime Consistency & Public Contract Correction
  status: active / phase 133 complete; closeout-ready (2026-04-02)
  phase: '133'
  phase_title: governance recovery, runtime consistency, and public contract correction
  phase_dir: 133-governance-recovery-runtime-consistency-and-public-contract-correction
latest_archived:
  version: v1.38
  name: Governance Story Compression, Archive Segregation & Public Entry Simplification
  status: archived / evidence-ready (2026-04-02)
  phase: '132'
  phase_title: current-story compression and archive-boundary cleanup
  phase_dir: 132-current-story-compression-and-archive-boundary-cleanup
  audit_path: .planning/v1.38-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_38_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.37
  name: Repo-Wide Terminal Audit, Hotspot Decomposition & Governance Continuity Decisions
  evidence_path: .planning/reviews/V1_37_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.39 active milestone route / starting from latest archived baseline = v1.38
  default_next_command: $gsd-complete-milestone v1.39
  latest_archived_evidence_pointer: .planning/reviews/V1_38_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->
## Current Milestone (v1.39)

**Name:** `Governance Recovery, Runtime Consistency & Public Contract Correction`

**Why it matters:** `v1.38` 已把 current selector、archive/history boundary 与 docs-first governance story 压回单一路径，但 milestone audit 仍明确保留 runtime/service/auth/request-policy/dispatch/firmware 等 sanctioned hotspot 作为后续显式路线；与此同时，当前治理红测继续要求补齐 source-path hygiene、FILE_MATRIX inventory 与 promoted-asset slug 一致性。`

**North-star fit:** `v1.39` 继续沿 single authority chain、formal homes、honesty over folklore 推进：当前路线重新回到 active milestone，治理恢复只修 current truth 与执行入口，runtime/public contract 只允许在既有正式 home 内 inward convergence，不新增第二故事线。`

**Current status:** `active / phase 133 complete; closeout-ready (2026-04-02)`
**Phase range:** `Phase 133 -> 133`
**Starting baseline:** `.planning/v1.38-MILESTONE-AUDIT.md`, `.planning/reviews/V1_38_EVIDENCE_INDEX.md`, `.planning/milestones/v1.38-ROADMAP.md`, `.planning/milestones/v1.38-REQUIREMENTS.md`
**Requirements basket:** `GOV-89, ARC-42, HOT-61, DOC-18, QLT-55, TST-53`
**Latest archived baseline:** `v1.38`
**Latest archived pointer:** `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.38-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-complete-milestone v1.39`
**Current phase handoff:** `Phase 133 的 4/4 计划、4/4 计划摘要、phase summary 与 verification 已完成；当前路线已进入 closeout-ready，下一步应执行 $gsd-complete-milestone v1.39。`

## Primary Sources

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Current Execution Workspace Inputs

- `.planning/phases/133-governance-recovery-runtime-consistency-and-public-contract-correction/133-01-PLAN.md`
- `.planning/phases/133-governance-recovery-runtime-consistency-and-public-contract-correction/133-02-PLAN.md`
- `.planning/phases/133-governance-recovery-runtime-consistency-and-public-contract-correction/133-03-PLAN.md`
- `.planning/phases/133-governance-recovery-runtime-consistency-and-public-contract-correction/133-04-PLAN.md`
- `.planning/phases/133-governance-recovery-runtime-consistency-and-public-contract-correction/133-01-SUMMARY.md`
- `.planning/phases/133-governance-recovery-runtime-consistency-and-public-contract-correction/133-02-SUMMARY.md`
- `.planning/phases/133-governance-recovery-runtime-consistency-and-public-contract-correction/133-03-SUMMARY.md`
- `.planning/phases/133-governance-recovery-runtime-consistency-and-public-contract-correction/133-04-SUMMARY.md`
- `.planning/phases/133-governance-recovery-runtime-consistency-and-public-contract-correction/133-SUMMARY.md`
- `.planning/phases/133-governance-recovery-runtime-consistency-and-public-contract-correction/133-VERIFICATION.md`
- `.planning/v1.38-MILESTONE-AUDIT.md`
- `.planning/codebase/CONCERNS.md`
- `.planning/codebase/ARCHITECTURE.md`

## Latest Archived Milestone (v1.38)

**Name:** `Governance Story Compression, Archive Segregation & Public Entry Simplification`

**Why it matters:** `v1.37` 已冻结为 latest archived baseline，但 current docs / release runbook / governance helpers / route handoff smoke 仍存在 route truth、historical literal 与 promoted asset family 的重复投影。本轮不再扩张 production hotspot，而是把 governance/docs/tests 的当前故事压回更清晰、更可维护的 single source。`

**North-star fit:** `v1.38` 继续沿 single authority chain、docs-first、machine-readable truth、honesty over folklore 推进：live selector 继续由 registry-backed route contract 仲裁，archive/history 退回 pull-only 位置，focused meta guards 不再为重复 prose 承担第二真源角色。`

**Current status:** `archived / evidence-ready (2026-04-02)`
**Phase range:** `Phase 132 -> 132`
**Starting baseline:** `.planning/v1.37-MILESTONE-AUDIT.md, .planning/reviews/V1_37_EVIDENCE_INDEX.md, .planning/milestones/v1.37-ROADMAP.md, .planning/milestones/v1.37-REQUIREMENTS.md`
**Requirements basket:** `AUD-07, GOV-88, DOC-17, OSS-19, QLT-54, TST-52`
**Latest archived baseline:** `v1.38`
**Latest archived pointer:** `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.38-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 132 的 summary / verification / validation / audit / evidence index 已冻结为 archived evidence，后续新路线应从 `$gsd-new-milestone` 开始。`

## Previous Archived Milestone (v1.37)

**Name:** `Repo-Wide Terminal Audit, Hotspot Decomposition & Governance Continuity Decisions`

**Why it matters:** `v1.36` 已完成 latest archived baseline 的 closeout，但 repo-internal hotspot 与 repo-external continuity debt 仍需诚实推进：本轮以全仓终极审阅为起点，把 REST/runtime hotspot 拆回更窄正式 home，同时把 external continuity / private fallback 限定为显式 decision boundary，不再让“后续再说”替代结构化治理。`

**North-star fit:** `v1.37` 继续沿单一主链、显式组合、honesty over folklore 推进：仓内可修的 hotspot 直接 inward decomposition，仓外无法凭空创造的 continuity 现实明确记为治理边界，避免用虚假闭环污染正式现状。`

**Current status:** `archived / evidence-ready (2026-04-01)`
**Phase range:** `Phase 129 -> 131`
**Starting baseline:** `.planning/v1.36-MILESTONE-AUDIT.md`, `.planning/reviews/V1_36_EVIDENCE_INDEX.md`, `.planning/milestones/v1.36-ROADMAP.md`, `.planning/milestones/v1.36-REQUIREMENTS.md`
**Requirements basket:** `AUD-06, ARC-40, HOT-59, TST-50, QLT-52, ARC-41, HOT-60, TST-51, GOV-87, DOC-16, OSS-18, QLT-53`
**Latest archived baseline:** `v1.37`
**Latest archived pointer:** `.planning/reviews/V1_37_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.37-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 129 -> 131 的 summary / verification / audit / evidence index 已冻结为 archived evidence frozen，后续新路线应从 `$gsd-new-milestone` 开始。`

## Historical Archived Milestone (v1.36)

**Name:** `Terminal Residual Convergence, Runtime Access De-Reflection & Open-Source Readiness Hardening`

**Why it matters:** `v1.35` archive promotion 后识别出的三类 remaining concern 已在 `v1.36` 逐项完成 closeout：diagnostics helper shell 的 duplicate mechanics / callback-home shadow 已收口、runtime_access 的 de-reflection / typed telemetry seam 已冻结、开源协作 readiness / benchmark / coverage / continuity 也已从 review note 落成 archived proof。`

**North-star fit:** `v1.36` 沿 single mainline / formal homes / honesty over folklore 完成最终归档：不把 archived `v1.35` 伪装成“全部问题已闭环”，而是把 remaining concern 分解成显式 phases、完成 inward 收口与 typed seam 固化，最终落成 archived closeout truth。`

**Current status:** `archived / evidence-ready (2026-04-01)`
**Phase range:** `Phase 126 -> 128`
**Starting baseline:** `.planning/v1.35-MILESTONE-AUDIT.md`, `.planning/reviews/V1_35_EVIDENCE_INDEX.md`, `.planning/milestones/v1.35-ROADMAP.md`, `.planning/milestones/v1.35-REQUIREMENTS.md`
**Requirements basket:** `ARC-38, HOT-57, GOV-85, TST-48, QLT-50, DOC-15, ARC-39, HOT-58, TST-49, OSS-17, GOV-86, QLT-51`
**Latest archived baseline:** `v1.36`
**Latest archived pointer:** `.planning/reviews/V1_36_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.36-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 126 -> 128 的 summary / verification / audit / evidence index 已冻结为 archived evidence frozen，后续新路线应从 `$gsd-new-milestone` 开始。`

## Historical Archived Milestone (v1.35)

## Historical Archived Reference Appendix

以下锚点保留为 continuity / archive truth 的快速索引，避免新 milestone 激活后丢失旧版本的公开可见性。

## v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement
**Current status:** `archived / evidence-ready (2026-03-20)`

## v1.23 Repository-Wide Terminal Code Audit, Residual Eradication & Closeout Truth Freeze
**Current status:** `archived / evidence-ready (2026-03-21)`

## v1.24 Runtime Boundary Tightening, Tooling Kernel Decoupling & Open-Source Entry Convergence
**Current status:** `archived / evidence-ready (2026-03-21)`

## v1.25 Hotspot Inward Decomposition, Typed Boundary Hardening & Redaction Convergence
**Current status:** `archived / evidence-ready (2026-03-21)`

## v1.28 Governance Portability, Verification Stratification & Open-Source Continuity Hardening
**Current status:** `archived / evidence-ready (2026-03-22)`

## v1.29 Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization
**Current status:** `archived / evidence-ready (2026-03-22)`
**Evidence pointer:** `.planning/reviews/V1_29_EVIDENCE_INDEX.md`
