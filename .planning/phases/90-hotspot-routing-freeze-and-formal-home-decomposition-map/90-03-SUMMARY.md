---
phase: 90-hotspot-routing-freeze-and-formal-home-decomposition-map
plan: "03"
status: completed
completed: 2026-03-28
---

# Summary 90-03

**Focused governance and hotspot guards now freeze Phase 90 from five angles: route truth, public-surface notes, dependency notes, ledger wording, and a dedicated no-regrowth guard file.**

## Outcome

- `tests/meta/test_phase90_hotspot_map_guards.py` now blocks formal-home/delete-target drift, shell-regrowth drift, and route-truth drift.
- `tests/meta/governance_current_truth.py`, route-handoff smokes, and follow-up route tests were aligned to the completed `Phase 90` story and next-step `Phase 91` discussion route.
- `tests/meta/public_surface_phase_notes.py` and `tests/meta/dependency_guards_review_ledgers.py` now assert the new Phase 90 baseline/review wording directly.

## Verification

- `uv run pytest -q tests/meta/test_phase90_hotspot_map_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py`
- `uv run pytest -q tests/meta`
- `uv run ruff check .`
- `uv run mypy`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- The focused guard landed as both a dedicated file and as extensions to the existing public-surface/dependency helper suites so the freeze is protected at the concern level and at the cross-route level.

## Next Readiness

- Phase 90 now has a complete execution trace and can hand off directly to `Phase 91` discussion / planning.
