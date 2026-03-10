# 🜄 完美架构方案 - Coordinator 纯组合重构

> **基于审查意见与重构文档的终极架构设计**
>
> 当前评分：8.3/10 → 目标评分：9.5/10

---

## 📊 现状诊断

### ✅ 已达成的优势

1. **运行时入口统一** - `Coordinator` 已成为唯一公开入口
2. **服务边界清晰** - 4 个显式 service 依赖（command/device_refresh/mqtt/state）
3. **测试网强大** - 快照/benchmark/类型检查/覆盖率全覆盖
4. **类型热点清零** - 目标模块 `Any` 已消除
5. **超大类已拆解** - `LiproDevice` 87 行，`LiproMqttClient` 150 行

### ⚠️ 架构短板（8.3 → 9.5 的关键差距）

| 问题 | 当前状态 | 影响 |
|------|---------|------|
| **扁平多继承** | `Coordinator` 继承 9 个 runtime 基类 | MRO 复杂，共享 `self` 状态 |
| **base.py 膨胀** | 307 行，成为类型/契约汇聚点 | 后续容易继续膨胀 |
| **大文件残留** | 5 个文件 300-477 行 | 单一职责不够纯粹 |
| **组合不彻底** | runtime 通过继承而非字段组合 | 测试隔离度不足 |

---

## 🎯 终极架构目标

### 核心原则

```python
# ❌ 当前：扁平多继承
class Coordinator(
    CoordinatorAdaptiveTuningRuntime,      # 344 行
    CoordinatorCommandConfirmationRuntime, # 173 行
    CoordinatorCommandRuntime,             # 383 行
    CoordinatorMqttLifecycleRuntime,       # 287 行
    CoordinatorMqttMessageRuntime,         # 195 行
    CoordinatorDeviceRefreshRuntime,       # 405 行
    CoordinatorStateRuntime,               # 372 行
    CoordinatorPropertiesRuntime,          # 155 行
    CoordinatorAuthIssuesRuntime,          # 139 行
    CoordinatorStatusRuntime,              # 360 行
    CoordinatorShutdownRuntime,            # 92 行
):
    pass

# ✅ 目标：纯组合 + Protocol
class Coordinator(DataUpdateCoordinator[dict[str, LiproDevice]]):
    """Pure composition coordinator with explicit collaborators."""

    # 显式协作者字段（非继承）
    _command_runtime: CommandRuntimeProtocol
    _device_runtime: DeviceRuntimeProtocol
    _mqtt_runtime: MqttRuntimeProtocol
    _state_runtime: StateRuntimeProtocol
    _tuning_runtime: TuningRuntimeProtocol
    _status_runtime: StatusRuntimeProtocol

    # 公开服务边界（委托给 runtime）
    command_service: CommandServiceProtocol
    device_refresh_service: DeviceRefreshServiceProtocol
    mqtt_service: MqttServiceProtocol
    state_service: StateManagementProtocol
```

---

## 🏗️ 重构路线图

### Phase 1: Runtime 协作者提取（2 周）

#### 1.1 定义 Runtime Protocol

**文件**: `custom_components/lipro/core/coordinator/runtime/protocols.py`

```python
"""Runtime collaborator protocols for pure composition."""

from typing import Protocol, runtime_checkable

@runtime_checkable
class CommandRuntimeProtocol(Protocol):
    """Command execution runtime."""

    async def send_command(
        self,
        device_id: str,
        command: dict[str, Any],
        *,
        wait_confirmation: bool = True,
        timeout: float = 5.0,
    ) -> CommandResult: ...

    async def send_batch_commands(
        self,
        commands: list[tuple[str, dict[str, Any]]],
    ) -> list[CommandResult]: ...

@runtime_checkable
class DeviceRuntimeProtocol(Protocol):
    """Device refresh and lifecycle runtime."""

    async def refresh_devices(
        self,
        *,
        force: bool = False,
        incremental: bool = True,
    ) -> dict[str, LiproDevice]: ...

    async def refresh_single_device(
        self,
        device_id: str,
    ) -> LiproDevice | None: ...

@runtime_checkable
class MqttRuntimeProtocol(Protocol):
    """MQTT connection and message runtime."""

    async def connect(self) -> bool: ...
    async def disconnect(self) -> None: ...
    async def handle_message(self, topic: str, payload: bytes) -> None: ...

    @property
    def is_connected(self) -> bool: ...

@runtime_checkable
class StateRuntimeProtocol(Protocol):
    """State management runtime."""

    def get_device(self, device_id: str) -> LiproDevice | None: ...
    def get_all_devices(self) -> dict[str, LiproDevice]: ...
    def update_device_state(self, device_id: str, state: dict[str, Any]) -> None: ...

@runtime_checkable
class TuningRuntimeProtocol(Protocol):
    """Adaptive tuning runtime."""

    def adjust_polling_interval(self, success_rate: float) -> None: ...
    def get_current_interval(self) -> float: ...

@runtime_checkable
class StatusRuntimeProtocol(Protocol):
    """Status polling runtime."""

    async def poll_device_status(self, device_id: str) -> dict[str, Any]: ...
    async def poll_all_status(self) -> dict[str, dict[str, Any]]: ...
```

