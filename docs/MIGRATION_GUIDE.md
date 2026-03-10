# Coordinator 架构迁移指南

## 📋 概述

本指南帮助开发者从基于 Mixin 继承的旧架构迁移到纯组合模式的新架构。

### 迁移背景

Lipro 集成的 Coordinator 经历了一次重大架构重构，从深度继承链（11 层 Mixin）转变为纯组合模式（Runtime 组件）。这次重构显著提升了代码的可测试性、可维护性和类型安全性。

**重构时间线**:
- **重构前**: Commit `775a64f` (2026-03-09)
- **重构后**: Commit `bfa9bac` → `295ee61` (2026-03-10)

### 为什么要迁移？

| 问题 | 旧架构 | 新架构 |
|------|--------|--------|
| **继承深度** | 11 层 Mixin 继承 | 1 层 (DataUpdateCoordinator) |
| **职责分离** | 混杂在 Mixin 中 | 独立 Runtime 组件 |
| **状态管理** | 共享 `self` 状态 | `CoordinatorSharedState` 显式管理 |
| **依赖注入** | 隐式继承 | 显式构造器注入 |
| **可测试性** | 需要 Mock 整个 Coordinator | 独立测试 Runtime 组件 |
| **类型安全** | 弱类型，依赖鸭子类型 | Protocol 定义契约 |

---

## 🏗️ 架构变化对比

### 旧架构 (775a64f)

```python
# 11 层 Mixin 继承
class Coordinator(
    CoordinatorAdaptiveTuningRuntime,           # 1. 自适应调优
    CoordinatorCommandConfirmationRuntime,      # 2. 命令确认
    CoordinatorCommandRuntime,                  # 3. 命令发送
    CoordinatorMqttLifecycleRuntime,            # 4. MQTT 生命周期
    CoordinatorMqttMessageRuntime,              # 5. MQTT 消息处理
    CoordinatorDeviceRefreshRuntime,            # 6. 设备刷新
    CoordinatorStateRuntime,                    # 7. 状态管理
    CoordinatorPropertiesRuntime,               # 8. 属性访问
    CoordinatorAuthIssuesRuntime,               # 9. 认证问题处理
    CoordinatorStatusRuntime,                   # 10. 状态轮询
    CoordinatorShutdownRuntime,                 # 11. 关闭清理
):
    """深度继承链，职责混杂."""

    def __init__(self, ...):
        super().__init__(...)  # 调用 11 层父类
        self._devices = {}     # 共享状态
        self._entities = {}
        # ... 大量状态变量
```

**问题**:
- 继承链过深，难以理解调用顺序
- 状态散落在各个 Mixin 中
- 测试需要 Mock 整个继承链
- 循环依赖风险高

### 新架构 (bfa9bac+)

```python
# 纯组合，无 Mixin
class Coordinator(DataUpdateCoordinator[dict[str, LiproDevice]]):
    """纯组合模式，显式依赖注入."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LiproClient,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ):
        super().__init__(...)  # 只继承 DataUpdateCoordinator

        # 共享状态容器
        self._shared_state = CoordinatorSharedState(
            devices={},
            entities={},
            entities_by_device={},
            # ...
        )

        # Runtime 组件（依赖注入）
        self._command_runtime = CommandRuntime(
            client=client,
            mqtt_client_provider=lambda: self._mqtt_client,
            confirmation_tracker=self._confirmation_tracker,
        )

        self._device_runtime = DeviceRuntime(
            client=client,
            shared_state=self._shared_state,
            identity_index=self._identity_index,
        )

        self._mqtt_runtime = MqttRuntime(...)
        self._state_runtime = StateRuntime(...)
        self._status_runtime = StatusRuntime(...)
        self._tuning_runtime = TuningRuntime(...)
```

**优势**:
- 继承深度从 11 层降至 1 层
- 职责清晰，每个 Runtime 专注单一功能
- 依赖显式，易于测试和替换
- 类型安全，Protocol 定义契约

---

## 🔄 代码迁移示例

### 1. 访问设备状态

#### 旧代码 (Mixin 方式)

