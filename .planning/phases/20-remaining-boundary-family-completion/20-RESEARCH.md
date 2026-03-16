# Phase 20 Research

**Phase:** `20 Remaining Boundary Family Completion`
**Source inputs:** `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `Phase 19` closeout truth, focused code scan
**Date:** 2026-03-16

## Inputs

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/phases/20-remaining-boundary-family-completion/20-CONTEXT.md`
- `custom_components/lipro/core/protocol/boundary/__init__.py`
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`
- `custom_components/lipro/core/protocol/boundary/schema_registry.py`
- `custom_components/lipro/core/protocol/contracts.py`
- `custom_components/lipro/core/api/endpoints/schedule.py`
- `custom_components/lipro/services/schedule.py`
- `custom_components/lipro/core/mqtt/topics.py`
- `custom_components/lipro/core/mqtt/message_processor.py`
- `tests/fixtures/api_contracts/README.md`
- `tests/fixtures/protocol_boundary/README.md`
- `tests/fixtures/protocol_replay/README.md`
- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/core/api/test_protocol_replay_rest.py`
- `tests/core/mqtt/test_protocol_replay_mqtt.py`
- `tests/integration/test_protocol_replay_harness.py`
- `tests/meta/test_protocol_replay_assets.py`

## Key Findings

### 1. 当前 boundary registry 已有正式主干，但 remaining families 尚未被“命名并入册”

当前仓库中，formal boundary family 已有清晰的正式 home：

- REST families：`rest.mqtt-config@v1`、`rest.device-list@v1`、`rest.device-status@v1`、`rest.mesh-group-status@v1`
- MQTT family：`mqtt.properties@v1`
- registry：`custom_components/lipro/core/protocol/boundary/schema_registry.py`
- public surface：`custom_components/lipro/core/protocol/boundary/__init__.py`
- protocol contract bridge：`custom_components/lipro/core/protocol/contracts.py`

因此 `Phase 20` 不是从零开始建边界系统，而是把**已经存在但仍隐含在 helper/endpoint/concrete path 中的剩余 family**升格为显式 registry-backed family。

### 2. `rest.list-envelope.v1` 的真实缺口，不在业务数据规范化，而在“分页/列表 envelope 仍是隐式 helper”

`custom_components/lipro/core/protocol/boundary/rest_decoder.py` 已经通过 `_extract_list_payload()`、`_coerce_total()` 与 `_decode_device_list_canonical()` 处理 list-like REST envelopes，但这些规则目前仍附着在具体 family（尤其 `rest.device-list`）上，而不是以 `rest.list-envelope.v1` 的 family 身份对外登记。

这带来两个问题：

1. list envelope 作为 cross-endpoint canonicalization 规律无法被独立治理、独立测试、独立 replay/fixture 引用；
2. 后续 schedule list、其他 REST list endpoints 若继续复用该规律，很容易再次走回 helper-level ad-hoc，而非统一 boundary family。

Phase 20 应把这类列表 envelope 抽成**formalized shared boundary family / helper-home with registry-facing identity**，再让 `rest.device-list`、`rest.device-status`、`rest.mesh-group-status` 或未来 schedule families 明确站在它之上，而不是继续隐式共享私有 helper。

### 3. `rest.schedule-json.v1` 当前主要停留在 endpoint/service codec 层，尚未进入 protocol boundary formal truth

schedule 路径目前主要分布于：

- `custom_components/lipro/core/api/endpoints/schedule.py`
- `custom_components/lipro/core/api/schedule_codec.py`
- `custom_components/lipro/services/schedule.py`

现状说明：

- schedule 请求/响应已有相当多 typed helper 与 codec；
- mesh schedule JSON 已有 `parse_mesh_schedule_json()` / `normalize_mesh_timing_rows()` 等处理链；
- service 层有 `normalize_schedule_row()` 等面向 HA service response 的投影。

但它仍缺少 Phase 20 需要的 formalization 要素：

- 没有 `rest.schedule-json@v1` 这样的 boundary registry identity；
- 没有 authority fixture family 明确承接 schedule JSON 的 canonical truth；
- 没有 replay manifest family 通过 protocol public path 覆盖 schedule JSON decode；
- schedule JSON 仍容易被误读为 endpoint/service codec，而不是 protocol-boundary truth。

因此 `Phase 20` 的关键，不是“再写一套 schedule service”，而是把已有 schedule JSON normalization 提升到 protocol boundary family home，并补齐 fixture / replay / drift assertions。

### 4. MQTT 还缺两层 formal family：`topic` 与 `message-envelope`

