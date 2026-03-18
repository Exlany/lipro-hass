# 30-01 Summary

## Outcome

- `custom_components/lipro/core/api/client.py` 继续保留单一 `LiproRestFacade` 正式 child façade，但 auth-recovery telemetry、result unwrapping 与 request/response codec 已压缩回 focused collaborator homes。
- `custom_components/lipro/core/api/endpoints/misc.py`、`custom_components/lipro/core/command/dispatch.py` 与 `custom_components/lipro/services/schedule.py` 现对齐更窄的 `JsonObject` / `Mapping[str, object]` / `ScheduleRows` 合同，REST response/result spine 不再向 protocol/control 扩散宽口 `Any`。
- `tests/core/api/test_auth_recovery_telemetry.py`、`tests/core/api/test_protocol_contract_matrix.py`、`tests/core/api/test_api_status_service.py`、`tests/core/api/test_api_schedule_service.py` 与 `tests/core/api/test_api_diagnostics_service.py` 已锁定 touched REST auth/busy/rate/result 语义。

## Key Files

- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/api/endpoints/misc.py`
- `custom_components/lipro/core/command/dispatch.py`
- `custom_components/lipro/services/schedule.py`
- `tests/core/api/test_auth_recovery_telemetry.py`
- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/core/api/test_api_status_service.py`
- `tests/core/api/test_api_schedule_service.py`
- `tests/core/api/test_api_diagnostics_service.py`

## Validation

- `uv run pytest -q tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_status_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_diagnostics_service.py`

## Notes

- 本 plan 修的是 REST response/result spine 的 typed ownership，不是把 `client.py` 再次扩写成所有 typed logic 的根。