# 31-01 Summary

## Outcome

- `custom_components/lipro/core/coordinator/coordinator.py`、`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` 与 `custom_components/lipro/core/coordinator/mqtt_lifecycle.py` 已把 runtime lifecycle / transport broad-catch 改成明确的 fail-closed、degraded 或 best-effort teardown 语义。
- `tests/core/test_coordinator.py`、`tests/core/coordinator/runtime/test_mqtt_runtime.py` 与 `tests/core/test_coordinator_integration.py` 现锁定的是负路径 failure semantics，而非“没有崩溃就算通过”。
- 本 wave 没有回退进 protocol/control typed work；runtime root 仍是唯一正式 orchestrator root。

## Key Files

- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`
- `custom_components/lipro/core/coordinator/mqtt_lifecycle.py`
- `tests/core/test_coordinator.py`
- `tests/core/coordinator/runtime/test_mqtt_runtime.py`
- `tests/core/test_coordinator_integration.py`

## Validation

- `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/test_coordinator_integration.py`

## Notes

- 这里修的是 runtime lifecycle 语义，不是新建 transport cleanup 控制面。