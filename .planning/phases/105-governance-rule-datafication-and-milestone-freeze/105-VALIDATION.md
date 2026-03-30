---
phase: 105
slug: governance-rule-datafication-and-milestone-freeze
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-28
---

# Phase 105 Validation Contract

## Wave Order

1. `105-01` datafy governance follow-up route specs and traceability helpers
2. `105-02` datafy file-matrix registry classifier families and recent governance ownership
3. `105-03` freeze `v1.29` route truth, focused guards, and promoted closeout evidence

## GSD Route Evidence

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → expected `milestone = v1.29`, `current_phase = 105`, `status = active`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → expected `Phase 103` / `104` / `105` complete, `next_phase = null`, `has_work_in_progress = false`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 105` → expected `phase_found = true`, `has_context = true`, `has_research = true`, `plan_count = 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 105` → expected `phase_found = true`, `incomplete_count = 0`, `plan_count = 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 105` → expected `incomplete = []`, 3 plans, wave 1 = `[105-01, 105-02]`, wave 2 = `[105-03]`
- 按 `$HOME/.codex/get-shit-done/workflows/next.md` 的路由规则，`$gsd-next` 现在应推进到 `$gsd-complete-milestone v1.29`
