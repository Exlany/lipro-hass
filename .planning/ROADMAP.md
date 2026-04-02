# Roadmap

## Milestones

- 🚧 **v1.42 Hotspot Burn-Down, Observability Truth & Governance Cost Compression** - `Phase 137 -> 137` active on 2026-04-02; current route = `v1.42 active milestone route / starting from latest archived baseline = v1.41`; latest archived evidence index = `.planning/reviews/V1_41_EVIDENCE_INDEX.md`
- ✅ **v1.41 Terminal Residual Audit, Remediation Charter & Maintainability Hardening** - `Phase 136 -> 136` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.41`; evidence index = `.planning/reviews/V1_41_EVIDENCE_INDEX.md`
- ✅ **v1.40 Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening** - `Phase 134 -> 135` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.40`; evidence index = `.planning/reviews/V1_40_EVIDENCE_INDEX.md`
- ✅ **v1.39 Governance Recovery, Runtime Consistency & Public Contract Correction** - `Phase 133 -> 133` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.39`; evidence index = `.planning/reviews/V1_39_EVIDENCE_INDEX.md`
- ✅ **v1.38 Governance Story Compression, Archive Segregation & Public Entry Simplification** - `Phase 132 -> 132` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.38`; evidence index = `.planning/reviews/V1_38_EVIDENCE_INDEX.md`

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
  version: v1.42
  name: Hotspot Burn-Down, Observability Truth & Governance Cost Compression
  status: active / phase 137 complete; closeout-ready (2026-04-02)
  phase: '137'
  phase_title: hotspot burn-down, command/observability convergence, and governance
    derivation compression
  phase_dir: 137-hotspot-burn-down-command-observability-and-governance-compression
  route_mode: v1.42 active milestone route / starting from latest archived baseline
    = v1.41
latest_archived:
  version: v1.41
  name: Terminal Residual Audit, Remediation Charter & Maintainability Hardening
  status: archived / evidence-ready (2026-04-02)
  phase: '136'
  phase_title: repo-wide terminal residual audit, hygiene fixes, and remediation charter
  phase_dir: 136-repo-wide-terminal-residual-audit-and-remediation-charter
  audit_path: .planning/v1.41-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_41_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.40
  name: Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening
  evidence_path: .planning/reviews/V1_40_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.42 active milestone route / starting from latest archived baseline
    = v1.41
  default_next_command: $gsd-complete-milestone v1.42
  latest_archived_evidence_pointer: .planning/reviews/V1_41_EVIDENCE_INDEX.md
contract_version: 1
```
<!-- governance-route-contract:end -->
## Overview

`v1.42` 直接继承 `v1.41` 的终极审阅与 remediation charter，不再重复浅层 audit，而是把已识别的 sanctioned hotspots 与 governance cost 一次性转为唯一 active execution route。

**Coverage:** `8/8` `v1.42` requirements complete in `Phase 137`.
**Default next command:** `$gsd-complete-milestone v1.42`

## Current Milestone

## v1.42: Hotspot Burn-Down, Observability Truth & Governance Cost Compression

**Milestone status:** `active / phase 137 complete; closeout-ready (2026-04-02)`
**Default next command:** `$gsd-complete-milestone v1.42`
**Current route story:** `v1.42 active milestone route / starting from latest archived baseline = v1.41`
**Latest archived pointer:** `.planning/reviews/V1_41_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.41-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.41-ROADMAP.md`, `.planning/milestones/v1.41-REQUIREMENTS.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
**Current phase handoff:** `Phase 137 的 3 份计划、3 份计划摘要、phase summary 与 verification 已闭环；当前 milestone 处于 closeout-ready，下一步直接执行 $gsd-complete-milestone v1.42。`

## Phases

- [x] **Phase 137: hotspot burn-down, command/observability convergence, and governance derivation compression** - 已完成 `137-01` governance/docs/test contract hardening、`137-02` protocol/rest/auth hotspot decomposition、`137-03` device/command/observability hardening，并产出 closeout-ready summaries/verification。 (complete 2026-04-02)

## Phase Details

### Phase 137: hotspot burn-down, command/observability convergence, and governance derivation compression

**Goal:** 把 v1.41 审阅章程中的 WS-01 ~ WS-06 收敛到一个 machine-checkable 的 active phase：先压低 governance derivation tax 与 semantic-guard blind spot，再处理 mega-facade / auth hotspot，最后同步压缩 device relay wall、typed command semantics 与 connect-status observability。
**Depends on:** none
**Requirements**: `ARC-46`, `HOT-67`, `HOT-68`, `HOT-69`, `OBS-01`, `GOV-92`, `DOC-20`, `TST-57`
**Success Criteria** (what must be TRUE):
  1. runbook/developer docs/current-route guards 对 latest archived pointer 与 current selector 的断言必须只有单一 canonical 角色，不允许“新旧 pointer 同页共存也算通过”。
  2. `core/api/rest_facade.py` 与 `core/protocol/facade.py` 必须继续减少 manual delegation wall / rebinding seam，但不能回退到 mixin、compat shell 或第二 public import chain。
  3. `core/auth/manager.py` 必须把 token/credential/refresh/relogin/adaptive-expiry 的职责边界收紧；新增行为不得继续堆进 manager monolith。
  4. `core/device/device.py` 与 `core/command/dispatch.py` 必须把 relay wall / stringly route grammar 进一步数据化、typed 化，fallback 语义与 trace 一致。
  5. `core/api/status_service.py` 及相关调用链必须显式区分 connect-status 查询失败 vs 真空结果，并继续遵守 log-safety。
  6. `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、registry、verification baseline、developer/runbook note 与 focused meta guards 必须共同承认 `v1.42 active milestone route / starting from latest archived baseline = v1.41`。
  7. `uv run pytest` focused suites、route guards、`uv run ruff check` 与必要的 governance checks 必须证明本轮 deliverable 是真实收口，而非临时修补。
**Plans**: 3 planned / 3 completed — summaries captured; next = `$gsd-complete-milestone v1.42`

## Latest Archived Milestone

## v1.41: Terminal Residual Audit, Remediation Charter & Maintainability Hardening

**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Default next command:** `$gsd-complete-milestone v1.42`
**Current route story:** `no active milestone route / latest archived baseline = v1.41`
**Latest archived pointer:** `.planning/reviews/V1_41_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.41-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.41-ROADMAP.md`, `.planning/milestones/v1.41-REQUIREMENTS.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
**Current phase handoff:** `Milestone closeout complete；Phase 136 的 requirement coverage、summary / verification / validation / audit / evidence index 已冻结为 latest archived baseline truth。`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.41`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.40`

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

## Previous Archived Milestone
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
