# Residual Ledger

## Active Residual Families

| Family | Current example | Owner phase | Residual owner | Exit condition |
|--------|------------------|-------------|----------------|----------------|
| API compat wrappers | `custom_components/lipro/core/api/power_service.py` 中仍保留的 canonical-to-legacy envelope shaping 与少量 helper-level payload compatibility 语义 | Phase 2 | `02-04 compat shell cleanup`（API/Protocol owner 主责，Runtime/Coordinator owner 迁移消费者） | legacy envelope shaping 不再出现在 REST/public façade 主链；剩余 helper-level compatibility 语义 继续向 canonical rows 收口 |
| API mixin inheritance | `_ClientBase` temporary typing anchor、`_ClientPacingMixin` / `_ClientAuthRecoveryMixin` / `_ClientTransportMixin` compat shells，以及 endpoint mixin helper classes | Phase 2 | `02-04 demixin closeout handoff`（API owner 主责，Phase 2.5/6/14 继续清退） | `_ClientEndpointsMixin` aggregate carrier 已删除；remaining helper spine 只能停留在 `core/api`，并受 architecture-policy locality guard 约束 |
| Split-root protocol surfaces | `custom_components/lipro/core/mqtt/mqtt_client.py` 中 direct transport class 的 legacy naming（Phase 12 已删除 façade-level concrete-transport seam） | Phase 2.5 | `02.5 unified protocol root closeout`（Protocol owner 主责，Runtime owner 配合迁移） | runtime-facing allowed consumers 只依赖 `LiproProtocolFacade`；Phase 14 只加固 residual ownership / import guard，physical rename 继续 deferred |
| External-boundary advisory naming | firmware remote advisory / support payload generated field naming 仍带 legacy semantics | Phase 2.6 | `02.6 external-boundary closeout` | authority truth 已固定后完成术语清理 |
| Protocol-boundary family coverage | `rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 仍停留在 inventory / helper collaborator 层，尚未全部 registry-backed | Phase 7.1 | `07.1 boundary expansion handoff` | inventory 中登记的 family 全部完成 registry-backed 接线，或在 v1.1 closeout 中被明确裁决为 de-scope / retire |
| Replay scenario coverage | `tests/fixtures/protocol_replay/` 当前只正式保留 representative `rest.mqtt-config@v1` 与 `mqtt.properties@v1`；`rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 已在 `07.5` 被显式裁决为 v1.1 de-scope，而非隐式遗漏 | Phase 7.4 | `07.5 closeout arbitration` | 若未来确有 black-box replay 价值，必须以新 phase 重新登记 family、补 manifest/evidence；`08` 只消费现有 representative corpus 与 evidence index，不直接扩大 replay 范围 |

## Closed Residual Families

- `Legacy public names` 已在 Phase 12 关闭：`core.api.LiproClient` compat shell 已删除，legacy constructor name 不再作为生产 public surface 存在。
- `Capability compat public name` 已在 Phase 12 关闭：`DeviceCapabilities` 与 `custom_components/lipro/core/device/capabilities.py` 已删除。
- `Domain dynamic delegation` 已在 Phase 13 关闭：`LiproDevice.__getattr__` / `DeviceState.__getattr__` 已移除，`custom_components/lipro/core/device/device_delegation.py` 已删除。
- `Control-plane scatter` 已在 Phase 11 关闭：formal router、runtime locator 与 HA adapter 边界已固定，control plane 不再以散落 helper / wiring 叙事存在。
- `Legacy service wiring carrier` 已在 Phase 11 关闭：`custom_components/lipro/services/wiring.py` 已正式删除，control-plane formal router truth 收口到 `custom_components/lipro/control/service_router.py`。
- `API aggregate endpoint mixin` 已在 Phase 11 关闭：`custom_components/lipro/core/api/endpoints/__init__.py` 不再导出 `_ClientEndpointsMixin`，active residual 只剩 endpoint helper-class-level demixin cleanup。

## Rules

- 新发现的 residual 必须登记，不能只在对话中提到。
- 每条 residual 至少要给出 **当前样本、owner、exit condition**，否则不算正式登记。
- 任何 residual 若进入第二个 phase 仍未收敛，必须解释为何继续存在。
- compat / mixin / legacy public-name residual 只允许存在于显式 compat shell / adapters 中，不得继续散落在正式 public surface 与业务逻辑内部。

## Phase 01 Closeout Review

