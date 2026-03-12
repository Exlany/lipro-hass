# Lipro Home Assistant Integration - Developer Architecture

> **Last Updated**: 2026-03-12  \
> **Version**: 3.6 (Post-audit convergence + north-star architecture alignment)
>
> ⚠️ 本文档仅描述"架构与模块边界"，不硬编码评分/覆盖率/通过率等易失真指标。  \
> 当前实现状态、验证结果与风险优先级请以 `docs/COMPREHENSIVE_AUDIT_2026-03-12.md` 为准。

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
│  │  ├─ DeviceCapabilities (不可变能力)                    │  │
│  │  ├─ DeviceNetworkInfo  (网络诊断)                      │  │
│  │  └─ DeviceExtras       (扩展特性)                      │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ API Client (显式 facade 目标态) │ MQTT Client │ AuthManager │  │
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
- 指标以 CI 或本地命令输出为准；历史快照统一归档在 `docs/archive/`
- 若后续继续演进，建议把长期有效的架构决策沉淀到 `docs/adr/`，避免再次出现“代码已演进、文档口径未收敛”

## 核心组件详解

### Coordinator (`core/coordinator/coordinator.py`)

**职责**（约 450 LOC）：

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
| `DeviceRuntime` | 全量设备快照刷新、过滤策略、缓存复用、设备增删对齐 | API client, auth manager |
| `StatusRuntime` | REST 状态轮询（批次优化 + 二分回退） | query callback, state runtime |
| `MqttRuntime` | MQTT 消息分发 + 设备状态应用 | RuntimeContext callbacks |
| `CommandRuntime` | 命令发送、确认跟踪、post-refresh 策略 | builder, sender, confirmation |
| `TuningRuntime` | 批次大小、命令确认延迟等调参 | 无外部依赖 |

### API Client (`core/api/`)

- `client.py`：`LiproClient`（目标态：显式 facade + domain collaborators；mixin 聚合不属于正式架构）
- `transport_core.py` / `transport_retry.py` / `transport_signing.py`：请求核心/重试/签名
- `endpoints/`：按域拆分端点（auth / status / devices / commands / ...）
- `*_service.py`：API 级服务封装（auth / schedule / mqtt / status）

### MQTT Client (`core/mqtt/`)

- `mqtt_client.py`：`LiproMqttClient` 薄门面
- `client_runtime.py`：运行时桥接
- `connection_manager.py`：指数退避重连
- `subscription_manager.py`：订阅管理
- `payload.py` / `topics.py`：消息解析、主题生成

### Device Model (`core/device/`)

- `device.py`：`LiproDevice`（薄 facade, dataclass + property delegation）
- `state.py`：`DeviceState`（可变状态视图 + derived accessors）
- `capabilities.py`：`DeviceCapabilities`（不可变能力描述）
- `identity.py`：`DeviceIdentity`（设备身份信息）
- `network_info.py`：`DeviceNetworkInfo`（网络诊断）
- `extras.py`：`DeviceExtras`（扩展数据）
- `device_views.py`：派生视图
- `device_delegation.py`：`__getattr__` 委托

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

- `registry.py`：声明式 HA 服务注册框架
- `registrations.py`：服务声明列表
- `diagnostics/`：开发者诊断服务包（按 handler / types / wiring 拆分）
- `wiring.py`：服务层布线

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
            → 创建 LiproMqttClient
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
│   ├── api/                       # REST API Client
│   │   ├── client.py              # LiproClient (显式 facade 目标态)
│   │   ├── endpoints/             # 按域拆分端点
│   │   └── transport_*.py         # 请求核心/重试/签名
│   ├── mqtt/                      # MQTT Client
│   │   ├── mqtt_client.py
│   │   ├── connection_manager.py
│   │   └── subscription_manager.py
│   ├── device/                    # Device 领域模型
│   │   ├── device.py              # LiproDevice (property delegation)
│   │   ├── state.py               # DeviceState (mutable)
│   │   ├── capabilities.py        # DeviceCapabilities (immutable)
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
| 仅文档改动 | 链接 / 路径 grep + `git diff -- docs/ README*.md` 自检 |

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
| API Client 去 mixin 化 | 目标态直接采用显式 facade + transport / auth / endpoint collaborators；mixin 聚合不视为可接受终态 | 当 API client 仍保留多重继承或隐式聚合时就应推进 |

### 建议的演进顺序（按性价比）

1. **先补 ADR 与边界审查清单**：已完成第一步，后续继续用 ADR 固化新增重大决策
2. **再补协议契约测试**：把供应商返回 payload 固化为 golden fixtures，优先守住 REST / MQTT 边界
3. **再补可观测性**：把“命令确认慢、刷新慢、MQTT 恢复慢”从体感问题变成可量化问题
4. **推进 API Client 去 mixin 化**：所有层遵循同一套显式组合标准，不接受“API 层例外”
5. **最后才评估边界层强类型升级**：只有当外部协议复杂度继续上升时，才考虑在 boundary layer 引入更强 schema 工具

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

## 参考文档

- `docs/COMPREHENSIVE_AUDIT_2026-03-12.md` — 当前权威审计/验证报告
- `docs/adr/README.md` — 长期生效的架构决策索引
- `docs/archive/` — 历史审计、重构计划与过期快照
- `CHANGELOG.md` — 变更日志
- Home Assistant Developer Docs: https://developers.home-assistant.io/