当前 MQTT formal truth 只有 `mqtt.properties@v1`：它专注“从 payload 中提取 canonical properties”。

但 MQTT 实际上还有两层尚未 formalized：

1. `mqtt.topic.v1`：`custom_components/lipro/core/mqtt/topics.py` 中的 `normalize_mqtt_biz_id()`、`build_topic()`、`parse_topic()` 实际定义了 topic grammar；
2. `mqtt.message-envelope.v1`：`custom_components/lipro/core/mqtt/message_processor.py` 中的 `decode_payload_text()`、JSON object gate、payload wrapper selection 等实际定义了“进入 properties decoder 前”的 message envelope 契约。

如果 Phase 20 不把它们 formalize：

- topic grammar 仍会停留在 concrete util，而非 protocol boundary truth；
- message envelope 仍会停留在 message processor / payload helper，而非 registry-backed family；
- replay 与 fixture 只能证明 `mqtt.properties`，无法证明 topic/message envelope 已被正式治理。

### 5. replay / fixture / meta 资产当前覆盖的是 representative families，不是 remaining families

### 6. registry visibility 本身就是 formalization 的一部分

`Phase 20` 的目标写的是“registry-backed boundary families”，这意味着代码层面的 formalization 不能停在新增 helper/decoder：

- `custom_components/lipro/core/protocol/boundary/__init__.py::build_protocol_boundary_registry()` 必须显式登记新增 families；
- `custom_components/lipro/core/protocol/contracts.py::CanonicalProtocolContracts.describe_boundary_decoders()` 的输出必须稳定暴露这些 families；
- `tests/core/api/test_protocol_contract_matrix.py` 当前只断言 5 个 families（`rest.mqtt-config`、`rest.device-list`、`rest.device-status`、`rest.mesh-group-status`、`mqtt.properties`），Phase 20 必须把新增 families 纳入同一 registry descriptor truth。

若这一步不做，即使内部 helper 已经存在，也不能诚实地称为“registry-backed”。

### 7. schedule candidate-query path 是 `rest.schedule-json.v1` 的隐性回归面

`schedule` 路径不只是一组 parse/normalize helpers。`custom_components/lipro/core/api/endpoints/schedule.py` 还承接 mesh candidate fallback、candidate request orchestration 与 `normalize_mesh_timing_rows()` 的组合，而这条链有专门测试：`tests/core/api/test_api_schedule_candidate_queries.py`。

这意味着 `rest.schedule-json.v1` 的 formalization 若只覆盖 `schedule_codec.py` 与 service-layer normalization，会遗漏最容易回归的 mesh candidate semantics。

Phase 20 的验证必须至少把以下两类测试一起纳入：

- `tests/core/api/test_schedule_codec.py`（codec canonicalization）
- `tests/core/api/test_api_schedule_candidate_queries.py`（candidate fallback / orchestration）

### 8. `parse_mqtt_payload()` 是 MQTT remaining family 的额外 public shim

`custom_components/lipro/core/mqtt/payload.py::parse_mqtt_payload()` 当前是通向 `decode_mqtt_properties_payload()` 的 lazy-import shim。若 `mqtt.message-envelope.v1` 在 `Phase 20` 中被正式化，这个 shim 的职责边界也必须被重新审视：

- 它要么继续只代理“envelope 之后的 properties canonicalization”；
- 要么显式接到新的 envelope family 后再向下游委派；

但无论如何，不能让 `payload.py` 自己长成第二条 formal authority path。

当前 replay/fixture truth 主要覆盖：

- REST：`rest.mqtt-config`、`rest.device-list`、`rest.device-status`、`rest.mesh-group-status`
- MQTT：`mqtt.properties`

证据位于：