```python
# 在 CoordinatorStateRuntime Mixin 中
class CoordinatorStateRuntime(_CoordinatorBase):
    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """直接访问 self._devices."""
        return self._devices.get(device_id)

    def get_all_devices(self) -> dict[str, LiproDevice]:
        """返回共享状态."""
        return self._devices
```

#### 新代码 (Runtime 组件)

```python
# 在 StateRuntime 组件中
class StateRuntime:
    def __init__(self, shared_state: CoordinatorSharedState):
        self._shared_state = shared_state

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """通过共享状态访问."""
        return self._shared_state.devices.get(device_id)

    def get_all_devices(self) -> dict[str, LiproDevice]:
        """返回不可变视图."""
        return self._shared_state.devices.copy()

# 在 Coordinator 中调用
device = self._state_runtime.get_device_by_id(device_id)
```

**迁移要点**:
- ✅ 状态访问通过 `CoordinatorSharedState`
- ✅ Runtime 组件不直接修改状态
- ✅ 返回不可变视图避免意外修改

---

### 2. 发送设备命令

#### 旧代码 (Mixin 方式)

```python
# 在 CoordinatorCommandRuntime Mixin 中
class CoordinatorCommandRuntime(_CoordinatorBase):
    async def send_device_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """直接访问 self.client, self._mqtt_client."""
        # 复杂的命令发送逻辑
        result = await execute_command_plan_with_trace(...)
        self._track_command_expectation(...)  # 访问其他 Mixin 方法
        return result

# 在实体中调用
await self.coordinator.send_device_command(device, "switch", [{"switch": "on"}])
```

#### 新代码 (Runtime 组件)

```python
# 在 CommandRuntime 组件中
class CommandRuntime:
    def __init__(
        self,
        client: LiproClient,
        mqtt_client_provider: Callable[[], LiproMqttClient | None],
        confirmation_tracker: CommandConfirmationTracker,
    ):
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
        """显式依赖注入，职责单一."""
        # 命令发送逻辑
        result = await execute_command_plan_with_trace(...)
        return CommandResult(success=True, trace=result)

# 在 Coordinator 中调用
result = await self._command_runtime.send_command(
    device_id=device.serial,
    command={"command": "switch", "properties": [{"switch": "on"}]},
)
```

**迁移要点**:
- ✅ 依赖通过构造器注入
- ✅ 返回结构化 `CommandResult`
- ✅ 不依赖其他 Mixin 方法

---

### 3. 刷新设备列表

#### 旧代码 (Mixin 方式)

```python
# 在 CoordinatorDeviceRefreshRuntime Mixin 中
class CoordinatorDeviceRefreshRuntime(_CoordinatorBase):
    async def _fetch_devices(self) -> None:
        """直接修改 self._devices."""
        raw_devices = await self.client.async_get_device_list()
        self._devices = self._build_device_snapshot(raw_devices)
        self._last_device_refresh = monotonic()

# 在 Coordinator 中调用
await self._fetch_devices()
```

#### 新代码 (Runtime 组件)

```python
# 在 DeviceRuntime 组件中
class DeviceRuntime:
    def __init__(
        self,
        client: LiproClient,
        shared_state: CoordinatorSharedState,
        identity_index: DeviceIdentityIndex,
    ):
        self._client = client
        self._shared_state = shared_state
        self._identity_index = identity_index

    async def refresh_devices(self, *, force: bool = False) -> None:
        """通过共享状态更新设备."""
        if not force and not self.should_refresh_device_list():
            return

        raw_devices = await self._client.async_get_device_list()
        devices = self._build_device_snapshot(raw_devices)

        # 更新共享状态
        self._shared_state.devices.clear()
        self._shared_state.devices.update(devices)
        self._last_device_refresh = monotonic()

# 在 Coordinator 中调用
await self._device_runtime.refresh_devices(force=True)
```

**迁移要点**:
- ✅ 状态更新通过 `CoordinatorSharedState`
- ✅ 支持增量刷新和强制刷新
- ✅ 时间戳管理在 Runtime 内部

---

### 4. MQTT 消息处理

#### 旧代码 (Mixin 方式)

