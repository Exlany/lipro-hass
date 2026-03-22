# Residual Ledger

## Active Residual Families

| Family | Current example | Owner phase | Residual owner | Exit condition |
|--------|------------------|-------------|----------------|----------------|
_None currently registered._

## Closed Residual Families

- `Command-result stringly-typed outcome contract` 已在 Phase 57 关闭：`custom_components/lipro/core/command/result_policy.py` / `result.py` 现已共享 typed state / verification / failure-reason vocabulary，runtime sender 与 diagnostics `query_command_result` response typing 也不再依赖 scattered raw strings。

- `Generic backoff helper leak` 已在 Phase 56 关闭：`compute_exponential_retry_wait_time()` 现已迁到 `custom_components/lipro/core/utils/backoff.py`，command/runtime/MQTT callers 不再从 `request_policy.py` 取用 generic helper，而 `RequestPolicy` 只继续拥有 API-local `429` / busy / pacing truth。

- `External-boundary advisory naming` 已在 Phase 38 关闭：firmware external-boundary 现统一为 local trust-root / remote advisory 语义；历史资产文件名 `firmware_support_manifest.json` 被保留，但不再被表述成 advisory truth。

- `Legacy public names` 已在 Phase 12 关闭：`core.api.LiproClient` compat shell 已删除，legacy constructor name 不再作为生产 public surface 存在。
- `Capability compat public name` 已在 Phase 12 关闭：`DeviceCapabilities` 与 `custom_components/lipro/core/device/capabilities.py` 已删除。
- `Domain dynamic delegation` 已在 Phase 13 关闭：`LiproDevice.__getattr__` / `DeviceState.__getattr__` 已移除，`custom_components/lipro/core/device/device_delegation.py` 已删除。
- `Control-plane scatter` 已在 Phase 11 关闭：formal router、runtime locator 与 HA adapter 边界已固定，control plane 不再以散落 helper / wiring 叙事存在。
- `Legacy service wiring carrier` 已在 Phase 11 关闭：`custom_components/lipro/services/wiring.py` 已正式删除，control-plane formal router truth 收口到 `custom_components/lipro/control/service_router.py`。
- `Private runtime auth seam` 已在 Phase 5 关闭：`custom_components/lipro/services/execution.py` 只保留正式 service execution facade 身份，不再作为 active residual family。
- `API aggregate endpoint mixin` 已在 Phase 11 关闭：`custom_components/lipro/core/api/endpoints/__init__.py` 不再导出 `_ClientEndpointsMixin`，active residual 只剩 endpoint helper-class-level demixin cleanup。

- `API compat wrappers` 已在 Phase 17 关闭：`power_service.py` 与 outlet-power runtime/protocol formal path 只承认 explicit row/list contract，synthetic `{"data": rows}` envelope 已退场。

- `API mixin inheritance` 已在 Phase 17 关闭：`_ClientBase`、`_ClientPacingMixin`、`_ClientAuthRecoveryMixin`、`_ClientTransportMixin` 与 endpoint legacy mixin family 已完成 physical retirement 或 truthful demotion。

- `Split-root protocol surfaces` 已在 Phase 17 关闭：legacy `LiproMqttClient` naming 已退场，`MqttTransport` 仅保留为 localized concrete transport。

- `Auth/session compat projection` 已在 Phase 17 关闭：token persistence 只消费 `AuthSessionSnapshot`，`get_auth_data()` compat projection 已删除。

