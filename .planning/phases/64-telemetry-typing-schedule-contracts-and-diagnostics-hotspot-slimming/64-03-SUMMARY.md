# Phase 64-03 Summary

## What

- 将 `custom_components/lipro/core/api/diagnostics_api_service.py` 退成 thin outward home，并把 OTA / sensor-history / misc query concern inward split 到 `diagnostics_api_ota.py`、`diagnostics_api_history.py`、`diagnostics_api_queries.py`。
- 保持 `query_ota_info*`、`fetch_sensor_history*`、`query_command_result`、`get_city`、`query_user_cloud` 的 outward import home 与行为契约不变；现有测试继续从 `diagnostics_api_service.py` 读取这些符号。
- 同轮更新 `.planning/reviews/FILE_MATRIX.md`，冻结 diagnostics split、telemetry typed contracts 与 schedule formal contracts 的新 topology truth。

## Why

- `diagnostics_api_service.py` 之前同时承担 OTA fallback、history wrapper 与 misc query home，认知半径过大。
- inward split 只改变本地协作拓扑，不改变 public root；这符合北极星对 protocol-plane outward home 与 helper-local decomposition 的要求。
- `FILE_MATRIX` 需要同步记录新的 collaborator homes，避免 stale hotspot/ownership wording 回流。

## Verification

- `uv run pytest tests/core/api/test_api_diagnostics_service.py tests/services/test_services_diagnostics.py tests/core/api/test_protocol_contract_matrix.py tests/snapshots/test_api_snapshots.py -q`
- 结果：`79 passed`（含 `2 snapshots passed`）
