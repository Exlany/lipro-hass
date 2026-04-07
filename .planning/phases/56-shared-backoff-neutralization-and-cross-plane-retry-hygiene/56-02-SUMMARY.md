# 56-02 Summary

## Outcome

- `custom_components/lipro/core/command/result_policy.py`、runtime `RetryStrategy` 与 `custom_components/lipro/core/mqtt/setup_backoff.py` 已统一从 `core/utils/backoff.py` import shared primitive。
- 非 API callers 不再通过 `request_policy.py` 获取 generic exponential backoff helper；cross-plane import leak 已在代码层关闭。
- command-result budget、runtime retry attempt semantics 与 MQTT setup jitter/cap 仍留在各自 plane-local homes，没有被误并成 shared retry manager。

## Validation

- `uv run pytest -q tests/core/test_command_result.py tests/core/mqtt/test_mqtt_backoff.py tests/core/api/test_api_request_policy.py`

## Notes

- 本计划只共享 primitive，不统一策略。