- `Protocol-boundary family coverage` 已在 Phase 20 关闭：`rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 现全部完成 registry-backed boundary formalization，不再保留为 active residual family。

- `Replay scenario coverage` 已在 Phase 21 关闭：remaining families 现已获得 explicit replay / evidence assurance coverage，不再保留 v1.1 de-scope carry-forward 叙事。

## Rules

- 新发现的 residual 必须登记，不能只在对话中提到。
- 每条 residual 至少要给出 **当前样本、owner、exit condition**，否则不算正式登记。
- 任何 residual 若进入第二个 phase 仍未收敛，必须解释为何继续存在。
- compat / mixin / legacy public-name residual 只允许存在于显式 compat shell / adapters 中，不得继续散落在正式 public surface 与业务逻辑内部。
- 本账本允许保留 legacy `Client` / `Mixin` / compat symbol 名称，但仅用于 archive / delete-gate / symbol-identity 说明；它们不得回流为当前架构术语。

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
- developer report 收集链已切到 exporter-only truth；legacy `build_developer_report()` compat / test seam 已移除。
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


## Phase 15 Residual Delta

- 本 phase **无新增 residual family**：收口的是既有 support/governance/tooling truth，而不是引入新的 compat 层。
- `_ClientBase` / helper mixin family 继续仅作为 `core/api` 本地 residual；`FILE_MATRIX` 与 `PUBLIC_SURFACES` 已显式写明 locality / ownership。
- `LiproMqttClient` direct-transport residual 已完成 physical rename closeout；`core/mqtt/transport.py` + package no-export 现为唯一有效故事。
- `coverage_diff.py`、benchmark baseline/threshold lane 与 dev `pip-audit` 现已被裁决为明确工具语义 / governed quality policy，而不是 residual family。

## Phase 16 Residual Delta

- `custom_components/lipro/services/execution.py` 的 coordinator 私有 auth seam 继续保持关闭；Phase 16 只允许把它记为正式 service execution facade，而不是 active residual / kill target。
- 本 phase 完成 second-pass audit 后，remaining residual inventory 仍集中在 `_ClientBase` / helper mixin typing spine、`LiproMqttClient` legacy naming、`get_auth_data()` fallback 与 helper-level compatibility envelope；不再允许无 owner / 无 delete gate / 无 evidence 的 silent carry-forward。
- Final closeout audit (`2026-03-15`) recorded `Any=711`、`except Exception=36`、`type: ignore=12`、dead pytest markers `=0`；remaining hits均落在既有 owner / delete gate 约束内，没有新的无主高风险残留。

| Item | Disposition | Owner | Phase | Delete gate | Evidence |
|------|-------------|-------|-------|-------------|----------|
| `_ClientBase` / `_Client*Mixin` typing spine | 保留为本地 residual | `core/api` | Phase 16 closeout | 当 helper consumers 全部收敛到显式 typed helpers，且不再存在 legacy mixin import 需求时删除 | `custom_components/lipro/core/api/session_state.py`, `.planning/reviews/KILL_LIST.md`, `.planning/baseline/PUBLIC_SURFACES.md` |
| `LiproMqttClient` legacy transport name | 保留为局部 legacy naming residual | `core/mqtt` | Phase 16 closeout | 当 transport-facing tests / imports 不再需要 concrete transport legacy name 时重命名/退场 | `custom_components/lipro/core/mqtt/transport.py`, `.planning/reviews/KILL_LIST.md` |
| `get_auth_data()` fallback in `persist_entry_tokens_if_changed()` | 保留为狭义 compatibility fallback | `entry_auth` | Phase 16 closeout | 当所有调用者 / test doubles 都以 `AuthSessionSnapshot` 为唯一正式契约时删除 | `custom_components/lipro/entry_auth.py`, `tests/core/test_init.py` |
| helper-level compatibility envelope (`power_service.py`) | 保留为低风险 helper-level compatibility | `core/api` | Phase 16 closeout | 当 power payload shape 只剩单一正式 contract，且 outlet-power callers 不再需要旧 shape 容忍时删除 | `custom_components/lipro/core/api/power_service.py`, `custom_components/lipro/core/coordinator/outlet_power.py` |


## Phase 17 Residual Delta

- `_ClientBase` / `_ClientPacingMixin` / `_ClientAuthRecoveryMixin` / `_ClientTransportMixin` 与 endpoint legacy mixin family 已完成 final disposition：production truth 不再把它们当作合法 skeleton / compat spine。
- `MqttTransport` 现为唯一 canonical concrete transport naming；legacy `LiproMqttClient` naming 已退出治理真源、package export 与 production/test mainline。
- `get_auth_data()` compat projection 与 helper-level outlet-power synthetic wrapper 已物理退场；`AuthSessionSnapshot` 与 explicit `OutletPowerInfoRow | list[OutletPowerInfoRow]` 成为唯一正式 typed contract。
- v1.1 remaining active residual 现只保留明确 de-scope / out-of-scope debt：external-boundary advisory naming、boundary family coverage 与 representative replay coverage。

## Phase 18 Residual Delta

- `custom_components/lipro/core/auth/bootstrap.py` 现为正式 host-neutral auth/bootstrap helper home；`config_flow.py` 与 `entry_auth.py` 只复用它装配 protocol/auth collaborators，没有引入新的 control/protocol root。
- `custom_components/lipro/helpers/platform.py` 现为唯一 HA platform projection home；`const/categories.py`、`CapabilitySnapshot`、`CapabilityRegistry`、`LiproDevice` 与 `device_views` 已不再把 HA platform strings 当成 domain truth。
- `ConfigEntryLoginProjection` 明确降格为 HA adapter projection，而不是新的 auth/session truth；`AuthSessionSnapshot` 继续是唯一正式 contract。
- 本 phase **无新增 active residual family / compat shell / file-level kill target**；新增的是更窄的 locality 守卫与 targeted bans，用来阻断旧 projection token 回流。

## Phase 19 Residual Delta

- `custom_components/lipro/headless/boot.py` 与 `tests/harness/headless_consumer.py` 只属于 local proof seam / assurance consumer；它们消费 formal truth，但不构成新的 protocol root、runtime root 或 authority family。
- `config_flow.py` 与 `entry_auth.py` 已统一 inward 到 shared headless boot seam；HA-specific projection、exception mapping 与 token persistence 继续留在 adapter shell，没有回灌到 nucleus。
- `helpers/platform.py` 与各平台 `async_setup_entry()` 现在显式收敛到 thin headless setup shell；`control/runtime_access.py` 仍是 control-plane locator，而不是 platform bridge。
- 本 phase **无新增 active residual family / compat shell / authority no-change exception**；新增的是 second-root / backflow 守卫与 proof-only identity wording。

## Phase 20 Residual Delta

- `Protocol-boundary family coverage` 已完成 closeout：`rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 均已进入正式 boundary family / authority / fixture / guard 主链。
- governance / inventory 真源现已明确：remaining families 只能沿既有 boundary / replay authority chain 收口，不得继续描述为 helper implicit behavior 或 v1.1 de-scope folklore。
- 本 phase 关闭的是 boundary-family formalization residual；显式 replay assurance closeout 继续由 `Phase 21` 收官。

