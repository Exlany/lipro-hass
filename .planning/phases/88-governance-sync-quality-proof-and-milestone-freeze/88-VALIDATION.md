# Phase 88 Validation Contract

## Wave Order

1. `88-01` evidence allowlist / historical audit identity / zero-active ledger posture freeze
2. `88-02` focused phase-88 guard / verification matrix / file-governance / testing truth registration
3. `88-03` live-route advance / closeout proof bundle / GSD next-step handoff

## Per-Plan Focused Gates

- `88-01`
  - `uv run pytest -q tests/meta/test_phase85_terminal_audit_route_guards.py tests/meta/test_governance_promoted_phase_assets.py`
  - `uv run pytest -q tests/meta/test_governance_closeout_guards.py`
- `88-02`
  - `uv run pytest -q tests/meta/test_phase85_terminal_audit_route_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_phase88_governance_quality_freeze_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_promoted_phase_assets.py`
  - `uv run ruff check tests/meta/test_phase85_terminal_audit_route_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_phase88_governance_quality_freeze_guards.py scripts/check_file_matrix_registry_overrides.py`
  - `uv run python scripts/check_file_matrix.py --check`
- `88-03`
  - `uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_closeout_guards.py tests/meta/test_phase88_governance_quality_freeze_guards.py tests/meta/test_version_sync.py`
  - `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
  - `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
  - `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 88`

## Final Gate

- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run pytest -q tests/meta`
- `uv run pytest -q tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_diagnostics_service_*.py tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_contract_*.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/runtime/test_mqtt_runtime_*.py`
- `uv run pytest -q tests/ --ignore=tests/benchmarks`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 88`

## Sign-off Checklist

- [x] current-route truth 与 GSD fast path 已共同承认 `Phase 88 complete`
- [x] promoted evidence allowlist / historical audit role / zero-active ledgers 已被 focused guards 冻结
- [x] `GOV-63` / `QLT-35` 在 requirements、verification matrix 与 phase evidence 中均为 completed
- [x] `$gsd-next` 的唯一下一跳已收口到 `$gsd-complete-milestone v1.23`
