---
phase: 80
slug: governance-typing-closure-and-final-meta-suite-hotspot-topicization
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-26
---

# Phase 80 Validation Contract

## Wave Order

1. `80-01` governance/tooling typing closure
2. `80-02` final giant meta-suite hotspot topicization
3. `80-03` live truth, promoted allowlist, and closeout proof freeze

## Per-Plan Focused Gates

- `80-01`
  - `uv run mypy --follow-imports=silent .` → `Success: no issues found in 646 source files`
  - `uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py` → `4 passed in 0.72s`
- `80-02`
  - `uv run ruff check tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_closeout_guards.py --select PLR0915` → `All checks passed!`
  - `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_version_sync.py` → `42 passed in 0.76s`
- `80-03`
  - `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` / `state json` / `phase-plan-index 80` 已共同证明 live truth、promoted allowlist 与 GSD fast-path 全部回到 milestone closeout。

## Final Gate

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → `Phase 80 = complete`, `next_phase = null`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → `v1.21 active`, `5/5 phases`, `15/15 plans`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 80` → `incomplete = []`
- `uv run python scripts/check_architecture_policy.py --check` → `passed`
- `uv run python scripts/check_file_matrix.py --check` → `passed`
- `uv run ruff check tests/meta scripts` → `All checks passed!`

## Sign-off Checklist

- [x] live governance route truth 已前推到 `v1.21 active route / Phase 80 complete / latest archived baseline = v1.20`
- [x] registry export seam 与 fast-path JSON helper 已回到诚实类型边界
- [x] remaining giant governance tests 已 topicize 为更小的 concern slices
- [x] promoted allowlist 只提升 closeout bundles，未提升 `PLAN / CONTEXT / RESEARCH` traces
- [x] residual / kill ledgers 已明确 `Phase 80` 无新增 active residual family / active kill target
- [x] 下一步已稳定收束为 `$gsd-complete-milestone v1.21`
