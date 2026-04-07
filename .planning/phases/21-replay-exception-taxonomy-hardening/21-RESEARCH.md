# Phase 21 Research

**Status:** `research complete`
**Date:** `2026-03-16`
**Mode:** `forced re-research via $gsd-plan-phase 21 --research`

## Executive Judgment

`Phase 21` 不是再补 boundary formalization，而是要把 `Phase 20` 的四个 remaining families 从“已经登记到 replay/evidence story 里”推进到“被 family-level assertions、evidence visibility、failure taxonomy 和 focused regression 真正锁死”。

最优拆分仍然是 `3 plans / 2 waves`：

- `21-01`：锁 replay / evidence coverage 真相
- `21-02`：收窄或契约化 broad-catch envelopes
- `21-03`：把 failure taxonomy 固定到 replay / telemetry / sink contract，并补 guards / closeout sync

## Code Reality Audit

### 1. 四个 Phase 20 families 已经“存在于 replay story”，但 coverage 仍偏 generic

现状：

- `tests/fixtures/protocol_replay/` 已包含：
  - `rest/get_device_list.envelope.replay.json`
  - `rest/query_mesh_schedule_json.v1.replay.json`
  - `mqtt/topic.device_state.v1.replay.json`
  - `mqtt/message_envelope.device_state.v1.replay.json`
- `tests/meta/test_protocol_replay_assets.py` 已断言这些 family 的 manifest / authority / operation 注册。
- `tests/integration/test_protocol_replay_harness.py` 已通过 manifest loop 跑全量 scenarios。
- `tests/harness/evidence_pack/collector.py` 也会遍历全部 manifests，把它们带入 `replay.summary` 与 `boundary.representative_families`。

缺口：

- `test_protocol_replay_harness.py` 目前主要是“manifest 全量跑通 + expected canonical”，没有把四个 `Phase 20` families 单独拉出来做 family-level coverage contract。
- `test_ai_debug_evidence_pack.py` 只检查 `representative_families` 非空、`scenario_count == len(scenarios)`，没有要求 evidence pack **必须包含** 这四个 families。
- `test_evidence_pack_authority.py` 仍主要锁 `Phase 8` authority / source path truth，没有新增 Phase 21 对 replay/evidence 族的硬性 coverage 断言。

结论：`SIM-04` 的真实缺口不是“没有 manifest”，而是“缺少对四个新增 families 的显式 replay/evidence coverage contract”。

### 2. replay summary / telemetry 仍把 raw exception type 当成 category

现状：

- `tests/harness/protocol/replay_models.py` 中 `ReplayExecutionResult.error_category` 当前承载的是 `type(err).__name__`。
- `tests/harness/protocol/replay_report.py` 直接把 `error_category` 暴露进 summary。
- `tests/harness/protocol/replay_assertions.py` 与 `core/telemetry/sinks.py` 里的 system-health 投影仍使用：
  - `protocol_mqtt_last_error_type`
  - `mqtt_last_transport_error`
- `tests/integration/test_telemetry_exporter_integration.py` 与 `tests/core/telemetry/test_sinks.py` 目前也按 raw type 断言。

缺口：

- 这还不是 `auth/network/protocol/runtime` 级别的 taxonomy，只是原始错误类型透传。
- 如果 `Phase 22` 要做到 consumer vocabulary convergence，`Phase 21` 必须先把“family-level taxonomy + raw detail”分层拆开。

结论：`21-03` 必须把 `error_category` 从“原始异常类名”语义提升为稳定 taxonomy（并保留 raw detail 字段），同时让 replay summary 与 telemetry sinks 说同一套词。

### 3. broad-catch 热点需要分成“必须收窄”与“允许 envelope catch”两类

#### A. 应优先收窄或至少变成明确 failure stage 的热点

