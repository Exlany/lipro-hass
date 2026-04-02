# Roadmap

## Milestones

- 🚧 **v1.39 Governance Recovery, Runtime Consistency & Public Contract Correction** - `Phase 133 -> 133` active on 2026-04-02; current route truth = `v1.39 active milestone route / starting from latest archived baseline = v1.38`; phase handoff = `active / phase 133 complete; closeout-ready (2026-04-02)`; next step = `$gsd-complete-milestone v1.39`
- ✅ **v1.38 Governance Story Compression, Archive Segregation & Public Entry Simplification** - `Phase 132 -> 132` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.38`; evidence index = `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
- ✅ **v1.37 Repo-Wide Terminal Audit, Hotspot Decomposition & Governance Continuity Decisions** - `Phase 129 -> 131` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.37`; evidence index = `.planning/reviews/V1_37_EVIDENCE_INDEX.md`
- ✅ **v1.36 Terminal Residual Convergence, Runtime Access De-Reflection & Open-Source Readiness Hardening** - `Phase 126 -> 128` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.36`; evidence index = `.planning/reviews/V1_36_EVIDENCE_INDEX.md`
- ✅ **v1.35 Master Audit Closure, Public Surface Finalization & Release Traceability** - `Phase 122 -> 125` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.35`; evidence index = `.planning/reviews/V1_35_EVIDENCE_INDEX.md`
- ✅ **v1.34 Terminal Audit Closure, Contract Hardening & Governance Truth Slimming** - `Phase 120 -> 121` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.34`; evidence index = `.planning/reviews/V1_34_EVIDENCE_INDEX.md`
- ✅ **v1.33 MQTT Boundary Decoupling, Runtime Contract Unification & Release Governance Hardening** - `Phase 119` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.33`; evidence index = `.planning/reviews/V1_33_EVIDENCE_INDEX.md`
- ✅ **v1.32 Residual Hotspot Eradication, Validation Completion & Continuity Hardening** - `Phase 115 -> 118` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.32`; evidence index = `.planning/reviews/V1_32_EVIDENCE_INDEX.md`
- ✅ **v1.31 Boundary Sealing, Governance Truth & Quality Hardening** - `Phase 111 -> 114` archived on 2026-03-31; historical closeout route truth = `no active milestone route / latest archived baseline = v1.31`; evidence index = `.planning/reviews/V1_31_EVIDENCE_INDEX.md`
- ✅ **v1.30 Protocol Hotspot Convergence, Transport De-friendization & Snapshot Surface Slimming** - `Phase 107 -> 110` archived on 2026-03-30; milestone audit: `.planning/v1.30-MILESTONE-AUDIT.md`; evidence index: `.planning/reviews/V1_30_EVIDENCE_INDEX.md`; snapshots archived at `.planning/milestones/v1.30-ROADMAP.md` / `.planning/milestones/v1.30-REQUIREMENTS.md`; historical closeout route truth = `no active milestone route / latest archived baseline = v1.30`

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
## Overview

`v1.39` 以 archived baseline `v1.38` 为起点，先恢复 current governance lane 的 route/source-path/projection 一致性，再把 `runtime_types.py`、coordinator service contracts、auth/request-policy/dispatch 与 public entry/release contract 的后续修正收束成 `Phase 133` 的单相位三计划入口。

**Coverage:** `6/6` `v1.39` requirements complete in `Phase 133`.
**Default next command:** `$gsd-complete-milestone v1.39`

## Current Milestone

## v1.39: Governance Recovery, Runtime Consistency & Public Contract Correction