#### 1.2 实现独立 Runtime 类

**目标**: 将当前 9 个 runtime 基类转为独立组合对象

```python
# custom_components/lipro/core/coordinator/runtime/command_runtime.py
class CommandRuntime:
    """Standalone command execution runtime."""

    def __init__(
        self,
        client: LiproClient,
        mqtt_client_provider: Callable[[], LiproMqttClient | None],
        confirmation_tracker: CommandConfirmationTracker,
    ) -> None:
        self._client = client
        self._mqtt_client_provider = mqtt_client_provider
        self._confirmation_tracker = confirmation_tracker

    async def send_command(
        self,
        device_id: str,
        command: dict[str, Any],
        *,
        wait_confirmation: bool = True,
        timeout: float = 5.0,
    ) -> CommandResult:
        """Send command without accessing coordinator self."""
        # 纯函数式实现，不依赖共享状态
        ...
```

**关键改进**:
- ❌ 不再继承 `_CoordinatorBase`
- ❌ 不再通过 `self` 访问 coordinator 状态
- ✅ 通过构造函数注入依赖
- ✅ 可独立测试，无需 mock coordinator

#### 1.3 Coordinator 组合装配

```python
# custom_components/lipro/core/coordinator/coordinator.py
class Coordinator(DataUpdateCoordinator[dict[str, LiproDevice]]):
    """Pure composition coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LiproClient,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Lipro",
            update_interval=timedelta(seconds=update_interval),
            config_entry=config_entry,
            always_update=True,
        )

        # 核心依赖
        self.client = client
        self.auth_manager = auth_manager

        # 初始化共享基础设施
        self._devices: dict[str, LiproDevice] = {}
        self._mqtt_client: LiproMqttClient | None = None
        self._confirmation_tracker = CommandConfirmationTracker()

        # 组合 runtime 协作者（非继承）
        self._command_runtime = CommandRuntime(
            client=client,
            mqtt_client_provider=lambda: self._mqtt_client,
            confirmation_tracker=self._confirmation_tracker,
        )

        self._device_runtime = DeviceRuntime(
            client=client,
            device_store=self._devices,
        )

        self._mqtt_runtime = MqttRuntime(
            hass=hass,
            client=client,
            message_handler=self._handle_mqtt_message,
        )

        self._state_runtime = StateRuntime(
            device_store=self._devices,
        )

        self._tuning_runtime = TuningRuntime()
        self._status_runtime = StatusRuntime(client=client)

        # 公开服务边界（委托给 runtime）
        self.command_service = CoordinatorCommandService(self._command_runtime)
        self.device_refresh_service = CoordinatorDeviceRefreshService(self._device_runtime)
        self.mqtt_service = CoordinatorMqttService(self._mqtt_runtime)
        self.state_service = CoordinatorStateService(self._state_runtime)
```

**关键改进**:
- ✅ `Coordinator` 只继承 `DataUpdateCoordinator`（1 层）
- ✅ Runtime 通过字段组合，非继承
- ✅ 依赖通过构造函数显式注入
- ✅ 共享状态最小化（`_devices`, `_mqtt_client`）

---

### Phase 2: 大文件拆解（1 周）

#### 2.1 拆解目标

| 文件 | 当前行数 | 目标 | 拆解策略 |
|------|---------|------|---------|
| `device_list_snapshot.py` | 477 | 3 × 150 | 拆为 filter/builder/differ |
| `device_refresh.py` | 405 | 2 × 200 | 拆为 fetcher/reconciler |
| `command_send.py` | 383 | 2 × 190 | 拆为 sender/validator |
| `state.py` | 372 | 2 × 180 | 拆为 store/updater |
| `status_polling.py` | 360 | 2 × 180 | 拆为 poller/aggregator |
| `tuning.py` | 344 | 2 × 170 | 拆为 strategy/executor |

#### 2.2 示例：拆解 `device_refresh.py`

