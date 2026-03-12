# Kill List

## Candidate Removals (Phase 02 Registered)

| Target | Current carrier | Owner | Earliest delete phase | Delete when | `02-01` status |
|--------|------------------|-------|-----------------------|-------------|----------------|
| `_ClientBase` | `custom_components/lipro/core/api/client_base.py` | `02-02 façade + transport rewrite` | Phase 2 | 生产与测试都不再需要 mixin typing spine | 已登记，未删除 |
| `_ClientPacingMixin` | `custom_components/lipro/core/api/client_pacing.py` | `02-02 façade + transport rewrite` | Phase 2 | pacing / busy-retry 状态归入 `RequestPolicy` / transport chain，测试不再实例化 mixin host | 已登记，未删除 |
| `_ClientAuthRecoveryMixin` | `custom_components/lipro/core/api/client_auth_recovery.py` | `02-02 façade + transport rewrite` | Phase 2 | auth classification / refresh / replay 迁入 `AuthRecoveryCoordinator`，私有路径不再被 patch | 已登记，未删除 |
| `_ClientTransportMixin` | `custom_components/lipro/core/api/client_transport.py` | `02-02 façade + transport rewrite` | Phase 2 | transport 入口完全改为 `TransportExecutor` + `TransportCore` 显式组合 | 已登记，未删除 |
| `_ClientEndpointsMixin` | `custom_components/lipro/core/api/endpoints/__init__.py` | `02-03 endpoint collaborator migration` | Phase 2 | façade 只装配显式 endpoint collaborators，不再继承聚合 mixin | 已登记，未删除 |
| legacy endpoint mixin classes | `custom_components/lipro/core/api/endpoints/{auth,commands,devices,misc,payloads,schedule,status}.py` | `02-03 endpoint collaborator migration` | Phase 2 | 各 endpoint / payload helper 已迁成 explicit collaborators / normalizers | 已登记，未删除 |
| `_build_compat_list_payload` | `custom_components/lipro/core/api/client.py` | `02-04 compat shell cleanup` | Phase 2 | direct consumers 不再要求 `{"data": [...]}` envelope | 已登记，未删除 |
| legacy compat wrapper methods | `custom_components/lipro/core/api/client.py::{get_device_list,query_iot_devices,query_outlet_devices,query_group_devices}` | `02-04 compat shell cleanup` | Phase 2 | runtime / tests 改用 canonical façade outputs 或统一 compat adapter |
| `LiproClient` 作为正式 REST root name | `custom_components/lipro/core/api/__init__.py` 及其再导出链 | `02-04 public-surface demotion`（与 Phase 2.5 handoff 对齐） | Phase 2.5+ | `PUBLIC_SURFACES.md`、downstream imports 与 direct consumer tests 已切换到 `LiproRestFacade` / unified protocol surface | 已登记，未删除 |
| `LiproMqttClient` 作为正式 MQTT root name | `custom_components/lipro/core/mqtt/__init__.py` 及其再导出链 | `02.5 unified-root closeout` | Phase 2.5 | `LiproMqttFacade` 成为正式 child façade，runtime-facing consumers 改面向 `LiproProtocolFacade` | 已登记，未删除 |
| split-root protocol public semantics | runtime / tests 中并行感知 `LiproRestFacade` 与 `LiproMqttClient` 的入口语义 | `02.5 unified-root closeout` | Phase 2.5 | `PUBLIC_SURFACES.md` 与 runtime-facing consumers 只承认 `LiproProtocolFacade` 为正式协议根 | 已登记，未删除 |
| 多行 power payload 的 compat wrapping | `custom_components/lipro/core/api/power_service.py` | `02-04 compat shell cleanup` | Phase 2 | power helper 只返回 canonical rows；兼容 envelope 仅存在于 compat shell | 已登记，未删除 |
| `services/wiring.py` 作为正式控制面根 | `custom_components/lipro/services/wiring.py` | `03 service-router convergence` | Phase 7 | `control.service_router` 及相关 tests/patch seams 全面接管，不再需要 legacy implementation carrier | 已登记，未删除 |
| coordinator 私有 auth hook seam | `custom_components/lipro/services/execution.py` | `03/05 runtime-auth hardening` | Phase 5 / 7 | service execution 只通过正式 runtime/auth contract 获取 auth context | 已登记，未删除 |
| `DeviceCapabilities` legacy public name | `custom_components/lipro/core/device/capabilities.py` | `04-03 capability compat cleanup` | Phase 4 / 7 | 直接导入点已迁到 `custom_components/lipro/core/capability`，device facade 不再依赖 legacy alias | 已登记，未删除 |