## Phase 21 Residual Delta

- `Replay scenario coverage` 已完成 closeout：remaining families 现已在 replay report、evidence pack 与 integration/meta guards 中获得显式 assurance coverage，不再保留为 active residual family。
- failure taxonomy contract 已冻结到 shared telemetry truth；remaining `except Exception` 数量被转入 repo-wide audit metric 与 future sustainment backlog，而不是继续以未仲裁 residual family 存在。
- 本 phase **无新增 compat shell / authority drift**；收口的是 failure classification 语言与关键 catch-all arbitration seam。

## Phase 22 Residual Delta

- `Observability consumer convergence` residual 已进一步收口：diagnostics / system health / developer / support / evidence consumers 现在共同暴露共享 `failure_summary` vocabulary，raw transport / API error fields 仅保留为 debug detail。
- developer report consumer 已完全回归 exporter-backed truth；`build_developer_report()` compat / test seam 已物理退场，不再保留第二入口。
- 本 phase **无新增 compat shell**；`failure_summary` contract 继续 pull exporter / service truth，后续 docs / release 只允许消费这些结果，不能再平行讲述第二套失败语义。

## Phase 23 Residual Delta

- contributor docs / templates / runbook / evidence index 现已统一消费 baseline / review / milestone truth；本 phase **无新增 active residual family**。
- `failure_summary` / `failure_entries` 提示已进入 support / troubleshooting / bug-report 路径，但这些公开入口只消费 shared contract，不新增第二套 consumer vocabulary。
- workflow narrative 维持 **no-change**：release 继续复用 `ci.yml` gate，`V1_2_EVIDENCE_INDEX.md` 只作为 pull-only evidence pointer，而不是新的 authority chain。
- `custom_components/lipro/core/coordinator/coordinator.py` 与 `custom_components/lipro/core/api/client.py` 已完成本轮第一刀减重 / 边界澄清，但更深拆分仍登记为 post-closeout follow-up，不再默认为 silent debt。

## Phase 24 Final Audit Disposition

- final repo audit (`2026-03-16`) 将 repo-wide metrics 记为：`Any=614`、`except Exception=36`、`type: ignore=12`；它们已被明确定性为 future sustainment backlog / distributed tech debt，而不是 silent defer。
- 当前已无 active residual family；remaining boundary/replay coverage、observability convergence 与 external-boundary naming residual 均已完成 closeout，不再悬空。
- `v1.2` closeout 现达到 archive-ready / handoff-ready：residual disposition、milestone audit、evidence index 与 handoff assets 已讲同一条最终故事线。


## Phase 38 Residual Delta