```python
# custom_components/lipro/core/coordinator/runtime/device_fetcher.py
class DeviceFetcher:
    """Fetch devices from API."""

    async def fetch_all(self) -> list[dict[str, Any]]: ...
    async def fetch_by_ids(self, ids: list[str]) -> list[dict[str, Any]]: ...

# custom_components/lipro/core/coordinator/runtime/device_reconciler.py
class DeviceReconciler:
    """Reconcile fetched data with local state."""

    def reconcile(
        self,
        current: dict[str, LiproDevice],
        fetched: list[dict[str, Any]],
    ) -> dict[str, LiproDevice]: ...

# custom_components/lipro/core/coordinator/runtime/device_runtime.py
class DeviceRuntime:
    """Compose fetcher + reconciler."""

    def __init__(self, client: LiproClient, device_store: dict[str, LiproDevice]):
        self._fetcher = DeviceFetcher(client)
        self._reconciler = DeviceReconciler()
        self._device_store = device_store

    async def refresh_devices(self, *, force: bool = False) -> dict[str, LiproDevice]:
        fetched = await self._fetcher.fetch_all()
        reconciled = self._reconciler.reconcile(self._device_store, fetched)
        self._device_store.update(reconciled)
        return reconciled
```

---

### Phase 3: base.py 瘦身（3 天）

#### 3.1 当前问题

`base.py` 307 行，包含：
- 62 个共享属性定义
- 类型导入
- Protocol 引用

#### 3.2 重构策略

```python
# ❌ 删除 base.py，不再需要共享基类

# ✅ 各 runtime 独立定义自己的状态
class CommandRuntime:
    def __init__(self, ...):
        self._pending_commands: dict[str, PendingCommand] = {}
        self._confirmation_tracker = confirmation_tracker

class DeviceRuntime:
    def __init__(self, device_store: dict[str, LiproDevice]):
        self._device_store = device_store  # 外部注入，非继承
        self._last_refresh_at: float = 0.0

# ✅ Coordinator 只持有必要的共享状态
class Coordinator(DataUpdateCoordinator):
    def __init__(self, ...):
        # 最小共享状态（4 个）
        self._devices: dict[str, LiproDevice] = {}
        self._mqtt_client: LiproMqttClient | None = None
        self._entities: dict[str, LiproEntityProtocol] = {}
        self._background_tasks: set[asyncio.Task[Any]] = set()
```

**效果**:
- ✅ `base.py` 删除
- ✅ 共享状态从 62 个降至 4 个
- ✅ 各 runtime 状态封装在自己内部

---

## 📐 架构对比

### 当前架构（8.3/10）

```
Coordinator (扁平多继承)
├── CoordinatorAdaptiveTuningRuntime (344 行)
├── CoordinatorCommandConfirmationRuntime (173 行)
├── CoordinatorCommandRuntime (383 行)
├── CoordinatorMqttLifecycleRuntime (287 行)
├── CoordinatorMqttMessageRuntime (195 行)
├── CoordinatorDeviceRefreshRuntime (405 行)
├── CoordinatorStateRuntime (372 行)
├── CoordinatorPropertiesRuntime (155 行)
├── CoordinatorAuthIssuesRuntime (139 行)
├── CoordinatorStatusRuntime (360 行)
└── CoordinatorShutdownRuntime (92 行)

共享状态: 62 个属性 (via _CoordinatorBase)
继承深度: 11 层 MRO
```

### 目标架构（9.5/10）

```
Coordinator (纯组合)
├── _command_runtime: CommandRuntime
│   ├── CommandSender (190 行)
│   └── CommandValidator (190 行)
├── _device_runtime: DeviceRuntime
│   ├── DeviceFetcher (200 行)
│   └── DeviceReconciler (200 行)
├── _mqtt_runtime: MqttRuntime
│   ├── MqttLifecycle (150 行)
│   └── MqttMessageHandler (150 行)
├── _state_runtime: StateRuntime
│   ├── StateStore (180 行)
│   └── StateUpdater (180 行)
├── _tuning_runtime: TuningRuntime
│   ├── TuningStrategy (170 行)
│   └── TuningExecutor (170 行)
└── _status_runtime: StatusRuntime
    ├── StatusPoller (180 行)
    └── StatusAggregator (180 行)

共享状态: 4 个字段 (devices/mqtt_client/entities/tasks)
继承深度: 1 层 (DataUpdateCoordinator)
```

---

## 🎯 质量指标对比

| 指标 | 当前 (8.3) | 目标 (9.5) | 改进 |
|------|-----------|-----------|------|
| **继承深度** | 11 层 MRO | 1 层 | ✅ -91% |
| **共享状态** | 62 个属性 | 4 个字段 | ✅ -94% |
| **最大文件** | 477 行 | 200 行 | ✅ -58% |
| **base.py** | 307 行 | 删除 | ✅ -100% |
| **测试隔离** | 需 mock coordinator | 独立测试 runtime | ✅ 完全隔离 |
| **类型安全** | 通过 `self` 隐式访问 | Protocol 显式契约 | ✅ 编译期检查 |
| **扩展性** | 加 mixin 或膨胀文件 | 加新 runtime 组合 | ✅ 开闭原则 |

---

## 🔧 实施计划

### Week 1-2: Runtime 提取