- `tests/fixtures/api_contracts/README.md`
- `tests/fixtures/protocol_boundary/README.md`
- `tests/fixtures/protocol_replay/README.md`
- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/core/api/test_protocol_replay_rest.py`
- `tests/core/mqtt/test_protocol_replay_mqtt.py`
- `tests/integration/test_protocol_replay_harness.py`
- `tests/meta/test_protocol_replay_assets.py`

这意味着 `Phase 20` 不能只改代码：必须同步 fixture families、replay manifests、asset guards 与 verification truth，才能真正关闭 `SIM-03` / `SIM-05`。

### 9. `rest.schedule-json.v1` 还必须覆盖 request-side grammar 与 facade public path

`custom_components/lipro/core/api/schedule_service.py` 承接 mesh candidate orchestration，`custom_components/lipro/core/api/schedule_endpoint.py` 承接 `scheduleJson` request-body encode、candidate 去重/排序与 endpoint-level contract，而 `custom_components/lipro/core/api/client.py` / `tests/core/api/test_api.py` 则是正式 REST facade 暴露 schedule 行为的 public path。

因此 `Phase 20` 若只 formalize read-side codec / endpoint normalization，会留下两类假闭环：

- 读路径进入 boundary family，但写路径仍保留第二套 `scheduleJson` grammar；
- helper / endpoint 测试通过，但 `LiproRestFacade` 的正式 public path 未被一起验证。

`20-01` 必须同时把以下锚点纳入计划与验证：

- `custom_components/lipro/core/api/schedule_service.py`
- `custom_components/lipro/core/api/schedule_endpoint.py`
- `custom_components/lipro/core/api/client.py`
- `tests/core/api/test_schedule_endpoint.py`
- `tests/core/api/test_api_schedule_endpoints.py`
- `tests/core/api/test_api.py` 中的 schedule-focused facade regression

### 10. replay harness typed operation whitelist / driver dispatch 必须与新 manifest 同轮演进

新增 `rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 若要进入 replay manifest，仅补 fixture / manifest / integration test 还不够。`tests/harness/protocol/replay_models.py` 的 typed operation whitelist 与 `tests/harness/protocol/replay_driver.py` 的 public-path dispatch 也必须同轮扩展，否则 manifest 可以落盘，但 replay driver 仍会卡在 operation validation 或 `assert_never()`。

这意味着 `20-01` / `20-02` 中任何新增 replay operation 的任务，都必须把 harness model + driver 视为同一原子修改，而不是推迟到后续 phase 补洞。

## Family-by-Family Gap Analysis

### `rest.list-envelope.v1`

**Current truth**
- 主要体现在 `rest_decoder.py` 的 `_extract_list_payload()`、`_coerce_total()`、payload fingerprinting 逻辑。
- 已被 `rest.device-list`、`rest.device-status`、`rest.mesh-group-status` 间接复用。

**Gap**
- 无独立 family identity / version。
- 无独立 authority/fixture description。
- 无独立 drift assertion / replay coverage。
- 复用方式仍偏 helper-local，而非 registry-formalized。

**Implication**
- future list-like REST endpoints 仍容易重复 ad-hoc handling。

### `rest.schedule-json.v1`

**Current truth**
- 主要体现在 `schedule_codec.py`、`endpoints/schedule.py` 与 `services/schedule.py`。
- 已有 mesh schedule JSON parse / normalize helpers。

**Gap**
- 没有 boundary registry entry。
- 没有 authority fixture family。
- 没有 replay manifest / protocol public-path assertion。
- schedule JSON 真相仍混杂在 endpoint/service homes。

**Implication**
- schedule family 仍是 formal boundary story 之外的“特例”。

### `mqtt.topic.v1`

**Current truth**
- 主要体现在 `core/mqtt/topics.py` 中的 topic grammar 与 biz/device normalization。
- `message_processor.py` 实际依赖该 grammar 决定消息是否合法。

**Gap**
- 没有 protocol-boundary family 身份。
- 没有 boundary fixture 明确承载 topic canonicalization truth。
- 没有 replay/asset matrix 显式覆盖 topic grammar。

**Implication**
- topic 仍像 transport util，而不是 canonical boundary contract。

### `mqtt.message-envelope.v1`

**Current truth**
- 主要体现在 `message_processor.py` 与 `mqtt_decoder.py` 的 wrapper selection / payload object gate。
- `mqtt.properties` family 只处理 envelope 进入 decoder 之后的 property canonicalization。

**Gap**
- 无独立 family identity。
- 无 fixture family 单独承载 envelope canonical truth。
- 无 replay/public-path assertion 覆盖 envelope → properties decoder chain。

**Implication**
- MQTT 的正式边界 story 仍只覆盖 payload body，不覆盖 topic + envelope 全链路。

## Recommended Task Split

### `20-01`: formalize remaining REST families

建议范围：

- 把 list envelope 从 helper-level 规则提升为 formal REST family truth（或至少成为明确登记的 shared family home）。
- 把 schedule JSON 从 endpoint/service codec 提升到 protocol boundary family。
- 补齐 schedule/list 相关 authority fixtures、focused contract tests、必要 replay manifests。

建议文件中心：

- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/core/protocol/boundary/__init__.py`
- `custom_components/lipro/core/protocol/contracts.py`
- `custom_components/lipro/core/api/schedule_codec.py`
- `custom_components/lipro/core/api/endpoints/schedule.py`
- `tests/fixtures/api_contracts/`
- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/core/api/test_protocol_replay_rest.py`
- `tests/core/api/test_api_schedule_candidate_queries.py`

