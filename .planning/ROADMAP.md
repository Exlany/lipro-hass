# Roadmap

## Milestones

- 🚧 **v1.41 Terminal Residual Audit, Remediation Charter & Maintainability Hardening** - `Phase 136 -> 136` active on 2026-04-02; current route truth = `v1.41 active milestone route / starting from latest archived baseline = v1.40`; phase handoff = `active / phase 136 complete; closeout-ready (2026-04-02)`; next step = `$gsd-complete-milestone v1.41`
- ✅ **v1.40 Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening** - `Phase 134 -> 135` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.40`; evidence index = `.planning/reviews/V1_40_EVIDENCE_INDEX.md`
- ✅ **v1.39 Governance Recovery, Runtime Consistency & Public Contract Correction** - `Phase 133 -> 133` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.39`; evidence index = `.planning/reviews/V1_39_EVIDENCE_INDEX.md`
- ✅ **v1.38 Governance Story Compression, Archive Segregation & Public Entry Simplification** - `Phase 132 -> 132` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.38`; evidence index = `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
- ✅ **v1.37 Repo-Wide Terminal Audit, Hotspot Decomposition & Governance Continuity Decisions** - `Phase 129 -> 131` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.37`; evidence index = `.planning/reviews/V1_37_EVIDENCE_INDEX.md`

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
  version: v1.41
  name: Terminal Residual Audit, Remediation Charter & Maintainability Hardening
  status: active / phase 136 complete; closeout-ready (2026-04-02)
  phase: '136'
  phase_title: repo-wide terminal residual audit, hygiene fixes, and remediation charter
  phase_dir: 136-repo-wide-terminal-residual-audit-and-remediation-charter
latest_archived:
  version: v1.40
  name: Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening
  status: archived / evidence-ready (2026-04-02)
  phase: '135'
  phase_title: runtime-access projection split, auth reason typing, and dispatch route
    hardening
  phase_dir: 135-runtime-access-auth-and-dispatch-contract-hardening
  audit_path: .planning/v1.40-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_40_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.39
  name: Governance Recovery, Runtime Consistency & Public Contract Correction
  evidence_path: .planning/reviews/V1_39_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.41 active milestone route / starting from latest archived baseline
    = v1.40
  default_next_command: $gsd-complete-milestone v1.41
  latest_archived_evidence_pointer: .planning/reviews/V1_40_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->
## Overview

`v1.41` 以 archived baseline `v1.40` 为唯一起点，先完成 repo-wide terminal residual audit，把 Python/docs/config/governance 的剩余热点按严重度与正式 home 重新分类，再通过首批 vendor-crypto / log-safety hygiene fixes 验证当前审阅不是纯文档演习，最终把后续 hotspot 清扫路径固化为单一 remediation charter。

**Coverage:** `6/6` `v1.41` requirements complete in `Phase 136`.
**Default next command:** `$gsd-complete-milestone v1.41`

## Current Milestone

## v1.41: Terminal Residual Audit, Remediation Charter & Maintainability Hardening

**Milestone status:** `active / phase 136 complete; closeout-ready (2026-04-02)`
**Default next command:** `$gsd-complete-milestone v1.41`
**Current route story:** `v1.41 active milestone route / starting from latest archived baseline = v1.40`
**Latest archived pointer:** `.planning/reviews/V1_40_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.40-MILESTONE-AUDIT.md`
**Starting baseline snapshots:** `.planning/milestones/v1.40-ROADMAP.md`, `.planning/milestones/v1.40-REQUIREMENTS.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
**Current phase handoff:** `Phase 136 已把终极审查、修复章程、focused hygiene fixes 与 governance route sync 收成单相位闭环。`

## Phases

- [x] **Phase 136: repo-wide terminal residual audit, hygiene fixes, and remediation charter** - 已完成 `136-01` terminal audit report + remediation charter、`136-02` vendor-crypto/log-safety hygiene fixes、`136-03` governance/docs/guards sync。 (complete 2026-04-02)

## Phase Details

### Phase 136: repo-wide terminal residual audit, hygiene fixes, and remediation charter

