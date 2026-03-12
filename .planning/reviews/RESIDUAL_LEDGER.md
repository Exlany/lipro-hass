# Residual Ledger

## Active Residual Families

| Family | Current example | Owner phase | Residual owner | Exit condition |
|--------|------------------|-------------|----------------|----------------|
| API compat wrappers | `custom_components/lipro/core/api/client.py` 中 `_build_compat_list_payload`、`get_device_list`、`query_iot_devices`、`query_outlet_devices`、`query_group_devices`，以及 `power_service.py` 的多行 `{"data": ...}` shaping | Phase 2 | `02-04 compat shell cleanup`（API/Protocol owner 主责，Runtime/Coordinator owner 迁移消费者） | `LiproRestFacade` canonical outputs 被 direct consumers 接受，compat wrappers 从 `LiproClient` / helper 层移除 |
| API mixin inheritance | `_ClientBase` temporary typing anchor、`_ClientPacingMixin` / `_ClientAuthRecoveryMixin` / `_ClientTransportMixin` compat shells、`_ClientEndpointsMixin` 与 endpoint mixin helper classes | Phase 2 | `02-04 demixin closeout handoff`（API owner 主责，Phase 2.5/6 继续清退） | 生产路径已脱离 mixin 根；剩余 mixin 仅限 helper-test / patch seam / typing 过渡角色，并在后续相位被删除 |
| Legacy public names | `custom_components.lipro.core.api.LiproClient`、`.core.LiproClient` 及 entry/config-flow/runtime 邻接 seam 中的 legacy constructor name | Phase 2 | `02-04 public-surface demotion`（API owner 收口；Entry/Auth owner 与 Runtime owner 迁移下游） | 内部类型与正式 public-root 叙事切到 `LiproRestFacade`；`LiproClient` 仅剩可删除 compat shell / factory alias |
| Split-root protocol surfaces | `LiproRestFacade` / `LiproMqttClient` 并行作为 runtime-facing protocol entry 的剩余认知，以及 `core/mqtt/__init__.py` 的旧导出方向 | Phase 2.5 | `02.5 unified protocol root closeout`（Protocol owner 主责，Runtime owner 配合迁移） | runtime-facing allowed consumers 只依赖 `LiproProtocolFacade`；child façade / compat shell 不再被当作正式 public root |
| Control-plane scatter | diagnostics / system_health / service wiring 分散 | Phase 3 | `Phase 3 control-plane closeout` | control plane public surface 收口 |
| Capability duplication | domain / entity / platform 多处表达 | Phase 4 | `Phase 4 capability registry closeout` | capability registry 成为单一真源 |
| Capability compat public name | `custom_components/lipro/core/device/capabilities.py` 继续提供 `DeviceCapabilities` 旧导入名 | Phase 4 | `04-03 capability compat cleanup` | 直接消费者改用 `CapabilitySnapshot` / `CapabilityRegistry`，旧 public name 不再必要 |
| External-boundary advisory naming | firmware remote advisory / support payload generated field naming 仍带 legacy semantics | Phase 2.6 | `02.6 external-boundary closeout` | authority truth 已固定后完成术语清理 |
| Legacy service wiring carrier | `custom_components/lipro/services/wiring.py` 仍承载部分实现闭包 | Phase 3 | `Phase 7 cleanup sweep` | `control.service_router` 完全接管且测试 patch seam 不再依赖 wiring carrier |
| Private runtime auth seam | `custom_components/lipro/services/execution.py` 仍存在 coordinator 私有 auth hook seam | Phase 3 / 5 | `Phase 5 runtime hardening` | 正式 runtime/auth contract 提供可替代 public surface |

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
- 新增 `Private runtime auth seam` residual family，显式登记 `custom_components/lipro/services/execution.py` 对 coordinator 私有 auth hook 的过渡依赖。


## Phase 04 / `04-01` Residual Delta

- `Capability duplication` residual 已从“没有正式 root”收敛到“已有正式 root，但仍有旧 consumer / helper 未迁移”的状态。
- `DeviceCapabilities` 已降级为显式 compat bridge；其继续存在的理由是保持 `core/device` 旧导入面稳定，删除动作后移到 `04-03 / Phase 7`。
- `state_accessors.supports_color_temp`、平台/实体投影判断与 helper 影子规则仍待 `04-02 / 04-03` 继续清退。
