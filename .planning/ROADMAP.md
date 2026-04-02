# Roadmap

## Milestones

- 🚧 **v1.38 Governance Story Compression, Archive Segregation & Public Entry Simplification** - `Phase 132 -> 132` active on 2026-04-02; current route truth = `v1.38 active milestone route / starting from latest archived baseline = v1.37`; phase handoff = `active / phase 132 complete; closeout-ready (2026-04-02)`; next step = `$gsd-complete-milestone v1.38`
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
  version: v1.38
  name: Governance Story Compression, Archive Segregation & Public Entry Simplification
  status: active / phase 132 complete; closeout-ready (2026-04-02)
  phase: '132'
  phase_title: current-story compression and archive-boundary cleanup
  phase_dir: 132-current-story-compression-and-archive-boundary-cleanup
latest_archived:
  version: v1.37
  name: Repo-Wide Terminal Audit, Hotspot Decomposition & Governance Continuity Decisions
  status: archived / evidence-ready (2026-04-01)
  phase: '131'
  phase_title: repo-wide terminal audit closeout and governance continuity decisions
  phase_dir: 131-repo-wide-terminal-audit-closeout-and-governance-continuity-decisions
  audit_path: .planning/v1.37-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_37_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.36
  name: Terminal Residual Convergence, Runtime Access De-Reflection & Open-Source Readiness Hardening
  evidence_path: .planning/reviews/V1_36_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.38 active milestone route / starting from latest archived baseline = v1.37
  default_next_command: $gsd-complete-milestone v1.38
  latest_archived_evidence_pointer: .planning/reviews/V1_37_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->
## Overview

`v1.38` 以 archived baseline `v1.37` 为起点，不再新增 production hotspot 迁移波次，而是把 current selector、archive/history boundary、release/public-entry wording 与 governance smoke/test helpers 压回单一 current story：`Phase 132` 统一 planning docs、developer/runbook 首屏、route-marker helper 与 promoted asset / handoff smoke 的职责边界。

**Coverage:** `6/6` `v1.38` requirements mapped exactly once.
**Default next command:** `$gsd-complete-milestone v1.38`

## Current Milestone

## v1.38: Governance Story Compression, Archive Segregation & Public Entry Simplification

**Milestone status:** `active / phase 132 complete; closeout-ready (2026-04-02)`
**Default next command:** `$gsd-complete-milestone v1.38`
**Current route story:** `v1.38 active milestone route / starting from latest archived baseline = v1.37`
**Latest archived pointer:** `.planning/reviews/V1_37_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.37-MILESTONE-AUDIT.md`
**Starting baseline snapshots:** `.planning/milestones/v1.37-ROADMAP.md`, `.planning/milestones/v1.37-REQUIREMENTS.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Phases

- [x] **Phase 132: current-story compression and archive-boundary cleanup** - 已完成 current planning docs / developer-runbook route compression、route-marker helper dedupe、recent promoted-asset coverage 回流与 handoff smoke 瘦身。 (complete 2026-04-02)

## Phase Details

### Phase 132: current-story compression and archive-boundary cleanup
**Goal:** 把 live selector、latest archived pointer、historical archive story 与 governance smoke/test helper 的职责重新分层：current docs 只讲当前路线与必要 handoff，archive/history 回到 pull-only 边界，meta guards 通过 canonical registry + shared helper 断言，而不再扩散相同 prose/asset family。
**Depends on:** Phase 131
**Requirements**: AUD-07, GOV-88, DOC-17, OSS-19, QLT-54, TST-52
**Success Criteria** (what must be TRUE):
  1. `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 共同承认 `v1.38 active milestone route / starting from latest archived baseline = v1.37`，并把 latest archived pointer / default next command 压成单一 active-route story。
  2. `docs/developer_architecture.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 首屏不再混用 archived-only frozen wording；current route / latest archived pointer 与 registry 投影一致。
  3. `tests/meta/governance_contract_helpers.py` 提供统一 route-marker helper，phase guards 不再各自重复 `CURRENT_ROUTE` / `CURRENT_MILESTONE_DEFAULT_NEXT` presence loops。
  4. `tests/meta/test_governance_route_handoff_smoke.py` 只保留 docs+GSD fast-path smoke；recent promoted asset family 回到 promoted-phase guards，不再在 smoke suite 里重复维护。
  5. `tests/meta/governance_current_truth.py` 不再内联 historical/forbidden-literal clutter；legacy markers 退回专属 helper home，canonical route 继续只读 registry-backed contract。
**Plans**: 3/3 complete — `132-01` active-route docs compression、`132-02` current-truth/helper dedupe、`132-03` promoted-asset / handoff smoke topic cleanup
**Execution summaries**: `132-01-SUMMARY.md`, `132-02-SUMMARY.md`, `132-03-SUMMARY.md`, `132-SUMMARY.md`
**Verification**: `132-VERIFICATION.md`
**Validation**: `132-VALIDATION.md`

## Latest Archived Milestone

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

## Previous Archived Milestone

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