---
phase: 112
slug: formal-home-discoverability-and-governance-anchor-normalization
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-31
---

# Phase 112 Validation Contract

## Wave Order

1. `112-01` normalize maintainer docs route truth and sanctioned-home discoverability
2. `112-02` de-ambiguate runtime-access coordinator naming without structural churn
3. `112-03` freeze governance truth and sanctioned-home inventory for phase 112

## Completion Expectations

- `112-01` 至 `112-03` 全部生成对应 `*-SUMMARY.md`，并在 `phase-plan-index 112` 中全部表现为 `has_summary = true`。
- `112-VERIFICATION.md` 对 `ARC-29` / `GOV-72` 给出 passed verdict 与 focused proof。
- maintainer docs、developer docs、planning selector family 与 focused meta guards 必须共同承认 sanctioned-home discoverability truth，而不是继续依赖命名折返或 stale governance anchors。
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 需显式提升：
  - `112-01-SUMMARY.md`
  - `112-02-SUMMARY.md`
  - `112-03-SUMMARY.md`
  - `112-SUMMARY.md`
  - `112-VERIFICATION.md`
  - `112-VALIDATION.md`

## GSD Route Evidence

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → expected `milestone = v1.31`, `status` points at active milestone route during Phase 112 execution
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap get-phase 112` → expected requirements `ARC-29, GOV-72`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 112` → expected 3 plans, wave order `1 -> 1 -> 2`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 112` → expected `plan_count = 3`
- historical next-step expectation after phase complete: 推进到 `Phase 113`

## Validation Commands

- `uv run pytest -q tests/meta/test_phase112_formal_home_governance_guards.py tests/meta/test_governance_route_handoff_smoke.py`
- `uv run pytest -q tests/core/test_runtime_access.py tests/core/test_control_plane.py tests/core/test_init_service_handlers_debug_queries.py`
- `uv run python scripts/check_file_matrix.py --check`

## Archive Truth Guardrail

- `v1.30` remained the latest archived baseline throughout Phase 112 execution.
- discoverability/governance cleanup did not legitimize a second root, compat shell, or archive-pointer drift.
