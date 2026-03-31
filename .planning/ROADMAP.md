# Roadmap

## Milestones

- ✅ **v1.30 Protocol Hotspot Convergence, Transport De-friendization & Snapshot Surface Slimming** - `Phase 107 -> 110` 已归档；latest archived baseline pointer = `.planning/reviews/V1_30_EVIDENCE_INDEX.md`
- 🚧 **v1.31 Boundary Sealing, Governance Truth & Quality Hardening** - `Phase 111 -> 114` 为当前 active route；starting from latest archived baseline = `v1.30`

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
active_milestone:
  version: v1.31
  name: Boundary Sealing, Governance Truth & Quality Hardening
  status: active / phase 112 complete; phase 113 discussion-ready (2026-03-31)
  phase: '113'
  phase_title: Hotspot burn-down and changed-surface assurance hardening
  phase_dir: 113-hotspot-burn-down-and-changed-surface-assurance-hardening
latest_archived:
  version: v1.30
  name: Protocol Hotspot Convergence, Transport De-friendization & Snapshot Surface Slimming
  status: archived / evidence-ready (2026-03-30)
  phase: '110'
  phase_title: Runtime snapshot surface reduction and milestone closeout
  phase_dir: 110-runtime-snapshot-surface-reduction-and-milestone-closeout
  audit_path: .planning/v1.30-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_30_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.29
  name: Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization
  evidence_path: .planning/reviews/V1_29_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.31 active milestone route / starting from latest archived baseline = v1.30
  default_next_command: $gsd-discuss-phase 113
  latest_archived_evidence_pointer: .planning/reviews/V1_30_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->

## Overview

`v1.31` 只沿单一 north-star 主线推进：封印 entity/control → runtime internals concrete bypass，统一 formal-home discoverability 与治理锚点，继续 burn-down 当前热点，并对 open-source reachability / security fallback 保持 honest-by-default。所有工作都以 `v1.30` 为 latest archived baseline，不引入 second root，不复活 compat shell。

**Coverage:** `8/8` v1.31 requirements mapped exactly once.
**Default next command:** `$gsd-discuss-phase 113`

## v1.31: Boundary Sealing, Governance Truth & Quality Hardening

**Milestone status:** `active / phase 112 complete; phase 113 discussion-ready (2026-03-31)`
**Default next command:** `$gsd-discuss-phase 113`
**Current route story:** `v1.31 active milestone route / starting from latest archived baseline = v1.30`
**Latest archived pointer:** `.planning/reviews/V1_30_EVIDENCE_INDEX.md`

## Phases

- [x] **Phase 111: Entity-runtime boundary sealing and dependency-guard hardening** - 已封印 entity/control 到 runtime internals 的 concrete bypass，并用 machine-checkable guards 与 changed-surface validation 固化完成态。
- [x] **Phase 112: Formal-home discoverability and governance-anchor normalization** - 统一 sanctioned root homes、formal-home discoverability 与 stale governance anchors。 (completed 2026-03-31)
- [ ] **Phase 113: Hotspot burn-down and changed-surface assurance hardening** - 继续 inward split 当前实现热点，或用 honest no-regrowth guards 固化 changed surface。
- [ ] **Phase 114: Open-source reachability honesty and security-surface normalization** - 让 public metadata / security docs 只陈述真实可达 surface 与未解 blocker。

## Phase Details

### Phase 111: Entity-runtime boundary sealing and dependency-guard hardening
**Goal**: Entity 与 control 消费者只经 sanctioned runtime public surface 协作，任何回流到 concrete runtime internals 的依赖漂移都会被自动拒绝。
**Depends on**: latest archived baseline `v1.30`
**Requirements**: ARC-28, GOV-71, TST-38
**Status**: Complete (`2026-03-31`)
**Success Criteria** (what must be TRUE):
  1. Maintainer 运行 architecture / dependency guards 时，若 entity 或 control 代码直接 import concrete `Coordinator`、做 runtime concrete cast、或穿透 runtime private state，检查会明确失败。
  2. Entity 与 control 相关行为仍可经 sanctioned runtime public contracts 正常工作，无需 compat shell、direct concrete binding 或 private-state reach-through。
  3. Focused changed-surface validation 会覆盖 command/request failure branches、new dependency guards 与 renamed read-model seams，使关键错误路径在 targeted runs 中即可暴露。