**Milestone status:** `active / phase 133 complete; closeout-ready (2026-04-02)`
**Default next command:** `$gsd-complete-milestone v1.39`
**Current route story:** `v1.39 active milestone route / starting from latest archived baseline = v1.38`
**Latest archived pointer:** `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.38-MILESTONE-AUDIT.md`
**Starting baseline snapshots:** `.planning/milestones/v1.38-ROADMAP.md`, `.planning/milestones/v1.38-REQUIREMENTS.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Phases

- [x] **Phase 133: governance recovery, runtime consistency, and public contract correction** - 已完成 `133-01` governance bootstrap / route recovery、`133-02` runtime consistency 修补、`133-03` strict preset + public contract correction、`133-04` governance closeout resync；当前已进入 `active / phase 133 complete; closeout-ready (2026-04-02)`，下一步为 `$gsd-complete-milestone v1.39`。 (complete 2026-04-02)

## Phase Details

### Phase 133: governance recovery, runtime consistency, and public contract correction
**Goal:** 把 v1.38 closeout 后遗留的 sanctioned carry-forward 明确拆成三条 lane：先修复 governance route/source-path/projection truth，再对 runtime formal homes 与 public-facing contract 的下一轮收口建立单一执行入口，避免继续把 production hotspot 混写进 docs-only 故事。
**Depends on:** Phase 132
**Requirements**: GOV-89, ARC-42, HOT-61, DOC-18, QLT-55, TST-53
**Success Criteria** (what must be TRUE):
  1. `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、`GOVERNANCE_REGISTRY.json`、`FILE_MATRIX.md` 与 `PROMOTED_PHASE_ASSETS.md` 共同承认 `v1.39 active milestone route / starting from latest archived baseline = v1.38`。
  2. governance current story 明确区分 Primary Sources 与 Current Execution Workspace Inputs，`STATE` 的 Session Continuity 只引用真实路径。
  3. runtime consistency lane 只允许围绕 `runtime_types.py`、coordinator service contracts、`core/auth/manager.py`、`request_policy.py`、`dispatch.py` 与 `firmware_update.py` 等 sanctioned formal homes inward 收口。
  4. public contract correction lane 必须同步 developer/public/runbook/support/manifest first-hop truth，不得再把 archived-only wording 伪装成 current route。
  5. `Phase 133` 的四条执行轨已全部完成：四份计划、四份计划摘要、phase summary 与 verification 已齐备，并把 next-step truth 切到 milestone closeout。
**Plans**: 3 planned — `133-01` governance lane recovery、`133-02` runtime consistency、`133-03` public contract correction
**Planning summaries**: `133-01-SUMMARY.md`, `133-02-SUMMARY.md`, `133-03-SUMMARY.md`, `133-SUMMARY.md`
**Verification**: `133-VERIFICATION.md`

## Latest Archived Milestone

## v1.38: Governance Story Compression, Archive Segregation & Public Entry Simplification

**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Default next command:** `$gsd-new-milestone`
**Current route story:** `no active milestone route / latest archived baseline = v1.38`
**Latest archived pointer:** `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.38-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.38-ROADMAP.md`, `.planning/milestones/v1.38-REQUIREMENTS.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Phases

- [x] **Phase 132: current-story compression and archive-boundary cleanup** - 已完成 current planning docs / developer-runbook route compression、route-marker helper dedupe、recent promoted-asset coverage 回流与 handoff smoke 瘦身。 (complete 2026-04-02)

## Phase Details

### Phase 132: current-story compression and archive-boundary cleanup
**Goal:** 把 live selector、latest archived pointer、historical archive story 与 governance smoke/test helper 的职责重新分层：current docs 只讲当前路线与必要 handoff，archive/history 回到 pull-only 边界，meta guards 通过 canonical registry + shared helper 断言，而不再扩散相同 prose/asset family。
**Depends on:** Phase 131
**Requirements**: AUD-07, GOV-88, DOC-17, OSS-19, QLT-54, TST-52
**Success Criteria** (what must be TRUE):
  1. `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 必须把 active-route compression 与 closeout 一并收敛到单一 registry-backed selector：live docs 只保留 archived-only current route、latest archived pointer 与 default next command。
  2. `docs/developer_architecture.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 首屏不再混用 archived-only frozen wording；current route / latest archived pointer 与 registry 投影一致。
  3. `tests/meta/governance_contract_helpers.py` 提供统一 route-marker helper，phase guards 不再各自重复 `CURRENT_ROUTE` / `CURRENT_MILESTONE_DEFAULT_NEXT` presence loops。
  4. `tests/meta/test_governance_route_handoff_smoke.py` 只保留 docs+GSD fast-path smoke；recent promoted asset family 回到 promoted-phase guards，不再在 smoke suite 里重复维护。
  5. `tests/meta/governance_current_truth.py` 不再内联 historical/forbidden-literal clutter；legacy markers 退回专属 helper home，canonical route 继续只读 registry-backed contract。
**Plans**: 3/3 complete — `132-01` active-route docs compression、`132-02` current-truth/helper dedupe、`132-03` promoted-asset / handoff smoke topic cleanup
**Execution summaries**: `132-01-SUMMARY.md`, `132-02-SUMMARY.md`, `132-03-SUMMARY.md`, `132-SUMMARY.md`
**Verification**: `132-VERIFICATION.md`
**Validation**: `132-VALIDATION.md`

## Previous Archived Milestone

## v1.37: Repo-Wide Terminal Audit, Hotspot Decomposition & Governance Continuity Decisions

**Milestone status:** `archived / evidence-ready (2026-04-01)`
**Default next command:** `$gsd-new-milestone`
**Current route story:** `no active milestone route / latest archived baseline = v1.37`
**Latest archived pointer:** `.planning/reviews/V1_37_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.37-MILESTONE-AUDIT.md`
**Starting baseline snapshots:** `.planning/milestones/v1.36-ROADMAP.md`, `.planning/milestones/v1.36-REQUIREMENTS.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Phases

