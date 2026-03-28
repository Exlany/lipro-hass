---
phase: 103
slug: root-adapter-thinning-test-topology-second-pass-and-terminology-contract-normalization
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-28
---

# Phase 103 Validation Contract

## Wave Order

1. `103-01` thin the HA root adapter by extracting lazy-loading and entry-auth support
2. `103-02` split topicized collection hooks and coordinator double out of `tests.conftest`
3. `103-03` codify terminology contract and activate the `v1.29` route truth

## GSD Route Evidence

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → expected `milestone = v1.29`, `current_phase = 103`, `status = active`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → expected `Phase 103 complete` and pending `Phase 104` / `Phase 105`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 103` → expected `phase_found = true`, `has_context = true`, `has_research = true`, `plan_count = 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 103` → expected `phase_found = true`, `incomplete_count = 0`, `plan_count = 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 103` → expected `incomplete = []`, 3 plans, wave 1 = `[103-01, 103-02]`, wave 2 = `[103-03]`
- 按 `$HOME/.codex/get-shit-done/workflows/next.md` 的路由规则，`$gsd-next` 现在应推进到 `$gsd-discuss-phase 104`
