# Phase 50 Verification

status: passed

## Goal

- 验证 `Phase 50: REST typed-surface reduction and command/result ownership convergence` 是否完成 `TYP-12` / `ARC-07`：REST child façade family 的 typed/helper honesty 已继续收紧，command-result policy 与 diagnostics auth-error duplication 已回收到单一 formal home，且 public surface / dependency truth / residual truth 没有漂移。

## Evidence

- `custom_components/lipro/core/api/endpoint_surface.py` 现在使用局部 typed collaborator protocols；`query_device_status`、`get_mqtt_config`、`query_command_result`、`get_city`、`query_user_cloud` 等 wrapper 返回值已回接到现有 typed truth，`on_batch_metric` 也不再用匿名 `Any`。
- `custom_components/lipro/core/api/request_gateway.py`、`rest_facade.py` 与 `rest_facade_request_methods.py` 现在通过 `ResponseHeaders`、`SanctionedBoundaryPayload`、`SanctionedRawMappingResult`、`ValidatedMappingResult` 等 formal aliases 收紧 raw mapping / helper honesty；`LiproRestFacade` 仍保持唯一 canonical REST child façade。
- `custom_components/lipro/core/command/result.py` 不再重复定义 `build_progressive_retry_delays()`、`run_delayed_refresh()`、`poll_command_result_state()`；这些算法继续由 `result_policy.py` 担任实现真源，`result.py` 则保留 stable export / failure arbitration home。
- `custom_components/lipro/services/execution.py` 新增 shared auth-error capture helper；`custom_components/lipro/services/diagnostics/helpers.py` 的 authenticated capability loop 改为复用 shared execution chain，而非直接操作 `coordinator.auth_service`。既有 diagnostics degrade-and-continue 行为仍由 focused tests 证明。
- `tests/meta/test_phase50_rest_typed_budget_guards.py` 新增后，Phase 50 touched zone 对 `Any` / broad-catch / `type: ignore` 预算均有 machine-checkable 约束；同时 `tests/meta/test_dependency_guards.py` 与 `tests/meta/test_public_surface_guards.py` 继续锁住 single REST child façade truth、shared execution truth 与 no second-root story。
- `.planning/reviews/FILE_MATRIX.md` 与 `.planning/baseline/VERIFICATION_MATRIX.md` 已同步 Phase 50 的 guard / verification route；`.planning/baseline/PUBLIC_SURFACES.md`、`.planning/baseline/DEPENDENCY_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md` 与 `.planning/reviews/KILL_LIST.md` 明确保留 unchanged，因为 formal-home truth 未被改写。

## Validation

- `uv run pytest tests/core/api/test_api_command_surface.py tests/core/api/test_api_status_service.py -q` → `77 passed`
- `uv run pytest tests/core/test_command_result.py -q` → `27 passed`
- `uv run pytest tests/services/test_execution.py tests/services/test_services_diagnostics.py tests/core/api/test_api_diagnostics_service.py -q` → `49 passed`
- `uv run pytest tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py -q` → `52 passed`
- `uv run pytest tests/core/api/test_api_command_surface.py tests/core/api/test_api_status_service.py tests/core/test_command_result.py tests/services/test_execution.py tests/services/test_services_diagnostics.py tests/core/api/test_api_diagnostics_service.py tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py -q` → `205 passed`
- `uv run ruff check custom_components/lipro/core/api/endpoint_surface.py custom_components/lipro/core/api/request_gateway.py custom_components/lipro/core/api/rest_facade.py custom_components/lipro/core/api/rest_facade_endpoint_methods.py custom_components/lipro/core/api/rest_facade_request_methods.py custom_components/lipro/core/api/types.py custom_components/lipro/core/command/result.py custom_components/lipro/services/execution.py custom_components/lipro/services/diagnostics/helpers.py tests/core/api/test_api_command_surface.py tests/core/api/test_api_status_service.py tests/core/test_command_result.py tests/services/test_execution.py tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py` → `passed`
- `uv run python scripts/check_file_matrix.py --check` → `passed`

## Notes

- `Phase 50` 没有新增 public root、compat shell、package-level shortcut import 或 helper-owned truth story；`request_gateway.py` / `endpoint_surface.py` 继续是 localized collaborator，`services/execution.py` 继续是 formal service execution facade。
- `50-SUMMARY.md` / `50-VERIFICATION.md` 已提升进 `PROMOTED_PHASE_ASSETS.md`；`50-CONTEXT.md`、`50-RESEARCH.md`、`50-VALIDATION.md` 与 `50-0x-PLAN.md` 仍是 execution-trace 资产。
- `Phase 46 -> 50` 的 formalized v1.7 follow-up route 至此全部 complete；下一步不再是继续执行本 route，而是基于 `gsd-progress` / `gsd-new-milestone` 选择后续审阅或新一轮路线。
