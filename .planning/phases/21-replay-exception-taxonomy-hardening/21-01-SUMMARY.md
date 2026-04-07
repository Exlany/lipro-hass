# 21-01 Summary

## Outcome

- 把 `rest.list-envelope`、`rest.schedule-json`、`mqtt.topic`、`mqtt.message-envelope` 四个 remaining families 从“隐式遍历覆盖”提升为 replay summary / evidence pack 中的显式 assurance truth。
- `replay.report.v1` 的 scenario 与 representative story 现在同时携带 normalized `failure_summary`、`error_category` 与 raw `error_type`，不再让原始异常名冒充最终分类语言。
- AI evidence pack 继续保持 pull-only authority chain，同时显式暴露 `remaining_family_projections` 与 representative failure/drift story，确保 remaining families 的存在与失败轨迹都可回归。

## Key Files

- `tests/harness/protocol/replay_models.py`
- `tests/harness/protocol/replay_driver.py`
- `tests/harness/protocol/replay_assertions.py`
- `tests/harness/protocol/replay_report.py`
- `tests/harness/evidence_pack/collector.py`
- `tests/core/api/test_protocol_replay_rest.py`
- `tests/core/mqtt/test_protocol_replay_mqtt.py`
- `tests/integration/test_protocol_replay_harness.py`
- `tests/integration/test_ai_debug_evidence_pack.py`
- `tests/meta/test_protocol_replay_assets.py`
- `tests/meta/test_evidence_pack_authority.py`

## Validation

- `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_protocol_replay_assets.py tests/meta/test_evidence_pack_authority.py` → `32 passed`
- `uv run ruff check custom_components/lipro/core/telemetry/sinks.py tests/core/telemetry/test_models.py tests/harness/protocol/replay_models.py tests/harness/protocol/replay_driver.py tests/harness/protocol/replay_assertions.py tests/harness/protocol/replay_report.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py` → passed

## Notes

- 本 plan 只强化 replay / evidence completeness，没有创建第二条 authority chain，也没有提前进入 contributor / release closeout 范围。
- representative failure/drift story 现在由 shared `failure_summary` vocabulary 驱动，后续 `Phase 22` consumer convergence 可以直接复用这条上游 truth。
