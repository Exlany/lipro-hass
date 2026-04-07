# Phase 21 Verification

status: passed

## Goal

- 核验 `Phase 21: Replay Coverage & Exception Taxonomy Hardening` 是否完成 `SIM-04` 与 `ERR-02`：remaining replay families 必须获得显式 coverage / evidence truth，关键 broad-catch 必须被裁决成可分类输入，且 replay / telemetry/exporter 必须共享同一 failure taxonomy。
- 终审结论：**`SIM-04` 与 `ERR-02` 已达成；Phase 21 已为 `Phase 22` consumer convergence 与 `Phase 23` governance sync 提供稳定、可验证的上游真相，因此本 phase 签核记为 `passed`。**

## Reviewed Assets

- Phase 资产：`.planning/phases/21-replay-exception-taxonomy-hardening/21-CONTEXT.md`、`.planning/phases/21-replay-exception-taxonomy-hardening/21-RESEARCH.md`、`.planning/phases/21-replay-exception-taxonomy-hardening/21-VALIDATION.md`
- 已生成 summaries：`.planning/phases/21-replay-exception-taxonomy-hardening/21-01-SUMMARY.md`、`.planning/phases/21-replay-exception-taxonomy-hardening/21-02-SUMMARY.md`、`.planning/phases/21-replay-exception-taxonomy-hardening/21-03-SUMMARY.md`
- 实现/测试真源：`tests/harness/protocol/{replay_models.py,replay_driver.py,replay_assertions.py,replay_report.py}`、`tests/harness/evidence_pack/collector.py`、`custom_components/lipro/core/telemetry/{models.py,sinks.py}`、`custom_components/lipro/core/protocol/telemetry.py`、`custom_components/lipro/core/coordinator/{coordinator.py,mqtt_lifecycle.py}`、`custom_components/lipro/core/coordinator/services/telemetry_service.py`、`custom_components/lipro/control/entry_lifecycle_controller.py`、`custom_components/lipro/services/diagnostics/helpers.py`

## Must-Haves

- **1. Remaining replay families are explicit assurance truth — PASS**
  - `rest.list-envelope`、`rest.schedule-json`、`mqtt.topic`、`mqtt.message-envelope` 现在被 replay summary、evidence pack 与 meta guards 共同显式断言。
  - representative failure/drift story 已覆盖 REST 与 MQTT 两条 remaining-family 轨迹，而不再只依赖 legacy representative family。

- **2. Broad-catch arbitration is narrowed or documented — PASS**
  - coordinator update、MQTT lifecycle / runtime、entry lifecycle abort 与 diagnostics helpers 的 catch 语义已完成裁决。
  - `asyncio.CancelledError` passthrough 已被保住，关键 failure 入口可以输出稳定 telemetry input。

- **3. Failure taxonomy is shared across replay / telemetry / exporter — PASS**
  - `failure_category`、`failure_origin`、`handling_policy`、`error_type` 已在 formal truth layer 冻结。
  - replay summary、AI evidence pack 与 exporter sinks 现在共同消费 structured `failure_summary`，raw exception type 只作为 debug detail 保留。

- **4. Focused and broad verification gates are green — PASS**
  - replay/evidence focused suite、runtime/control regression、helper/model/exporter tests、meta guards、`ruff` 与 targeted `mypy` 全部通过。

## Evidence

- `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_protocol_replay_assets.py tests/meta/test_evidence_pack_authority.py` → `32 passed`
- `uv run pytest -q tests/core/test_init.py tests/core/test_init_edge_cases.py tests/core/test_coordinator.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/services/test_telemetry_service.py tests/services/test_service_resilience.py tests/integration/test_mqtt_coordinator_integration.py` → `272 passed`
- `uv run pytest -q tests/core/telemetry/test_models.py tests/core/telemetry/test_sinks.py tests/core/telemetry/test_exporter.py tests/core/coordinator/services/test_telemetry_service.py tests/integration/test_telemetry_exporter_integration.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py` → `28 passed`
- `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py` → `67 passed`
- `uv run ruff check custom_components/lipro/core/telemetry/sinks.py tests/core/telemetry/test_models.py tests/harness/protocol/replay_models.py tests/harness/protocol/replay_driver.py tests/harness/protocol/replay_assertions.py tests/harness/protocol/replay_report.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py` → 退出码 `0`
- `uv run mypy custom_components/lipro/core/telemetry/models.py custom_components/lipro/core/telemetry/sinks.py custom_components/lipro/core/protocol/telemetry.py custom_components/lipro/core/protocol/facade.py custom_components/lipro/core/coordinator/services/telemetry_service.py custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py custom_components/lipro/core/coordinator/mqtt_lifecycle.py custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/control/entry_lifecycle_controller.py custom_components/lipro/services/diagnostics/helpers.py tests/harness/protocol/replay_models.py tests/harness/protocol/replay_driver.py tests/harness/protocol/replay_assertions.py tests/harness/protocol/replay_report.py` → `Success: no issues found in 14 source files`

## Risks / Notes

- `Phase 21` 已完成 code-and-test truth 的冻结，但没有越界去更新 contributor docs / release evidence / lifecycle 真源；这些仍按计划交给 `Phase 23` 统一收口。
- `Phase 22` 现在可以安全消费 `Phase 21` 的 shared failure taxonomy，而无需再解释 replay / runtime failure 语言的来源。
- `Phase 23` 的主要任务已从“补技术真相”转为“同步治理真源与对外叙事”。