- 已复核当前 residual families 与 Phase 01 baseline 的关系：本阶段只锁定 protocol boundary truth，不试图提前消除 residual。
- 本次**无新增 residual family**；canonical snapshots 与 immutable constraints 没有引入新的桥接层或临时兼容结构。
- `API compat wrappers` 与 `API mixin inheritance` 继续由 Phase 2 负责清理；Phase 01 仅为其提供不可漂移的 contract 输入边界。

## Phase 02 / `02-01` Residual Delta

- 为 `API compat wrappers`、`API mixin inheritance` 补齐了明确 owner 与 file-level current examples。
- 新增 `Legacy public names` residual family，用于约束 `LiproClient` 作为 public root name 的过渡存在方式。
- 本计划只做登记，不关闭 residual；真正清退动作留给 `02-02` ~ `02-04`。


## Phase 02 / `02-04` Residual Delta

- `API mixin inheritance` 已从正式生产主链中退出，但仍以 helper-test / patch seam / typing anchor 的形式受控残留。
- `Legacy public names` 已完成 public-surface demotion：正式叙事与内部类型依赖改为 `LiproRestFacade`，保留 `LiproClient` 只为过渡工厂与兼容包装。
- `API compat wrappers` 暂未删除；其删除门槛明确交给 direct consumer migration / unified protocol root 相位继续完成。

## Phase 02.5 / `02.5-01` Residual Delta

- 新增 `Split-root protocol surfaces` residual family，专门约束 `REST root + MQTT root` 双入口语义。
- `LiproClient` 的 public-root demotion 已完成，但 `LiproMqttClient` 与 runtime-facing protocol entry 仍需在 `Phase 2.5` 继续收口。
- 后续所有 protocol-plane 清理动作都必须以 `LiproProtocolFacade` 为唯一 exit target。

## Phase 02.5 / `02.5-02 ~ 02.5-03` Residual Delta

- `Split-root protocol surfaces` 已从生产主链中清出：runtime/control 构造点、MQTT lifecycle 与 coordinator-facing seams 都只承认 `LiproProtocolFacade` 为正式协议根。
- `Legacy public names` residual 继续存在，但已缩窄为显式 compat alias / wrapper：`LiproClient` 与 `LiproMqttClient` 不再承担 formal-root 语义，只剩测试/导出/过渡层使用。
- `API compat wrappers` 仍未删除；其后续退出条件保持不变，但 unified root 已把 direct consumer 迁移主线切换完成。


## Phase 02.6 Residual Delta

- 新增 `External-boundary advisory naming` residual family：authority 已被矫正，但 remote advisory 与 generated payload 的部分命名仍需在 cleanup phase 统一为更诚实的术语。
- external-boundary 真相已经从实现代码迁出到 authority matrix / inventory / fixtures / meta guards；因此 Phase 2.6 不再保留“隐式 boundary folklore”这类未登记残留。

## Phase 03 Residual Delta

- `Control-plane scatter` residual 已从生产主链显著缩小：正式 owner 已迁入 `custom_components/lipro/control/`，剩余问题集中在 legacy carrier 与少量 private seam。
- 本 phase 曾新增 `Legacy service wiring carrier` residual family；该 residual 已在 Phase 11 随 `services/wiring.py` 删除而关闭。
- `custom_components/lipro/services/execution.py` 的私有 auth hook seam 已在 Phase 5 关闭：service execution 现在只消费正式 `auth_service` contract。


## Phase 04 Residual Delta

- `Capability duplication` 已从生产主链关闭：platform/entity/device/state 的正式能力判断现在都围绕 canonical capability truth。
- `DeviceCapabilities` residual 继续存在，但已被明确缩减为旧 public-name compat alias；它不再定义任何正式 capability 语义。


## Phase 05 Residual Delta

- `Private runtime auth seam` 已关闭：`custom_components/lipro/services/execution.py` 不再依赖 coordinator 私有 auth hook，而只通过正式 `auth_service` contract 获取认证上下文。
- runtime signal ports 已 formalize；`connect-status` shadow chain 未被 resurrect，相关 dead modules 已转入 Phase 7 治理 closeout。


## Phase 07.1 / `07.1-03` Residual Delta

- 新增 `Protocol-boundary family coverage` residual family：`rest.mqtt-config@v1` 与 `mqtt.properties@v1` 已接入 registry，但 inventory 中其余 family 仍待收口或裁决。
- `tests/fixtures/protocol_boundary/` 已建立 replay-ready evidence family；因此后续 phase 不得绕过这些 fixtures 另造 decoder/replay 真源。
- 本计划没有新增 compat shell；残留只描述尚未完成 family coverage，而不是允许 boundary truth 重新散落。

