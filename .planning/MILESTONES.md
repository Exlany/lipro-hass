# Milestones

## Current Milestone (v1.40)

**Name:** `Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening`
**Status:** `active / phase 134 complete; closeout-ready (2026-04-02)`
**Current route:** `v1.40 active milestone route / starting from latest archived baseline = v1.39`
**Phase range:** `134 -> 134`
**Progress:** `1/1 phases, 3/3 plans`
**Default next command:** `$gsd-complete-milestone v1.40`
**Latest archived pointer:** `.planning/reviews/V1_39_EVIDENCE_INDEX.md`
**Archived audit reference:** `.planning/v1.39-MILESTONE-AUDIT.md`
**Starting baseline snapshots:** `.planning/milestones/v1.39-ROADMAP.md`, `.planning/milestones/v1.39-REQUIREMENTS.md`

**Active phase story:**

- `Phase 134`: request-policy ownership, entity de-reflection, and fan truth hardening ✅ (`134-01` RequestPolicy owner convergence + `134-02` entity projection de-reflection / fan truth correction + `134-03` docs/guards/tests/verification sync complete；当前 next = `$gsd-complete-milestone v1.40`)

## Latest Archived Milestone (v1.39)

**Name:** `Governance Recovery, Runtime Consistency & Public Contract Correction`
**Status:** `archived / evidence-ready (2026-04-02)`
**Current route:** `no active milestone route / latest archived baseline = v1.39`
**Phase range:** `133 -> 133`
**Progress:** `1/1 phases, 4/4 plans`
**Default next command:** `$gsd-new-milestone`
**Latest archived pointer:** `.planning/reviews/V1_39_EVIDENCE_INDEX.md`
**Archived audit:** `.planning/v1.39-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.39-ROADMAP.md`, `.planning/milestones/v1.39-REQUIREMENTS.md`

**Archived phase story:**

- `Phase 133`: governance recovery, runtime consistency, and public contract correction ✅ (`133-01` governance bootstrap + `133-02` runtime consistency + `133-03` public contract correction + `133-04` governance closeout/resync complete；closeout 已冻结，latest archived evidence pointer = `.planning/reviews/V1_39_EVIDENCE_INDEX.md`)

## Previous Archived Milestone (v1.38)

**Name:** `Governance Story Compression, Archive Segregation & Public Entry Simplification`
**Status:** `archived / evidence-ready (2026-04-02)`
**Current route:** `no active milestone route / latest archived baseline = v1.38`
**Phase range:** `132 -> 132`
**Progress:** `1/1 phases, 3/3 plans`
**Default next command:** `$gsd-new-milestone`
**Latest archived pointer:** `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
**Archived audit:** `.planning/v1.38-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.38-ROADMAP.md`, `.planning/milestones/v1.38-REQUIREMENTS.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.38`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.37`

**Archived phase story:**

- `Phase 132`: current-story compression and archive-boundary cleanup ✅ (`132-01` active-route docs compression + `132-02` current-truth/helper dedupe + `132-03` promoted asset / handoff smoke cleanup complete)

## Historical Archived Milestone (v1.37)

**Name:** `Repo-Wide Terminal Audit, Hotspot Decomposition & Governance Continuity Decisions`
**Status:** `archived / evidence-ready (2026-04-01)`
**Current route:** `no active milestone route / latest archived baseline = v1.37`
**Phase range:** `129 -> 131`
**Progress:** `3/3 phases, 7/7 plans`
**Default next command:** `$gsd-new-milestone`
**Latest archived pointer:** `.planning/reviews/V1_37_EVIDENCE_INDEX.md`
**Archived audit:** `.planning/v1.37-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.37-ROADMAP.md`, `.planning/milestones/v1.37-REQUIREMENTS.md`

## Historical Archived Milestone (v1.36)

**Name:** `Terminal Residual Convergence, Runtime Access De-Reflection & Open-Source Readiness Hardening`
**Status:** `archived / evidence-ready (2026-04-01)`
**Current route:** `no active milestone route / latest archived baseline = v1.36`
**Phase range:** `126 -> 128`
**Progress:** `3/3 phases, 7/7 plans`
**Default next command:** `$gsd-new-milestone`
**Latest archived pointer:** `.planning/reviews/V1_36_EVIDENCE_INDEX.md`
**Archived audit:** `.planning/v1.36-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.36-ROADMAP.md`, `.planning/milestones/v1.36-REQUIREMENTS.md`

---

> Machine-readable bootstrap truth now lives in the shared `governance-route` contract block below; milestone chronology remains human-readable archive history instead of the parser-visible selector.

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
  status: active / phase 134 complete; closeout-ready (2026-04-02)
  phase: '134'
  phase_title: request-policy ownership, entity de-reflection, and fan truth hardening
  phase_dir: 134-request-policy-ownership-entity-de-reflection-and-fan-truth-hardening
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
## Archived Chronology Appendix


## v1.2 Host-Neutral Core & Replay Completion
- historical continuity anchor retained.

## v1.5 Governance Truth Consolidation & Control-Surface Finalization
- historical continuity anchor retained.

## v1.6 Delivery Trust Hardening, Runtime Boundary Decoupling & Maintainability Closure
- historical continuity anchor retained.

## v1.13 Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence
- historical continuity anchor retained.

## v1.14 Governance Truth Realignment, Typed Runtime Access & Final Hidden-Root Closure
- evidence pointer: `.planning/reviews/V1_14_EVIDENCE_INDEX.md`

## v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement
- historical continuity anchor retained.

## v1.23 Repository-Wide Terminal Code Audit, Residual Eradication & Closeout Truth Freeze
- evidence pointer: `.planning/reviews/V1_23_EVIDENCE_INDEX.md`

## v1.24 Runtime Boundary Tightening, Tooling Kernel Decoupling & Open-Source Entry Convergence
- evidence pointer: `.planning/reviews/V1_24_EVIDENCE_INDEX.md`

## v1.25 Hotspot Inward Decomposition, Typed Boundary Hardening & Redaction Convergence
- evidence pointer: `.planning/reviews/V1_25_EVIDENCE_INDEX.md`

## v1.28 Governance Portability, Verification Stratification & Open-Source Continuity Hardening
- evidence pointer: `.planning/reviews/V1_28_EVIDENCE_INDEX.md`

## v1.29 Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization
- evidence pointer: `.planning/reviews/V1_29_EVIDENCE_INDEX.md`
