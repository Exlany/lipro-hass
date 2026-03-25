# Phase 72 Validation Contract

## Wave Order

1. `72-01` Coordinator bootstrap / runtime-root 装配收口
2. `72-02` runtime_access probing folklore 退役 + runtime_infra listener hotspot 切薄
3. `72-03` lifecycle/root wiring 去 kwargs bag + typed collaborator 收口
4. `72-04` current-route 回写 + focused no-growth guards + developer_architecture 文档修正

## Per-Plan Focused Gates

- `72-01`
  - `uv run pytest -q tests/core/coordinator/test_runtime_root.py tests/integration/test_mqtt_coordinator_integration.py`
- `72-02`
  - `uv run pytest -q tests/core/test_runtime_access.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_runtime_infra.py tests/services/test_maintenance.py`
- `72-03`
  - `uv run pytest -q tests/core/test_entry_root_wiring.py tests/core/test_entry_lifecycle_controller.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_unload_reload.py`
- `72-04`
  - `uv run pytest -q tests/meta/test_phase72_runtime_bootstrap_route_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_milestone_archives.py tests/meta/test_version_sync.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_toolchain_truth.py`

## Final Gate

- `uv run ruff check .`
- `uv run mypy --follow-imports=silent .`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q`

## Sign-off Checklist

- [ ] `Coordinator` / runtime-root 装配被 inward split，未重开第二 runtime root
- [ ] `runtime_access` public seam 不再把 probe-style folklore 讲成正式合同
- [ ] `entry_root_wiring` / `EntryLifecycleController` / `__init__.py` 不再依赖巨大 kwargs bag
- [ ] `VERIFICATION_MATRIX` / `RESIDUAL_LEDGER` / docs / meta guards 对 `v1.20 / Phase 72` current-route truth 一致
- [ ] `docs/developer_architecture.md` 只引用真实存在的测试路径，且有自动守卫
