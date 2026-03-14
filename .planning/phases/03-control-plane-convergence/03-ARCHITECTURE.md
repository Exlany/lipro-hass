# Phase 03 Architecture: Control Plane North-Star Convergence Design

## Objective

把当前散落在 integration 根模块、flow helpers、service wiring、diagnostics/system health 中的控制逻辑，重建为**单一正式 control plane**：

- Home Assistant 规定的根模块继续存在，但只作为 adapter shell
- 内部正式组件集中到 control-plane 命名化结构
- control → runtime 通过稳定 access contracts / read models 访问
- tests 围绕正式 public surfaces 与 redaction / lifecycle contracts 建立

Phase 3 的判断标准不是“入口还能不能跑”，而是：
- 正式 control components 是否清晰
- runtime 接缝是否稳定、显式、可测
- service / diagnostics / system health 是否共享统一控制面叙事
- 全仓治理资产是否与新边界同步收敛

## Preconditions

Phase 3 的 target architecture 只有在以下条件成立时才可执行：

- `Phase 2.6` 已完成并产出 `inventory / authority / fixtures / validation / summaries` 等可引用 outputs
- `Phase 1 / 1.5` 已完成 contract baseline 与 baseline asset pack 的收尾，避免 control plane 建立在未冻结的 truth 上
- `Phase 2 / 2.5` 已把协议根与 normalized contracts 锁定，确保 control plane 不会反向定义 protocol shape

未满足以上条件时，Phase 3 只能用于 design arbitration，不应直接进入执行。

## Current Structural Problem

当前控制面大致是以下散点协作：

- `custom_components/lipro/__init__.py` 负责 setup / unload / service sync / runtime cleanup
- `custom_components/lipro/config_flow.py` 与 `flow/**` 负责用户接入、reauth、options
- `custom_components/lipro/services/wiring.py` 充当事实上的 service root
- `custom_components/lipro/diagnostics.py` 与 `system_health.py` 各自直接读取 runtime internals
- `entry_auth.py`、`entry_options.py`、`runtime_infra.py`、`domain_data.py`、`coordinator_entry.py` 已有局部分工，但没有单一 owner 将它们组织成正式控制面

这导致：

1. **正式边界不存在**：控制面没有一个能被命名、被测试、被治理的 root 叙事
2. **热点文件过载**：`services/wiring.py` 承担过多职责，成为事实 mega-root
3. **runtime backdoor 普遍存在**：support surface 直接读取 `runtime_data` / `coordinator.devices` / `mqtt_service.connected`
4. **测试冻结旧结构**：部分 tests 仍围绕私有 handler 或内部字段断言
5. **治理口径易漂移**：如果不同时更新 governance assets，就会形成“代码与规划两套世界”

## Target Topology

### External HA Adapters

以下文件由于 Home Assistant 约束必须保留在 integration 根：

- `custom_components/lipro/__init__.py`
- `custom_components/lipro/config_flow.py`
- `custom_components/lipro/diagnostics.py`
- `custom_components/lipro/system_health.py`

但它们在终态中只承担：
- HA required signatures
- 参数校验 / minimal routing
- 把调用委托给内部正式组件

### Internal Control Home

推荐建立单一内部控制面 home，例如：

