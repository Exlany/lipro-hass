# Protocol Replay Fixtures

本目录是 `Phase 7.4` 之后继续扩展的 replay manifest family。

## 规则

- 每个 replay scenario 只记录 `authority_path / family / version / seed / clock_baseline / assertion_families` 等编排信息。
- 当 authority payload 已存在于 `tests/fixtures/api_contracts/` 或 `tests/fixtures/protocol_boundary/` 时，manifest 只能引用，不得复制第二份 payload truth。
- replay harness 只允许走正式 `LiproProtocolFacade` / `core/protocol/boundary/*` public path。
- `Phase 10` 新增的 `rest.device-list`、`rest.device-status`、`rest.mesh-group-status` family 只允许通过 protocol contracts public path 回放。
- `Phase 20` remaining family（`rest.list-envelope`、`rest.schedule-json`、`mqtt.topic`、`mqtt.message-envelope`）若落地，也只能复用同一 formal public path 与 authority chain，不得让 helper / transport path 自己长成 replay truth。
- telemetry assertions 继续 pull `07.3` exporter truth，不允许 replay 自己定义第二套 telemetry 口径。

## Boundary Synchronization Rule

- inventory / README / asset guard 可以先同步 boundary fixture 规则，但正式完成态仍应由当前 governance docs / tests 裁决，而不是由本 README 单独宣告。
- `mqtt/` 子目录中的 boundary-family manifests 必须与 `tests/meta/test_protocol_replay_assets.py`、`tests/integration/test_protocol_replay_harness.py` 一起更新；只改 README 或只加 manifest 都不算 fixture truth 收口。

## 目录

- `rest/`：REST replay scenarios（含 `mqtt-config`、`device-list`、`device-status`、`mesh-group-status`）
- `mqtt/`：MQTT replay scenarios（含 `topic`、`message-envelope`、`properties`）
