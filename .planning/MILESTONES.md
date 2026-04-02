# Milestones

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

**Active phase story:**

- `Phase 133`: governance recovery, runtime consistency, and public contract correction ✅ (`133-01` governance bootstrap + `133-02` runtime consistency + `133-03` public contract correction + `133-04` governance closeout/resync complete；closeout 已冻结，latest archived evidence pointer = `.planning/reviews/V1_39_EVIDENCE_INDEX.md``)

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

**Archived phase story:**

- `Phase 129`: rest fallback explicit-surface convergence and api hotspot slimming ✅ (`129-01` façade explicit-surface convergence + `129-02` fallback seam tightening complete)
- `Phase 130`: runtime command and firmware-update hotspot decomposition ✅ (`130-01` runtime command inward split + `130-02` firmware-update thin-shell/task-outcome tightening complete)
- `Phase 131`: repo-wide terminal audit closeout and governance continuity decisions ✅ (`131-01` terminal audit + topology closeout, `131-02` docs-first / toolchain / registry honesty sync, `131-03` selector closeout / promoted evidence / validation freeze complete)

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

**Archived phase story:**

- `Phase 126`: service-router developer callback-home convergence and diagnostics helper residual slimming ✅ (`126-01` diagnostics helper shell thinning + route bootstrap + focused/full verification complete)
- `Phase 127`: runtime-access de-reflection, typed runtime entry contracts, and hotspot continuation ✅ (`127-01` typed telemetry seam + `127-02` support-view de-reflection + `127-03` focused/full verification and governance sync complete)
- `Phase 128`: open-source readiness, benchmark-coverage gates, and maintainer continuity hardening ✅ (`128-01` readiness honesty / version-source / selector projection sync + `128-02` coverage baseline diff / artifacts + `128-03` benchmark smoke / strict markers / evidence freeze complete)

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
  current_route: no active milestone route / latest archived baseline = v1.39
  default_next_command: $gsd-new-milestone
  latest_archived_evidence_pointer: .planning/reviews/V1_39_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->
## Latest Archived Milestone (v1.39)

**Phase range:** `133 -> 133`
**Phases completed:** `1/1 phases, 4/4 plans, 0 tasks`
**Status:** `archived / evidence-ready (2026-04-02)`
**Route truth:** `no active milestone route / latest archived baseline = v1.39`
**Latest archived baseline:** `v1.39`
**Default next command:** `$gsd-new-milestone`
**Route truth:** latest archived evidence index = `.planning/reviews/V1_39_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.39-MILESTONE-AUDIT.md`

**Active milestone intent:**

- 已完成 governance lane recovery、runtime consistency 修补与 public contract correction，并把它们压回单一 `Phase 133` 主线。
- `v1.39` 已完成 closeout，并正式前推为 latest archived baseline。
- `$gsd-next` 的等价结论现已回到 `$gsd-new-milestone`，而不是重复归档或重放 execute-phase。

## Previous Archived Milestone (v1.38)

**Phase range:** `132 -> 132`
**Phases completed:** `1/1 phases, 3/3 plans, 0 tasks`
**Status:** `archived / evidence-ready (2026-04-02)`
**Route truth:** `no active milestone route / latest archived baseline = v1.38`
**Latest archived baseline:** `v1.38`
**Default next command:** `$gsd-new-milestone`
**Route truth:** latest archived evidence index = `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.38-MILESTONE-AUDIT.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.38`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.37`

**Archived phase story:**

- `Phase 132`: current-story compression and archive-boundary cleanup ✅ (`132-01` active-route docs compression + `132-02` current-truth/helper dedupe + `132-03` promoted asset / handoff smoke cleanup complete)

**Archived milestone intent:**

- 把 live selector、latest archived pointer 与 historical archive story 压回更清晰的 single-source hierarchy。
- 让 governance/docs/test helpers 更偏向 canonical registry + shared helper，而不是继续扩散 prose-heavy second truth。
- 为后续 production hotspot reopen 留出更诚实的 phase boundary，而不是把它们混写进 docs-only story。

## Historical Archived Milestone (v1.37)

**Phase range:** `129 -> 131`
**Phases completed:** `3/3 phases, 7/7 plans, 0 tasks`
**Status:** `archived / evidence-ready (2026-04-01)`
**Route truth:** `no active milestone route / latest archived baseline = v1.37`
**Latest archived baseline:** `v1.37`
**Default next command:** `$gsd-new-milestone`
**Route truth:** latest archived evidence index = `.planning/reviews/V1_37_EVIDENCE_INDEX.md`
**Current audit artifact:** `.planning/v1.37-MILESTONE-AUDIT.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.37`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.36`

**Archived phase story:**

- `Phase 129`: rest fallback explicit-surface convergence and api hotspot slimming ✅ (`129-01` façade explicit-surface convergence + `129-02` fallback seam tightening complete)
- `Phase 130`: runtime command and firmware-update hotspot decomposition ✅ (`130-01` runtime command inward split + `130-02` firmware-update thin-shell/task-outcome tightening complete)
- `Phase 131`: repo-wide terminal audit closeout and governance continuity decisions ✅ (`131-01` terminal audit + topology closeout, `131-02` docs-first / toolchain / registry honesty sync, `131-03` selector closeout / promoted evidence / validation freeze complete)

## Historical Archived Milestone (v1.36)

**Phase range:** `126 -> 128`
**Phases completed:** `3/3 phases, 7/7 plans, 0 tasks`
**Status:** `archived / evidence-ready (2026-04-01)`
**Route truth:** `no active milestone route / latest archived baseline = v1.36`
**Latest archived baseline:** `v1.36`
**Default next command:** `$gsd-new-milestone`
**Route truth:** latest archived evidence index = `.planning/reviews/V1_36_EVIDENCE_INDEX.md`
**Current audit artifact:** `.planning/v1.36-MILESTONE-AUDIT.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.36`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.35`

## Historical Archived Milestone (v1.35)

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
