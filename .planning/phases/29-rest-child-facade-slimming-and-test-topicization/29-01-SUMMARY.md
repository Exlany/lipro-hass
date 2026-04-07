# 29-01 Summary

## Outcome

- `custom_components/lipro/core/api/client.py` 继续保留单一 `LiproRestFacade` 正式 child façade，但把 request/auth/result bridge 明确压缩到 `transport_executor.py`、`auth_recovery.py` 与 endpoint adapter；façade 不再持有大片 helper shadow。
- `custom_components/lipro/core/api/endpoints/payloads.py` 仍保留 public wrapper 的默认参数 fast-path，兼容旧测试 patch 点，同时不把职责重新抬回 façade 顶层。
- `tests/core/api/test_api_transport_executor.py`、`tests/core/api/test_auth_recovery_telemetry.py` 与新增的 `tests/core/api/test_api_request_policy.py` 已把 transport、401 refresh、request-policy 行为锁定到 focused homes。

## Key Files

- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/api/transport_executor.py`
- `custom_components/lipro/core/api/auth_recovery.py`
- `custom_components/lipro/core/api/endpoints/payloads.py`
- `tests/core/api/test_api.py`
- `tests/core/api/test_api_transport_executor.py`
- `tests/core/api/test_auth_recovery_telemetry.py`
- `tests/core/api/test_api_request_policy.py`

## Validation

- `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_api_request_policy.py tests/core/api/test_api_command_service.py tests/core/api/test_helper_modules.py tests/core/api/test_api_transport_executor.py`

## Notes

- 本 plan 修的是 façade 过胖与职责漂移，不是把 helper 重新塞回 `client.py`；`close()`、fast-path 与 focused collaborator ownership 现在讲的是同一条正式 REST 主链故事。
