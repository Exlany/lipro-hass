# Roadmap

## Milestones

- ✅ **v1.31 Boundary Sealing, Governance Truth & Quality Hardening** - `Phase 111 -> 114` archived on 2026-03-31; latest archived baseline pointer = `.planning/reviews/V1_31_EVIDENCE_INDEX.md`
- 🚧 **v1.32 Residual Hotspot Eradication, Validation Completion & Continuity Hardening** - `Phase 115 -> 117` is the current active route; starting from latest archived baseline = `v1.31`

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
active_milestone:
  version: v1.32
  name: Residual Hotspot Eradication, Validation Completion & Continuity Hardening
  status: active / phase 117 complete; closeout-ready (2026-03-31)
  phase: '117'
  phase_title: Validation backfill and continuity hardening
  phase_dir: 117-validation-backfill-and-continuity-hardening
latest_archived:
  version: v1.31
  name: Boundary Sealing, Governance Truth & Quality Hardening
  status: archived / evidence-ready (2026-03-31)
  phase: '114'
  phase_title: Open-source reachability honesty and security-surface normalization
  phase_dir: 114-open-source-reachability-honesty-and-security-surface-normalization
  audit_path: .planning/v1.31-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_31_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.30
  name: Protocol Hotspot Convergence, Transport De-friendization & Snapshot Surface Slimming
  evidence_path: .planning/reviews/V1_30_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.32 active milestone route / starting from latest archived baseline = v1.31
  default_next_command: $gsd-complete-milestone v1.32
  latest_archived_evidence_pointer: .planning/reviews/V1_31_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->

## Overview

`v1.32` 继续只沿单一 north-star 主线推进：基于 `v1.31` latest archived baseline，先冻结 `status_fallback` 入口 contract，再继续收窄 `rest_facade.py`、`anonymous_share/manager.py` 与 validation / continuity debt。所有工作都必须在 formal homes 内完成，不引入 second root，不复活 compat shell。

**Coverage:** `4/4` v1.32 requirements mapped exactly once.
**Default next command:** `$gsd-complete-milestone v1.32`

## v1.32: Residual Hotspot Eradication, Validation Completion & Continuity Hardening

