# Milestones

## v1.40 Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening (Shipped: 2026-04-02)

**Status:** `archived / evidence-ready (2026-04-02)`
**Current route:** `no active milestone route / latest archived baseline = v1.40`
**Phase range:** `134 -> 135`
**Progress:** `2/2 phases, 6/6 plans`
**Default next command:** `$gsd-new-milestone`
**Latest archived pointer:** `.planning/reviews/V1_40_EVIDENCE_INDEX.md`
**Archived audit reference:** `.planning/v1.40-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.40-ROADMAP.md`, `.planning/milestones/v1.40-REQUIREMENTS.md`
**Archive state:** `archived snapshots created / handoff-ready`

**Shipped phase story:**

- `Phase 134`: request-policy ownership, entity de-reflection, and fan truth hardening ✅ (`134-01` RequestPolicy owner convergence + `134-02` entity projection de-reflection / fan truth correction + `134-03` docs/guards/tests/verification sync complete)
- `Phase 135`: runtime-access projection split, auth reason typing, and dispatch route hardening ✅ (`135-01` runtime-access projection split + `135-02` auth reason typing / dispatch route typing + `135-03` docs/guards/route sync complete)

## Previous Archived Milestone (v1.39)

## v1.39 Governance Recovery, Runtime Consistency & Public Contract Correction (Shipped: 2026-04-02)

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

## v1.38 Governance Story Compression, Archive Segregation & Public Entry Simplification (Shipped: 2026-04-02)

**Status:** `archived / evidence-ready (2026-04-02)`
**Current route:** `no active milestone route / latest archived baseline = v1.38`
**Phase range:** `132 -> 132`
**Progress:** `1/1 phases, 3/3 plans`
**Default next command:** `$gsd-new-milestone`
**Latest archived pointer:** `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
**Archived audit:** `.planning/v1.38-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.38-ROADMAP.md`, `.planning/milestones/v1.38-REQUIREMENTS.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.39`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.38`

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
active_milestone: null
latest_archived:
  version: v1.40
  name: Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening
  status: archived / evidence-ready (2026-04-02)
  phase: '135'
  phase_title: runtime-access projection split, auth reason typing, and dispatch route hardening
  phase_dir: 135-runtime-access-auth-and-dispatch-contract-hardening
  audit_path: .planning/v1.40-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_40_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.39
  name: Governance Recovery, Runtime Consistency & Public Contract Correction
  evidence_path: .planning/reviews/V1_39_EVIDENCE_INDEX.md
bootstrap:
  current_route: no active milestone route / latest archived baseline = v1.40
  default_next_command: $gsd-new-milestone
  latest_archived_evidence_pointer: .planning/reviews/V1_40_EVIDENCE_INDEX.md
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

## Historical Governance Continuity Anchors

- revalidated 2026-03-17
- .planning/v1.4-MILESTONE-AUDIT.md
- .planning/v1.5-MILESTONE-AUDIT.md
- V1_4_EVIDENCE_INDEX.md
- V1_5_EVIDENCE_INDEX.md

## Historical Archive Snapshot References

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
