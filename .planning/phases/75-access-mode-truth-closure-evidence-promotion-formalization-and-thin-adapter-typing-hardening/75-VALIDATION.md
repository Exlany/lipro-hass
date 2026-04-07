---
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-25
---

# Phase 75 Validation Contract

## Wave Order

1. `75-01` private-access docs / issue-template honesty
2. `75-02` metadata + focused honesty guards alignment
3. `75-03` diagnostics / system-health / options-flow thin-adapter typing hardening
4. `75-04` promoted evidence allowlist + current-route closeout-ready truth freeze

## Per-Plan Focused Gates

- `75-01/75-02`
  - `uv run pytest -q tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py tests/meta/test_phase75_access_mode_honesty_guards.py`
  - Result: `44 passed`
- `75-03`
  - `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_diagnostics_config_entry.py tests/core/test_diagnostics_device.py tests/core/test_diagnostics_redaction.py tests/core/test_system_health.py tests/flows/test_options_flow.py tests/flows/test_options_flow_utils.py`
  - Result: `63 passed`
- `75-04`
  - `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_phase75_governance_closeout_guards.py tests/meta/governance_followup_route_current_milestones.py`
  - Result: `19 passed`

## Final Gate

- `uv run ruff check .` → `All checks passed!`
- `uv run mypy --follow-imports=silent .` → `Success: no issues found in 638 source files`
- `uv run python scripts/check_architecture_policy.py --check` → `passed`
- `uv run python scripts/check_file_matrix.py --check` → `passed`
- `uv run pytest -q` → `2608 passed in 61.80s`

## Sign-off Checklist

- [x] private-access docs / issue-template / metadata truth 已收敛到 docs-first canonical route
- [x] diagnostics / system-health / options-flow thin adapters 继续保持 thin + typed honesty
- [x] `72/73/74` closeout bundles 已提升到 explicit promoted allowlist
- [x] `Phase 75` current route truth 已稳定为 `v1.20 active / closeout-ready / Phase 75 complete / latest archived baseline = v1.19`
- [x] focused + repo-wide verification evidence 已完整记录，可直接支撑 milestone closeout
