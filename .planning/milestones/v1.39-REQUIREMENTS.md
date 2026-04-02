# Requirements: Lipro-HASS v1.39

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

**Milestone Goal:** 基于 `v1.38` latest archived baseline，先恢复 current governance lane 的 route/source-path/projection 一致性，再为 runtime consistency 与 public contract correction 建立单一执行入口，不再把 sanctioned hotspot 混写进 docs-only closeout。
**Milestone status:** `active / phase 133 complete; closeout-ready (2026-04-02)`
**Current route mode:** `v1.39 active milestone route / starting from latest archived baseline = v1.38`
**Starting baseline:** `.planning/v1.38-MILESTONE-AUDIT.md, .planning/reviews/V1_38_EVIDENCE_INDEX.md, .planning/milestones/v1.38-ROADMAP.md, .planning/milestones/v1.38-REQUIREMENTS.md`
**Requirements basket:** `GOV-89, ARC-42, HOT-61, DOC-18, QLT-55, TST-53`
**Latest archived baseline:** `v1.38`
**Archive pointer:** `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.38-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-complete-milestone v1.39`
**Current phase handoff:** `Phase 133 的 governance/runtime/public-contract/closeout 四条执行轨均已完成，requirements 已在单一 phase 中闭合；下一步为 $gsd-complete-milestone v1.39。`

### Governance Recovery
- [x] **GOV-89**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、`GOVERNANCE_REGISTRY.json`、`FILE_MATRIX.md` 与 `PROMOTED_PHASE_ASSETS.md` 必须共同承认 `v1.39 active milestone route / starting from latest archived baseline = v1.38`，并把 `Phase 133` 作为唯一 active phase。

### Runtime Consistency
- [x] **ARC-42**: `runtime_types.py`、coordinator service contracts 与 runtime-facing typed contract families 必须明确收口到单一下一轮 formal-home 修正路线，不再让 runtime consistency debt 以 vague carry-forward 形式漂浮在 milestone audit 中。
- [x] **HOT-61**: `core/auth/manager.py`、`request_policy.py`、`dispatch.py` 与 `entities/firmware_update.py` 的 sanctioned hotspot 需要在同一条 phase story 中被列为 runtime consistency lane，而不是散落为未编排 debt。 

### Public Contract & Quality
- [x] **DOC-18**: developer/public/runbook/support/manifest first-hop 必须回到 current formal home truth，避免 archived-only wording、stale route token 或 public contract drift 继续污染 active milestone。
- [x] **QLT-55**: route source-path hygiene、Session Continuity 真实路径、FILE_MATRIX inventory 与 promoted-phase allowlist slug 必须在同一轮治理修复内通过 focused checks。
- [x] **TST-53**: 当前 governance red-test 所依赖的 planning docs、phase asset inventory 与 promoted/file-matrix 文档面必须先收敛，再进入后续 execute-phase。 

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GOV-89 | Phase 133 | Complete |
| ARC-42 | Phase 133 | Complete |
| HOT-61 | Phase 133 | Complete |
| DOC-18 | Phase 133 | Complete |
| QLT-55 | Phase 133 | Complete |
| TST-53 | Phase 133 | Complete |

## Coverage

- v1.39 requirements: 6 total
- Current mapped: 6
- Current complete: 6
- Current pending: 0

## Historical Traceability Appendix

为保持 archived continuity guards 与历史 requirement mapping 的单一叙事，保留以下已归档 traceability 锚点：

| Requirement | Phase | Status |
|-------------|-------|--------|
| HOT-14 | Phase 60 | Complete |
| TST-12 | Phase 60 | Complete |
| GOV-44 | Phase 60 | Complete |


## Latest Archived Milestone (v1.38)

**Milestone Goal:** 基于 `v1.37` latest archived baseline，压缩 current selector / archive boundary / docs-first governance story，把 route-marker / promoted-asset / handoff smoke 的重复断言压回 shared helper 与单一 canonical source。
**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Current route mode:** `no active milestone route / latest archived baseline = v1.38`
**Starting baseline:** `.planning/v1.37-MILESTONE-AUDIT.md, .planning/reviews/V1_37_EVIDENCE_INDEX.md, .planning/milestones/v1.37-ROADMAP.md, .planning/milestones/v1.37-REQUIREMENTS.md`
**Requirements basket:** `AUD-07, GOV-88, DOC-17, OSS-19, QLT-54, TST-52`
**Latest archived baseline:** `v1.38`
**Archive pointer:** `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.38-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 132 的 requirement coverage、summary / verification / validation / audit / evidence index 已冻结为 archived baseline truth。`

## Previous Archived Milestone (v1.37)

**Milestone Goal:** 基于 `v1.36` latest archived baseline，先完成一次不遗漏 Python/docs/config/governance 切面的 repo-wide terminal audit，再把首批 repo-internal hotspots（REST fallback / runtime-command / firmware-update）继续 inward decomposition，最后把 open-source continuity / private fallback reality 诚实固化为治理决策边界与最终审阅报告。
**Milestone status:** `archived / evidence-ready (2026-04-01)`
**Current route mode:** `no active milestone route / latest archived baseline = v1.37`
**Starting baseline:** `.planning/v1.36-MILESTONE-AUDIT.md, .planning/reviews/V1_36_EVIDENCE_INDEX.md, .planning/milestones/v1.36-ROADMAP.md, .planning/milestones/v1.36-REQUIREMENTS.md`
**Requirements basket:** `AUD-06, ARC-40, HOT-59, TST-50, QLT-52, ARC-41, HOT-60, TST-51, GOV-87, DOC-16, OSS-18, QLT-53`
**Latest archived baseline:** `v1.37`
**Archive pointer:** `.planning/reviews/V1_37_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.37-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 129 -> 131 的 requirement coverage、summary / verification / audit / evidence index 已冻结为 archived evidence frozen。`

## Historical Archived Milestone (v1.35)