```python
# 在 CoordinatorMqttMessageRuntime Mixin 中
class CoordinatorMqttMessageRuntime(_CoordinatorBase):
    def _handle_mqtt_message(self, topic: str, payload: dict[str, Any]) -> None:
        """直接访问 self._devices, self._entities."""
        device_id = self._extract_device_id(topic)
        device = self._devices.get(device_id)
        if device:
            device.update_from_mqtt(payload)
            self._notify_entities(device_id)

# MQTT 客户端回调
coordinator._handle_mqtt_message(topic, payload)
```

#### 新代码 (Runtime 组件)

```python
# 在 MqttRuntime 组件中
class MqttRuntime:
    def __init__(
        self,
        mqtt_client: LiproMqttClient,
        shared_state: CoordinatorSharedState,
        message_processor: MqttMessageProcessor,
    ):
        self._mqtt_client = mqtt_client
        self._shared_state = shared_state
        self._message_processor = message_processor

    async def handle_message(self, topic: str, payload: dict[str, Any]) -> None:
        """处理 MQTT 消息."""
        device_id = self._message_processor.extract_device_id(topic)
        device = self._shared_state.devices.get(device_id)

        if device:
            device.update_from_mqtt(payload)
            await self._notify_entities(device_id)

# MQTT 客户端回调
await coordinator._mqtt_runtime.handle_message(topic, payload)
```

**迁移要点**:
- ✅ 消息处理逻辑独立
- ✅ 通过共享状态访问设备
- ✅ 异步通知实体更新

---

## 🧪 测试迁移

### 旧测试方式 (Mock Coordinator)

```python
@pytest.fixture
def coordinator(hass, client, auth_manager, config_entry):
    """需要 Mock 整个 Coordinator."""
    coordinator = Coordinator(hass, client, auth_manager, config_entry)

    # 需要设置大量 Mock
    coordinator._mqtt_client = Mock()
    coordinator._devices = {
        "device1": Mock(serial="device1", name="Light"),
    }
    coordinator._entities = {}
    coordinator._confirmation_tracker = Mock()
    # ... 更多 Mock

    return coordinator

async def test_send_command(coordinator):
    """测试命令发送."""
    # 需要 Mock 多个 Mixin 方法
    coordinator._track_command_expectation = Mock()
    coordinator._schedule_post_command_refresh = Mock()

    result = await coordinator.send_device_command(
        device=coordinator._devices["device1"],
        command="switch",
        properties=[{"switch": "on"}],
    )

    assert result["success"]
```

**问题**:
- ❌ 需要 Mock 大量内部状态
- ❌ 测试脆弱，依赖实现细节
- ❌ 难以隔离测试单一功能

---

### 新测试方式 (独立 Runtime)

```python
@pytest.fixture
def command_runtime(client):
    """只需要 Mock 直接依赖."""
    return CommandRuntime(
        client=client,
        mqtt_client_provider=lambda: None,
        confirmation_tracker=Mock(),
    )

async def test_send_command(command_runtime, client):
    """测试命令发送."""
    # Mock API 响应
    client.async_send_command = AsyncMock(return_value={"success": True})

    result = await command_runtime.send_command(
        device_id="device1",
        command={"command": "switch", "properties": [{"switch": "on"}]},
    )

    assert result.success
    assert "trace" in result.trace
    client.async_send_command.assert_called_once()
```

**优势**:
- ✅ 只 Mock 直接依赖
- ✅ 测试独立，不依赖其他组件
- ✅ 易于编写和维护

---

### 集成测试示例

```python
@pytest.fixture
async def coordinator(hass, client, auth_manager, config_entry):
    """集成测试使用真实 Coordinator."""
    coordinator = Coordinator(hass, client, auth_manager, config_entry)
    await coordinator.async_config_entry_first_refresh()
    return coordinator

async def test_full_command_flow(coordinator, client):
    """测试完整命令流程."""
    # Mock API 响应
    client.async_send_command = AsyncMock(return_value={"success": True})

    # 通过 Coordinator 发送命令
    result = await coordinator._command_runtime.send_command(
        device_id="device1",
        command={"command": "switch", "properties": [{"switch": "on"}]},
    )

    assert result.success

    # 验证设备状态更新
    device = coordinator._state_runtime.get_device_by_id("device1")
    assert device is not None
```