- `custom_components/lipro/core/protocol/facade.py`
  - `start()` / `stop()` / `sync_subscriptions()` / `wait_until_connected()`
  - 当前 catch-all 只做 `record_mqtt_error(err)` 然后 re-raise
  - 问题：没有 stage-aware arbitration，taxonomy 输入不足
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`
  - `connect()` / `sync_subscriptions()` / `disconnect()`
  - 当前 generic `_LOGGER.exception(...)` + `False`
  - 问题：无法区分 connect / subscription / wait / disconnect 四类 failure
- `custom_components/lipro/core/coordinator/mqtt_lifecycle.py`
  - MQTT setup 顶层 catch-all
  - 问题：setup envelope 合理，但需要稳定 stage/reason 语义
- `custom_components/lipro/core/coordinator/coordinator.py`
  - `_async_update_data()` 的 final `except Exception -> UpdateFailed("Unexpected update failure")`
  - 问题：unexpected branch 合理存在，但需要统一 failure family / detail / logging contract

#### B. 可以保留 catch-all，但必须写成“有契约的 envelope”

- `custom_components/lipro/control/entry_lifecycle_controller.py`
  - first refresh / forward setups 的 abort envelope
  - unload 时的 shutdown warning envelope
- `custom_components/lipro/services/diagnostics/helpers.py`
  - per-entry capability collect / developer-report collect 的 best-effort skip envelope
- `custom_components/lipro/core/coordinator/coordinator.py`
  - `async_shutdown()` 清理阶段的 warning envelope

结论：`ERR-02` 不应被执行成“无脑 BLE001 清零”，而应执行成“热点处置表 + retained envelope contract + focused regression”。

### 4. 现有 service-layer failure contract 可以作为 taxonomy 风格参考，但不能直接照搬

- `custom_components/lipro/services/contracts.py::CommandFailureSummary` 已有 `reason / code / route / device_id` 这种“分类 + detail”结构。
- `custom_components/lipro/services/errors.py` 已把 command failure 映射到稳定 translation keys。
- `custom_components/lipro/services/execution.py` 已把 `auth_expired / auth_error / api_error` 通过统一 facade 归一。

启示：

- Phase 21 的 taxonomy 也应采用“**stable family + raw detail**”两层结构。
- 但不要直接把 service-layer translation key 反向提升为 protocol/runtime telemetry taxonomy。

## Recommended Plan Structure

### Plan 21-01 — lock replay and evidence coverage for Phase 20 families

目标：把四个新增 families 从“被 manifest loop 带到”升级为“被 family-level assertions、evidence summary、asset guards 明确锁定”。

推荐文件域：

- `tests/harness/protocol/replay_driver.py`
- `tests/harness/protocol/replay_report.py`
- `tests/integration/test_protocol_replay_harness.py`
- `tests/integration/test_ai_debug_evidence_pack.py`
- `tests/meta/test_protocol_replay_assets.py`
- `tests/meta/test_evidence_pack_authority.py`
- `tests/core/api/test_protocol_replay_rest.py`
- `tests/core/mqtt/test_protocol_replay_mqtt.py`
- `tests/fixtures/protocol_replay/README.md`

关键要求：

- 四个 `Phase 20` families 必须分别在 harness 与 evidence pack 断言中可见。
- replay summary 与 `boundary.representative_families` 必须能显式证明这些 families 在 evidence output 中存在。
- 不改变 authority source path 结构，不引入新的 public path。

### Plan 21-02 — narrow or document broad-catch envelopes

目标：把关键 broad-catch 热点按“收窄 / 保留 envelope catch”分类落地，并留下稳定 reason/stage 语义。

推荐文件域：

- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`
- `custom_components/lipro/core/coordinator/mqtt_lifecycle.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/control/entry_lifecycle_controller.py`
- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/services/maintenance.py`
- `tests/core/test_init.py`
- `tests/core/coordinator/runtime/test_mqtt_runtime.py`
- `tests/integration/test_mqtt_coordinator_integration.py`
- `tests/services/test_service_resilience.py`
- `tests/services/test_services_diagnostics.py`
- `tests/services/test_maintenance.py`
- `tests/services/test_execution.py`

关键要求：

- 永远保留 `CancelledError/KeyboardInterrupt/SystemExit` 直通。
- retained envelope catches 必须补稳定日志 reason / telemetry detail / focused regression。
- 不为 Phase 21 新造对外 public exception class。

### Plan 21-03 — formalize failure taxonomy contract and guards

目标：把 failure taxonomy 固定到 replay / telemetry / sink contract，成为 `Phase 22` observability convergence 的正式上游输入。

推荐文件域：

- `tests/harness/protocol/replay_models.py`
- `tests/harness/protocol/replay_driver.py`
- `tests/harness/protocol/replay_report.py`
- `tests/harness/protocol/replay_assertions.py`
- `custom_components/lipro/core/telemetry/models.py`
- `custom_components/lipro/core/telemetry/sinks.py`
- `custom_components/lipro/control/telemetry_surface.py`
- `tests/core/telemetry/test_sinks.py`
- `tests/core/telemetry/test_exporter.py`
- `tests/integration/test_telemetry_exporter_integration.py`
- `tests/core/test_diagnostics.py`
- `tests/core/test_system_health.py`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_dependency_guards.py`
- phase closeout 时同步的 baseline/review assets

