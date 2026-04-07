# Phase 92 Discussion Log

**Date:** 2026-03-28
**Mode:** Auto-planned from Phase 91 closeout + repository audit

## Decisions captured for planning

- Phase 92 承接 `Phase 91` 已冻结的 protocol/runtime typed-boundary truth，不再重开 formal-home ownership 讨论。
- 目标是把 `control/redaction.py`、`core/anonymous_share/sanitize.py`、`core/telemetry/json_payloads.py` 与 diagnostics/developer/exporter consumers 收敛到单一 redaction policy story。
- 未知 secret-like key 默认 fail-closed；diagnostics 可以继续使用 `**REDACTED**`，anonymous share 可以继续保留 `[TOKEN]/[IP]/[MAC]/[DEVICE_ID]` 这类 sink-specific marker，但 key registry、pattern registry 与 detection 逻辑必须共源。
- 本 phase 同时继续把四个指定 mega suites topicize 成 thin shell + sibling suites：
  - `tests/core/api/test_api_status_service.py`
  - `tests/core/api/test_api_command_surface_responses.py`
  - `tests/platforms/test_light_entity_behavior.py`
  - `tests/services/test_services_diagnostics.py`
- `Phase 92` 完成后，current-route 应切到 `Phase 92 complete / next = 93`。
