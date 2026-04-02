# Roadmap

## Milestones

- 🚧 **v1.40 Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening** - `Phase 134 -> 135` active on 2026-04-02; current route truth = `v1.40 active milestone route / starting from latest archived baseline = v1.39`; default next = `$gsd-complete-milestone v1.40`; latest archived baseline = `v1.39`
- ✅ **v1.39 Governance Recovery, Runtime Consistency & Public Contract Correction** - `Phase 133 -> 133` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.39`; evidence index = `.planning/reviews/V1_39_EVIDENCE_INDEX.md`
- ✅ **v1.38 Governance Story Compression, Archive Segregation & Public Entry Simplification** - `Phase 132 -> 132` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.38`; evidence index = `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
- ✅ **v1.37 Repo-Wide Terminal Audit, Hotspot Decomposition & Governance Continuity Decisions** - `Phase 129 -> 131` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.37`; evidence index = `.planning/reviews/V1_37_EVIDENCE_INDEX.md`
- ✅ **v1.36 Terminal Residual Convergence, Runtime Access De-Reflection & Open-Source Readiness Hardening** - `Phase 126 -> 128` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.36`; evidence index = `.planning/reviews/V1_36_EVIDENCE_INDEX.md`

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
  status: active / phase 135 complete; closeout-ready (2026-04-02)
  phase: '135'
  phase_title: runtime-access projection split, auth reason typing, and dispatch route hardening
  phase_dir: 135-runtime-access-auth-and-dispatch-contract-hardening
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
## Overview

`v1.40` 以 archived baseline `v1.39` 为唯一起点，先把 `RequestPolicy` 的 pacing/busy-retry state 收回单一 owner，再把 `descriptors.py` / `binary_sensor.py` / `light.py` 的反射/stringly projection 收口为显式 reader，修复 `fan.py` 的 unknown-mode truth，随后在契约者继续要求的终极深审下显式追加 `Phase 135`，把 `runtime_access.py`、`auth_service.py` 与 `dispatch.py` 三个 sanctioned hotspots 继续压回 typed / thin / support-split 主链。

**Coverage:** `12/12` `v1.40` requirements complete in `Phase 134 -> 135`.
**Default next command:** `$gsd-complete-milestone v1.40`

## v1.40: Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening

**Milestone status:** `active / phase 135 complete; closeout-ready (2026-04-02)`
**Default next command:** `$gsd-complete-milestone v1.40`
**Current route story:** `v1.40 active milestone route / starting from latest archived baseline = v1.39`
**Starting baseline:** `.planning/v1.39-MILESTONE-AUDIT.md, .planning/reviews/V1_39_EVIDENCE_INDEX.md, .planning/milestones/v1.39-ROADMAP.md, .planning/milestones/v1.39-REQUIREMENTS.md`
**Latest archived baseline:** `v1.39`
**Latest archived pointer:** `.planning/reviews/V1_39_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.39-MILESTONE-AUDIT.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
**Current phase handoff:** `契约者继续要求彻底 deep audit 后，v1.40 已显式扩 scope 吸收 Phase 135；当前 milestone 再次进入 closeout-ready，而不是假装已完成 closeout。`

## Phases

- [x] **Phase 134: request-policy ownership, entity de-reflection, and fan truth hardening** - 已完成 `134-01` request-policy ownership convergence、`134-02` entity de-reflection + fan truth correction、`134-03` docs/guards/tests/verification sync。 (complete 2026-04-02)
- [x] **Phase 135: runtime-access projection split, auth reason typing, and dispatch route hardening** - 已完成 `135-01` runtime-access projection split、`135-02` auth reason typing + dispatch route typing、`135-03` docs/guards/route sync；当前 milestone 重新回到 closeout-ready。 (complete 2026-04-02)

## Phase Details

### Phase 134: request-policy ownership, entity de-reflection, and fan truth hardening

**Requirements**: `GOV-90`, `ARC-43`, `HOT-62`, `HOT-63`, `QLT-56`, `TST-54`
**Success Criteria** (what must be TRUE):
  1. `RequestPolicy` 必须把 pacing caches / busy counters / target locks 收回单一实例 owner，module-level mutating pacing entry 不再作为第二条正式主链。
  2. `request_policy_support.py` 的 pacing helpers 必须围绕 `_CommandPacingCaches` bundle 协作，不再在 support surface 里搬运多组并行 dict state。
  3. `entities/descriptors.py`、`light.py` 与 `binary_sensor.py` 不再依赖 dotted-path/getattr 反射；entity projection 改为显式 resolver / state reader。
  4. `fan.py` 的 unknown `fanMode` 不再伪装成 `cycle`；preset 与 supported-features 投影必须保持 truthful 一致。
  5. current governance docs、developer/runbook route note、follow-up guards 与 phase assets 必须共同承认 `v1.40 active milestone route / starting from latest archived baseline = v1.39` 与 `$gsd-complete-milestone v1.40`。
  6. focused tests / meta guards / ruff 必须通过，且 phase assets 足以支撑 `$gsd-next` 等价收敛到 `$gsd-complete-milestone v1.40`。
**Plans**: 3 planned — `134-01` request-policy ownership convergence、`134-02` entity de-reflection + fan truth correction、`134-03` docs/guards/tests/verification sync
**Planning summaries**: `134-01-SUMMARY.md`, `134-02-SUMMARY.md`, `134-03-SUMMARY.md`, `134-SUMMARY.md`
**Verification**: `134-VERIFICATION.md`
**Validation**: `134-VALIDATION.md`

### Phase 135: runtime-access projection split, auth reason typing, and dispatch route hardening

**Requirements**: `ARC-44`, `HOT-64`, `HOT-65`, `HOT-66`, `QLT-57`, `TST-55`
**Success Criteria** (what must be TRUE):
  1. `runtime_access.py` 必须继续薄化为 outward import home；runtime snapshot / diagnostics projection coercion 回到 support surface。
  2. `runtime_types.py` / `auth_service.py` / `services/execution.py` 必须围绕单一 `RuntimeReauthReason` contract 协作，不再把 reauth reason 继续保留为裸字符串约定。
  3. `dispatch.py` / sender / runtime command path 的 route contract 必须采用 enum-backed canonical form，阻断 stringly drift。
  4. 新增 typed contract / support split 后，focused tests / meta guards / ruff 必须通过，且不引入新的 compat root。
  5. current governance docs、registry、verification matrix 与 phase assets 必须共同承认 `Phase 135 complete; closeout-ready` 与 `$gsd-complete-milestone v1.40`。
  6. `$gsd-next` 的等价结果必须重新回到 `$gsd-complete-milestone v1.40`，而不是留在 half-reopened 中间态。
**Plans**: 3 planned — `135-01` runtime-access projection split、`135-02` auth reason typing + dispatch route typing、`135-03` docs/guards/route sync
**Planning summaries**: `135-01-SUMMARY.md`, `135-02-SUMMARY.md`, `135-03-SUMMARY.md`, `135-SUMMARY.md`
**Verification**: `135-VERIFICATION.md`
**Validation**: `135-VALIDATION.md`

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