---

## 📚 常见问题 (FAQ)

### Q1: 如何访问旧的 Mixin 方法？

**A**: 旧的 Mixin 方法已被移到对应的 Runtime 组件中。

| 旧 Mixin | 新 Runtime | 位置 |
|----------|-----------|------|
| `CoordinatorStateRuntime` | `StateRuntime` | `core/coordinator/runtime/state_runtime.py` |
| `CoordinatorCommandRuntime` | `CommandRuntime` | `core/coordinator/runtime/command_runtime.py` |
| `CoordinatorDeviceRefreshRuntime` | `DeviceRuntime` | `core/coordinator/runtime/device_runtime.py` |
| `CoordinatorMqttLifecycleRuntime` | `MqttRuntime` | `core/coordinator/runtime/mqtt_runtime.py` |
| `CoordinatorStatusRuntime` | `StatusRuntime` | `core/coordinator/runtime/status_runtime.py` |
| `CoordinatorAdaptiveTuningRuntime` | `TuningRuntime` | `core/coordinator/runtime/tuning_runtime.py` |

**迁移步骤**:
1. 找到旧方法所在的 Mixin
2. 查看对应的 Runtime 组件
3. 通过 `coordinator._xxx_runtime` 调用

---

### Q2: 为什么测试失败？

**A**: 检查以下几点：

1. **Import 路径错误**
   ```python
   # ❌ 旧路径
   from custom_components.lipro.core.coordinator.state import CoordinatorStateRuntime

   # ✅ 新路径
   from custom_components.lipro.core.coordinator.runtime.state_runtime import StateRuntime
   ```

2. **方法签名变化**
   ```python
   # ❌ 旧方法
   await coordinator.send_device_command(device, "switch", [{"switch": "on"}])

   # ✅ 新方法
   await coordinator._command_runtime.send_command(
       device_id=device.serial,
       command={"command": "switch", "properties": [{"switch": "on"}]},
   )
   ```

3. **状态访问方式**
   ```python
   # ❌ 直接访问
   devices = coordinator._devices

   # ✅ 通过 Runtime
   devices = coordinator._state_runtime.get_all_devices()
   ```

---

### Q3: 如何添加新功能？

**A**: 在对应的 Runtime 组件中添加，而不是创建新的 Mixin。

**步骤**:
1. 确定功能属于哪个 Runtime（命令/设备/MQTT/状态/状态轮询/调优）
2. 在对应 Runtime 中添加方法
3. 如果需要新的 Runtime，创建新组件并在 `Coordinator.__init__` 中注入
4. 更新 `protocols.py` 定义契约

**示例**:
```python
# 在 CommandRuntime 中添加批量命令
class CommandRuntime:
    async def send_batch_commands(
        self,
        commands: list[tuple[str, dict[str, Any]]],
    ) -> list[CommandResult]:
        """发送批量命令."""
        results = []
        for device_id, command in commands:
            result = await self.send_command(device_id, command)
            results.append(result)
        return results
```

---

### Q4: 如何理解 `CoordinatorSharedState`？

**A**: `CoordinatorSharedState` 是新架构的核心状态容器。

**设计原则**:
- 所有共享状态集中管理
- Runtime 组件通过引用访问
- 避免状态散落在各个组件中

**结构**:
```python
@dataclass
class CoordinatorSharedState:
    """Coordinator 共享状态容器."""

    # 设备状态
    devices: dict[str, LiproDevice]

    # 实体注册
    entities: dict[str, LiproEntityProtocol]
    entities_by_device: dict[str, list[LiproEntityProtocol]]

    # 运行时状态
    last_device_refresh: float
    last_status_update: float

    # 配置选项
    mqtt_enabled: bool
    debug_mode: bool
    # ...
```

