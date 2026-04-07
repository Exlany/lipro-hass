# Project: Lipro-HASS

**Status:** `active / phase 143 planned; execution-ready (2026-04-04)`
**Current route:** `v1.44 active milestone route / Phase 143 planned / execution-ready / latest archived baseline = v1.43`；latest archived evidence index = `.planning/reviews/V1_43_EVIDENCE_INDEX.md`.
**Goal:** `在 v1.43 archived baseline 之上，把 governance load shedding、derived-truth hardening 与 sanctioned hotspot narrowing 作为一个显式新里程碑重新开启：先减轻 selector / docs / toolchain 的维护负担，再继续 inward split `runtime_types.py`、`request_policy.py`、`dispatch.py`、`auth/manager.py` 与 `firmware_update.py` 这类 formal homes。`
**Default next step:** `$gsd-execute-phase 143`
**Archived baseline chain:** latest archived baseline = `v1.43`；previous archived baseline = `v1.42`.

<!-- governance-route-contract:start -->
```yaml
contract_name: governance-route
projection_targets:
- .planning/PROJECT.md
- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- .planning/STATE.md
- .planning/MILESTONES.md
active_milestone:
  version: v1.44
  name: Governance Load Shedding & Sanctioned Hotspot Narrowing
  status: active / phase 143 planned; execution-ready (2026-04-04)
  phase: '143'
  phase_title: toolchain freshness hardening and route-projection automation
  phase_dir: 143-toolchain-freshness-hardening-and-route-projection-automation
  route_mode: v1.44 active milestone route / Phase 143 planned / execution-ready / latest archived baseline = v1.43
latest_archived:
  version: v1.43
  name: Hotspot Second-Pass Slimming & Governance Load Shedding
  status: archived / evidence-ready (2026-04-04)
  phase: '141'
  phase_title: control/runtime hotspot narrowing and device aggregate hardening
  phase_dir: 141-control-runtime-hotspot-narrowing-and-device-aggregate-hardening
  audit_path: .planning/v1.43-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_43_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.42
  name: Hotspot Burn-Down, Observability Truth & Governance Cost Compression
  evidence_path: .planning/reviews/V1_42_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.44 active milestone route / Phase 143 planned / execution-ready / latest archived baseline = v1.43
  default_next_command: $gsd-execute-phase 143
  latest_archived_evidence_pointer: .planning/reviews/V1_43_EVIDENCE_INDEX.md
contract_version: 1
```
<!-- governance-route-contract:end -->
## Current Milestone (v1.44)

**Milestone theme:** `Governance Load Shedding & Sanctioned Hotspot Narrowing`
**Current status:** `active / phase 143 planned; execution-ready (2026-04-04)`
**Default next command:** `$gsd-execute-phase 143`
**Why it matters:** `v1.43` 的 closeout 把仓库带回了 zero-active archived posture，但这不等于“已没有高价值演进空间”。剩余 work 必须通过新的 milestone 显式重开：治理减负优先清掉 derived truth / route hardcode / toolchain folklore，再继续对 sanctioned hotspots 做 inward split，而不是回流为 Phase 141 的隐性补丁。`
**North-star fit:** `v1.44` 继续沿 single formal home、machine-checkable selector truth、derived-view non-authority 与 helper inward decomposition 推进；正式 roots 继续只允许收窄，不允许误判为 delete target。`
**Latest archived baseline:** `v1.43`
**Latest archived audit artifact:** `.planning/v1.43-MILESTONE-AUDIT.md`
**Current phase handoff:** Phase 142 已完成治理减负 / derived-truth audit；Phase 143 现已生成 143-01 ~ 143-03 计划束，current route 已切到 execution-ready，下一步进入 `$gsd-execute-phase 143`。
**Planned next focus:** 执行 `$gsd-execute-phase 143`，按 143-01 / 143-02 / 143-03 落地 nested worktree proof、freshness/link automation 与 docs-entry continuity guards，然后再继续 Phase 144 -> 145 的 sanctioned hotspot narrowing。

## Latest Archived Milestone (v1.43)

**Name:** `Hotspot Second-Pass Slimming & Governance Load Shedding`

