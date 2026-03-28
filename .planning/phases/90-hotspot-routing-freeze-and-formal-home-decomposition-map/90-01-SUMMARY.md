---
phase: 90-hotspot-routing-freeze-and-formal-home-decomposition-map
plan: "01"
status: completed
completed: 2026-03-28
---

# Summary 90-01

**Planning truth now records one honest Phase 90 story: five hotspots remain formal homes, four outward shells stay protected, and the route advances to Phase 91 instead of lingering in planning-ready drift.**

## Outcome

- `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` now agree that `Phase 90` is complete and the next command is `$gsd-discuss-phase 91`.
- `HOT-40` is marked complete in requirements traceability, while `ARC-24 / TYP-23 / SEC-01 / TST-29 / QLT-37` stay deferred to `Phase 91 -> 93`.
- Current-route prose now says `v1.25 active route / Phase 90 complete / latest archived baseline = v1.24` across every machine-readable governance contract.

## Verification

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 90`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- `MILESTONES.md` was updated alongside the other route-contract mirrors because the machine-readable governance contract lives there too.

## Next Readiness

- `90-02` can now sync baseline/review/derived docs to the same frozen ownership map without carrying route ambiguity.
