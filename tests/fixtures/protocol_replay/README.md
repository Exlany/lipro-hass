# Protocol Replay Fixtures

本目录是 `Phase 7.4` 之后继续扩展的 replay manifest family。

## 规则

- 每个 replay scenario 只记录 `authority_path / family / version / seed / clock_baseline / assertion_families` 等编排信息。
- 当 authority payload 已存在于 `tests/fixtures/api_contracts/` 或 `tests/fixtures/protocol_boundary/` 时，manifest 只能引用，不得复制第二份 payload truth。
- replay harness 只允许走正式 `LiproProtocolFacade` / `core/protocol/boundary/*` public path。
- `Phase 10` 新增的 `rest.device-list`、`rest.device-status`、`rest.mesh-group-status` family 只允许通过 protocol contracts public path 回放。
- telemetry assertions 继续 pull `07.3` exporter truth，不允许 replay 自己定义第二套 telemetry 口径。

## 目录

- `rest/`：REST replay scenarios（含 `mqtt-config`、`device-list`、`device-status`、`mesh-group-status`）
- `mqtt/`：MQTT replay scenarios