## Phase 07.2 Residual Delta

- 本 phase **无新增 residual family**；`ARCHITECTURE_POLICY.md` 只是把既有 baseline truth formalize 成单一 enforcement baseline，而不是引入第二真源。
- future `observer-only surface` / `assurance-only boundary consumer` 例外必须先回写 `ARCHITECTURE_POLICY.md` 与 baseline docs，再进入 helper / script / tests allowlist。
- targeted regression bans 只封堵已知 backdoor / export / property regression，不构成新的正式 public surface 或新 root。

## Phase 07.3 / `07.3-01` Residual Delta

- 新增 `Telemetry consumer convergence` residual family：本计划只完成 exporter formal home、contracts、ports 与 control bridge，consumer 全量收口明确留给 `07.3-02`。
- 本计划**无新增 compat shell**；`core/telemetry/*` 与 `control/telemetry_surface.py` 是正式 observer-only surface，不得被解释为第二条 runtime/control 主链。
- 后续 replay / evidence phases 只能 pull `07.3` exporter truth；若需要新增 sink/collector，必须先复用现有 contracts，而不是另立 telemetry 真源。

## Phase 07.3 / `07.3-02` Residual Delta

- `Telemetry consumer convergence` residual family 已关闭：diagnostics / system health / developer / CI sinks 的生产路径现在都统一 pull exporter truth。
- `services/diagnostics/helpers.py` 保留的 legacy `build_developer_report()` 分支只作为测试 / patch seam 兼容位，不再定义生产 telemetry 真相。
- 本计划**无新增 compat shell**；`07.4` replay harness 与 `08` evidence pack 只能继续 pull `07.3` exporter truth，不能平行定义第二套 telemetry schema。

## Phase 07.4 / `07.4-03` Residual Delta

- 新增 `Replay scenario coverage` residual family：当前 replay harness 已 formalize，但仍只覆盖 representative `rest.mqtt-config@v1` 与 `mqtt.properties@v1` 场景；其余 replay-worthy family 留给 `07.5` 做 expand / de-scope 裁决。
- `tests/harness/protocol/`、`tests/fixtures/protocol_replay/` 与 replay run summary 已形成 assurance-only 正式家园；后续 phase 只能 pull 它们，不得重新长出第二套 simulator truth。
- 本 phase **无新增 compat shell**；replay 只是 assurance consumer，不构成新的 protocol/runtime root。

## Phase 07.5 Residual Delta

- `Replay scenario coverage` 已完成 closeout arbitration：v1.1 只正式保留 representative `rest.mqtt-config@v1` 与 `mqtt.properties@v1` 场景，其余 boundary inventory families 被显式 de-scope，而不是继续以“未来再说”方式悬空。
- `V1_1_EVIDENCE_INDEX.md` 与 `07.5-SUMMARY.md` 只作为 pull-only governance / closeout 指针，不构成新的 production root、simulator root 或 telemetry truth。
- 本 phase **无新增 compat shell**；现有 file-level kill targets 继续以 `KILL_LIST.md` 中既定 delete gate 为准。

## Phase 08 Residual Delta

- 本 phase **无新增 residual family**：AI debug evidence pack 只 pull `07.3 / 07.4 / 07.5` 正式真源，不扩大 replay corpus，也不新建第二套 telemetry / governance truth。
- `entry_ref` / `device_ref` 的报告内稳定、跨报告不可关联策略继续继承 `07.3` exporter 裁决；这属于既有政策的消费，不新增新的隐含残留。
- 本 phase **无新增 compat shell / file-level kill target**；evidence-pack tooling 与导出产物仅作为 assurance-only artifacts 保留。

## Phase 09 Residual Delta