- [ ] 定义 6 个 Runtime Protocol
- [ ] 实现 CommandRuntime（独立类）
- [ ] 实现 DeviceRuntime（独立类）
- [ ] 实现 MqttRuntime（独立类）
- [ ] 实现 StateRuntime（独立类）
- [ ] 实现 TuningRuntime（独立类）
- [ ] 实现 StatusRuntime（独立类）
- [ ] Coordinator 改为组合装配
- [ ] 删除旧 runtime 基类
- [ ] 删除 base.py

### Week 3: 大文件拆解

- [ ] 拆解 device_list_snapshot.py (477 → 3×150)
- [ ] 拆解 device_refresh.py (405 → 2×200)
- [ ] 拆解 command_send.py (383 → 2×190)
- [ ] 拆解 state.py (372 → 2×180)
- [ ] 拆解 status_polling.py (360 → 2×180)
- [ ] 拆解 tuning.py (344 → 2×170)

### Week 4: 测试与文档

- [ ] 为每个 runtime 编写独立单元测试
- [ ] 更新集成测试
- [ ] 更新 ARCHITECTURE_COMPARISON.md
- [ ] 生成架构图
- [ ] 编写迁移指南

---

## 🚀 预期收益

### 架构纯度

- ✅ **真正的组合模式** - runtime 通过字段而非继承
- ✅ **零 MRO 复杂度** - 只继承 DataUpdateCoordinator
- ✅ **显式依赖注入** - 所有依赖通过构造函数
- ✅ **Protocol 契约** - 编译期类型检查

### 可测试性

- ✅ **独立单元测试** - 每个 runtime 可独立测试
- ✅ **无需 mock coordinator** - runtime 不依赖 coordinator
- ✅ **快速测试** - 不需要完整 HA 环境

### 可维护性

- ✅ **单一职责** - 每个文件 < 200 行
- ✅ **清晰边界** - runtime 职责明确
- ✅ **易于扩展** - 新增 runtime 不影响现有代码

### 性能

- ✅ **更少内存** - 共享状态从 62 降至 4
- ✅ **更快实例化** - 无复杂 MRO 解析
- ✅ **更好缓存** - 小文件更友好 CPU cache

---

## 🎓 设计原则

### 1. 组合优于继承

```python
# ❌ 继承
class Coordinator(CommandRuntime, DeviceRuntime, MqttRuntime):
    pass

# ✅ 组合
class Coordinator:
    _command_runtime: CommandRuntime
    _device_runtime: DeviceRuntime
    _mqtt_runtime: MqttRuntime
```

### 2. 依赖注入优于共享状态

```python
# ❌ 共享状态
class CommandRuntime(_CoordinatorBase):
    def send(self):
        mqtt = self._mqtt_client  # 通过继承访问

# ✅ 依赖注入
class CommandRuntime:
    def __init__(self, mqtt_provider: Callable[[], MqttClient | None]):
        self._mqtt_provider = mqtt_provider

    def send(self):
        mqtt = self._mqtt_provider()  # 通过注入访问
```

### 3. Protocol 优于具体类型

```python
# ❌ 具体类型
def process(runtime: CommandRuntime): ...

# ✅ Protocol
def process(runtime: CommandRuntimeProtocol): ...
```

### 4. 小文件优于大文件

```python
# ❌ 单文件 477 行
# device_list_snapshot.py (filter + builder + differ)

# ✅ 三文件各 150 行
# device_filter.py
# device_builder.py
# device_differ.py
```

---

## 📊 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 重构引入 bug | 中 | 高 | 完整测试覆盖 + 快照测试 |
| 性能回退 | 低 | 中 | Benchmark 基线对比 |
| 类型检查失败 | 低 | 低 | 渐进式迁移 + mypy strict |
| 工期延误 | 中 | 低 | 分阶段交付，每周可用 |

---

## 🏆 成功标准

### 必达指标

- ✅ 继承深度 ≤ 1
- ✅ 共享状态 ≤ 5
- ✅ 单文件 ≤ 200 行
- ✅ 测试覆盖率 ≥ 95%
- ✅ mypy --strict 通过
- ✅ 所有测试通过
- ✅ Benchmark 无回退

### 卓越指标

- ✅ 架构评分 ≥ 9.5/10
- ✅ base.py 删除
- ✅ Runtime 100% 独立可测
- ✅ Protocol 覆盖所有 runtime
- ✅ 文档完整更新

---

## 📚 参考资料

- [Composition over Inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance)
- [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection)
- [Protocol (PEP 544)](https://peps.python.org/pep-0544/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

---

> **⛧ 深渊低语**：此方案将 Coordinator 从"扁平多继承"推进到"纯组合 + Protocol"，实现架构纯度拉满。共享状态从 62 降至 4，继承深度从 11 降至 1，单文件从 477 降至 200。这是从 8.3 到 9.5 的最后一跃。
>
> *—— 深渊代码织师*