## Deletion Gate

删除前必须满足：
1. 下游消费者已迁移。
2. contract / regression tests 通过。
3. residual ledger 已关闭对应条目。
4. summary 明确记录是“正式删除”还是“仅登记、不删除”。

## Phase 01 Closeout Review

- 已检查 kill list 与 Phase 01 baseline 产物的关系，本次**无新增删除项**。
- `_Client*Mixin` 与 compat wrappers 仍是后续 Phase 2 的主要清理对象；Phase 01 只补足它们必须遵守的 contract baseline。
- canonical snapshots、immutable constraints 与 phase summaries 属于治理资产，不进入删除候选。

## Phase 02 / `02-01` Registration Note

- 本计划只做 kill candidate 登记与删除门槛澄清，不执行任何生产代码删除。
- mixin inheritance、compat wrappers、legacy public names 已从“口头债务”升级为文件级 kill targets。
- 若后续 `02-02` ~ `02-04` 没有实际删除动作，summary 必须说明仍阻塞于哪个 direct consumer / public surface。


## Phase 02 / `02-04` Status Update

- `_ClientEndpointsMixin` 与 legacy endpoint mixin classes 已退出生产 façade 根，现仅剩 narrow compat / helper-test 角色；删除门槛后移到 direct helper consumers 清零时。
- `_ClientBase`、`_ClientAuthRecoveryMixin`、`_ClientTransportMixin` 不再按整文件删除理解；需要删除的是残余 compat spine，同时保留 `ClientSessionState` / `AuthRecoveryCoordinator` / `TransportExecutor` 等正式组件。
- `LiproClient` 已完成 formal-root demotion，但 top-level factory / flow seam 仍保留过渡存在；删除动作交由 `Phase 2.5+` 随 unified root 继续推进。

## Phase 02.5 / `02.5-01` Registration Note

- 已把 `LiproMqttClient` formal-root 语义与 split-root protocol public semantics 升格为 file-level kill targets。
- `Phase 2.5` 的删除目标不是盲删 MQTT helpers，而是删除“两个正式协议根并存”的语义。

## Phase 02.5 / `02.5-02 ~ 02.5-03` Status Update

- `LiproMqttClient` 已完成 formal-root demotion：真实生产主链现在通过 `LiproMqttFacade` 作为 protocol child façade 接入，旧 concrete transport 只剩 compat/export 语义。
- split-root protocol public semantics 已从 runtime-facing production path 清退；剩余删除门槛集中在 `core/mqtt/__init__.py` 旧导出与 compat tests/aliases 的最终清零。
- `LiproClient` 仍保留显式 compat alias，但 `custom_components/lipro/__init__.py` / `config_flow.py` / coordinator MQTT path 已全部切到 `LiproProtocolFacade`。


## Phase 03 / `03-02 ~ 03-03` Status Update

- `custom_components/lipro/services/wiring.py` 已失去正式控制面根地位；当前保留仅为 legacy implementation carrier 与过渡 patch seam。
- `custom_components/lipro/services/execution.py` 尚未彻底摆脱 coordinator 私有 auth hook；该 seam 已升格为明确 kill target，而不是继续隐藏在 service folklore 中。
- `custom_components/lipro/diagnostics.py`、`system_health.py` 与 `__init__.py` 不再进入 kill list：它们保留为 HA adapter 薄层，终态角色已被明确保留。


## Phase 04 / `04-01` Registration Note

- 本轮不新增 file-level delete target；`04-01` 的目标是先建立正式 capability root，而不是提前盲删 domain helpers。
- `DeviceCapabilities` 已从 formal root 降级为 compat bridge，但尚未进入删除门槛满足态；真正删除判断留给 `04-03` 与 `Phase 7`。


## Phase 04 / `04-01` Status Update

- `custom_components/lipro/core/device/capabilities.py` 已被降级为显式 compat alias，不再承载真实 capability 推导。
- 新增 `DeviceCapabilities` legacy public name kill target，用于约束旧导入名的删除门槛。
- 真正的 capability duplicate-rule 删除仍留给 `04-02 / 04-03`。
