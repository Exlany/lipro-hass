# v1.35 Master Audit Ledger

**Milestone:** `v1.35 Master Audit Closure, Public Surface Finalization & Release Traceability`
**Baseline:** latest archived baseline = `v1.34`
**Status:** closeout-ready remediation ledger
**Updated:** 2026-04-01

## Purpose

This ledger is the single active synthesis surface for the `v1.35` repo-wide audit. It does **not** replace `.planning/v1.34-MILESTONE-AUDIT.md` or `.planning/reviews/V1_34_EVIDENCE_INDEX.md`; those remain the archived baseline. This file records the current audit verdict, remediation status, and carry-forward routing for the closeout-ready milestone.

## Coverage

### Production / scripts review
- Covered: `custom_components/lipro/**/*.py`, `scripts/**/*.py`
- Approximate Python files reviewed in this slice: `345`
- Additional authority references: `AGENTS.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `.planning/reviews/RESIDUAL_LEDGER.md`, `.planning/reviews/KILL_LIST.md`

### Assurance review
- Covered: `tests/**`
- Approximate Python files reviewed in this slice: `416`
- Collected pytest items snapshot: `2683`

### Open-source / governance review
- Covered: `README.md`, `README_zh.md`, `docs/README.md`, `SUPPORT.md`, `SECURITY.md`, `CHANGELOG.md`, `pyproject.toml`, `custom_components/lipro/manifest.json`, `.planning/baseline/**`, `.planning/reviews/**`, release/security workflows, issue templates

## Strengths Confirmed

### Architecture
- thin Home Assistant entry shells remain intact and do not regrow a second runtime/protocol root
- formal protocol root, runtime root, and control-plane homes remain explicit and machine-guarded
- entity/platform layers continue to consume sanctioned runtime surfaces rather than direct protocol clients
- boundary decoders still normalize vendor payloads before they leak into runtime/domain concerns

### Quality / Assurance
- production hotspots are real but mostly controlled; the largest production files still stay below the hard 500-line ceiling
- no live `TODO/FIXME/HACK/XXX` debt was found in production code
- tests remain broad and behaviorally strong, especially in `core`, `platforms`, and `meta`
- release/security contract is unusually mature for a private-access integration: CI reuse, `pip-audit`, tagged `CodeQL`, `SBOM`, attestation, and `cosign` are all present

### Open-source surface
- docs-first public routing is coherent and already better than many private-access repositories
- bilingual entry navigation remains explicit and consistent
- security/support honesty about access mode, future public mirror, and lack of guaranteed non-GitHub fallback remains intact

## Blocking Findings For v1.35

| ID | Finding | Status | Resolution Route |
| --- | --- | --- | --- |
| `AUD-05` | Repo-wide audit conclusions were spread across archived audits, phase-local artifacts, and conversational review notes | resolved | `V1_35_MASTER_AUDIT_LEDGER.md` now serves as the single active synthesis surface |
| `DOC-12` | `SUPPORT.md` / `SECURITY.md` allowed maintainer appendix continuity truth to compete with first-hop user routing | resolved | public routing now stays ahead of the appendix while continuity truth remains available as deep follow-up |
| `OSS-16` | release-facing metadata projections in `pyproject.toml` / `manifest.json` floated on `blob/main` instead of the current tag | resolved | all release-facing projections now target `/blob/v1.0.0/...` and are frozen by focused tests |
| `GOV-81` | active route truth needed to align audit ledger, boundary cleanup, metadata traceability, and focused guards into one route story | resolved | `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` now all tell the same closeout-ready `v1.35` story |
| `TST-44` | focused guards did not yet freeze appendix ordering and tagged-release metadata projection | resolved | focused meta suites now reject appendix-first drift and `/blob/main/` regressions |

## Non-Blocking Carry-Forward Findings

### Code hotspots (carry-forward, not blockers for v1.35)
- `custom_components/lipro/runtime_types.py` remains a heavy cross-plane contract hub
- `custom_components/lipro/control/runtime_access*` remains a notable support-family hotspot, but `service_router` non-diagnostics callback fragmentation has now been closed by Phase 123
- `custom_components/lipro/core/auth/manager.py`, `custom_components/lipro/core/command/result_policy.py`, `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`, and `scripts/check_architecture_policy.py` remain priority inward-split candidates
- some compatibility handling still exists in localized runtime/device helpers, but it is currently controlled rather than regrown into a public seam

### Assurance / governance hotspots
- `tests/meta` has become expensive and sometimes prose-heavy; a meaningful slice of runtime cost now comes from governance scanning rather than behavior verification
- several docs/governance guards still freeze token wording or historical phase naming more tightly than the underlying semantic contract requires
- helper/harness code remains under-tested directly and is often validated only indirectly through higher-level suites

### Open-source/governance limitations that remain honest but unresolved
- no guaranteed non-GitHub private vulnerability reporting fallback exists today
- issue/discussion/security UI remains access-mode dependent for this private-access repository
- `.planning` remains a heavy maintainer-facing governance surface; this is intentional, but it still increases outside-contributor cognitive load

## Remediation Status Snapshot

| Plan | Focus | Status | Notes |
| --- | --- | --- | --- |
| `122-01` | master audit ledger / route truth | complete | ledger truth, route contract alignment, and closeout audit handoff are all in place |
| `122-02` | public first-hop boundary cleanup | complete | docs/support/security now keep public routing ahead of maintainer appendix continuity truth |
| `122-03` | metadata traceability + focused guards | complete | tag-aware metadata projections and focused tests are now sealed |
| `123-01` | route reopen + phase assets | complete | planning selector truth, phase assets, and current route handoff are now aligned |
| `123-02` | service-router reconvergence | complete | non-diagnostics callbacks reconverged and four thin shells removed |
| `123-03` | docs/governance freeze refresh | complete | developer/public architecture docs and governance ledgers now match the reconverged topology |

## Explicit Non-Goals

- do not reopen archived `v1.34` evidence as live truth
- do not invent undocumented delegate, hidden maintainer, or non-existent private fallback story
- do not expand `v1.35` into broad runtime/protocol refactors; code-hotspot carry-forward remains separate work

## Exit Criteria For This Ledger

This ledger is complete for `v1.35` when:
1. the public first-hop files clearly finish their user-facing route before the maintainer appendix begins
2. metadata projections track the current package tag and focused tests fail on regression
3. planning docs and phase summaries can point here as the single active audit synthesis surface
4. unresolved code/test hotspot items remain explicitly marked as carry-forward rather than silently forgotten

## Phase 123 Carry-forward Closure

### Resolved in this phase
- `ARC-34` / `HOT-54`: `service_router` non-diagnostics callback family reconverged into `service_router_handlers.py`; four over-thin split shells were removed.
- `DOC-13`: developer/public architecture docs now distinguish current reconverged topology from the archived Phase 104 predecessor split.
- `GOV-82` / `TST-45`: planning route truth, file-matrix projection, and focused guards now acknowledge `Phase 123` as the honest final closeout carry-forward for `v1.35`.
