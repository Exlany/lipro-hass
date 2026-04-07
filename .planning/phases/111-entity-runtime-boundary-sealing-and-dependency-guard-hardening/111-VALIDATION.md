---
phase: 111
slug: entity-runtime-boundary-sealing-and-dependency-guard-hardening
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-31
---

# Phase 111 Validation Contract

## Wave Order

1. `111-01` replace concrete entity coordinator binding with sanctioned runtime surface
2. `111-02` enforce entity/control runtime-boundary bans through policy and focused guards
3. `111-03` extend changed-surface validation for runtime access and command-result failure branches

## Completion Expectations

- `111-01` 至 `111-03` 全部生成对应 `*-SUMMARY.md`，并在 `phase-plan-index 111` 中全部表现为 `has_summary = true`。
- `111-VERIFICATION.md` 对 `ARC-28`、`GOV-71`、`TST-38` 给出 passed verdict 与命令证据。
- `.planning/baseline/VERIFICATION_MATRIX.md` 必须同步承认本阶段新增的 dependency guards 与 focused changed-surface proof。
- 若本阶段新增 architecture policy rule ids / targeted bans，`tests/meta/test_governance_guards.py` 与 `scripts/check_architecture_policy.py --check` 必须共同通过。
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 在 phase closeout 时需显式提升：
  - `111-01-SUMMARY.md`
  - `111-02-SUMMARY.md`
  - `111-03-SUMMARY.md`
  - `111-VERIFICATION.md`
  - `111-VALIDATION.md`
  - `111-SUMMARY.md`

## GSD Route Evidence

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → expected `milestone = v1.31`, `current_phase = 111`, `status = planning|executing`, `progress.total_phases = 4`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap get-phase 111` → expected phase name and requirements `ARC-28, GOV-71, TST-38`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 111` → expected 3 plans, wave order `1 -> 2 -> 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 111` → expected `plan_count = 3`
- `$gsd-next` route expectation after phase complete: 推进到 `Phase 112`

## Validation Commands

- `uv run pytest tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/core/test_runtime_access.py tests/platforms/test_entity_base.py tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py -q`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run pytest -q`

## Wave 0 Gaps

- [x] `tests/meta/test_phase111_runtime_boundary_guards.py` — concrete import/cast/private-state no-regrowth proof for `ARC-28` / `GOV-71`
- [x] `tests/core/test_runtime_access.py` — malformed / underspecified `runtime_data` rejection or degraded-read-model case
- [x] `tests/core/test_init_service_handlers_debug_queries.py` — service-level `failed` / `unconfirmed` terminal branches for `query_command_result`
- [x] `tests/meta/test_governance_guards.py` + `scripts/check_architecture_policy.py` inventories — sync new rule ids in the same change

## Archive Truth Guardrail

- `v1.30` remains the latest archived baseline throughout Phase 111.
- `Phase 111` may tighten entity/control/runtime boundaries, but may not reintroduce compat shell, second root, or fake public-surface expansion.
