# 22-01 Summary

## Outcome

- 让 diagnostics / system health 两类 control-plane consumer 统一暴露共享 `failure_summary`，不再各自解释 transport / runtime 错误语义。
- 扩展 runtime snapshot contract，使 `RuntimeCoordinatorSnapshot` 稳定携带 `entry_ref` 与 `failure_summary`，为上层 surface 提供单一读口。
- 在 system health 聚合结果中显式加入 `failure_entries`，让 coarse-grained 健康视图也能消费与 diagnostics 同源的失败摘要。

## Key Files

- `custom_components/lipro/core/telemetry/sinks.py`
- `custom_components/lipro/control/models.py`
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/diagnostics_surface.py`
- `custom_components/lipro/control/system_health_surface.py`
- `tests/core/telemetry/test_sinks.py`
- `tests/core/test_control_plane.py`
- `tests/core/test_diagnostics.py`
- `tests/core/test_system_health.py`
- `tests/integration/test_telemetry_exporter_integration.py`

## Validation

- `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_control_plane.py tests/core/telemetry/test_sinks.py tests/integration/test_telemetry_exporter_integration.py` → `49 passed`
- `uv run ruff check .` → passed

## Notes

- 本 plan 只负责把 `Phase 21` 已冻结的 failure taxonomy 暴露给 control-plane consumers，没有新增第二套 taxonomy home。
- unloaded / degraded / missing-runtime 场景继续保持稳定 output shape，避免 consumer 再次回退到 adapter-local 分支判断。
