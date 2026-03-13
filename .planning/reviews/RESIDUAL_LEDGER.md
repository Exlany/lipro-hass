# Residual Ledger

## Active Residual Families

| Family | Current example | Owner phase | Residual owner | Exit condition |
|--------|------------------|-------------|----------------|----------------|
| API compat wrappers | `custom_components/lipro/core/api/client.py` 中 `_build_compat_list_payload`、`get_device_list`、`query_iot_devices`、`query_outlet_devices`、`query_group_devices`，以及 `power_service.py` 的多行 `{"data": ...}` shaping | Phase 2 | `02-04 compat shell cleanup`（API/Protocol owner 主责，Runtime/Coordinator owner 迁移消费者） | `LiproRestFacade` canonical outputs 被 direct consumers 接受，compat wrappers 从 `LiproClient` / helper 层移除 |
| API mixin inheritance | `_ClientBase` temporary typing anchor、`_ClientPacingMixin` / `_ClientAuthRecoveryMixin` / `_ClientTransportMixin` compat shells、`_ClientEndpointsMixin` 与 endpoint mixin helper classes | Phase 2 | `02-04 demixin closeout handoff`（API owner 主责，Phase 2.5/6 继续清退） | 生产路径已脱离 mixin 根；剩余 mixin 仅限 helper-test / patch seam / typing 过渡角色，并在后续相位被删除 |
| Legacy public names | `custom_components.lipro.core.api.LiproClient`、`.core.LiproClient` 及 entry/config-flow/runtime 邻接 seam 中的 legacy constructor name | Phase 2 | `02-04 public-surface demotion`（API owner 收口；Entry/Auth owner 与 Runtime owner 迁移下游） | 内部类型与正式 public-root 叙事切到 `LiproRestFacade`；`LiproClient` 仅剩可删除 compat shell / factory alias |
| Split-root protocol surfaces | `LiproRestFacade` / `LiproMqttClient` 并行作为 runtime-facing protocol entry 的剩余认知，以及 `core/mqtt/__init__.py` 的旧导出方向 | Phase 2.5 | `02.5 unified protocol root closeout`（Protocol owner 主责，Runtime owner 配合迁移） | runtime-facing allowed consumers 只依赖 `LiproProtocolFacade`；child façade / compat shell 不再被当作正式 public root |
| Control-plane scatter | diagnostics / system_health / service wiring 分散 | Phase 3 | `Phase 3 control-plane closeout` | control plane public surface 收口 |
| Capability compat public name | `custom_components/lipro/core/device/capabilities.py` 继续提供 `DeviceCapabilities` 旧导入名 | Phase 4 | `04-03 capability compat cleanup` | 直接消费者改用 `CapabilitySnapshot` / `CapabilityRegistry`，旧 public name 不再必要 |
| External-boundary advisory naming | firmware remote advisory / support payload generated field naming 仍带 legacy semantics | Phase 2.6 | `02.6 external-boundary closeout` | authority truth 已固定后完成术语清理 |
| Legacy service wiring carrier | `custom_components/lipro/services/wiring.py` 仍承载部分实现闭包 | Phase 3 | `Phase 7 cleanup sweep` | `control.service_router` 完全接管且测试 patch seam 不再依赖 wiring carrier |
| Protocol-boundary family coverage | `rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 仍停留在 inventory / helper collaborator 层，尚未全部 registry-backed | Phase 7.1 | `07.1 boundary expansion handoff` | inventory 中登记的 family 全部完成 registry-backed 接线，或在 v1.1 closeout 中被明确裁决为 de-scope / retire |
| Replay scenario coverage | `tests/fixtures/protocol_replay/` 当前只正式保留 representative `rest.mqtt-config@v1` 与 `mqtt.properties@v1`；`rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 已在 `07.5` 被显式裁决为 v1.1 de-scope，而非隐式遗漏 | Phase 7.4 | `07.5 closeout arbitration` | 若未来确有 black-box replay 价值，必须以新 phase 重新登记 family、补 manifest/evidence；`08` 只消费现有 representative corpus 与 evidence index，不直接扩大 replay 范围 |

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
- 新增 `Legacy service wiring carrier` residual family，显式登记 `custom_components/lipro/services/wiring.py` 的删除条件。
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
