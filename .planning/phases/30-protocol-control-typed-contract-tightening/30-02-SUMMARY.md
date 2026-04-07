# 30-02 Summary

## Outcome

- `custom_components/lipro/core/protocol/contracts.py` 继续作为统一 protocol root 下的 canonical contract home，`CanonicalPropertyMap`、`CanonicalMqttTopic`、`CanonicalDeviceListPage` 等 typed truth 已向 boundary/consumer 同步收口。
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py` 与 `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py` 现通过 `TYPE_CHECKING` + 前向引用字符串 cast 保持 canonical decode 合同，同时切断 boundary ↔ contracts 循环导入。
- `custom_components/lipro/core/protocol/facade.py` 继续保留单一正式 protocol root，但 transport/session failure 语义已回到 typed arbitration；`tests/core/api/test_protocol_replay_rest.py`、`tests/core/mqtt/test_protocol_replay_mqtt.py` 与 `tests/integration/test_protocol_replay_harness.py` 也已锁定 canonical shape。

## Key Files

- `custom_components/lipro/core/protocol/contracts.py`
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`
- `custom_components/lipro/core/protocol/facade.py`
- `tests/core/api/test_protocol_replay_rest.py`
- `tests/core/mqtt/test_protocol_replay_mqtt.py`
- `tests/integration/test_protocol_replay_harness.py`
- `tests/core/coordinator/test_entity_protocol.py`

## Validation

- `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/core/coordinator/test_entity_protocol.py`

## Notes

- 本 plan 没有创建新的 protocol root 或平行 decoder pipeline；它只把 canonical contract truth 收回到正式 protocol 主链。