**Why it matters:** `v1.43` 兑现了“不要带着非阻塞残留与治理漂移进入下一轮”的约束：不仅完成了 REST/protocol second-pass slimming、release/governance freshness 与 control/runtime/device hotspot narrowing，还把历史 guard 真源、open-source wording honesty 与 closeout 审计一起收进同一 archived evidence chain。`

**North-star fit:** `v1.43` 继续沿 single formal home、explicit composition、typed boundary、honesty-over-folklore 与 public/internal docs separation 推进；closeout 后不再维持 active milestone 幻觉，而是把所有结论冻结为 latest archived baseline truth。`

**Current status:** `archived / evidence-ready (2026-04-04)`
**Phase range:** `Phase 139 -> 141`
**Starting baseline:** `.planning/v1.42-MILESTONE-AUDIT.md, .planning/reviews/V1_42_EVIDENCE_INDEX.md, .planning/milestones/v1.42-ROADMAP.md, .planning/milestones/v1.42-REQUIREMENTS.md`
**Requirements basket:** `ARC-48, HOT-70, HOT-71, GOV-94, DOC-22, TST-59, AUD-09, GOV-95, DOC-23, TST-60, ARC-49, ARC-50, ARC-51, HOT-72, HOT-73, GOV-96, DOC-24, TST-61`
**Latest archived baseline:** `v1.43`
**Latest archived pointer:** `.planning/reviews/V1_43_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.43-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `v1.43 已完成 milestone closeout；Phase 139 / 140 / 141 的 summaries / verification / validation、milestone audit、archived snapshots 与 evidence index 现已冻结为 latest archived baseline truth。`
## Previous Archived Milestone (v1.42)

**Milestone theme:** `Hotspot Burn-Down, Observability Truth & Governance Cost Compression`
**Current status:** `archived / evidence-ready (2026-04-02)`
**Latest archived pointer:** `.planning/reviews/V1_42_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.42-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Why it matters:** `v1.42 把 sanctioned hotspot burn-down、runtime/service contract split、connect-status outcome honesty 与 docs/archive alignment 冻结成可 pull 的 archived baseline，为 v1.43 提供了单一 predecessor truth。`
**Current phase handoff:** `Phase 137 -> 138` 的 summaries / verification / validation、archived snapshots 与 evidence index 现仅作为 latest archived evidence chain 使用，不再伪装成 live route。`
## Previous Archived Milestone (v1.41)

**Milestone theme:** `Terminal Residual Audit, Remediation Charter & Maintainability Hardening`
**Current status:** `archived / evidence-ready (2026-04-02)`
**Latest archived pointer:** `.planning/reviews/V1_41_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.41-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Why it matters:** `v1.41 的终极审阅报告与 remediation charter 继续作为 v1.43 follow-up decisions 的 predecessor evidence，但必须通过当前仓库路径与 docs contract 重新校准，不能继续携带已过期的验证命令。`

## Previous Archived Milestone (v1.40)

**Name:** `Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening`

**Why it matters:** `契约者在 Phase 134 closeout-ready 后继续要求一次性、彻底地收口 repo-wide 剩余 sanctioned hotspots；因此 v1.40 不直接 closeout，而是显式扩 scope 纳入 runtime_access / auth_service / dispatch 三个 formal-home 热点。`

