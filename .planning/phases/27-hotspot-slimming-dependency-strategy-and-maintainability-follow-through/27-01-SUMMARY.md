# 27-01 Summary

## Outcome

- `custom_components/lipro/runtime_types.py` 现在显式定义 `ProtocolServiceLike`，`LiproCoordinator` 正式暴露 `protocol_service` 能力口，而不是让下游继续猜测 `Coordinator` 上有哪些临时属性。
- schedule、diagnostics 与 firmware-update consumer 已统一改走 `coordinator.protocol_service.async_*`，formal capability surface 与 runtime-owned contract 达成单源收口。
- `tests/conftest.py`、`tests/core/test_init.py`、`tests/services/test_services_diagnostics.py`、`tests/services/test_service_resilience.py` 与 firmware-update 相关平台测试已同步到新 contract。

## Key Files

- `custom_components/lipro/runtime_types.py`
- `custom_components/lipro/services/schedule.py`
- `custom_components/lipro/services/diagnostics/handlers.py`
- `custom_components/lipro/entities/firmware_update.py`
- `tests/conftest.py`
- `tests/services/test_services_diagnostics.py`
- `tests/services/test_service_resilience.py`

## Validation

- `uv run pytest -q tests/services/test_services_diagnostics.py tests/services/test_service_resilience.py tests/platforms/test_update.py tests/platforms/test_firmware_update_entity_edges.py tests/platforms/test_update_task_callback.py` → `106 passed`

## Notes

- `protocol_service` 被明确定位为 runtime-owned formal capability port；这次收口没有创建第二 root，也没有把 capability 面重新塞回 `Coordinator` 的 ad-hoc forwarder。
