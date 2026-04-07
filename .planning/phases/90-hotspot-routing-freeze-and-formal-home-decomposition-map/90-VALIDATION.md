---
phase: 90
slug: hotspot-routing-freeze-and-formal-home-decomposition-map
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-28
---

# Phase 90 Validation Contract

## Wave Order

1. `90-01` planning truth freeze and route completion sync
2. `90-02` baseline/review/derived-doc freeze sync
3. `90-03` focused guards and route-handoff verification

## Per-Plan Focused Gates

- `90-01`
  - `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → `passed`
  - `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → `passed`
  - `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 90` → `passed`
- `90-02`
  - `uv run python scripts/check_file_matrix.py --check` → `passed`
  - `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py` → `passed`
- `90-03`
  - `uv run pytest -q tests/meta/test_phase90_hotspot_map_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py` → `passed`

## Final Gate

- `uv run pytest -q tests/meta` → `passed`
- `uv run ruff check .` → `passed`
- `uv run mypy` → `passed`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → `Phase 90 = complete`, `summary_count = 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → `v1.25 active`, `1/4 phases`, `3/3 plans`, `status = complete`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 90` → `incomplete = []`

## Sign-off Checklist

- [x] all three Phase 90 plans have focused automated gates tied to route truth, baseline/review truth, and no-regrowth guards
- [x] delete-gate policy stays explicit and localized; no ownerless carry-forward was introduced
- [x] final repo-wide gate stays green after current-route truth advanced to `v1.25 / Phase 90 complete`
- [x] next step is stably reduced to `$gsd-discuss-phase 91`
