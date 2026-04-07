# 32-05 Summary

## Outcome

- `helpers/platform.py` 已直接依附正式 `LiproCoordinator` contract；`binary_sensor.py`、`climate.py`、`select.py`、`sensor.py` 与相关实体/runtime typing 现已闭环，不再让 platform helper 与 runtime public surface 各讲一套 coordinator 故事。
- API `JsonObject` callback、protocol replay harness、MQTT/runtime tests 与 Phase 31 typed-budget guard 已完成真修，`uv run mypy` 现对全仓 `448` 个 source files 真绿。
- touched tests 没有靠 `cast` 泛滥来掩盖问题，而是把 helper 返回类型、replay canonical override、runtime property payload 与 failure-summary 语义拉回正式契约。

## Key Files

- `custom_components/lipro/helpers/platform.py`
- `custom_components/lipro/{binary_sensor.py,climate.py,select.py,sensor.py}`
- `custom_components/lipro/runtime_types.py`
- `custom_components/lipro/entities/{base.py,firmware_update.py}`
- `tests/core/api/{test_helper_modules.py,test_api_diagnostics_service.py,test_protocol_contract_matrix.py}`
- `tests/core/coordinator/runtime/{test_mqtt_runtime.py,test_device_runtime.py}`
- `tests/harness/protocol/replay_driver.py`
- `tests/integration/test_protocol_replay_harness.py`
- `tests/meta/test_phase31_runtime_budget_guards.py`
- `tests/platforms/test_select.py`
- `tests/snapshots/test_api_snapshots.py`

## Validation

- `uv run mypy`
- `uv run pytest -q tests/core/api/test_helper_modules.py tests/core/api/test_api_diagnostics_service.py tests/core/api/test_protocol_contract_matrix.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/runtime/test_device_runtime.py tests/integration/test_protocol_replay_harness.py tests/platforms/test_select.py tests/platforms/test_sensor.py tests/platforms/test_climate.py tests/platforms/test_update.py tests/meta/test_phase31_runtime_budget_guards.py`

## Notes

- 本 wave 优先做“契约真修 + repo-wide green”，没有为了追求表面体积变化而发明第二 root 或伪包装层。