**Requirements**: `AUD-08`, `GOV-91`, `DOC-19`, `ARC-45`, `QLT-58`, `TST-56`
**Success Criteria** (what must be TRUE):
  1. 全仓 Python/docs/config/governance 审查必须形成单一 `V1_41_TERMINAL_AUDIT_REPORT.md` verdict home，而不是散落在 summary 片段中。
  2. `V1_41_REMEDIATION_CHARTER.md` 必须把热点按 severity、formal home、delete gate 与后续计划分流，明确哪些已修复、哪些仍需后续 phase。
  3. 首批生产修复必须至少覆盖一类策略漂移：本轮选定 vendor-crypto helper 统一与 log-safety placeholder 一致性。
  4. `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、registry、verification baseline、developer/runbook note 与 current-route guards 必须共同承认 `v1.41 active milestone route / starting from latest archived baseline = v1.40`。
  5. phase assets、focused tests 与 `uv run ruff check` 必须证明本轮 deliverable 不是文档空转，而是可回放的 closeout-ready current route。 
**Plans**: 3/3 complete — `136-01` audit+charter、`136-02` hygiene fixes、`136-03` governance route sync
**Execution summaries**: `136-01-SUMMARY.md`, `136-02-SUMMARY.md`, `136-03-SUMMARY.md`, `136-SUMMARY.md`
**Verification**: `136-VERIFICATION.md`
**Validation**: `136-VALIDATION.md`

## Latest Archived Milestone

## v1.40: Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening

**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Default next command:** `$gsd-new-milestone`
**Current route story:** `no active milestone route / latest archived baseline = v1.40`
**Starting baseline:** `.planning/v1.39-MILESTONE-AUDIT.md, .planning/reviews/V1_39_EVIDENCE_INDEX.md, .planning/milestones/v1.39-ROADMAP.md, .planning/milestones/v1.39-REQUIREMENTS.md`
**Latest archived baseline:** `v1.40`
**Latest archived pointer:** `.planning/reviews/V1_40_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.40-MILESTONE-AUDIT.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
**Current phase handoff:** `Milestone closeout complete；Phase 134 -> 135 的 summary / verification / validation / audit / evidence index 已冻结为 latest archived baseline truth。`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.40`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.39`

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
  5. closeout 后 current governance docs、developer/runbook route note、follow-up guards 与 phase assets 必须共同承认 `no active milestone route / latest archived baseline = v1.40` 与 `$gsd-new-milestone`。
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

## Previous Archived Milestone


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

## Historical Archive Snapshot Index

- `v1.1-ROADMAP.md`
- `v1.1-REQUIREMENTS.md`
- `v1.2-ROADMAP.md`
- `v1.2-REQUIREMENTS.md`
- `v1.4-ROADMAP.md`
- `v1.4-REQUIREMENTS.md`
- `v1.5-ROADMAP.md`
- `v1.5-REQUIREMENTS.md`
- `v1.6-ROADMAP.md`
- `v1.6-REQUIREMENTS.md`
- `v1.12-ROADMAP.md`
- `v1.12-REQUIREMENTS.md`
- `v1.13-ROADMAP.md`
- `v1.13-REQUIREMENTS.md`
- `v1.14-ROADMAP.md`
- `v1.14-REQUIREMENTS.md`
- `v1.15-ROADMAP.md`
- `v1.15-REQUIREMENTS.md`
- `v1.16-ROADMAP.md`
- `v1.16-REQUIREMENTS.md`
- `v1.17-ROADMAP.md`
- `v1.17-REQUIREMENTS.md`
- `v1.21-ROADMAP.md`
- `v1.21-REQUIREMENTS.md`
- `v1.22-ROADMAP.md`
- `v1.22-REQUIREMENTS.md`
- `v1.23-ROADMAP.md`
- `v1.23-REQUIREMENTS.md`
- `v1.24-ROADMAP.md`
- `v1.24-REQUIREMENTS.md`
- `v1.25-ROADMAP.md`
- `v1.25-REQUIREMENTS.md`
- `v1.26-ROADMAP.md`
- `v1.26-REQUIREMENTS.md`
- `v1.27-ROADMAP.md`
- `v1.27-REQUIREMENTS.md`
- `v1.28-ROADMAP.md`
- `v1.28-REQUIREMENTS.md`
