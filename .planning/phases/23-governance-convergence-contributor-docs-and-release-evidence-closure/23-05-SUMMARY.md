# 23-05 Summary

## Outcome

- 给 runtime formal command path 补上显式 contract：实体命令优先走 `coordinator.command_service.async_send_command(...)`，旧测试 double 才 fallback 到 `coordinator.async_send_command(...)`。
- 收紧 runtime device snapshot authority：去掉在 runtime 内对 vendor raw row 的形态修补，只保留最小 canonical row 补齐与 identity alias 投影。
- 把 device refresh 相关测试 fixture 调整到 canonical shape，减少 mock/compat 对真实 contract 的遮蔽。

## Key Files

- `custom_components/lipro/runtime_types.py`
- `custom_components/lipro/entities/base.py`
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`
- `tests/platforms/test_entity_base.py`
- `tests/core/test_device_refresh.py`
- `tests/core/test_coordinator.py`
- `tests/meta/test_dependency_guards.py`

## Validation

- `uv run pytest tests/platforms/test_entity_base.py tests/test_coordinator_public.py tests/services/test_execution.py -q` → passed
- `uv run pytest tests/core/test_device_refresh.py tests/core/test_coordinator.py -q` → passed
- `uv run pytest tests/meta/test_dependency_guards.py -q` → passed

## Notes

- 本 plan 没有把 entity 直接改去摸更多 coordinator internals，而是先固定 formal seam，避免平台层 mock 大面积连锁漂移。
- runtime compat normalization 继续遵守“边界归一化优于上层修 vendor 原始形态”。