- [x] **Phase 129: rest fallback explicit-surface convergence and api hotspot slimming** - 已完成 `rest_facade.py` / `status_fallback_support.py` 的显式组合化瘦身、focused regression 冻结与 archived closeout sync。 (complete 2026-04-01)
- [x] **Phase 130: runtime command and firmware-update hotspot decomposition** - 已完成 `command_runtime.py` / `entities/firmware_update.py` 的 inward split、focused proof freeze 与 archived-route/governance sync。 (complete 2026-04-01)
- [x] **Phase 131: repo-wide terminal audit closeout and governance continuity decisions** - 已完成终极审阅报告、统一 current docs/governance truth、补齐 promoted evidence / selector closeout，并将 external continuity/private-fallback debt 冻结为 honest governance boundary。

## Historical Archived Milestone

## v1.36: Terminal Residual Convergence, Runtime Access De-Reflection & Open-Source Readiness Hardening

**Milestone status:** `archived / evidence-ready (2026-04-01)`
**Default next command:** `$gsd-new-milestone`
**Current route story:** `no active milestone route / latest archived baseline = v1.36`
**Latest archived pointer:** `.planning/reviews/V1_36_EVIDENCE_INDEX.md`
**Current audit artifact:** `.planning/v1.36-MILESTONE-AUDIT.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.36`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.35`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Phases

- [x] **Phase 126: service-router developer callback-home convergence and diagnostics helper residual slimming** - 已完成 diagnostics helper inward thinning：`handlers.py` 直连 mechanics home、`helpers.py` 删除未使用 duplicate helper、`developer_router_support.py` 复用统一 iterator builder，并同步 v1.36 route / plan / verification truth。 (complete 2026-04-01)
- [x] **Phase 127: runtime-access de-reflection, typed runtime entry contracts, and hotspot continuation** - 已完成 `runtime_access` typed telemetry seam 收口、support-view de-reflection 与 focused/full verification 证据冻结，control/runtime seam 不再依赖 stringly dict fallback 或 `type(...).__getattribute__` 反射。 (complete 2026-04-01)
- [x] **Phase 128: open-source readiness, benchmark-coverage gates, and maintainer continuity hardening** - 已把 private-access / single-maintainer continuity / security fallback 限制诚实 codify，并把 coverage baseline diff、benchmark smoke、strict markers 与 final evidence freeze 固化为 archived evidence chain。 (complete 2026-04-01)

## Historical Archived Milestone

## Archive Chronology Appendix

## v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement
- archived continuity anchor preserved for release/history guards.

## v1.23 Repository-Wide Terminal Code Audit, Residual Eradication & Closeout Truth Freeze
- historical archived milestone reference retained for continuity guards.

## v1.24 Runtime Boundary Tightening, Tooling Kernel Decoupling & Open-Source Entry Convergence
- historical archived milestone reference retained for continuity guards.

## v1.25: Hotspot Inward Decomposition, Typed Boundary Hardening & Redaction Convergence
- archived roadmap anchor retained for Phase 90 hotspot freeze guards.

## v1.28 Governance Portability, Verification Stratification & Open-Source Continuity Hardening
- historical archived milestone reference retained for continuity guards.

## v1.29 Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization
- evidence pointer: `.planning/reviews/V1_29_EVIDENCE_INDEX.md`
