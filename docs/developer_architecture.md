# Lipro Home Assistant Integration - Developer Architecture

> **Last Updated**: 2026-03-15  \
> **Version**: 4.3 (Phase 17 closeout truth aligned)
>
> ⚠️ 本文档仅描述"当前收敛后的架构与模块边界"，不硬编码评分/覆盖率/通过率等易失真指标。  \
> 北极星终态裁决请见 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`。  \
> 当前阶段、需求、状态与治理真源请以 `.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`、`.planning/baseline/PUBLIC_SURFACES.md`、`.planning/baseline/ARCHITECTURE_POLICY.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md` 为准。  \
> `.planning/codebase/*.md` 只是 derived collaboration maps / 协作图谱：帮助维护者快速理解仓库，但不构成新的 authority chain。  \
> 历史审计/执行计划已从仓库中移除；当前以 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/*` 与 `AGENTS.md` 为准。

## 快速导航

| 模块 | 路径 | 说明 |
|------|------|------|
| 集成入口 | `__init__.py` | HA 集成注册 + 平台加载 |
| Coordinator | `core/coordinator/coordinator.py` | HA DataUpdateCoordinator 适配 |
| Orchestrator | `core/coordinator/orchestrator.py` | Runtime 组件装配（DI 布线） |
| RuntimeContext | `core/coordinator/runtime_context.py` | 统一依赖注入协议 |
| Runtime 组件 | `core/coordinator/runtime/` | 6 个可组合 Runtime |
| Service 层 | `core/coordinator/services/` | API 稳定边界层 |
| 数据容器 | `core/coordinator/factory.py` | CoordinatorRuntimes + StateContainers |
| 设备模型 | `core/device/device.py` | LiproDevice 薄 facade |
| API Client | `core/api/client.py` | REST API 客户端 |
| MQTT Client | `core/mqtt/mqtt_client.py` | MQTT 实时通信 |
| 实体基类 | `entities/base.py` | 防抖 + 乐观更新 + CoordinatorEntity |
| 描述符 | `entities/descriptors.py` | 声明式属性描述符 |
| 命令对象 | `entities/commands.py` | 声明式命令（CQRS-lite 写侧） |
| 平台 helpers | `helpers/platform.py` | 声明式规则引擎 |

## 架构概览

## North Star 2.0 Addendum (AI Debug Ready, HA-only)

本仓库的“先进化”方向已升级为北极星 2.0：在不引入第二条主链的前提下，把 **可观测 / 可回放 / 可给 AI 分析的证据链**正式化。

关键裁决：

- **Telemetry truth 单一**：telemetry 的正式真相链必须收口为 exporter → sinks；diagnostics/system-health 不得再二次拼 truth。
- **Pull-first exporter**：exporter 只读 protocol/runtime sources；sources 可维护有界事件摘要，但 exporter 不作为事件总线。
- **伪匿名化引用**：sinks 可输出 `entry_ref`/`device_ref` 作为报告内稳定关联键（跨报告不可关联）；禁止输出凭证等价物。
- **允许真实时间戳**：telemetry/evidence 允许包含真实时间戳（用于时序定位与 AI 分析），仍需遵守脱敏与基数预算。

参考真源：`.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` / `.planning/STATE.md` / `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`。

### 分层架构图

```
┌─────────────────────────────────────────────────────────────┐
│  Platform Layer (9 个平台)                                    │
│  light / cover / switch / fan / climate / binary_sensor /    │
│  sensor / select / update                                    │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ 声明式规则引擎: build_device_entities_from_rules()  │     │
│  │ 声明式命令对象: PowerCommand / SliderCommand / ...   │     │
│  │ 声明式描述符:   DeviceAttr[T] / ScaledBrightness    │     │
│  └─────────────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│  Entity Layer (entities/)                                    │
│  LiproEntity → CoordinatorEntity                             │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ 防抖保护 + 乐观更新 + Protection Window              │     │
│  │ async_send_command / async_change_state              │     │
│  └─────────────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│  Service Layer (Stable Interface Pattern)                    │
│  CommandService / StateService / MqttService / RefreshSvc    │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ API 稳定边界层 (Dependency Inversion)               │     │
│  │ Entity → Service → Runtime (隔离实现变更)           │     │
│  └─────────────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│  Coordinator + Orchestrator                                  │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ Coordinator (HA DataUpdateCoordinator 适配)           │   │
│  │   ├─ _async_update_data() 更新循环                    │   │
│  │   ├─ async_setup_mqtt()  MQTT 生命周期               │   │
│  │   └─ RuntimeContext 回调提供者                         │   │
│  ├───────────────────────────────────────────────────────┤   │
│  │ RuntimeOrchestrator (DI 布线 + 组件装配)              │   │
│  │   ├─ build_state_containers() → StateContainers       │   │
│  │   └─ build_runtimes(context) → CoordinatorRuntimes    │   │
│  ├───────────────────────────────────────────────────────┤   │
│  │ RuntimeContext (依赖注入协议, frozen dataclass)        │   │
│  │   ├─ get_device_by_id   (设备解析)                    │   │
│  │   ├─ apply_properties_update (状态变更)               │   │
│  │   ├─ schedule_listener_update (HA 通知)               │   │
│  │   ├─ request_refresh    (Coordinator 刷新)            │   │
│  │   ├─ trigger_reauth     (重新认证)                    │   │
│  │   └─ is_mqtt_connected  (MQTT 状态)                   │   │
│  └───────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Runtime Layer (6 个可组合 Runtime)                           │
│  ┌──────────┬──────────┬──────┬───────┬──────┬──────┐       │
│  │ Command  │  Device  │ Mqtt │ State │Status│Tuning│       │
│  └──────────┴──────────┴──────┴───────┴──────┴──────┘       │
├─────────────────────────────────────────────────────────────┤
│  Core Domain Layer                                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ LiproDevice (薄 facade + property delegation)          │  │
│  │  ├─ DeviceState        (可变状态)                      │  │
│  │  ├─ CapabilitySnapshot (不可变能力真源)                │  │
│  │  ├─ DeviceNetworkInfo  (网络诊断)                      │  │
│  │  └─ DeviceExtras       (扩展特性)                      │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ Protocol Plane (formal root + child façades) │ MQTT │ AuthManager │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 通信模型

"MQTT 推送 + REST 兜底轮询"的混合模型：

- **MQTT**：用于实时属性变更与在线状态更新
- **REST**：用于设备列表/状态轮询与 MQTT 不可用时的降级兜底

支持的平台：`light`, `cover`, `switch`, `fan`, `climate`, `binary_sensor`, `sensor`, `select`, `update`

## 架构原则

### 1) 组合优于继承 (Composition over Mixins)

该原则适用于**所有层**，而不只是 Coordinator：

- `Coordinator / Runtime`：显式 Runtime 组合 + `RuntimeContext` 注入
- `API Client`：显式 facade + domain collaborators / services，不以 mixin 聚合作为正式架构
- `Device Model`：property delegation + views，而不是继承叠加
- `Service / Diagnostics / Flow`：优先组合 helper / service / wiring，不做多重继承聚合

**历史残留不构成另一套标准**：如果某层仍存在 mixin 或兼容包袱，那只是待清理偏差，不是“该层可以例外”。

### 2) 依赖注入与上下文传递 (Dependency Injection via RuntimeContext)

```python
@dataclass(frozen=True, slots=True)
class RuntimeContext:
    get_device_by_id: Callable[[str], LiproDevice | None]
    apply_properties_update: Callable[..., Awaitable[bool]]
    schedule_listener_update: Callable[[], None]
    request_refresh: Callable[[], Awaitable[None]]
    trigger_reauth: Callable[[str], Awaitable[None]]
    is_mqtt_connected: Callable[[], bool]
```

- RuntimeContext 注入**回调函数**而非对象引用，打破潜在的循环依赖
- RuntimeOrchestrator 负责集中布线，Coordinator 提供回调实现
- 所有 Runtime 通过构造器注入依赖，无 setter 注入

### 3) 声明式编程优先 (Declarative First)

| 声明式机制 | 适用场景 | 示例 |
|-----------|---------|------|
| `build_device_entities_from_rules()` | 平台实体创建 (1:N) | fan.py, sensor.py, switch.py |
| `create_platform_entities()` | 平台实体创建 (1:1) | light.py, cover.py, climate.py |
| `DeviceAttr[T]` | 设备属性转发 | LiproLight.is_on, brightness |
| `PowerCommand` / `PropertyToggleCommand` | 命令发送 (CQRS-lite) | LiproSwitch._power, LiproLight._power |
| `ServiceRegistration` | HA 服务注册 | services/registrations.py |
| `PropertySwitchConfig` | 功能开关声明 | switch.py LIGHT_FEATURE_SWITCHES |

### 4) 边界清晰：Entity → Service → Runtime → Client

- **Entity**：HA 平台胶水 + UI 表现，不直接做 API/MQTT 细节
- **Service**：Stable Interface Pattern — 隔离 Entity 与 Runtime 实现变更
- **Runtime**：业务能力承载（可单测）
- **Client**：外部 IO 与协议封装

### 5) 决策记录（ADR-lite）

- 重大架构决策不只留在 PR 或审计结论里；至少记录 **背景 / 决策 / 取舍 / 后果 / 回滚条件**
- 当前必须显式保留的 4 条核心决策：
  1. `Coordinator` 是唯一编排根，不把编排逻辑下沉回 Entity / Platform
  2. 刷新只通过 `Coordinator.async_refresh_devices()` / `_async_refresh_device_snapshot()` 统一建模
  3. 外部状态写入统一走 `Coordinator._apply_properties_update()`，先确认过滤，再进入 `StateRuntime`
  4. 技术栈保持显式、轻量、可审计，不为中等规模集成过早引入重型框架
- 已落地 ADR 索引：`docs/adr/README.md`

### 6) 文档策略

- 不维护易失真的数字指标（覆盖率/测试数量/行数）
- 指标以 CI 或本地命令输出为准；不再依赖仓库内历史快照
- 若后续继续演进，建议把长期有效的架构决策沉淀到 `docs/adr/`，避免再次出现“代码已演进、文档口径未收敛”

## 核心组件详解

### Coordinator (`core/coordinator/coordinator.py`)

**职责**（约 712 LOC，需持续沿 formal boundary 继续切薄）：

- 维护运行时状态容器（`_state: CoordinatorStateContainers`）
- 持有运行时组件注册表（`_runtimes: CoordinatorRuntimes`）
- 对接 HA `DataUpdateCoordinator` 的更新循环
- 提供 RuntimeContext 回调实现
- 作为 Service 层门面

**初始化流程**：

```
RuntimeOrchestrator
    → build_state_containers()  → CoordinatorStateContainers
    → build_runtimes(context)   → CoordinatorRuntimes
Coordinator
    → RuntimeContext(callbacks)  → 注入到 Orchestrator
    → _init_service_layer()     → 4 个 Service 实例
```

### RuntimeOrchestrator (`core/coordinator/orchestrator.py`)

**职责**（约 260 LOC）：

- 集中管理所有 Runtime 组件的依赖注入布线
- 构建 `CoordinatorStateContainers`（状态容器）
- 构建 `CoordinatorRuntimes`（运行时注册表）
- 消除 lambda 闭包（使用 RuntimeContext 回调替代）

### 数据容器 (`core/coordinator/factory.py`)

**职责**（约 66 LOC）：

- 定义 `CoordinatorStateContainers` dataclass（可变状态容器）
- 定义 `CoordinatorRuntimes` dataclass（运行时注册表）
- 提供 `normalize_device_key()` 工具函数

> **Note**: 此文件在 Phase C 重构后已精简为纯数据定义模块。
> 所有 DI 布线逻辑已移至 `orchestrator.py`，MQTT 创建逻辑在 `mqtt_lifecycle.py`。

### Runtime 组件 (`core/coordinator/runtime/`)

说明：`DeviceRuntime` 只负责设备列表与快照生命周期；steady-state 状态同步由 `MqttRuntime` + `StatusRuntime` 承担，避免重复状态拉取路径。

| Runtime | 职责 | 关键依赖 |
|---------|------|---------|
| `StateRuntime` | 设备查找、属性更新、实体注册索引 | devices dict, identity index |
| `DeviceRuntime` | 全量设备快照刷新、过滤策略、缓存复用、设备增删对齐 | protocol façade, auth manager |
| `StatusRuntime` | REST 状态轮询（批次优化 + 二分回退） | query callback, state runtime |
| `MqttRuntime` | MQTT 消息分发 + 设备状态应用 | RuntimeContext callbacks |
| `CommandRuntime` | 命令发送、确认跟踪、post-refresh 策略 | builder, sender, confirmation |
| `TuningRuntime` | 批次大小、命令确认延迟等调参 | 无外部依赖 |

- `runtime/device/snapshot.py` 继续只负责 full snapshot orchestration；typed snapshot container 与 rejection contract 已下沉到 `runtime/device/snapshot_models.py`。
- `runtime/mqtt_runtime.py` 继续保留 transport lifecycle / message flow / runtime metrics；message-handler callback adapters 已下沉到 `runtime/mqtt/adapters.py`。
- `core/command/result.py` 继续作为 command-result arbitration home；classification / retry / post-refresh policy helper 已拆到 `core/command/result_policy.py`。

### API Client / Protocol Plane (`core/api/`, `core/mqtt/`)

- `client.py`：`LiproRestFacade` 是唯一正式 REST child façade；其残余仅限 `core/api` 内部 typing/helper spine，而非 compat shell
- `core/api/`：`LiproRestFacade` + transport / auth / endpoint collaborators；高漂移 REST 形态在 `core/protocol/boundary/rest_decoder.py` 与 `CanonicalProtocolContracts` 中先完成 canonicalization
- `core/protocol/boundary/rest_decoder.py`：保留 family metadata、decoder classes 与 public wrappers；pure canonicalization helpers 已下沉到同 family 的 `rest_decoder_support.py`，避免把 payload-shape glue 继续堆回 decoder root。
- `core/command/result_policy.py`：承接 command-result classification / retry / delayed-refresh policy；`result.py` 保留 patch-friendly arbitration seam 与 failure trace writing。
- `schedule_service.py`：仅保留 focused schedule helpers；`ScheduleApiService` 已退出正式故事线，schedule truth 固定为 `ScheduleEndpoints` + helper modules
- `status_service.py` / `status_fallback.py`：`status_service.py` 保留 public orchestration，binary-split fallback kernel 下沉到 `status_fallback.py`
- `core/mqtt/`：MQTT transport collaborators 与 `MqttTransportClient` 已作为 `LiproMqttFacade` child façade 挂到统一协议根，生产路径通过 `LiproProtocolFacade` / `MqttTransportFacade` contract 协作
- `core/auth/`：`LiproAuthManager` + `AuthSessionSnapshot`；HA adapters 通过 formal auth/session contract 协作，而不是解析 raw login dict
- `transport_core.py` / `transport_retry.py` / `transport_signing.py`：请求核心/重试/签名
- `endpoints/`：按域拆分端点（auth / status / devices / commands / ...）
- `core/coordinator/services/protocol_service.py`：`CoordinatorProtocolService` 承接 runtime protocol-facing ops，统一 `Coordinator` 内部 `protocol` 术语
- `*_service.py`：协议级服务封装（auth / mqtt / status helper families）；schedule 已从 service class 回环收回 formal endpoint 协作者
- `connection_manager.py`：指数退避重连
- `subscription_manager.py`：订阅管理
- `payload.py` / `topics.py`：消息解析、主题生成

### Phase 10 Boundary Clarifications

- `rest.device-list`、`rest.device-status`、`rest.mesh-group-status` 等高漂移 family 现在都要求先在 protocol boundary 输出 canonical contract；runtime / control / platform 不再自己理解 vendor envelope、field alias 或分页差异。
- `core/__init__.py` 不再导出 `Coordinator`；HA runtime home 继续固定在 `custom_components/lipro/coordinator_entry.py`，`control/runtime_access.py` 负责控制面定位 runtime root。
- 未来 CLI / 其他宿主若要复用，只能建立在 `LiproProtocolFacade`、boundary contracts、`AuthSessionSnapshot` 与 device/capability truth 之上，而不是把 HA runtime 直接抽成 shared core。

### Phase 11 Control-Plane Closeout

- `custom_components/lipro/control/service_router.py` 已成为唯一正式 service callback home；`services/registrations.py` 只负责把 HA service declaration 绑定到 formal router。
- `custom_components/lipro/control/developer_router_support.py` 已承接 developer report collection、optional capability glue 与 sensor-history shared wrapper；`service_router.py` 保留 public handler 身份。
- developer diagnostics 现直接复用 `runtime_types.LiproCoordinator` / `LiproDevice` 正式 contract；`developer_router_support.py` 不再通过投影设备或平级 diagnostics coordinator 协议自造第二层 typed truth。
- `custom_components/lipro/services/wiring.py` 已正式删除；control plane 不再保留 legacy wiring compat shell。
- control-facing runtime lookup 继续经 `custom_components/lipro/control/runtime_access.py` 收口，避免 `entry.runtime_data` 访问重新散落。

### Device Model (`core/device/`)

- `device.py`：`LiproDevice`（薄 façade，显式 property / method surface + 组合根）
- `state.py`：`DeviceState`（显式状态视图 + leaf accessors；不再依赖动态 `__getattr__`）
- `core/capability/`：`CapabilityRegistry` / `CapabilitySnapshot` 是唯一正式能力真源；`DeviceCapabilities` compat alias 已在 Phase 12 删除
- `identity.py`：`DeviceIdentity`（设备身份信息）
- `network_info.py`：`DeviceNetworkInfo`（网络诊断）
- `extras.py`：`DeviceExtras`（扩展数据）
- `device_views.py`：派生视图
- `state_accessors.py`：显式状态 accessor helpers（内部实现细节，不再承担动态扩面职责）

### Entity Layer (`entities/`)

- `base.py`：`LiproEntity`（CoordinatorEntity 子类）
  - 乐观更新 + 防抖保护窗口 + post-command buffer
  - `async_send_command()` / `async_change_state()` 统一命令路径
- `descriptors.py`：`DeviceAttr[T]` / `ScaledBrightness` / `ConditionalAttr[T]`
  - 泛型描述符，`Generic[T]` + `@overload` 确保 mypy 类型安全
- `commands.py`：`PowerCommand` / `PropertyToggleCommand` / `SliderCommand`
  - 声明式命令对象（CQRS-lite 写侧标准化）

### Platform Layer

| 平台 | 实体创建模式 | 说明 |
|------|-------------|------|
| light.py | `create_platform_entities` | 简单 1:1 映射 |
| cover.py | `create_platform_entities` | 简单 1:1 映射 |
| climate.py | `create_platform_entities` | 简单 1:1 映射 |
| update.py | 列表推导式 | 极简 1:1 映射 |
| fan.py | `build_device_entities_from_rules` | 声明式规则引擎 |
| sensor.py | `build_device_entities_from_rules` | 声明式规则引擎 |
| binary_sensor.py | `build_device_entities_from_rules` | 声明式规则引擎 |
| select.py | `build_device_entities_from_rules` | 声明式规则引擎 |
| switch.py | `build_device_entities_from_rules` | 声明式规则引擎 (compound predicate) |

### Service Layer (`services/`)

- `control/service_router.py`：正式 control-plane service callback home
- `registry.py`：声明式 HA 服务注册框架
- `registrations.py`：服务声明列表（绑定 formal router）
- `diagnostics/`：开发者诊断服务包（按 handler / types / wiring 拆分）

## 边界规则

### 允许的依赖方向

- `Entity -> Coordinator public API / Service`
- `Service -> Runtime`
- `Runtime -> RuntimeContext callbacks / injected collaborators`
- `Coordinator -> RuntimeOrchestrator / Runtime registry / State containers`

### 不建议的依赖方向

- `Entity -> Runtime` 直连
- `Platform -> API Client` 直连
- `Service -> coordinator._state` 私有容器直写
- `Runtime` 之间通过全局单例或 setter 临时回连
- 在多个入口重复实现刷新、确认、状态写入策略

### 当前主链约束

- 命令主链以 `CommandRuntime.send_device_command()` 为唯一正式运行时入口
- 设备刷新主链以 `Coordinator.async_refresh_devices()` / `_async_refresh_device_snapshot()` 为唯一正式刷新原语
- 外部状态写入统一先经过 `Coordinator._apply_properties_update()`，再进入 `StateRuntime`

## 数据流

### 1) 状态更新（MQTT / REST → Entity）

```
┌──────────┐     ┌──────────┐
│ MQTT Msg │────→│MqttRuntime│────┐
└──────────┘     └──────────┘    │
                                  ├──→ Coordinator._apply_properties_update()
┌──────────┐     ┌────────────┐  │       ├─ CommandRuntime.filter_pending_state_properties()
│ REST Poll│────→│StatusRuntime│──┘       ├─ CommandRuntime.observe_state_confirmation()
└──────────┘     └────────────┘          ├─ StateRuntime.apply_properties_update()
                                         ├─ 更新 LiproDevice.properties
                                         └─ schedule_listener_update() → HA
```

### 2) 命令执行（User → Entity → API → Confirm）

```
User Action → Entity.async_turn_on()
    → PowerCommand.turn_on(entity)
        → LiproEntity.async_send_command()
            → Coordinator.async_send_command()
                → CoordinatorCommandService.async_send_command()
                    → CommandRuntime.send_device_command()
                        → CommandBuilder → CommandSender → API
                        → ConfirmationManager → post-refresh
```

### 2.5) 设备刷新（显式 refresh / 周期 refresh）

```
HA Service / Coordinator update loop
    → Coordinator.async_refresh_devices() 或 Coordinator._async_update_data()
        → Coordinator._async_refresh_device_snapshot()
            → DeviceRuntime.refresh_devices(force=...)
                → full snapshot or cached snapshot reuse
            → state.devices 同步
            → mqtt_service.async_sync_subscriptions()
            → async_set_updated_data() / listener update
```

### 3) MQTT 生命周期

```
Coordinator._async_update_data() (首次)
    → async_setup_mqtt()
        → mqtt_lifecycle.setup_mqtt_lifecycle()
            → 解密 MQTT 凭证
            → 创建 `MqttTransportClient` concrete transport（localized concrete transport；formal root 仍是 `LiproProtocolFacade`）
            → 创建 MqttRuntime (with RuntimeContext)
            → 替换 _runtimes.mqtt
```

### 4) 认证（AuthManager → 401 recovery）

- `core/auth/manager.py` 负责 token 生命周期、refresh、必要时触发 reauth
- API transport 层在 401 时触发 refresh 回调并重试

## 一致性与故障模型

### 权威源裁决

- **设备拓扑 / 能力信息**：以 `DeviceRuntime` 拉取的 device snapshot 为权威源
- **即时状态变更**：优先信任 MQTT 推送，追求低延迟
- **兜底状态同步**：`StatusRuntime` 的 REST 轮询负责 MQTT 不可用或状态漂移时的重同步
- **命令后的瞬态状态**：统一通过 confirmation tracker + stale 过滤裁决，避免“旧状态回写覆盖新命令”

### 失败处理原则

- MQTT 未连接或断连时，不阻断主链；系统退回 REST 轮询 + 显式 refresh
- 命令确认超时后，不盲目强写本地状态；由 confirmation / post-refresh 机制触发重新对齐
- 401 / token 失效由 transport → auth manager 的恢复链处理，必要时升级为 reauth
- 快照缓存复用失效、identity miss 或索引不一致时，优先回退到完整 snapshot 对齐，而不是局部猜测修补

### 乱序与重复消息处理

- 所有外部状态写入统一经过 `Coordinator._apply_properties_update()`
- `CommandRuntime.filter_pending_state_properties()` 负责保护窗口内的 stale 属性过滤
- `CommandRuntime.observe_state_confirmation()` 负责学习确认延迟并收敛命令确认链路

## Config Entry 生命周期

- `async_setup_entry()`：构建 client / coordinator / services，完成首次 refresh 后再 forward 平台
- `async_unload_entry()`：先卸载平台，再关闭 coordinator / MQTT 生命周期，并清理 entry 级资源
- `async_reload_entry()`：通过 unload + setup 重建运行时，保持入口语义一致
- `config_flow.py` 负责初始接入、reauth 与 options flow；它属于运行前控制面，不直接承载运行时业务逻辑

## 目录结构

```
custom_components/lipro/
├── core/
│   ├── coordinator/
│   │   ├── coordinator.py         # HA glue + Runtime 编排
│   │   ├── orchestrator.py        # DI 布线 + 组件装配
│   │   ├── runtime_context.py     # 依赖注入协议
│   │   ├── factory.py             # 数据容器定义
│   │   ├── mqtt_lifecycle.py      # MQTT 生命周期管理
│   │   ├── runtime/               # 6 个 Runtime 组件
│   │   │   ├── command_runtime.py
│   │   │   ├── device_runtime.py
│   │   │   ├── mqtt_runtime.py
│   │   │   ├── state_runtime.py
│   │   │   ├── status_runtime.py
│   │   │   └── tuning_runtime.py
│   │   └── services/              # Service 层 (Stable Interface Pattern)
│   │       ├── command_service.py
│   │       ├── state_service.py
│   │       ├── mqtt_service.py
│   │       └── device_refresh_service.py
│   ├── api/                       # REST / IoT protocol slice
│   │   ├── client.py              # `LiproRestFacade` + explicit endpoint collaborators
│   │   ├── endpoints/             # 按域拆分端点
│   │   └── transport_*.py         # 请求核心/重试/签名
│   ├── mqtt/                      # MQTT protocol slice（child façade under LiproProtocolFacade）
│   │   ├── mqtt_client.py
│   │   ├── connection_manager.py
│   │   └── subscription_manager.py
│   ├── device/                    # Device 领域模型
│   │   ├── device.py              # LiproDevice (property delegation)
│   │   ├── state.py               # DeviceState (mutable)
│   │   ├── ../capability/          # CapabilityRegistry / CapabilitySnapshot 真源
│   │   └── identity.py            # DeviceIdentity
│   ├── auth/                      # 认证管理
│   ├── command/                   # 命令执行
│   └── ota/                       # OTA 固件更新
├── entities/                      # Entity 基类 + 声明式工具
│   ├── base.py                    # LiproEntity (防抖 + 乐观更新)
│   ├── descriptors.py             # DeviceAttr[T] 声明式描述符
│   └── commands.py                # PowerCommand 声明式命令
├── helpers/                       # 平台 helpers
│   └── platform.py                # 声明式规则引擎
├── services/                      # HA 服务注册
├── const/                         # 常量定义
├── flow/                          # 配置流程
├── diagnostics.py                 # 诊断导出（脱敏）
├── system_health.py               # 系统健康检查
├── entry_options.py               # Options / reload 辅助
└── 9 个平台文件                    # light.py, cover.py, switch.py, ...
```

## 扩展指南

### 新增 Runtime

1. 在 `core/coordinator/runtime/` 下实现单一职责组件
2. 依赖通过构造器注入；若需要回调 coordinator，优先扩展 `RuntimeContext`
3. 在 `orchestrator.py` 中集中 wiring
4. 只通过 `Coordinator` 暴露必要 public accessor，不向 Entity 暴露内部细节
5. 为 runtime 自身补 unit tests，再为 wiring 补 integration-style tests

### 新增 Service

1. 仅在存在“稳定边界价值”时新增 Service，避免空壳抽象
2. Service 负责 API 稳定性与跨 runtime 协调，不复制 runtime 规则
3. Service 不直接写 `_state`，除非明确由 coordinator 提供正式原语
4. 若 service 引入副作用链，必须补对应 orchestration tests

### 新增 Platform / Entity

1. 优先复用 `build_device_entities_from_rules()` / `create_platform_entities()`
2. 写侧统一走 `LiproEntity.async_send_command()`
3. 乐观更新必须与 coordinator 锁、防抖保护窗口一致
4. 新平台若需要专属读取逻辑，优先新增 descriptor / helper，而不是在实体里堆分支

## 验证命令

统一使用 `uv`：

```bash
uv run ruff check .                                      # Lint
uv run mypy                                              # 类型检查
uv run pytest -q                                         # 全量测试
```

## 最小验证矩阵

| 变更区域 | 至少执行 |
|---|---|
| `core/coordinator/**` 或 Runtime / Service 主链 | `uv run pytest tests/core/coordinator tests/test_coordinator_public.py -q` |
| `core/api/**` 或协议编解码 | `uv run pytest tests/core/api tests/snapshots/test_api_snapshots.py -q` |
| `core/mqtt/**` | `uv run pytest tests/core/mqtt tests/integration/test_mqtt_coordinator_integration.py -q` |
| `entities/**` / `platforms/**` | `uv run pytest tests/entities tests/platforms -q` |
| `config_flow.py` / `entry_options.py` / config entry 生命周期 | `uv run pytest tests/flows -q` |
| 仅文档改动 | 链接 / 路径 grep + `git diff -- docs/developer_architecture.md .planning/ROADMAP.md .planning/PROJECT.md CONTRIBUTING.md CHANGELOG.md` 自检 |

## 贡献约定

1. 保持"组合式 Runtime + 薄 facade + Service 委托 + RuntimeContext DI"方向
2. 新增平台：使用 `build_device_entities_from_rules()` 或 `create_platform_entities()`
3. 新增命令：使用声明式命令对象（`PowerCommand` / `PropertyToggleCommand`）
4. 新增属性：评估是否适用 `DeviceAttr[T]` 描述符
5. 优先补齐单测，确保 ruff / mypy / pytest 通过
6. 对外 API 通过 Service 层暴露，Entity 不直接调用 Runtime

## 技术选型评估

### 当前应继续坚持的选择

| 选型 | 判断 | 原因 |
|---|---|---|
| `DataUpdateCoordinator` 作为 HA 适配根 | 保持 | 与 HA 运行模型天然兼容，外部集成成本最低 |
| 全层显式组合 | 保持 | 同一套标准适用于 Coordinator、API Client、Device、Service，避免多套心智模型并存 |
| `dataclasses` + TypedDict / 明确类型别名 | 保持 | 足够轻量，适合当前代码规模 |
| `RuntimeContext` 回调注入 | 保持 | 依赖图清晰，避免 coordinator 反向渗透 |
| `uv + ruff + mypy + pytest` | 保持 | 当前质量/成本比最佳 |

### 有提升空间，但不建议立刻重构的方向

| 方向 | 建议 | 触发条件 |
|---|---|---|
| ADR 文档化 | 已落地 `docs/adr/`；后续新增重大决策时继续按 ADR 追加，而非回写审计文档 | 当边界或主链再次发生实质性变化时 |
| 协议边界 schema 校验 | 只在 API / MQTT 外部边界增加更强的 payload schema，不侵入领域模型 | 当上游协议漂移频繁导致回归成本升高时 |
| 可观测性 | 增加命令确认延迟、刷新耗时、MQTT 恢复时间的结构化指标 | 当线上问题定位成本继续升高时 |
| 契约测试 | 为供应商协议增加 golden payload / snapshot contract tests | 当端到端回归覆盖仍不足以防协议漂移时 |
| 边界专用强类型库 | 若外部 payload 复杂度继续上升，可仅在边界层评估 `pydantic v2` 或 `msgspec` | 当手写校验与 TypedDict 维护成本显著上升时 |
| Protocol Plane 漂移隔离 | 已完成：正式根为 `LiproProtocolFacade`；`LiproRestFacade` / `LiproMqttFacade` 作为 child façade 协作，高漂移 REST family 已在 boundary 完成 canonicalization | 当新增 drift family、host-neutral contract 或 replay authority 需要扩展时，必须继续沿 formal boundary 演进 |

### 建议的演进顺序（按性价比）

1. **继续用 ADR 固化重大决策**：避免再次出现“代码已演进、文档口径未收敛”
2. **新增高漂移 payload 时先补 boundary contract / replay fixtures**：让 drift 先失败在 protocol proof
3. **协议 / auth / control 变更优先跑 targeted guards**：先覆盖 contract matrix、auth、public-surface、governance guards
4. **再补结构化 observability 指标**：把命令确认延迟、刷新耗时、MQTT 恢复时间继续沉淀为 exporter truth
5. **最后才评估边界层强类型升级**：只在外部 payload 复杂度继续上升时考虑 `pydantic v2` / `msgspec`

### 当前不建议引入的重型方案

- 不建议引入通用 DI 框架：当前 `RuntimeOrchestrator` 已足够清晰
- 不建议把全域模型切到 `pydantic`：会提高样板和运行时成本，收益不足
- 不建议引入事件总线替代显式调用链：会削弱可追踪性与调试可读性
- 不建议为本地状态再引入持久化层/仓储模式：当前场景以协调器内存态为主，复杂度不匹配

### 北极星原则

- 目标架构先于历史实现：架构决策先看理想边界，再看迁移路径
- 历史债只能影响排期，不影响“什么是正确终态”的判断
- 同一套标准适用于所有层：显式组合、单一正式主链、边界可审计、依赖方向固定
- 任何偏离这套标准的实现，都应在文档中被标注为偏差或迁移残留，而不是被包装成第二套合法架构

### 总结判断

当前技术选型整体是合理的，**提升空间主要在“文档化、契约化、可观测性”三个方向，而不是框架级重写**。如果继续演进，最优先的不是换技术栈，而是让既有架构决策更显式、边界更可审计、协议回归更自动化。

## 协作图谱身份

- `.planning/codebase/*.md` 是受约束的协作图谱 / 派生视图：帮助贡献者理解目录、热点、测试镜像与治理边界，但**不高于** north-star、ROADMAP/STATE、baseline 或 review 真源。
- 若 codebase map 与 `.planning/baseline/*.md`、`.planning/reviews/*.md`、`docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 或 `AGENTS.md` 冲突，必须以后者为准，并回写 codebase map。
- codebase map 可以总结、导航、局部解释，但不能反向定义 public surface、authority、residual 或 delete gate。

## 参考文档

- `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` / `.planning/STATE.md` / `.planning/reviews/FILE_MATRIX.md` — 当前执行、状态与治理真源
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 北极星目标架构（终态基准）
- `docs/adr/README.md` — 长期生效的架构决策索引
- `CHANGELOG.md` — 变更日志
- Home Assistant Developer Docs: https://developers.home-assistant.io/
