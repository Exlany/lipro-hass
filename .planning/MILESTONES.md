# Milestones

## Current Milestone (v1.38)

**Name:** `Governance Story Compression, Archive Segregation & Public Entry Simplification`
**Status:** `active / phase 132 complete; closeout-ready (2026-04-02)`
**Current route:** `v1.38 active milestone route / starting from latest archived baseline = v1.37`
**Phase range:** `132 -> 132`
**Progress:** `1/1 phases, 3/3 plans`
**Default next command:** `$gsd-complete-milestone v1.38`
**Latest archived pointer:** `.planning/reviews/V1_37_EVIDENCE_INDEX.md`
**Latest archived audit:** `.planning/v1.37-MILESTONE-AUDIT.md`
**Starting baseline snapshots:** `.planning/milestones/v1.37-ROADMAP.md`, `.planning/milestones/v1.37-REQUIREMENTS.md`

**Current phase story:**

- `Phase 132`: current-story compression and archive-boundary cleanup ✅ (`132-01` active-route docs compression + `132-02` current-truth/helper dedupe + `132-03` promoted asset / handoff smoke cleanup complete)

## Latest Archived Milestone (v1.37)

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

## Previous Archived Milestone (v1.36)

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

**Phase range:** `132 -> 132`
**Phases completed:** `1/1 phases, 3/3 plans, 0 tasks`
**Status:** `active / phase 132 complete; closeout-ready (2026-04-02)`
**Route truth:** `v1.38 active milestone route / starting from latest archived baseline = v1.37`
**Latest archived baseline:** `v1.37`
**Default next command:** `$gsd-complete-milestone v1.38`
**Route truth:** latest archived evidence index = `.planning/reviews/V1_37_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.37-MILESTONE-AUDIT.md`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.37`

**Current phase story:**

- `Phase 132`: current-story compression and archive-boundary cleanup ✅ (`132-01` active-route docs compression + `132-02` current-truth/helper dedupe + `132-03` promoted asset / handoff smoke cleanup complete)

**Current milestone intent:**

- 把 live selector、latest archived pointer 与 historical archive story 压回更清晰的 single-source hierarchy。
- 让 governance/docs/test helpers 更偏向 canonical registry + shared helper，而不是继续扩散 prose-heavy second truth。
- 为后续 production hotspot reopen 留出更诚实的 phase boundary，而不是把它们混写进 docs-only story。

## Latest Archived Milestone (v1.37)

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

## Previous Archived Milestone (v1.36)

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