**Plans**: 3/3 complete
**Evidence**: `.planning/phases/111-entity-runtime-boundary-sealing-and-dependency-guard-hardening/{111-01-SUMMARY.md,111-02-SUMMARY.md,111-03-SUMMARY.md,111-SUMMARY.md,111-VERIFICATION.md,111-VALIDATION.md}`

### Phase 112: Formal-home discoverability and governance-anchor normalization
**Goal**: sanctioned root homes、formal ownership 与治理文档共同讲一条当前主线故事，不再出现目录拓扑与 governance anchor 长期分叉。
**Depends on**: Phase 111
**Requirements**: ARC-29, GOV-72
**Success Criteria** (what must be TRUE):
  1. Maintainer 阅读 north-star / baseline / planning / runbook 文档时，能无歧义识别 runtime、control、auth 与 root-level homes 的正式归属，不再被 `coordinator.coordinator` 一类折返叙事误导。
  2. `SUPPORT.md`、`SECURITY.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、planning / baseline / review docs 全部指向 `v1.31` active route 与 `v1.30` latest archived baseline，不再保留 stale milestone anchors。
  3. `runtime_infra.py`、`runtime_types.py`、`entry_auth.py` 等 root-level homes 要么被归并，要么在正式治理真源中显式登记为 sanctioned homes，使目录拓扑与 formal ownership 一致。
**Status**: Complete (`2026-03-31`)
**Plans**: 3/3 complete
**Evidence**: `.planning/phases/112-formal-home-discoverability-and-governance-anchor-normalization/{112-01-SUMMARY.md,112-02-SUMMARY.md,112-03-SUMMARY.md,112-SUMMARY.md,112-VERIFICATION.md}`

### Phase 113: Hotspot burn-down and changed-surface assurance hardening
**Goal**: 当前 top-priority implementation hotspots 继续 inward split，或被 bounded no-regrowth guards 冻结，不再依赖“永久大型文件例外”叙事存活。
**Depends on**: Phase 112
**Requirements**: QLT-46
**Success Criteria** (what must be TRUE):
  1. 当前 top-priority hotspots 至少达到二选一：体量/职责继续 inward split，或已有明确 no-regrowth guard 阻止热点再次膨胀。
  2. Maintainer 可通过 focused assurance runs 直接验证 changed hotspots 的关键 surface，而不是只依赖 repo-wide line coverage 掩盖热点回流。
  3. 治理与质量工件对剩余 hotspot allowance 采用显式、可删除、可审计的 bounded exception 叙事，而不是把 large-file exception 默许为长期合法状态。
**Plans**: TBD

### Phase 114: Open-source reachability honesty and security-surface normalization
**Goal**: public metadata 与 security reporting 只陈述真实可达 surface，并把缺失的私有回报通道或 delegate continuity 明确保留为外部 blocker。
**Depends on**: Phase 113
**Requirements**: OSS-14, SEC-09
**Success Criteria** (what must be TRUE):
  1. Public-facing metadata 与 docs 会清楚区分 truly reachable public surfaces 和 access-gated private surfaces，不再暗示不存在的公开入口。
  2. Security reporting docs 会明确说明是否存在 guaranteed non-GitHub private fallback；若不存在，则以 governance blocker 诚实登记，而不是伪装成已解决入口。
  3. `manifest.json`、`pyproject.toml`、support/security docs 与 planning truth 不会编造 public endpoint、delegate identity 或 backup maintainer；外部 blocker 保持显式待 maintainer 处理。
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 111. Entity-runtime boundary sealing and dependency-guard hardening | 3/3 | Complete | 2026-03-31 |
| 112. Formal-home discoverability and governance-anchor normalization | 3/3 | Complete    | 2026-03-31 |
| 113. Hotspot burn-down and changed-surface assurance hardening | 0/TBD | Not started | - |
| 114. Open-source reachability honesty and security-surface normalization | 0/TBD | Not started | - |