**Milestone status:** `active / phase 117 complete; closeout-ready (2026-03-31)`
**Default next command:** `$gsd-complete-milestone v1.32`
**Current route story:** `v1.32 active milestone route / starting from latest archived baseline = v1.31`
**Latest archived pointer:** `.planning/reviews/V1_31_EVIDENCE_INDEX.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Phases

- [x] **Phase 115: Status-fallback query-flow normalization** - 已冻结空输入 / fallback-depth / no-I/O contract，并补入 focused regression。 (completed 2026-03-31)
- [x] **Phase 116: Anonymous-share and REST façade hotspot slimming** - 已收敛 `rest_facade.py` 的 state binding 样板与 `anonymous_share/manager.py` 的 scope-state / aggregate outcome 语义，并补齐 focused regressions。 (completed 2026-03-31)
- [x] **Phase 117: Validation backfill and continuity hardening** - 已回补 `Phase 112 -> 114` validation / changed-surface / continuity 资产，修复 active-route drift，并冻结 closeout-ready selector truth。 (completed 2026-03-31)

## Phase Details

### Phase 115: Status-fallback query-flow normalization
**Goal**: `status_fallback` family 的入口语义必须在空输入、primary batch 与 fallback-depth 维度上保持单一正式 contract，不再允许 public entry 与 binary-split support 再次分叉。
**Depends on**: latest archived baseline `v1.31`
**Requirements**: HOT-48
**Status**: Complete (`2026-03-31`)
**Success Criteria** (what must be TRUE):
  1. 空 `ids` 下，`query_with_fallback()` 与 binary-split support 都立即返回空结果，不触发无意义 I/O。
  2. `record_fallback_depth` 在空输入路径上保持 `0`，与“没有发生 fallback”的语义一致。
  3. Focused regression 会冻结这一 contract，避免后续 hotspot slimming 让入口语义再次漂移。
**Plans**: 1/1 complete
**Evidence**: `.planning/phases/115-status-fallback-query-flow-normalization/{115-01-SUMMARY.md,115-SUMMARY.md,115-VERIFICATION.md}`

### Phase 116: Anonymous-share and REST façade hotspot slimming
**Goal**: `AnonymousShareManager` 与 `LiproRestFacade` 继续 inward split，但 formal outward home、stable import shell 与 child-façade composition truth 保持不变。
**Depends on**: Phase 115
**Requirements**: HOT-49
**Success Criteria** (what must be TRUE):
  1. aggregate/scoped submit semantics 与 façade state-proxy / wrapper density 继续下降，而不是通过新增 helper shell 掩盖复杂度。
  2. `anonymous_share/manager.py` 与 `rest_facade.py` 不会长出第二条 production path、compat shell 或新的 outward root。
  3. Focused tests 会明确冻结 formal home / factory / stable import / wrapper contract，不靠仓库全量测试碰运气。
**Status**: Complete (`2026-03-31`)
**Plans**: 3/3 complete
**Evidence**: `.planning/phases/116-anonymous-share-and-rest-fa-ade-hotspot-slimming/{116-01-SUMMARY.md,116-02-SUMMARY.md,116-03-SUMMARY.md,116-SUMMARY.md,116-VERIFICATION.md}`

### Phase 117: Validation backfill and continuity hardening
**Goal**: `Phase 112 -> 114` 的 validation / changed-surface / continuity proof 必须补齐，让 archived baseline 与下一条 active route 之间的 selector、runbook、evidence chain 继续保持单一 truth。
**Depends on**: Phase 116
**Requirements**: TST-39, GOV-73
**Success Criteria** (what must be TRUE):
  1. `Phase 112 -> 114` 缺失的 validation / changed-surface 资产被补齐，并与 latest archived evidence chain 对齐。
  2. `docs/developer_architecture.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md` 与 planning selector family 会共同承认 `v1.32` active route / `v1.31` latest archived baseline truth。
  3. 当前 route 的 next-step / archived pointer / continuity note 继续 machine-checkable，不回退成 conversation-only story。
**Status**: Complete (`2026-03-31`)
**Plans**: 3/3 complete
**Evidence**: `.planning/phases/117-validation-backfill-and-continuity-hardening/{117-01-SUMMARY.md,117-02-SUMMARY.md,117-03-SUMMARY.md,117-SUMMARY.md,117-VERIFICATION.md}`

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 115. Status-fallback query-flow normalization | 1/1 | Complete | 2026-03-31 |
| 116. Anonymous-share and REST façade hotspot slimming | 3/3 | Complete | 2026-03-31 |
| 117. Validation backfill and continuity hardening | 3/3 | Complete | 2026-03-31 |

## v1.31: Boundary Sealing, Governance Truth & Quality Hardening

> `v1.31` 沿 `v1.30` latest archived baseline 的唯一 north-star 主线，把 `Phase 111 -> 114` 的 boundary / governance / quality / honesty 修复收口为 closeout bundle，并翻转为 archived-only baseline。

**Milestone Goal:** 封印 entity/control → runtime concrete bypass、统一 formal-home discoverability 与治理锚点、继续 burn-down 当前热点，并把 open-source reachability / security continuity 的外部 blocker 诚实冻结为 pull-only archived truth。
**Milestone status:** `archived / evidence-ready (2026-03-31)`
**Starting baseline:** `.planning/v1.30-MILESTONE-AUDIT.md`, `.planning/reviews/V1_30_EVIDENCE_INDEX.md`, `.planning/milestones/v1.30-ROADMAP.md`, `.planning/milestones/v1.30-REQUIREMENTS.md`
**Requirements basket:** `ARC-28`, `ARC-29`, `GOV-71`, `GOV-72`, `QLT-46`, `TST-38`, `OSS-14`, `SEC-09`
**Latest archived baseline:** `v1.31`
**Latest archived pointer:** `.planning/reviews/V1_31_EVIDENCE_INDEX.md`
**Current route mode:** `no active milestone route / latest archived baseline = v1.31`
**Default next command:** `$gsd-new-milestone`
**Current follow-up target:** start next route with `$gsd-new-milestone`.

### Phase 111: Entity-runtime boundary sealing and dependency-guard hardening
**Goal**: Entity 与 control 消费者只经 sanctioned runtime public surface 协作，任何回流到 concrete runtime internals 的依赖漂移都会被自动拒绝。
**Depends on**: latest archived baseline `v1.30`
**Requirements**: ARC-28, GOV-71, TST-38
**Status**: Complete (`2026-03-31`)
**Plans**: 3/3 complete
**Closeout assets**: `.planning/phases/111-entity-runtime-boundary-sealing-and-dependency-guard-hardening/{111-01-SUMMARY.md,111-02-SUMMARY.md,111-03-SUMMARY.md,111-SUMMARY.md,111-VERIFICATION.md,111-VALIDATION.md}`

### Phase 112: Formal-home discoverability and governance-anchor normalization
**Goal**: sanctioned root homes、formal ownership 与治理文档共同讲一条当前主线故事，不再出现目录拓扑与 governance anchor 长期分叉。
**Depends on**: Phase 111
**Requirements**: ARC-29, GOV-72
**Status**: Complete (`2026-03-31`)
**Plans**: 3/3 complete
**Closeout assets**: `.planning/phases/112-formal-home-discoverability-and-governance-anchor-normalization/{112-01-SUMMARY.md,112-02-SUMMARY.md,112-03-SUMMARY.md,112-SUMMARY.md,112-VERIFICATION.md}`

### Phase 113: Hotspot burn-down and changed-surface assurance hardening
**Goal**: 当前 top-priority implementation hotspots 继续 inward split，或被 bounded no-regrowth guards 冻结，不再依赖“永久大型文件例外”叙事存活。
**Depends on**: Phase 112
**Requirements**: QLT-46
**Status**: Complete (`2026-03-31`)
**Plans**: 4/4 complete
**Closeout assets**: `.planning/phases/113-hotspot-burn-down-and-changed-surface-assurance-hardening/{113-01-SUMMARY.md,113-02-SUMMARY.md,113-03-SUMMARY.md,113-04-SUMMARY.md,113-SUMMARY.md,113-VERIFICATION.md,113-AUDIT.md}`

### Phase 114: Open-source reachability honesty and security-surface normalization
**Goal**: public metadata 与 security reporting 只陈述真实可达 surface，并把缺失的私有回报通道或 delegate continuity 明确保留为外部 blocker。
**Depends on**: Phase 113
**Requirements**: OSS-14, SEC-09
**Status**: Complete (`2026-03-31`)
**Plans**: 3/3 complete
**Closeout assets**: `.planning/phases/114-open-source-reachability-honesty-and-security-surface-normalization/{114-01-SUMMARY.md,114-02-SUMMARY.md,114-03-SUMMARY.md,114-SUMMARY.md,114-VERIFICATION.md,114-AUDIT.md}`
**Closeout evidence index**: `.planning/reviews/V1_31_EVIDENCE_INDEX.md`
**Milestone audit**: `.planning/v1.31-MILESTONE-AUDIT.md`