- `LiproProtocolFacade` 与 `LiproMqttFacade` 的 `__getattr__` / `__dir__` 隐式扩面已关闭；formal protocol contract 改为显式 methods/properties，child surface 不再反向定义 root。
- `custom_components/lipro/__init__.py`、`config_flow.py`、`core/__init__.py` 与 `core/mqtt/__init__.py` 的 legacy public-name / compat exports 已关闭；`Legacy public names` residual 已缩窄为 `core.api.LiproClient` 显式 compat shell、`LiproProtocolFacade.get_device_list` compat wrapper，以及 direct transport module / `LiproMqttFacade.raw_client` seam。
- protocol root 的 implicit child-defined surface 已关闭后，`Split-root protocol surfaces` residual 只剩 `raw_client` concrete-transport seam；该 seam 仅作为显式、可计数、可删除的 compat/test seam 存在。
- runtime public surface 已收口：`Coordinator.devices` 改为 read-only mapping，`LiproDevice.outlet_power_info` 成为 outlet power formal primitive，sensor/diagnostics/runtime 统一读取该真源。
- `extra_data["power_info"]` 已退出正式 outlet-power truth 角色，仅设备对象内部保留 legacy read fallback，以承接旧夹具/旧构造。
- 本 phase **未关闭全部 compat residual**：现存 residual 只能继续收窄，不能回流为 formal public surface。

## Phase 10 Residual Delta

- `rest.device-list@v1`、`rest.device-status@v1` 与 `rest.mesh-group-status@v1` 已完成 boundary-first 收口：API drift 应先打在 protocol contract / replay proof，而不是 runtime 或 HA adapter。
- `AuthSessionSnapshot` 已成为 formal auth/session truth；`config_flow.py` 与 `entry_auth.py` 已迁到 auth manager formal contract。`get_auth_data()` fallback 仅为 legacy mocks / older callers 保留，仍属显式 compat seam。
- `custom_components/lipro/core/__init__.py` 不再导出 `Coordinator`；runtime home 继续固定在 `custom_components/lipro/coordinator_entry.py`，`control/runtime_access.py` 成为 control-plane locator。
- remaining active delete-gated compat seams 仍集中在 `core.api.LiproClient`、`LiproProtocolFacade.get_device_list` 与 `LiproMqttFacade.raw_client`；本 phase 未新增新的无 gate compat root。


## Phase 11 Residual Delta

- `custom_components/lipro/control/service_router.py` 已成为真实 formal router implementation home；`services/registrations.py` 继续绑定 control-plane handler。
- 仓库内测试已迁移到 `custom_components.lipro.control.service_router`，不再把 `services/wiring.py` 当成 patch-first truth。
- `custom_components/lipro/services/wiring.py` compat shell 已删除，`Legacy service wiring carrier` residual family 已关闭。
- `custom_components/lipro/core/api/endpoints/__init__.py` 不再导出 `_ClientEndpointsMixin`；`API mixin inheritance` residual 现只覆盖 remaining helper mixin / typing anchors。


## Phase 12 Residual Delta

- `core.api.LiproClient` compat shell 已删除；`LiproRestFacade` 成为唯一正式 REST child façade。
- `LiproProtocolFacade.get_device_list` compat wrapper 已删除；device-list canonical contract 固定为 `rest.device-list@v1`。
- `LiproMqttFacade.raw_client` compat seam 已删除；concrete transport 不再通过 protocol façade 暴露。
- `DeviceCapabilities` compat alias 与 `core/device/capabilities.py` 已删除；能力真源固定为 `CapabilityRegistry` / `CapabilitySnapshot`。
- `_ClientBase` 保留为 internal endpoint typing contract，但不再被视为 active public residual 或 compat shell。

## Phase 13 Residual Delta

- `LiproDevice` 与 `DeviceState` 的动态 `__getattr__` 已删除；domain surface 正式改成显式 property / method 集合。
- `custom_components/lipro/core/device/device_delegation.py` 已物理删除；`state_accessors.py` 仅保留显式 helper 角色。
- 本 phase **无新增 residual family**：收口的是既有 domain dynamic delegation，而不是引入新的 compat 层。
- active residual 现主要集中在 `_ClientBase` / `_Client*Mixin` typing/helper spine、`LiproMqttClient` legacy naming 与 helper-level compatibility envelope；hotspot glue 已完成第一次拆分。


## Phase 14 Residual Delta

- 本 phase **无新增 residual family**：`Coordinator` 的 protocol-facing passthrough 已收口到 `CoordinatorProtocolService`，但这不是新的兼容层。
- `ScheduleApiService` 已退出正式 schedule 主链；remaining API residual 继续集中在 `_ClientBase` / helper mixin family 与 helper-level compatibility，而不是 service-loop 回环。
- `custom_components/lipro/core/api/status_fallback.py` 与 `custom_components/lipro/control/developer_router_support.py` 已成为 internal helper homes；`status_service.py` 与 `service_router.py` 保留 public orchestration / handler identity。
