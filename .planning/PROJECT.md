# Project: Lipro-HASS North Star Evolution

**Status:** `active / phase 134 complete; closeout-ready (2026-04-02)`
**Current route:** `v1.40 active milestone route / starting from latest archived baseline = v1.39`；latest archived evidence index = `.planning/reviews/V1_39_EVIDENCE_INDEX.md`.
**Goal:** `以 v1.39 latest archived baseline 为唯一起点，把 RequestPolicy pacing ownership、entity projection de-reflection 与 fan preset truth 在一个 active milestone 内彻底收口，并把默认下一步诚实推进到 milestone closeout。`
**Default next step:** `$gsd-complete-milestone v1.40`
**Archived baseline chain:** latest archived baseline = `v1.39`；previous archived baseline = `v1.38`.

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
  version: v1.40
  name: Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening
  status: active / phase 134 complete; closeout-ready (2026-04-02)
  phase: '134'
  phase_title: request-policy ownership, entity de-reflection, and fan truth hardening
  phase_dir: 134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening
  route_mode: v1.40 active milestone route / starting from latest archived baseline = v1.39
latest_archived:
  version: v1.39
  name: Governance Recovery, Runtime Consistency & Public Contract Correction
  status: archived / evidence-ready (2026-04-02)
  phase: '133'
  phase_title: governance recovery, runtime consistency, and public contract correction
  phase_dir: 133-governance-recovery-runtime-consistency-and-public-contract-correction
  audit_path: .planning/v1.39-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_39_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.38
  name: Governance Story Compression, Archive Segregation & Public Entry Simplification
  evidence_path: .planning/reviews/V1_38_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.40 active milestone route / starting from latest archived baseline = v1.39
  default_next_command: $gsd-complete-milestone v1.40
  latest_archived_evidence_pointer: .planning/reviews/V1_39_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->
## Current Milestone (v1.40)

**Name:** `Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening`

**Why it matters:** `v1.39 closeout 后，repo-wide 深审仍明确暴露三类残留：RequestPolicy 仍保留多入口 / 高参数密度 pacing story，entity descriptors 与 binary sensors 仍有反射/stringly projection，fan unknown mode 仍伪装成 cycle，导致平台 truth 与能力 truth 自相矛盾。`

**North-star fit:** `v1.40` 继续沿 single owner、formal home、explicit projection 与 honesty-over-folklore 推进：RequestPolicy 把 pacing state 收回实例 owner；entity/platform projection 不再依赖 dotted-path/getattr 反射；fan preset 投影不再捏造 cycle fallback。`

**Current status:** `active / phase 134 complete; closeout-ready (2026-04-02)`
**Phase range:** `Phase 134 -> 134`
**Starting baseline:** `.planning/v1.39-MILESTONE-AUDIT.md, .planning/reviews/V1_39_EVIDENCE_INDEX.md, .planning/milestones/v1.39-ROADMAP.md, .planning/milestones/v1.39-REQUIREMENTS.md`
**Requirements basket:** `GOV-90, ARC-43, HOT-62, HOT-63, QLT-56, TST-54`
**Latest archived baseline:** `v1.39`
**Latest archived pointer:** `.planning/reviews/V1_39_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.39-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-complete-milestone v1.40`
**Current phase handoff:** `Phase 134 的 3 份 PLAN、3 份 plan summary、phase summary、verification 与 validation 已齐备；当前 route 已推进到 phase complete / closeout-ready。`

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
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

## Current Execution Workspace Inputs

- `.planning/phases/134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening/134-CONTEXT.md`
- `.planning/phases/134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening/134-RESEARCH.md`
- `.planning/phases/134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening/134-01-PLAN.md`
- `.planning/phases/134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening/134-02-PLAN.md`
- `.planning/phases/134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening/134-03-PLAN.md`
- `.planning/phases/134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening/134-01-SUMMARY.md`
- `.planning/phases/134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening/134-02-SUMMARY.md`
- `.planning/phases/134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening/134-03-SUMMARY.md`
- `.planning/phases/134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening/134-SUMMARY.md`
- `.planning/phases/134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening/134-VERIFICATION.md`
- `.planning/phases/134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening/134-VALIDATION.md`
- `.planning/milestones/v1.39-ROADMAP.md`
- `.planning/milestones/v1.39-REQUIREMENTS.md`
- `.planning/v1.39-MILESTONE-AUDIT.md`
- `docs/developer_architecture.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`

## Latest Archived Milestone (v1.39)

**Name:** `Governance Recovery, Runtime Consistency & Public Contract Correction`
**Current status:** `archived / evidence-ready (2026-04-02)`
**Latest archived pointer:** `.planning/reviews/V1_39_EVIDENCE_INDEX.md`
**Archived audit artifact:** `.planning/v1.39-MILESTONE-AUDIT.md`
**Role now:** `作为 v1.40 的 starting baseline / latest archived selector anchor / pull-only evidence home 持续被消费，不再承担 current active milestone 职责。`

## Previous Archived Milestone (v1.38)


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

## Historical Archived Milestone (v1.37)

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
