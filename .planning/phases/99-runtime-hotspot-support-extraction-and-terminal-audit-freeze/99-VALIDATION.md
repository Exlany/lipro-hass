---
phase: 99
slug: runtime-hotspot-support-extraction-and-terminal-audit-freeze
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-28
---

# Phase 99 Validation Contract

## Wave Order

1. `99-01` slim status fallback into outward home plus support collaborator
2. `99-02` slim command runtime into orchestration home plus support collaborator
3. `99-03` advance phase 99 governance truth and freeze final verification

## Focused Gates

- `99-01`
  - `uv run pytest -q tests/core/api/test_api_status_service_fallback.py tests/core/api/test_api_status_service_regressions.py` → `passed`
- `99-02`
  - `uv run pytest -q tests/core/coordinator/runtime/test_command_runtime.py tests/core/coordinator/runtime/test_command_runtime_builder_retry.py tests/core/coordinator/runtime/test_command_runtime_confirmation.py tests/core/coordinator/runtime/test_command_runtime_orchestration.py tests/core/coordinator/runtime/test_command_runtime_sender.py tests/core/coordinator/runtime/test_command_runtime_support.py tests/core/coordinator/runtime/test_runtime_telemetry_methods.py` → `passed`
- `99-03`
  - `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase90_hotspot_map_guards.py tests/meta/test_phase97_governance_assurance_freeze_guards.py tests/meta/test_phase98_route_reactivation_guards.py tests/meta/test_phase99_runtime_hotspot_support_guards.py` → `passed`
  - `uv run python scripts/check_file_matrix.py --write` → `passed`
  - `uv run python scripts/check_file_matrix.py --check` → `passed`

## Repo-wide Gates

- `uv run pytest -q tests/meta` → `passed`
- `uv run pytest -q` → `passed`
- `uv run python scripts/check_architecture_policy.py --check` → `passed`
- `uv run python scripts/check_markdown_links.py` → `passed`
- `uv run ruff check .` → `passed`
- `uv run mypy` → `passed`

## GSD Route Evidence

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → `milestone = v1.27`, `current_phase = 99`, `status = active`, `completed_phases = 2`, `completed_plans = 6`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → `Phase 98 complete`, `Phase 99 complete`, `next_phase = null`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 99` → `phase_found = true`, `has_context = true`, `has_research = true`, `plan_count = 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 99` → `phase_found = true`, `incomplete_count = 0`, `plan_count = 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 99` → `incomplete = []`, `waves = {1: [99-01, 99-02], 2: [99-03]}`
- 按 `$HOME/.codex/get-shit-done/workflows/next.md` route-7 规则（all phases complete → complete milestone），`$gsd-next` 当前应推进到 `$gsd-complete-milestone v1.27`

## Sign-off Checklist

- [x] `99-01` / `99-02` support extraction 已完成且 focused runtime suites 通过
- [x] `99-03` governance freeze、maps/ledgers sync 与 focused meta suites 已完成
- [x] repo-wide quality gates、GSD parser truth 与 next-step routing 已全部闭环
