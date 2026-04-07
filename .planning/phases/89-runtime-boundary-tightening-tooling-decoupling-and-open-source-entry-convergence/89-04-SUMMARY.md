---
phase: 89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence
plan: "04"
subsystem: governance
tags: [docs, governance, metadata, opensource, routing]
requires:
  - phase: 89-01
    provides: narrowed runtime boundary truth
  - phase: 89-02
    provides: single bootstrap wiring truth
  - phase: 89-03
    provides: tooling helper ownership truth
provides:
  - docs-first public entry convergence
  - active v1.24 planning route truth
  - focused entry-route regression guards
affects: [README.md, docs/README.md, custom_components/lipro/manifest.json, .planning, tests/meta]
tech-stack:
  added: []
  patterns:
    - docs-first public entry story backed by focused governance guards
key-files:
  created:
    - tests/meta/test_phase89_entry_route_guards.py
  modified:
    - README.md
    - README_zh.md
    - docs/README.md
    - .github/ISSUE_TEMPLATE/bug.yml
    - .github/ISSUE_TEMPLATE/feature_request.yml
    - custom_components/lipro/manifest.json
    - .planning/PROJECT.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/STATE.md
    - .planning/MILESTONES.md
    - .planning/baseline/GOVERNANCE_REGISTRY.json
    - .planning/codebase/ARCHITECTURE.md
    - .planning/codebase/CONCERNS.md
    - .planning/codebase/STRUCTURE.md
    - .planning/codebase/TESTING.md
    - .planning/reviews/FILE_MATRIX.md
key-decisions:
  - "Keep `docs/README.md` as the canonical first hop and make manifest/templates point to honest docs/support routes instead of pretending public GitHub surfaces are guaranteed."
  - "Sync current governance truth to `v1.24 / Phase 89 / planning-ready` until execution artifacts exist; do not prematurely promote execution traces to authority."
patterns-established:
  - "Public entry, issue-routing, and current-route governance truth must be updated together and guarded together."
requirements-completed:
  - OSS-12
  - GOV-64
  - QLT-36
  - TST-28
duration: session-carried
completed: 2026-03-27
---

# Summary 89-04

**README, docs, templates, manifest metadata, and active governance maps now tell one docs-first story for a private-access repository, with Phase 89 planning truth synchronized across the current route.**

## Outcome

- `README.md`, `README_zh.md`, and `docs/README.md` now point readers to one canonical docs-first first hop and consistently describe conditional GitHub surfaces.
- GitHub issue templates and `custom_components/lipro/manifest.json` were aligned to the same support / security / documentation routes.
- `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/baseline/GOVERNANCE_REGISTRY.json`, `.planning/codebase/*`, and `FILE_MATRIX.md` now describe Phase 89 as the active `v1.24 / planning-ready` route and record the runtime/tooling convergence from 89-01/02/03.
- Focused governance tests were added/updated so route drift, docs drift, and metadata drift fail close to the source.

## Verification

- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_version_sync.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase89_entry_route_guards.py`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- None — docs, metadata, and governance route truth were converged without inventing a new public issue/support surface.

## Next Readiness

- The phase now has complete plan-level execution trace and can enter phase-level verification / completion routing.