- `External-boundary advisory naming` 已关闭：firmware authority truth 现明确为 bundled local trust-root asset + remote advisory payload；历史文件名保留，但 active residual family 已清零。

## Phase 25.2 Residual Delta

- `coordinator.client` telemetry ghost seam 已关闭：`custom_components/lipro/control/telemetry_surface.py` 只再 pull `Coordinator.protocol` formal surface，不再把 legacy alias 合法化为 observer bridge 输入。
- touched `.planning/codebase/STRUCTURE.md` 已同步这一事实，但 derived map 身份保持不变；authority 仍以 north-star / baseline / review / active truth 为准。
- 本 phase **无新增 active residual family / compat shell / second-root story**；关闭的是 formal-surface honesty seam，而不是重做 telemetry schema。


## Phase 27 Residual Delta

- `Coordinator` 顶层 schedule / diagnostics / OTA / outlet-power pure forwarder cluster 已退场：external consumers 现在只 pull `coordinator.protocol_service`，不再把 runtime root 混成 protocol passthrough façade。
- runtime 正式代码中的 `Phase C` / `Phase H4` 历史叙事已清理；关闭的是 narration seam，而不是引入新的 abstraction layer。
- 本 phase **无新增 compat shell / second-root story / active residual family**；remaining `LiproRestFacade` hotspot 仍被诚实记录为 child-façade maintainability debt，但它不是新的 public root，也不允许反向定义 runtime truth。


## Phase 35 Residual Delta

- `client.py` 已收窄为 stable import home，`rest_facade.py` / `request_gateway.py` / `transport_executor.py` / `endpoint_surface.py` / `rest_port.py` 与 `mqtt_facade.py` 继续承接内部复杂度；它们都没有升级成新的 public root 或 compat shell。
- `LiproRestFacade` / `LiproProtocolFacade` 仍保留为 formal child/root story；remaining residual 仅是后续可继续优化的 body-size maintainability debt，不再是 public-surface honesty seam。
- 本 phase **无新增 active residual family / second-root story / export growth**；关闭的是 protocol hotspot ballast 与 endpoint-operation glue 漂浮。

## Phase 36 Residual Delta

- `Coordinator` 仍保留少量 root-owned orchestration 与 sanctioned broad-catch budget，但 polling/status/outlet/snapshot cluster 已正式下沉到 `CoordinatorPollingService`，runtime root ballast 明显下降。
- `snapshot.py`、`device_runtime.py`、`mqtt_runtime.py`、`mqtt_lifecycle.py` 与 `command_service.py` 的主链宽异常已收口到 typed arbitration / fail-closed path；remaining budget 只保留 machine-guarded sanctioned points。
- 本 phase **无新增 runtime bypass seam / second manager/root**；关闭的是 broad-catch 灰区与 coordinator polling hotspot。

## Phase 37 Residual Delta

- init/service-handler/runtime/governance phase-history 巨石测试已拆成稳定 topic suites；保留的聚合文件只承担 shared helper / topic root 身份，不再吸附所有子故事线。
- `.planning/codebase/*` 与 verification/testing guidance 已重新同步到真实拓扑；remaining residual 只是不时需要跟随新增测试文件刷新 derived maps，而不是 authority drift。
- 本 phase **无新增 active residual family**；关闭的是 test-topology drift、旧单文件锚点与高噪音 prose-coupled closeout 断言。

## Phase 39 Residual Delta

- `custom_components/lipro/core/protocol/compat.py` dead shell 已物理删除；Phase 39 不再保留任何“空 compat 壳也算合法存在”的 folklore。
- `get_device_list.envelope.json` 现被固定为唯一 authority asset；相关 replay manifests、tests、readmes 与 guards 已完成单命名收口，不再存在 compat / wrapped / envelope 并行叙事。
- `custom_components/lipro/control/` 已在 north-star、developer docs、review ledgers 与治理守卫中被统一确认为 formal control-plane home；`custom_components/lipro/services/` 只再承担 service declarations / adapters / helpers 身份。
- governance current-story placeholder 已关闭：`v1.4` 已完成 milestone archive promotion，`Phase 39 complete` 作为 historical closeout evidence 保留，本 phase **无新增 active residual family**。


## Phase 40 Residual Delta

