# Summary 112-02

## What changed
- 在 `RuntimeCoordinatorView` 上增加了向后兼容的 `runtime_coordinator` 只读 alias，用来显式表达该 view 携带的是 runtime root。
- 把 `runtime_access_support_views.py`、`runtime_access_support_devices.py`、`developer_router_support.py` 中的 `.coordinator.coordinator` 调用点统一改为 `.coordinator.runtime_coordinator`。
- 更新 `tests/core/test_runtime_access.py` 与 `tests/core/test_control_plane.py` 的 focused assertions，使 changed-surface tests 冻结新的命名 contract。

## Why it changed
- `Phase 112` 的成功标准要求消除 `coordinator.coordinator` 这类误导性 discoverability 叙事。
- 该修复必须保持低风险：不移动文件、不重命名 `RuntimeEntryView.coordinator`、不引入结构 churn。

## Verification
- `uv run pytest -q tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_contract.py tests/core/test_runtime_access.py tests/core/test_control_plane.py tests/core/test_init_service_handlers_debug_queries.py`
- `65 passed in 1.38s`
- `uv run ruff check custom_components/lipro/control/runtime_access_types.py custom_components/lipro/control/runtime_access_support_views.py custom_components/lipro/control/runtime_access_support_devices.py custom_components/lipro/control/developer_router_support.py tests/core/test_runtime_access.py tests/core/test_control_plane.py tests/core/test_init_service_handlers_debug_queries.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_contract.py`
- `All checks passed!`

## Outcome
- targeted control/runtime access helper files 不再传播 `.coordinator.coordinator` 残留。
- runtime-access changed-surface tests 证明 alias 缝合没有改变 runtime lookup / projection 行为。
