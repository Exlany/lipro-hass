---
phase: 78
slug: quality-gate-formalization-route-handoff-ergonomics-and-milestone-closeout-readiness
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-26
---

# Phase 78 Validation Contract

## Wave Order

1. `78-01` live route truth + fast-path handoff activation
2. `78-02` verification matrix / file matrix / registry gate formalization
3. `78-03` promoted evidence + review ledgers + closeout bundle freeze

## Per-Plan Focused Gates

- `78-01/78-02`
  - `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py`
  - Result: `45 passed`
- `78-03`
  - `uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase75_governance_closeout_guards.py tests/meta/test_governance_promoted_phase_assets.py`
  - Result: `41 passed`

## Final Gate

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → `phase 78 complete`, `summary_count = 4`, `next_phase = null`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → `v1.21 active`, `3/3 phases`, `9/9 plans`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 78` → `incomplete = []`
- `uv run python scripts/check_architecture_policy.py --check` → `passed`
- `uv run python scripts/check_file_matrix.py --check` → `passed`
- `uv run ruff check tests/meta` → `All checks passed!`

## Sign-off Checklist

- [x] live governance route truth 已前推到 `v1.21 active route / Phase 78 complete / latest archived baseline = v1.20`
- [x] fast-path smoke / verification matrix / file matrix / registry 已冻结为同一 closeout-ready handoff contract
- [x] promoted allowlist 只提升 closeout bundles，未提升 `PLAN / CONTEXT / RESEARCH` traces
- [x] residual / kill ledgers 已明确 `Phase 76 / 77 / 78` 无新增 active residual family / active kill target
- [x] 下一步已稳定收束为 `$gsd-complete-milestone v1.21`
