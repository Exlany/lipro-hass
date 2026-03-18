# 27-02 Summary

## Outcome

- `custom_components/lipro/core/coordinator/coordinator.py` 已删除一簇纯协议转发方法，schedule / diagnostics / OTA / outlet-power 等调用不再借壳 `Coordinator.async_*` 形成伪 public surface。
- `_async_run_outlet_power_polling()` 已直接依赖 `self.protocol_service.async_fetch_outlet_power_info`；历史 `Phase C` / `Phase H4` 等阶段叙事也已从 runtime hotspot 文档字符串中清退。
- `runtime_context.py` 与 `orchestrator.py` 的 phase narration 残留同步清理，避免正式代码继续暴露迁移叙事噪声。

## Key Files

- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/core/coordinator/runtime_context.py`
- `custom_components/lipro/core/coordinator/orchestrator.py`
- `tests/core/test_coordinator.py`
- `tests/test_coordinator_public.py`

## Validation

- `uv run pytest -q tests/core/test_init.py tests/core/test_init_service_handlers.py tests/services/test_services_diagnostics.py tests/services/test_service_resilience.py tests/test_coordinator_public.py tests/core/test_coordinator.py` → `245 passed`

## Notes

- 这一步是“退场 pure forwarders”，不是把能力拆成第二 runtime root；`Coordinator` 仍是唯一正式 runtime orchestration root。
