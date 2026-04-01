# Plan 121-01 Summary

## What changed

- `custom_components/lipro/control/runtime_access_types.py` 把 `RuntimeCoordinatorView` 收紧为 fact-only read-model，不再通过 view re-export raw `LiproCoordinator`。
- `custom_components/lipro/control/runtime_access_support_views.py`、`custom_components/lipro/control/runtime_access_support_devices.py` 与 `custom_components/lipro/control/developer_router_support.py` 全部改为通过 dedicated runtime-access helpers 解析 raw coordinator，而不是 reach-through `.coordinator.runtime_coordinator`。
- `custom_components/lipro/control/runtime_access.py` 快照与 diagnostics 投影直接消费 narrowed facts；`custom_components/lipro/control/runtime_access_support_telemetry.py` 也继续沿显式 snapshot coercion 收紧 support seam。
- `custom_components/lipro/control/__init__.py` 去掉与当前 formal-home truth 不再需要的 runtime/telemetry aggregate export，缩小 control aggregate surface。
- focused guards 已同步到 `tests/core/test_runtime_access.py`、`tests/meta/test_phase112_formal_home_governance_guards.py`、`tests/meta/test_runtime_contract_truth.py` 与 `tests/meta/dependency_guards_service_runtime.py`。

## Outcome

- `ARC-33`：control runtime read-model 不再把 raw coordinator 当作 view payload 暴露。
- `TST-43`：runtime-access seam closure 已有 focused tests/meta guards 冻结。

