# 68-03 Summary

## Outcome

Phase `68-03` 让 `runtime_infra.py` 与 `runtime_access.py` 继续变薄，同时保住 listener / pending reload / control runtime-read 的唯一正式归属。

## What Changed

- `custom_components/lipro/runtime_infra.py` 抽出 device-registry update 解析、disabled toggle 判定、reload 调度/取消与锁内 setup helper。
- `custom_components/lipro/control/runtime_access_support.py` 下沉 explicit bool/mapping narrowing 与 entry/coordinator projection helper。
- `custom_components/lipro/control/runtime_access.py` 显式经 `_support` 聚合导出，继续作为唯一 control-plane runtime read home。
- `custom_components/lipro/services/maintenance.py` 保持薄投影，只消费注入的 runtime-access provider。
- 补齐 `tests/services/test_maintenance.py`、`tests/core/test_init_runtime_setup_entry.py` 与 `tests/meta/test_dependency_guards.py`。

## Verification

- `uv run pytest -q tests/services/test_maintenance.py tests/core/test_init.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_unload_reload.py tests/meta/test_dependency_guards.py tests/core/test_diagnostics.py tests/core/test_system_health.py`
- `uv run ruff check custom_components/lipro/runtime_infra.py custom_components/lipro/control/runtime_access_support.py custom_components/lipro/control/runtime_access.py custom_components/lipro/services/maintenance.py tests/services/test_maintenance.py tests/core/test_init_runtime_setup_entry.py tests/meta/test_dependency_guards.py`