关键要求：

- taxonomy 至少应能稳定表达 `auth / network / protocol / runtime`；必要时再补 `unexpected`，但不要无限扩张。
- raw exception type / error code 保留为 detail 字段，而不是 taxonomy 本身。
- diagnostics / system health adapters 继续 thin；真正 vocabulary truth 来自 replay/exporter contracts。

## Validation Architecture

### Wave 1

- `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_protocol_replay_assets.py tests/meta/test_evidence_pack_authority.py`
- `uv run pytest -q tests/core/coordinator/runtime/test_mqtt_runtime.py tests/integration/test_mqtt_coordinator_integration.py tests/core/test_init.py tests/services/test_service_resilience.py tests/services/test_services_diagnostics.py tests/services/test_maintenance.py tests/services/test_execution.py`

### Wave 2

- `uv run pytest -q tests/core/telemetry/test_sinks.py tests/core/telemetry/test_exporter.py tests/integration/test_telemetry_exporter_integration.py tests/core/test_system_health.py tests/core/test_diagnostics.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_protocol_replay_assets.py tests/meta/test_evidence_pack_authority.py`
- `uv run ruff check custom_components/lipro/core/protocol custom_components/lipro/core/coordinator custom_components/lipro/core/telemetry custom_components/lipro/control custom_components/lipro/services/diagnostics tests/harness/protocol tests/harness/evidence_pack tests/integration tests/core/telemetry tests/meta`

## Risks And Rollback Guidance

### Main Risks

- 把 taxonomy 设计得过大，导致 `Phase 21` 变成半个 `Phase 22`。
- 把 retained catch-all 全部硬删，反而破坏 setup/unload/diagnostics 的 envelope semantics。
- 在 replay/evidence 里增加 coverage 时不小心改动 authority source 或新增第二条 helper-local story。

### Rollback Strategy

- `21-01` 如 family-level evidence assertions 设计不稳，可先回滚到“显式 family enumeration + non-empty evidence coverage”最小版本，再逐步补 richer summary assertions。
- `21-02` 如 narrowing 触发大面积回归，可保留 catch-all，但必须引入 stage/reason/detail 结构与 focused tests，避免回到纯 generic wording。
- `21-03` 如 taxonomy 字段命名影响面过大，优先采用“新增 stable field + 保留旧 raw detail 字段”的向前兼容方案，不做激进 rename。

## Governance Follow-Through Required At Execution Time

`Phase 21` 虽不是 contributor-doc / release closeout phase，但如果改变了 formal replay/exporter/guard truth，执行收官时仍必须同步：

- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`

这些回写属于 **phase truth sync**，不等于提前执行 `Phase 23`。