**使用方式**:
```python
# 在 Runtime 中访问
class DeviceRuntime:
    def __init__(self, shared_state: CoordinatorSharedState):
        self._shared_state = shared_state

    def get_device_count(self) -> int:
        return len(self._shared_state.devices)
```

---

### Q5: 性能是否受影响？

**A**: 委托开销 < 5%，可接受。

**性能对比** (来自 `REFACTOR_QUALITY_REPORT.md`):
- 方法调用增加一层委托
- 内存占用略有增加（Runtime 对象）
- 启动时间基本无变化

**优化建议**:
- 避免频繁创建 Runtime 对象
- 使用缓存减少重复计算
- 批量操作优于单次调用

---

## ✅ 迁移检查清单

### 代码迁移

- [ ] 更新 import 语句到新 Runtime 路径
- [ ] 替换 Mixin 方法调用为 Runtime 方法
- [ ] 更新方法签名和参数
- [ ] 移除对 `_CoordinatorBase` 的依赖
- [ ] 使用 `CoordinatorSharedState` 访问状态

### 测试迁移

- [ ] 更新测试使用独立 Runtime
- [ ] 移除不必要的 Mock
- [ ] 添加 Runtime 单元测试
- [ ] 验证集成测试通过
- [ ] 检查测试覆盖率

### 质量验证

- [ ] 运行类型检查: `uv run mypy --hide-error-context --no-error-summary`
- [ ] 运行代码检查: `uv run ruff check .`
- [ ] 运行测试套件: `uv run pytest tests/ --ignore=tests/benchmarks -q`
- [ ] 检查覆盖率: `uv run pytest --cov=custom_components/lipro --cov-report=json`
- [ ] 验证功能等价性

### 文档更新

- [ ] 更新 API 文档
- [ ] 更新架构图
- [ ] 更新开发者指南
- [ ] 添加迁移示例

---

## 📖 参考资源

### 项目文档

- [重构质量报告](./REFACTOR_QUALITY_REPORT.md) - 详细的架构对比和质量分析
- [最佳实践研究](./BEST_PRACTICES_RESEARCH.md) - 国际优秀项目的架构模式
- [开发者架构指南](./developer_architecture.md) - 新架构的详细说明
- [测试指南](./developer_testing_guide.md) - 测试策略和示例

### 核心文件

- `custom_components/lipro/core/coordinator/coordinator.py` - Coordinator 主文件
- `custom_components/lipro/core/coordinator/runtime/protocols.py` - Runtime 契约定义
- `custom_components/lipro/core/coordinator/runtime/shared_state.py` - 共享状态容器
- `custom_components/lipro/core/coordinator/runtime/*_runtime.py` - 各 Runtime 实现

### 外部资源

- [Home Assistant Developer Docs](https://developers.home-assistant.io/docs/integration_fetching_data/)
- [Composition Over Inheritance](https://python-patterns.guide/gang-of-four/composition-over-inheritance/)
- [PEP 544 – Protocols](https://www.python.org/dev/peps/pep-0544)

---

## 🎯 总结

### 迁移收益

| 维度 | 改进 |
|------|------|
| **可测试性** | ⭐⭐⭐⭐⭐ 独立测试 Runtime |
| **可维护性** | ⭐⭐⭐⭐⭐ 职责清晰，易于修改 |
| **类型安全** | ⭐⭐⭐⭐⭐ Protocol 定义契约 |
| **扩展性** | ⭐⭐⭐⭐⭐ 组合优于继承 |
| **性能** | ⭐⭐⭐⭐☆ 委托开销 < 5% |

### 迁移成本

- **学习曲线**: 需要理解新的 Runtime 组件结构
- **代码修改**: 需要更新 import 和方法调用
- **测试更新**: 需要重写部分测试

### 建议

1. **优先迁移核心功能**: 命令发送、设备刷新、状态管理
2. **逐步迁移测试**: 先迁移单元测试，再迁移集成测试
3. **保持功能等价**: 确保迁移后行为一致
4. **利用类型检查**: 使用 mypy 发现潜在问题

---

**文档版本**: v1.0
**最后更新**: 2026-03-10
**作者**: 深渊代码织师
**适用版本**: Commit `bfa9bac` 及之后
