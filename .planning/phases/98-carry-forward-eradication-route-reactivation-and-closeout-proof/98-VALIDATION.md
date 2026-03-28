---
phase: 98
slug: carry-forward-eradication-route-reactivation-and-closeout-proof
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-28
---

# Phase 98 Validation Contract

## Wave Order

1. `98-01` carry-forward eradication truth freeze and command-runtime duplication trim
2. `98-02` current-route doc/test/map reactivation and historical-closeout guard split
3. `98-03` full proof chain, phase98 closeout bundle, and next-step determination

## Focused Gates

- `98-01`
  - `uv run pytest -q tests/meta/public_surface_runtime_contracts.py tests/platforms/test_sensor.py` → `passed` (`46 passed`)
  - `uv run ruff check custom_components/lipro/core/coordinator/runtime/command_runtime.py tests/meta/public_surface_runtime_contracts.py tests/platforms/test_sensor.py` → `passed`
- `98-02`
  - `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase90_hotspot_map_guards.py tests/meta/test_phase97_governance_assurance_freeze_guards.py tests/meta/test_phase98_route_reactivation_guards.py` → `passed` (`22 passed`)
  - `uv run python scripts/check_file_matrix.py --write` → `passed`
  - `uv run python scripts/check_file_matrix.py --check` → `passed`
- `98-03`
  - `uv run pytest -q tests/meta` → `passed` (`234 passed`)
  - `uv run pytest -q` → `passed` (`2550 passed`, `5 snapshots passed`)
  - `uv run python scripts/check_architecture_policy.py --check` → `passed`
  - `uv run python scripts/check_markdown_links.py` → `passed`
  - `uv run ruff check .` → `passed`
  - `uv run mypy` → `passed` (`Success: no issues found in 690 source files`)

## GSD Route Evidence

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → `milestone = v1.27`, `current_phase = 98`, `status = active`, `completed_phases = 1`, `completed_plans = 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → `Phase 98 complete`, `phase_count = 1`, `next_phase = null`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 98` → `phase_found = true`, `has_context = true`, `has_research = true`, `plan_count = 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 98` → `phase_found = true`, `incomplete_count = 0`, `plan_count = 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 98` → `incomplete = []`, `waves = {1: [98-01, 98-02], 2: [98-03]}`
- 按 `$HOME/.codex/get-shit-done/workflows/next.md` 的 route-7 规则（all phases complete → complete milestone），`$gsd-next` 当前应推进到 `$gsd-complete-milestone v1.27`

## Sign-off Checklist

- [x] carry-forward eradication、route reactivation、FILE_MATRIX / TESTING / VERIFICATION projections 与 focused guards 已共同闭环
- [x] `Phase 98` 计划资产、summary bundle 与 parser-facing GSD commands 全部可解析
- [x] repo-wide quality proof 已全部通过，下一跳只剩 `$gsd-complete-milestone v1.27`