**North-star fit:** `v1.40` 继续沿 single owner、formal home、typed contract、inward support split 与 honesty-over-folklore 推进：Phase 134 解决 request-policy/entity/fan truth，Phase 135 再把 runtime projection、runtime auth reason 与 command dispatch route 的 stringly drift 收回正式主链。`

**Current status:** `archived / evidence-ready (2026-04-02)`
**Phase range:** `Phase 134 -> 135`
**Starting baseline:** `.planning/v1.39-MILESTONE-AUDIT.md, .planning/reviews/V1_39_EVIDENCE_INDEX.md, .planning/milestones/v1.39-ROADMAP.md, .planning/milestones/v1.39-REQUIREMENTS.md`
**Requirements basket:** `GOV-90, ARC-43, HOT-62, HOT-63, QLT-56, TST-54, ARC-44, HOT-64, HOT-65, HOT-66, QLT-57, TST-55`
**Latest archived baseline:** `v1.40`
**Latest archived pointer:** `.planning/reviews/V1_40_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.40-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 134 -> 135 的 summary / verification / validation / audit / evidence index 已冻结为 latest archived baseline truth。`

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

- `.planning/reviews/V1_41_TERMINAL_AUDIT_REPORT.md`
- `.planning/reviews/V1_41_REMEDIATION_CHARTER.md`
- `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-CONTEXT.md`
- `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-RESEARCH.md`
- `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-01-PLAN.md`
- `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-02-PLAN.md`
- `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-03-PLAN.md`
- `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-01-SUMMARY.md`
- `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-02-SUMMARY.md`
- `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-03-SUMMARY.md`
- `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-SUMMARY.md`
- `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-VERIFICATION.md`
- `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/136-VALIDATION.md`

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
- `.planning/phases/135-runtime-access-auth-and-dispatch-contract-hardening/135-CONTEXT.md`
- `.planning/phases/135-runtime-access-auth-and-dispatch-contract-hardening/135-RESEARCH.md`
- `.planning/phases/135-runtime-access-auth-and-dispatch-contract-hardening/135-01-PLAN.md`
- `.planning/phases/135-runtime-access-auth-and-dispatch-contract-hardening/135-02-PLAN.md`
- `.planning/phases/135-runtime-access-auth-and-dispatch-contract-hardening/135-03-PLAN.md`
- `.planning/phases/135-runtime-access-auth-and-dispatch-contract-hardening/135-01-SUMMARY.md`
- `.planning/phases/135-runtime-access-auth-and-dispatch-contract-hardening/135-02-SUMMARY.md`
- `.planning/phases/135-runtime-access-auth-and-dispatch-contract-hardening/135-03-SUMMARY.md`
- `.planning/phases/135-runtime-access-auth-and-dispatch-contract-hardening/135-SUMMARY.md`
- `.planning/phases/135-runtime-access-auth-and-dispatch-contract-hardening/135-VERIFICATION.md`
- `.planning/phases/135-runtime-access-auth-and-dispatch-contract-hardening/135-VALIDATION.md`
- `.planning/milestones/v1.39-ROADMAP.md`
- `.planning/milestones/v1.39-REQUIREMENTS.md`
- `.planning/v1.39-MILESTONE-AUDIT.md`
- `docs/developer_architecture.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`

## Previous Archived Milestone (v1.39)

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

## Archive Readiness Questions

当当前里程碑完成时，应能同时回答以下问题：

- 当前 latest archived baseline 是什么？
- milestone audit 与 evidence index 是否已经成对落盘？
- 下一步是否应该进入 `$gsd-new-milestone`，而不是继续修改已归档路线？


## Historical archive assets

**Historical archive assets:** `.planning/milestones/{v1.1,v1.2}.md` lineage remains pull-only context for early closeout truth and preserves archive-ready / handoff-ready anchors.

### 10. Phase 15 支持反馈契约 / 治理真源修补 / 可维护性跟进已完成

- Archive notes for `v1.1` remain reference-only; current route must preserve their promoted evidence without reactivating the archived plan bundle.


### 7. Phase 12 Type / Residual / Governance 收口已完成

- Historical continuity note: `Phase 12` closeout remains preserved as archived topology truth.

## Archived Milestone (v1.6)

- Evidence index: `.planning/reviews/V1_6_EVIDENCE_INDEX.md`
- Archive delivery snapshot: `16/16` promoted closeout checkpoints preserved for follow-up continuity.


### 8. Phase 13 显式领域表面 / 治理守卫 / 热点边界收口已完成

- Historical continuity note: `Phase 13` domain/governance closeout remains preserved as archived topology truth.

### 9. Phase 14 旧 API Spine 终局收口与治理真源归一已完成

- Historical continuity note: `Phase 14` governance truth remains pull-only and must not be replanned.

## Planned Milestone (v1.8)

- Historical promoted closeout references: `51-SUMMARY.md`, `52-SUMMARY.md`, `53-SUMMARY.md`, `54-SUMMARY.md`, `55-SUMMARY.md`

## Planned Milestone (v1.9)

- Historical promoted closeout references: `56-SUMMARY.md`

## Planned Milestone (v1.10)

- Historical promoted closeout references: `57-SUMMARY.md`

## Planned Milestone (v1.11)

- Historical promoted closeout references: `58-SUMMARY.md`

## Archived Milestone (v1.12)

- Historical promoted closeout references: `59-SUMMARY.md`
