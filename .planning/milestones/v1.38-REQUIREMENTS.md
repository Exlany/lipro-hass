# Requirements: Lipro-HASS v1.38

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
## Current Milestone (v1.38)

**Milestone Goal:** 基于 `v1.37` latest archived baseline，压缩 current selector / archive boundary / docs-first governance story，把 route-marker / promoted-asset / handoff smoke 的重复断言压回 shared helper 与单一 canonical source。
**Milestone status:** `active / phase 132 complete; closeout-ready (2026-04-02)`
**Current route mode:** `v1.38 active milestone route / starting from latest archived baseline = v1.37`
**Starting baseline:** `.planning/v1.37-MILESTONE-AUDIT.md, .planning/reviews/V1_37_EVIDENCE_INDEX.md, .planning/milestones/v1.37-ROADMAP.md, .planning/milestones/v1.37-REQUIREMENTS.md`
**Requirements basket:** `AUD-07, GOV-88, DOC-17, OSS-19, QLT-54, TST-52`
**Latest archived baseline:** `v1.37`
**Archive pointer:** `.planning/reviews/V1_37_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.37-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-complete-milestone v1.38`
**Current phase handoff:** `Phase 132 已完成 current docs/governance compression 与 focused helper dedupe；下一步进入 $gsd-complete-milestone v1.38，把 v1.38 提升为 latest archived baseline truth。`

### Audit & Governance
- [x] **AUD-07**: 必须完成一轮 docs/config/governance current-entry audit，只聚焦 live selector、latest archived pointer、public-entry wording、release runbook 与 meta guard 当前职责边界，不再扩张 repo-wide production hotspot 波次。
- [x] **GOV-88**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 必须共同承认 `v1.38 active milestone route / starting from latest archived baseline = v1.37`，并把 latest archived pointer / default next command / current phase handoff 统一压回 registry-backed 单一路径。
- [x] **DOC-17**: `docs/developer_architecture.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 首屏必须只讲 current route + latest archived pointer + current responsibilities，不再混用 archived-only frozen wording 与 phase-log 语气作为 live entry。
- [x] **OSS-19**: private-access / continuity / public-entry wording 继续保持 honest-by-default，但 route notes 应优先引用 registry-backed selector / latest archived evidence，而不是在多处手写近似陈述。

### Testing & Quality
- [x] **QLT-54**: `tests/meta/governance_current_truth.py` 不再内联历史 closeout literals / stale forbidden prose 清单；legacy archive-history markers 与 recent promoted asset packs 必须退回更窄 helper home。
- [x] **TST-52**: `tests/meta/governance_contract_helpers.py` 必须提供统一 route-marker helper；`test_governance_route_handoff_smoke.py` 只保留 docs/gsd fast-path smoke，recent promoted asset family 回流至 promoted-phase suites 或专属 helper 驱动断言。

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUD-07 | Phase 132 | Complete |
| GOV-88 | Phase 132 | Complete |
| DOC-17 | Phase 132 | Complete |
| OSS-19 | Phase 132 | Complete |
| QLT-54 | Phase 132 | Complete |
| TST-52 | Phase 132 | Complete |

## Coverage

- v1.38 requirements: 6 total
- Current mapped: 6
- Current complete: 6
- Current pending: 0

## Latest Archived Milestone (v1.37)

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