- `custom_components/lipro/services/execution.py` 继续明确保持为 formal service execution facade；`schedule.py` 现已复用 shared executor，不再维护局部 auth/error chain，也不会回流为 active residual / kill target。
- `custom_components/lipro/core/api/endpoint_surface.py` 与 `rest_facade_endpoint_methods.py` 的 touched 语义继续收口到 endpoint operations / façade wording；历史 `forwarding` 只保留在归档语境，不再作为当前架构口径。
- 本 phase **无新增 active residual family / compat shell / second-root story**；关闭的是 governance truth layering、runtime read-model 散点与 schedule execution duplication。

## Phase 43 Residual Delta

- `custom_components/lipro/control/runtime_access.py` 现已承接 typed diagnostics/system-health projection；`diagnostics_surface.py` 不再混搭 coordinator internals 与 ad-hoc runtime mapping 读取。
- `custom_components/lipro/runtime_infra.py` 现已收回 device-registry listener / pending reload task ownership；`services/maintenance.py` 只保留 `refresh_devices` thin adapter。
- `custom_components/lipro/services/device_lookup.py` 已降为 service-facing device-id resolver；`control/service_router_support.py` 成为最终 `(device, coordinator)` bridge。本 phase **无新增 active residual family / second control root**；关闭的是 helper-owned runtime truth 与 listener ownership 混淆。

## Phase 44 Residual Delta

- legacy `Client` / `Mixin` / `forwarding` symbol 名称现已被明确隔离到 residual / archive 语境；active ADR、baseline 与 docs index 统一改讲 `protocol` / `façade` / `operations` 语言。
- contributor fast-path、maintainer appendix 与 bilingual boundary 现已在 `README.md` / `README_zh.md`、`CONTRIBUTING.md`、`docs/README.md`、`SUPPORT.md`、`SECURITY.md` 与 PR template 中显式分层；维护者 continuity 真相继续保留在深层附录，不再压回根入口。
- 本 phase **无新增 active residual family / compat shell / future kill target**；收口的是 governance 噪音、术语漂移与入口边界，而不是新增 delete campaign。

## Phase 45 Residual Delta

- `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py` 已沿 localized helper seams 继续瘦身；`rest_decoder.py` 现拥有 schedule/MQTT endpoint-scoped decode logic，但 formal decoder boundary 与 public surface 未扩张。
- diagnostics/share/message touched-zone 现已共享 typed `OperationOutcome` / reason-code 语义；旧 bool wrappers 只保留为兼容薄壳，不再代表 active truth。
- benchmark lane 现已拥有 baseline manifest 与 threshold semantics，同时继续保持 `schedule` / `workflow_dispatch` maintainer-facing 边界；本 phase **无新增 active residual family / second governance story**。


## Phase 47 Residual Delta

- 本轮 **无新增 active residual family**；关闭的是 docs/tooling discoverability 与 release-signature identity 过宽 contract，而不是开启新的架构故事线。
- `scripts/agent_worker.py` 与 `scripts/orchestrator.py` 仍保留为 explicit retired compatibility stubs，但它们现在只是 fail-fast deprecation entry，不再伪装成可继续成功执行的 active tooling。
- runtime hotspot、mega-test topicization 与 REST typed-surface debt 仍已诚实路由到 `Phase 48 -> 50`，不作为 silent defer 继续漂浮。

## Phase 52 Residual Delta

- `LiproProtocolFacade` 仍是唯一 formal protocol root；`protocol_facade_rest_methods.py`、`rest_port.py` 与 `mqtt_facade.py` 只是在统一主线下继续 inward slimming，没有新增 second-root residual。
- `RequestPolicy` / `RestRequestGateway` / `RestTransportExecutor` 的 ownership 现已被代码、guards 与 baseline truth 对齐：busy / pacing / 429 决策回到 policy home，mapping/auth-aware retry-context orchestration 留在 gateway，executor 只再承担 transport execution。
- 本 phase 新增的是对 `compute_exponential_retry_wait_time()` cross-plane leak 的显式登记：它从 silent defer 变成可审计 deferred residual；后续若继续清理，只能迁往更诚实的 shared backoff home，而不是把 `request_policy.py` 再讲成跨平面 utility root。



## Phase 58 Status Update

- 本 phase **无新增 active residual family**；它刷新的是 repo-wide verdict 与 route truth，而不是新开 residual campaign。
- refreshed audit 明确认可：active residual ledger 当前仍为空；后续 follow-up 主要是 maintainability precision，而不是历史错根回潮。
- `58-REMEDIATION-ROADMAP.md` 现承担 `Phase 59+` route seed 身份；它不是 archive artifact，也不是新的 baseline root。