### `20-02`: formalize remaining MQTT families

建议范围：

- 把 `mqtt.topic.v1` 升格为 formal boundary grammar family。
- 把 `mqtt.message-envelope.v1` 升格为 formal boundary envelope family。
- 让 `mqtt.properties@v1` 明确成为 envelope 之后的 downstream canonical family，而不是涵盖全部 MQTT boundary story。
- 补齐 boundary fixture / focused tests / replay coverage。

建议文件中心：

- `custom_components/lipro/core/mqtt/topics.py`
- `custom_components/lipro/core/mqtt/message_processor.py`
- `custom_components/lipro/core/mqtt/payload.py`
- `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`
- `custom_components/lipro/core/protocol/boundary/__init__.py`
- `custom_components/lipro/core/protocol/contracts.py`
- `tests/fixtures/protocol_boundary/`
- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/core/mqtt/test_mqtt_payload.py`
- `tests/core/mqtt/test_message_processor.py`
- `tests/core/mqtt/test_protocol_replay_mqtt.py`

### `20-03`: sync inventory / fixtures / manifests / guards

建议范围：

- 更新 protocol-boundary fixture matrix 与 replay README。
- 为新增 families 补齐 manifests / asset guards / verification matrix。
- 若 public/dependency/review truth 受影响，同轮同步 baseline/reviews/phase docs。
- 为 `Phase 20` 执行完成预留 roadmap/requirements/state 最小回写路径。

建议文件中心：

- `tests/fixtures/api_contracts/README.md`
- `tests/fixtures/protocol_boundary/README.md`
- `tests/fixtures/protocol_replay/README.md`
- `tests/meta/test_protocol_replay_assets.py`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

## Explicit Defers

以下内容必须 defer 到后续 phases：

1. `Phase 21`：broad-catch / exception taxonomy / observability classification hardening
2. `Phase 22`：governance/docs/release 全局 closeout
3. 新 runtime root / new host abstraction / second CLI root
4. 非 boundary formalization 的大规模 helper churn
5. diagnostics/system-health/exporter 语义改造

## Risks

### 1. 把 shared helper 直接包装成 family，可能制造“名字变了但真相没变”

**Mitigation:** family formalization 必须同时具备 registry entry、fixture authority、tests/replay path；不能只停在 rename。

### 2. schedule formalization 容易误触 service response 语义

**Mitigation:** boundary family 只处理 protocol canonical truth；HA service-layer response projection 继续留在 `services/schedule.py`。

### 3. MQTT topic/envelope formalization 容易与 transport/concrete processor 职责纠缠

**Mitigation:** 把 topic grammar 与 envelope validation/normalization 作为 boundary family，message processor 只消费 formal decoder result，不重新当 authority。

### 4. replay coverage 若只补 fixtures 不补 public path assertions，会留下假闭环

**Mitigation:** 每个新增 family 都至少要有 protocol contract test + replay asset test + integration replay harness visibility。

## Validation Architecture

### REST-focused loop

- `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_replay_rest.py tests/core/api/test_schedule_codec.py tests/core/api/test_schedule_endpoint.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_candidate_queries.py tests/services/test_services_schedule.py tests/core/api/test_api.py -k "schedule"`

### MQTT-focused loop

- `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/mqtt/test_mqtt.py tests/core/mqtt/test_topic_builder.py tests/core/mqtt/test_mqtt_payload.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_client_refactored.py tests/core/mqtt/test_protocol_replay_mqtt.py`

### Replay / asset loop

- `uv run pytest -q tests/integration/test_protocol_replay_harness.py tests/meta/test_protocol_replay_assets.py tests/meta/test_evidence_pack_authority.py`

### Governance / full-confidence loop

- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`
- `uv run ruff check .`
- `uv run mypy`
- `uv run pytest -q`

## Planning Recommendation

最优计划结构仍应保持 roadmap 中的 `3 plans / 3 waves`：

- **Wave 1 / 20-01**：先 formalize REST remaining families，尤其 list envelope + schedule JSON
- **Wave 2 / 20-02**：在 REST truth 就位后 formalize MQTT topic + message envelope
- **Wave 3 / 20-03**：最后统一回写 fixtures / manifests / guards / docs，锁定 `SIM-03` / `SIM-05` 关闭态

这样可以最大限度避免在同一波次里同时修改 REST + MQTT + governance 三大面，保持执行原子性与验证清晰度。
