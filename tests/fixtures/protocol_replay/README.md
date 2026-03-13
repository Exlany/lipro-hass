# Protocol Replay Fixtures

本目录是 `Phase 7.4` 的 replay manifest family。

## 规则

- 每个 replay scenario 只记录 `authority_path / family / version / seed / clock_baseline / assertion_families` 等编排信息。
- 当 authority payload 已存在于 `tests/fixtures/api_contracts/` 或 `tests/fixtures/protocol_boundary/` 时，manifest 只能引用，不得复制第二份 payload truth。
- replay harness 只允许走正式 `LiproProtocolFacade` / `core/protocol/boundary/*` public path。
- `07.4` 只拥有 replay truth；telemetry assertions 必须 pull `07.3` exporter truth。

## 目录

- `rest/`：REST replay scenarios
- `mqtt/`：MQTT replay scenarios