- `custom_components/lipro/control/entry_lifecycle_controller.py`
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/service_registry.py`
- `custom_components/lipro/control/service_router.py`
- `custom_components/lipro/control/diagnostics_surface.py`
- `custom_components/lipro/control/system_health_surface.py`
- `custom_components/lipro/control/redaction.py`
- `custom_components/lipro/control/models.py`

> 具体文件名可调整，但“HA 根模块薄壳 + 内部 control package 正式承载逻辑”是锁定设计。

## Target Components

### 1. `EntryLifecycleController`

**Owns**:
- setup / unload / reload / reauth / options 的正式 lifecycle story
- `entry_auth.py`、`entry_options.py`、`runtime_infra.py`、`domain_data.py`、`coordinator_entry.py` 的协调装配
- service registry 与 runtime cleanup 的生命周期挂钩

**Must not own**:
- 具体 service handler 业务逻辑
- diagnostics payload 构建细节
- runtime plane 内部编排语义

### 2. `ServiceRegistry`

**Owns**:
- service declarations、注册、撤销、developer/debug gating、runtime resolution、error wrapping 的正式边界
- `contracts.py + registrations.py + registry.py` 的权威整合
- service public surface 的唯一 owner

**Must not own**:
- coordinator 细节暴露
- diagnostics / system health 聚合
- 第二套 debug gating 逻辑

### 3. `DiagnosticsSurface`

**Owns**:
- config entry diagnostics、device diagnostics、support payload aggregation
- 脱敏规则应用与 support read models
- 对 runtime 状态的只读消费

**Must not own**:
- runtime lifecycle
- service registration
- 原始 coordinator 内部字段知识的扩散

### 4. `SystemHealthSurface`

**Owns**:
- 健康度聚合、entry 级汇总、依赖可用性探针
- 高层 health payload 输出

**Must not own**:
- diagnostics payload 构建
- 设备领域规则解释
- runtime internals 的直接读取

### 5. Control → Runtime Access Contracts

Phase 3 不最终定义整个 runtime plane 的 canonical public surface，但必须在控制面侧建立稳定接缝，例如：

- lifecycle 用的 runtime setup / unload adapter
- services 用的 runtime resolver / execution accessor
- diagnostics / system health 用的 read models / runtime canonical-state projections

**约束**：
- 控制面只通过这些 contracts 与 runtime 交互
- `entry.runtime_data` 只能由 access layer 内部读取，不能继续在多处散落直连
- runtime plane 的更深层 public surface 统一化留给 Phase 5

**Allowed operations**：
- 读取 entry 级 runtime summary、设备计数、连接状态、health probes
- 解析 service execution 所需的 runtime resolver / accessor
- 调用 lifecycle 所需的 setup / unload / cleanup hooks

**Forbidden operations**：
- 直接写入 coordinator 内部状态或设备领域状态
- 直接消费 raw protocol payload 或 external-boundary 原始结构
- 在 control plane 内裁决 capability truth、平台规则或 runtime 编排策略
- 在 access layer 外部直接读取 `entry.runtime_data`、`coordinator.devices`、`mqtt_service.connected`

## Cross-Phase Guardrails

为保证 Phase 1 ~ 3 的叙事一致，本 phase 明确接受以下护栏：

- **Protocol truth 不在此 phase 改写**：Phase 1 已冻结最小高价值 contract baseline；Phase 3 只能把它视为上游事实。
- **Unified protocol root 不在此 phase 重做**：`LiproRestFacade / LiproProtocolFacade` 的正式协议根叙事由 Phase 2 / 2.5 负责。
- **External boundaries 不在此 phase 拍板**：`share / firmware / support payload / external endpoints` 的 owner、fixtures、authority source 由 Phase 2.6 负责；`DiagnosticsSurface` 只能消费其结果。
- **Capability truth 不在此 phase 旁生**：control-plane read models 只服务 diagnostics / health / services，不得形成平行 capability system。
- **Runtime final root 不在此 phase 双生**：control-owned runtime access contracts 是消费者边界，不是第二套 runtime public surface；Phase 5 仍是 runtime 正式 public surface 的唯一统一阶段。

## Canonical Public Surfaces

### HA-facing Public Surfaces
- `async_setup`
- `async_setup_entry`
- `async_unload_entry`
- `async_reload_entry`
- `ConfigFlow` / `OptionsFlow`
- `async_get_config_entry_diagnostics`
- `async_get_device_diagnostics`
- `async_register` / `system_health_info`
- Home Assistant service registration entry points

### Internal Formal Surfaces
- `EntryLifecycleController`
- `ServiceRegistry`
- `DiagnosticsSurface`
- `SystemHealthSurface`
- control-owned runtime access contracts

### Non-Canonical / To Be Removed
- `services/wiring.py` 继续充当事实根
- tests 直接导入 `_async_handle_*`
- support surface 直接读取 coordinator 内部字段
- 多处重复 debug gating / service registration policy

## File Treatment

### Keep as Thin Adapters
- `custom_components/lipro/__init__.py`
- `custom_components/lipro/config_flow.py`
- `custom_components/lipro/diagnostics.py`
- `custom_components/lipro/system_health.py`

### Refactor into Formal Components
- `custom_components/lipro/entry_auth.py`
- `custom_components/lipro/entry_options.py`
- `custom_components/lipro/runtime_infra.py`
- `custom_components/lipro/domain_data.py`
- `custom_components/lipro/coordinator_entry.py`
- `custom_components/lipro/services/contracts.py`
- `custom_components/lipro/services/registry.py`
- `custom_components/lipro/services/registrations.py`
- `custom_components/lipro/services/execution.py`
- `custom_components/lipro/services/device_lookup.py`
- `custom_components/lipro/services/errors.py`
- `custom_components/lipro/services/command.py`
- `custom_components/lipro/services/schedule.py`
- `custom_components/lipro/services/share.py`
- `custom_components/lipro/services/maintenance.py`

### Break Apart / Demote / Delete Path
- `custom_components/lipro/services/wiring.py`
- `custom_components/lipro/services/diagnostics/__init__.py`（若只是 re-export / compat shell，则纳入删除路径）
- 任何继续暴露旧控制面 public name 的 compat wrappers

### Review with Control-Plane Lens
- `tests/flows/*.py`
- `tests/services/*.py`
- `tests/core/test_init.py`
- `tests/core/test_entry_update_listener.py`
- `tests/core/test_token_persistence.py`
- `tests/core/test_diagnostics.py`
- `tests/core/test_system_health.py`
- `tests/core/coordinator/services/*.py`

## Execution Shape

### Plan 03-01
- 冻结 control contracts、public surfaces、dependency edges 与全仓 control-plane governance matrix
- 提炼 `EntryLifecycleController`
- 让根 lifecycle adapter 开始变薄

### Plan 03-02
- 收口 `ServiceRegistry`
- 拆解 `services/wiring.py`
- 正式化 `DiagnosticsSurface / SystemHealthSurface` 与 runtime read models

### Plan 03-03
- 补齐 flow / lifecycle / services / diagnostics / system health / redaction tests
- 清退控制面旧 public names、私有测试耦合与残留导入
- 完成 Phase 3 governance closeout 与 handoff

## Evolution Path

- **Phase 2 / 2.5**：协议平面已先定义正式根，不再由 control plane 反向裁决协议结构
- **Phase 3**：形成正式 control plane 与稳定 runtime 接缝
- **Phase 4**：领域能力真源与平台/实体消费统一
- **Phase 5**：runtime plane 正式 public surface 与 invariants 最终化
- **Phase 6**：architecture guards / observability / CI enforcement
- **Phase 7**：compat / shadow / archive / dead code 最终清零
