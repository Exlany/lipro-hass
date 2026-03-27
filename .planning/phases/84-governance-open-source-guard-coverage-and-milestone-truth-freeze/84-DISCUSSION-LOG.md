# Phase 84: Governance/open-source guard coverage and milestone truth freeze - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `84-CONTEXT.md` — this log only records the auto-selected path.

**Date:** 2026-03-27
**Phase:** 84-governance-open-source-guard-coverage-and-milestone-truth-freeze
**Mode:** auto / no interactive questions
**Areas discussed:** guard-home strategy, route-freeze target, ledger scope, closeout boundary

---

## Guard Home Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse existing suites | Extend existing governance/open-source suites and shared helpers where the concern home already exists | ✓ |
| Create new dedicated phase test file | Add a new phase-specific guard suite for every new concern | |
| Broad repo-wide generic guard | Add one large catch-all governance file | |

**User's choice:** auto-selected “Reuse existing suites”
**Notes:** Focus on maintainability and failure localization; only add a new file if an existing concern home is clearly missing.

## Route Freeze Target

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 84 complete / closeout-ready | Finish the last active phase of `v1.22` and route next action to milestone closeout | ✓ |
| Keep Phase 83 complete as live route | Avoid updating current route during this phase | |
| Jump directly to archived-only state | Treat this phase as archive promotion | |

**User's choice:** auto-selected “Phase 84 complete / closeout-ready”
**Notes:** Archive promotion remains milestone-closeout work, not phase execution work.

## Ledger Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Update only touched ledgers | Align verification/review ledgers that own the new guard and route-freeze truth | ✓ |
| Rewrite all governance ledgers | Touch every review/baseline file for stylistic consistency | |
| Skip ledger writeback | Leave current planning/review ledgers unchanged | |

**User's choice:** auto-selected “Update only touched ledgers”
**Notes:** Keep changes surgical and honest; if a ledger has no new residual/kill target, say so explicitly.

## Closeout Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Phase closeout only | Write `84-*` summaries/verification/validation and return next step to milestone closeout | ✓ |
| Phase closeout + milestone archive promotion | Finish both phase and milestone in one bundle | |
| Guards only, no closeout bundle | Skip phase evidence packaging | |

**User's choice:** auto-selected “Phase closeout only”
**Notes:** `$gsd-next` should become the formal handoff into milestone closeout after this phase.
