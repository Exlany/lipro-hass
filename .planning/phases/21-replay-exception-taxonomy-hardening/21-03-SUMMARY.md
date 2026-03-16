# 21-03 Summary

## Outcome

- 在 `custom_components/lipro/core/telemetry/models.py` 正式冻结了最小 failure taxonomy：`failure_category`、`failure_origin`、`handling_policy` 与 raw `error_type` 成为统一 contract。
- `custom_components/lipro/core/telemetry/sinks.py` 已改为直接复用 shared helper，不再维护私有的分类/提取逻辑，消除了 replay/exporter/sink 之间的双真源风险。
- replay summary、AI evidence pack 与 exporter-backed telemetry views 现在共享同一 failure language：scenario 级 summary 不再只输出 raw exception 名，而是同时给出 normalized category、raw type 与 structured `failure_summary`。
- 补齐了 failure-summary helper 的模型测试与 replay/evidence 集成断言，锁住 normalized taxonomy 的上游 contract。

## Key Files

- `custom_components/lipro/core/telemetry/models.py`
- `custom_components/lipro/core/telemetry/sinks.py`
- `custom_components/lipro/core/protocol/telemetry.py`
- `custom_components/lipro/core/coordinator/services/telemetry_service.py`
- `tests/harness/protocol/replay_assertions.py`
- `tests/harness/protocol/replay_report.py`
- `tests/core/telemetry/test_models.py`
- `tests/core/telemetry/test_sinks.py`
- `tests/integration/test_telemetry_exporter_integration.py`
- `tests/integration/test_protocol_replay_harness.py`
- `tests/integration/test_ai_debug_evidence_pack.py`
- `tests/meta/test_evidence_pack_authority.py`

## Validation

- `uv run pytest -q tests/core/telemetry/test_models.py tests/core/telemetry/test_sinks.py tests/core/telemetry/test_exporter.py tests/core/coordinator/services/test_telemetry_service.py tests/integration/test_telemetry_exporter_integration.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py` → `28 passed`
- `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py` → `67 passed`
- `uv run ruff check custom_components/lipro/core/telemetry/sinks.py tests/core/telemetry/test_models.py tests/harness/protocol/replay_models.py tests/harness/protocol/replay_driver.py tests/harness/protocol/replay_assertions.py tests/harness/protocol/replay_report.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py` → passed
- `uv run mypy custom_components/lipro/core/telemetry/models.py custom_components/lipro/core/telemetry/sinks.py custom_components/lipro/core/protocol/telemetry.py custom_components/lipro/core/protocol/facade.py custom_components/lipro/core/coordinator/services/telemetry_service.py custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py custom_components/lipro/core/coordinator/mqtt_lifecycle.py custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/control/entry_lifecycle_controller.py custom_components/lipro/services/diagnostics/helpers.py tests/harness/protocol/replay_models.py tests/harness/protocol/replay_driver.py tests/harness/protocol/replay_assertions.py tests/harness/protocol/replay_report.py` → `Success: no issues found in 14 source files`

## Notes

- 本 plan 把 taxonomy home 固定在 formal truth layer，没有把 `Phase 22` 的 consumer convergence 偷跑回 adapter-local surface。
- lifecycle / baseline / review 的长期治理同步仍由 `Phase 23` 集中收口；这里先把 code-and-test truth 压实，避免 phase 边界交叉漂移。
