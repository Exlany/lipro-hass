---
phase: 79
slug: governance-tooling-hotspot-decomposition-and-release-contract-topicization
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-26
---

# Phase 79 Validation Contract

## Wave Order

1. `79-01` live route truth + phase-79 exit contract freeze
2. `79-02` registry hotspot decomposition + focused refactor proof
3. `79-03` release-contract topicization + closeout bundle freeze

## Per-Plan Focused Gates

- `79-01`
  - `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_version_sync.py` → covered inside final `81 passed`
- `79-02`
  - `uv run ruff check scripts/check_file_matrix_registry.py --select C901` → `All checks passed!`
  - `uv run pytest -q tests/test_refactor_tools.py` → `12 passed in 0.30s`
  - `uv run python scripts/check_file_matrix.py --check` → `passed`
- `79-03`
  - `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py` → covered inside final `81 passed`

## Final Gate

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → `Phase 79 complete`, `next_phase = null`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → `v1.21 active`, `4/4 phases`, `12/12 plans`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 79` → `incomplete = []`
- `uv run python scripts/check_architecture_policy.py --check` → `passed`
- `uv run python scripts/check_file_matrix.py --check` → `passed`
- `uv run ruff check tests/meta scripts` → `All checks passed!`

## Sign-off Checklist

- [x] live governance route truth 已前推到 `v1.21 active route / Phase 79 complete / latest archived baseline = v1.20`
- [x] registry hotspot 已拆薄，`C901` 命中消失，且 file-matrix contract 保持稳定
- [x] release-contract coverage 已 topicize 成 anchor / docs / continuity 三件套
- [x] promoted allowlist 只提升 closeout bundles，未提升 `PLAN / CONTEXT / RESEARCH` traces
- [x] residual / kill ledgers 已明确 `Phase 79` 无新增 active residual family / active kill target
- [x] 下一步已稳定收束为 `$gsd-complete-milestone v1.21`
