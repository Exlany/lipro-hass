# Lipro Home Assistant Integration - Developer Architecture

> **Last Updated**: 2026-03-11  \
> **Version**: 3.0 (Post-refactor: RuntimeContext + Orchestrator)
>
> ⚠️ 本文档仅描述"架构与模块边界"，不硬编码评分/覆盖率/通过率等易失真指标。  \
> 质量验收与重构收口进度请以 `docs/refactor_completion_plan.md` 的回填记录为准。

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
│  │ API Client (mixin 组合) │ MQTT Client │ AuthManager    │  │
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

Coordinator 不依赖 mixin 聚合，而是将职责拆成可独立测试/替换的 Runtime 组件。
LiproDevice 使用 property delegation 组合 State/Capabilities/NetworkInfo/Extras 视图。

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

### 5) 文档策略

- 不维护易失真的数字指标（覆盖率/测试数量/行数）
- 指标以 CI 或本地命令输出为准，回填到 `docs/refactor_completion_plan.md`

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

| Runtime | 职责 | 关键依赖 |
|---------|------|---------|
| `StateRuntime` | 设备查找、属性更新、实体注册索引 | devices dict, identity index |
| `DeviceRuntime` | 设备列表刷新、过滤策略、设备增删对齐 | API client, auth manager |
| `StatusRuntime` | REST 状态轮询（批次优化 + 二分回退） | query callback, state runtime |
| `MqttRuntime` | MQTT 消息分发 + 设备状态应用 | RuntimeContext callbacks |
| `CommandRuntime` | 命令发送、确认跟踪、post-refresh 策略 | builder, sender, confirmation |
| `TuningRuntime` | 批次大小、MQTT 过期窗口等调参 | 无外部依赖 |

### API Client (`core/api/`)

- `client.py`：`LiproClient`（端点 mixin + transport mixin 组合入口）
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
- `diagnostics_service.py`：开发者诊断服务（668行，待拆分）
- `wiring.py`：服务层布线

## 数据流

### 1) 状态更新（MQTT / REST → Entity）

```
┌──────────┐     ┌──────────┐
│ MQTT Msg │────→│MqttRuntime│────┐
└──────────┘     └──────────┘    │
                                  ├──→ StateRuntime.apply_properties_update()
┌──────────┐     ┌────────────┐  │       ├─ 更新 LiproDevice.properties
│ REST Poll│────→│StatusRuntime│──┘       ├─ 通知实体（debounce-aware）
└──────────┘     └────────────┘          └─ schedule_listener_update() → HA
```

### 2) 命令执行（User → Entity → API → Confirm）

```
User Action → Entity.async_turn_on()
    → PowerCommand.turn_on(entity)
        → LiproEntity.async_send_command()
            → Coordinator.async_send_device_command()
                → CommandRuntime.send_device_command()
                    → CommandBuilder → CommandSender → API
                    → ConfirmationManager → post-refresh
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

## 目录结构

```
custom_components/lipro/
├── core/
│   ├── coordinator/
│   │   ├── coordinator.py         # HA glue + Runtime 编排 (≈450 LOC)
│   │   ├── orchestrator.py        # DI 布线 + 组件装配 (≈260 LOC)
│   │   ├── runtime_context.py     # 依赖注入协议 (≈110 LOC)
│   │   ├── factory.py             # 数据容器定义 (≈66 LOC)
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
│   │   ├── client.py              # LiproClient (mixin 组合)
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
└── 9 个平台文件                    # light.py, cover.py, switch.py, ...
```

## 验证命令

统一使用 `uv`：

```bash
uv run ruff check .                                    # Lint
uv run --extra dev mypy custom_components/lipro tests   # 类型检查
uv run pytest -q                                        # 全量测试
```

## 贡献约定

1. 保持"组合式 Runtime + 薄 facade + Service 委托 + RuntimeContext DI"方向
2. 新增平台：使用 `build_device_entities_from_rules()` 或 `create_platform_entities()`
3. 新增命令：使用声明式命令对象（`PowerCommand` / `PropertyToggleCommand`）
4. 新增属性：评估是否适用 `DeviceAttr[T]` 描述符
5. 优先补齐单测，确保 ruff / mypy / pytest 通过
6. 对外 API 通过 Service 层暴露，Entity 不直接调用 Runtime

## 参考文档

- `docs/refactor_completion_plan.md` — 重构进度 + 验收记录
- `CODE_QUALITY_REVIEW.md` — 代码质量审查
- `CHANGELOG.md` — 变更日志
- Home Assistant Developer Docs: https://developers.home-assistant.io/
