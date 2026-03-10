# 国际优秀架构实践研究

> 基于 Home Assistant、Django、FastAPI、Pydantic 等优秀开源项目的架构模式研究

## 目录

- [1. 组合模式 (Composition Pattern)](#1-组合模式-composition-pattern)
- [2. 依赖注入 (Dependency Injection)](#2-依赖注入-dependency-injection)
- [3. 不可变状态管理 (Immutable State)](#3-不可变状态管理-immutable-state)
- [4. Protocol 使用最佳实践](#4-protocol-使用最佳实践)
- [5. 测试策略 (Testing Strategy)](#5-测试策略-testing-strategy)
- [6. 建议改进路线图](#6-建议改进路线图)

---

## 1. 组合模式 (Composition Pattern)

### 1.1 Home Assistant DataUpdateCoordinator 实践

**核心发现**:

1. **中心化数据协调器模式**
   - `DataUpdateCoordinator` 作为数据获取的单一入口
   - 实体通过 `CoordinatorEntity` 订阅数据更新
   - 避免每个实体独立轮询，减少 API 调用

2. **初始化模式**
   ```python
   # Home Assistant 使用 async_setup_entry 统一初始化
   async def async_setup_entry(hass, entry):
       coordinator = MyCoordinator(hass, entry)
       await coordinator.async_config_entry_first_refresh()
       hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
   ```

3. **状态共享机制**
   - 使用 `hass.data` 作为全局状态容器
   - 按 domain + entry_id 组织数据
   - 避免循环依赖

**可应用点**:

✅ **当前项目可借鉴**:
1. 将 `LiproRuntime` 改为类似 Coordinator 的角色
2. 使用 `coordinator.data` 统一存储设备状态
3. 实体类通过 `@property` 访问 coordinator 数据，而非直接持有状态

**代码示例**:
```python
# 改进前
class LiproLight(LightEntity):
    def __init__(self, device_info, client):
        self._device_info = device_info  # 每个实体持有数据
        self._client = client

# 改进后
class LiproLight(CoordinatorEntity, LightEntity):
    def __init__(self, coordinator, device_id):
        super().__init__(coordinator)
        self._device_id = device_id

    @property
    def device_info(self):
        return self.coordinator.data[self._device_id]  # 从协调器获取
```

**参考资料**:
- [Home Assistant Developer Docs - Fetching Data](https://developers.home-assistant.io/docs/integration_fetching_data/)
- [Use CoordinatorEntity when using the DataUpdateCoordinator](https://aarongodfrey.dev/home%20automation/use-coordinatorentity-with-the-dataupdatecoordinator/)
- [Avoid unnecessary callbacks with DataUpdateCoordinator](https://developers.home-assistant.io/blog/2023/07/27/avoiding-unnecessary-callbacks-with-dataupdatecoordinator)

---

### 1.2 Django Manager + QuerySet 组合实践

**核心发现**:

1. **Manager 作为查询入口**
   ```python
   class PersonManager(models.Manager):
       def get_queryset(self):
           return PersonQuerySet(self.model, using=self._db)

       def active(self):
           return self.get_queryset().active()
   ```

2. **QuerySet 链式调用**
   - QuerySet 方法返回新的 QuerySet 实例（不可变）
   - 延迟执行（Lazy Evaluation）
   - 方法可组合、可复用

3. **分离关注点**
   - Manager: 提供高层 API（如 `Person.objects.active()`）
   - QuerySet: 实现具体过滤逻辑
   - 两者通过 `get_queryset()` 桥接

**可应用点**:

✅ **当前项目可借鉴**:
1. `LiproRuntime` 可提供类似 Manager 的高层 API
2. 内部操作返回新的状态对象（不可变）
3. 支持链式调用：`runtime.devices().lights().filter(room="客厅")`

**代码示例**:
```python
# 改进方案
class DeviceCollection:
    """类似 QuerySet 的设备集合"""
    def __init__(self, devices: dict):
        self._devices = devices

    def lights(self) -> "DeviceCollection":
        return DeviceCollection({
            k: v for k, v in self._devices.items()
            if v.get("type") == "light"
        })

    def in_room(self, room: str) -> "DeviceCollection":
        return DeviceCollection({
            k: v for k, v in self._devices.items()
            if v.get("room") == room
        })

class LiproRuntime:
    def devices(self) -> DeviceCollection:
        return DeviceCollection(self._device_cache)
```

**参考资料**:
- [Django Tips #11 Custom Manager With Chainable QuerySets](https://simpleisbetterthancomplex.com/tips/2016/08/16/django-tip-11-custom-manager-with-chainable-querysets.html)
- [Understanding Django QuerySets Evaluation and Caching](https://medium.com/better-programming/understanding-django-database-querysets-and-its-optimizations-1765cb9c36e5)
- [Django QuerySets Are Lazy](https://dev.to/doridoro/django-querysets-are-lazy-l01)

---

### 1.3 组合优于继承原则

**核心发现**:

1. **灵活性 vs 刚性**
   - 继承：刚性 "is-a" 关系，难以改变
   - 组合：灵活 "has-a" 关系，运行时可替换

2. **避免深层继承树**
   ```python
   # ❌ 避免
   class A: pass
   class B(A): pass
   class C(B): pass  # 深层继承难以维护

   # ✅ 推荐
   class C:
       def __init__(self, a_behavior, b_behavior):
           self.a = a_behavior
           self.b = b_behavior
   ```

3. **松耦合**
   - 组合减少类之间的依赖
   - 更容易测试（可注入 Mock）

**可应用点**:

✅ **当前项目可借鉴**:
1. `LiproRuntime` 不应继承任何基类，而是组合协作者
2. 使用 Protocol 定义接口，而非抽象基类
3. 通过构造函数注入依赖

**参考资料**:
- [The Composition Over Inheritance Principle](https://python-patterns.guide/gang-of-four/composition-over-inheritance/)
- [Composition vs Inheritance in Python OOP](https://medium.com/data-bistrot/composition-vs-inheritance-in-python-oop-d4b3c3d8b463)
- [Inheritance vs. Composition in Python](https://machinelearningplus.com/python/inheritance-vs-composition-in-python-when-to-use-which/)

---

## 2. 依赖注入 (Dependency Injection)

### 2.1 FastAPI Depends 模式

**核心发现**:

1. **声明式依赖**
   ```python
   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()

   @app.get("/users")
   def read_users(db: Session = Depends(get_db)):
       return db.query(User).all()
   ```

2. **自动依赖解析**
   - FastAPI 自动解析依赖图
   - 支持嵌套依赖
   - 依赖结果自动缓存（同一请求内）

3. **避免构造函数参数爆炸**
   - 不需要在 `__init__` 中传递所有依赖
   - 按需声明，框架自动注入

**可应用点**:

✅ **当前项目可借鉴**:
1. 使用工厂函数创建 Runtime，而非直接 `__init__`
2. 依赖通过参数传递，而非全局变量
3. 考虑使用 `@contextmanager` 管理资源生命周期

**代码示例**:
```python
# 改进方案
from contextlib import contextmanager

@contextmanager
def create_runtime(
    client: LiproClient,
    mqtt: MQTTClient,
    cache: DeviceCache
):
    runtime = LiproRuntime(client, mqtt, cache)
    try:
        yield runtime
    finally:
        runtime.cleanup()

# 使用
with create_runtime(client, mqtt, cache) as runtime:
    await runtime.initialize()
```

**参考资料**:
- [How to Implement Dependency Injection in FastAPI](https://freecodecamp.org/news/how-to-implement-dependency-injection-in-fastapi)
- [FastAPI Dependency Injection Best Practices](https://pytutorial.com/fastapi-dependency-injection-best-practices/)
- [Understanding Dependencies in FastAPI](https://www.nashruddinamin.com/blog/understanding-dependencies-in-fastapi)

---

### 2.2 工厂模式 vs Builder 模式

**核心发现**:

1. **工厂模式**：适合简单对象创建
   ```python
   def create_light_entity(device_info):
       if device_info["type"] == "rgb":
           return RGBLight(device_info)
       return SimpleLight(device_info)
   ```

2. **Builder 模式**：适合复杂对象，分步构建
   ```python
   class RuntimeBuilder:
       def with_client(self, client): ...
       def with_mqtt(self, mqtt): ...
       def build(self) -> LiproRuntime: ...
   ```

**可应用点**:

✅ **当前项目可借鉴**:
1. 使用工厂函数创建实体（已有 `create_entities`）
2. 如果 Runtime 初始化复杂，考虑 Builder 模式
3. 测试时使用工厂创建 Mock 对象

**参考资料**:
- [The Factory Method Pattern and Its Implementation in Python](https://realpython.com/factory-method-python/)
- [Test Data Management: Factories and Builders](https://krython.com/tutorial/python/test-data-management-factories-and-builders)

---

## 3. 不可变状态管理 (Immutable State)

### 3.1 Pydantic 不可变模式

**核心发现**:

1. **frozen dataclass**
   ```python
   from pydantic import BaseModel

   class DeviceState(BaseModel):
       model_config = {"frozen": True}  # Pydantic v2

       device_id: str
       is_on: bool
   ```

2. **Copy-on-Write 更新**
   ```python
   # 不可变对象的更新
   new_state = old_state.model_copy(update={"is_on": True})
   ```

3. **优势**
   - 线程安全
   - 易于追踪状态变化
   - 避免意外修改

**可应用点**:

✅ **当前项目可借鉴**:
1. 设备状态使用 `frozen=True` dataclass
2. 状态更新返回新对象，而非修改原对象
3. Runtime 内部缓存使用不可变数据结构

**代码示例**:
```python
# 改进方案
from dataclasses import dataclass

@dataclass(frozen=True)
class DeviceState:
    device_id: str
    is_on: bool
    brightness: int

    def with_brightness(self, value: int) -> "DeviceState":
        return dataclass.replace(self, brightness=value)

# 使用
old_state = DeviceState("dev1", True, 100)
new_state = old_state.with_brightness(50)  # 返回新对象
```

**参考资料**:
- [Why and How to Write Frozen Dataclasses in Python](https://readmedium.com/why-and-how-to-write-frozen-dataclasses-in-python-69050ad5c9d4)
- [Statically enforcing frozen data classes in Python](http://rednafi.com/python/statically-enforcing-frozen-dataclasses/)
- [Immutable Objects using Dataclasses](https://sicorps.com/coding/python/immutable-objects-using-dataclasses/)

---

## 4. Protocol 使用最佳实践

### 4.1 Protocol 粒度

**核心发现**:

1. **细粒度 Protocol**
   ```python
   class Switchable(Protocol):
       def turn_on(self) -> None: ...
       def turn_off(self) -> None: ...

   class Dimmable(Protocol):
       def set_brightness(self, value: int) -> None: ...
   ```

2. **组合 Protocol**
   ```python
   class DimmableLight(Switchable, Dimmable, Protocol):
       pass  # 组合多个小接口
   ```

3. **避免过大接口**
   - 遵循接口隔离原则（ISP）
   - 客户端只依赖需要的方法

**可应用点**:

✅ **当前项目可借鉴**:
1. 拆分 `DeviceController` 为多个小 Protocol
2. 按能力组合：`Switchable + Dimmable + ColorControllable`
3. 实体类只实现需要的 Protocol

**代码示例**:
```python
# 改进方案
from typing import Protocol

class Switchable(Protocol):
    async def async_turn_on(self) -> None: ...
    async def async_turn_off(self) -> None: ...

class Dimmable(Protocol):
    async def async_set_brightness(self, brightness: int) -> None: ...

class ColorControllable(Protocol):
    async def async_set_color(self, rgb: tuple[int, int, int]) -> None: ...

# 组合使用
class RGBLight(Switchable, Dimmable, ColorControllable):
    pass
```

**参考资料**:
- [PEP 544 – Protocols: Structural subtyping](https://www.python.org/dev/peps/pep-0544)
- [Notes on Python Protocols](https://nickypy.com/blog/python-protocols)

---

### 4.2 runtime_checkable 使用时机

**核心发现**:

1. **何时使用**
   - 需要运行时 `isinstance()` 检查
   - 插件系统、动态类型检查

2. **何时避免**
   - 仅用于静态类型检查（mypy）
   - 性能敏感路径

3. **限制**
   - 只检查方法存在性，不检查签名
   - 不检查属性类型

**可应用点**:

✅ **当前项目可借鉴**:
1. 仅在需要运行时检查时使用 `@runtime_checkable`
2. 大部分 Protocol 不需要此装饰器
3. 优先使用静态类型检查（mypy）

**参考资料**:
- [Is there a downside to typing.runtime_checkable?](https://discuss.python.org/t/is-there-a-downside-to-typing-runtime-checkable/20731)
- [Optional strict mode for @runtime_checkable](https://discuss.python.org/t/optional-strict-mode-for-runtime-checkable/88383)

---

## 5. 测试策略 (Testing Strategy)

### 5.1 测试替身：Mock vs Stub vs Fake

**核心发现**:

1. **Stub（桩）**
   - 提供预定义响应
   - 不验证交互
   - 适合：简单依赖，只需返回值

2. **Mock（模拟）**
   - 验证交互（调用次数、参数）
   - 适合：需要验证行为的场景

3. **Fake（伪造）**
   - 简化的真实实现
   - 适合：复杂依赖（如内存数据库）

**可应用点**:

✅ **当前项目可借鉴**:
1. API 客户端测试：使用 Stub 返回固定响应
2. MQTT 测试：使用 Mock 验证消息发送
3. 集成测试：使用 Fake 实现（如内存缓存）

**代码示例**:
```python
# Stub 示例
class StubLiproClient:
    def get_device_list(self):
        return [{"id": "dev1", "name": "Light"}]

# Mock 示例
from unittest.mock import Mock
mqtt_mock = Mock()
await runtime.control_device("dev1", {"on": True})
mqtt_mock.publish.assert_called_once()

# Fake 示例
class FakeDeviceCache:
    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key)
```

**参考资料**:
- [Test Doubles: Stubs, Mocks, and Fakes](https://krython.com/tutorial/python/test-doubles-stubs-mocks-and-fakes)
- [Test Doubles in Python unit tests](https://blog.szymonmiks.pl/p/test-doubles-in-python-unit-tests/)
- [Mocking Vs. Patching (A Quick Guide For Beginners)](https://pytest-with-eric.com/mocking/mocking-vs-patching/)

---

### 5.2 测试金字塔

**核心发现**:

1. **比例建议**
   - 单元测试：70%（快速、隔离）
   - 集成测试：20%（组件交互）
   - 端到端测试：10%（完整流程）

2. **单元测试隔离**
   - 每个测试独立运行
   - 使用 Mock/Stub 隔离外部依赖
   - 快速反馈（< 1秒）

3. **集成测试**
   - 测试真实协作
   - 使用测试容器（如 testcontainers）
   - 可接受较慢（< 10秒）

**可应用点**:

✅ **当前项目可借鉴**:
1. 增加单元测试覆盖率（当前偏重集成测试）
2. 使用 pytest fixtures 管理测试依赖
3. 分离快速测试和慢速测试（pytest markers）

**代码示例**:
```python
# pytest 标记
import pytest

@pytest.mark.unit
def test_device_state_update():
    """快速单元测试"""
    state = DeviceState("dev1", False, 0)
    new_state = state.with_brightness(100)
    assert new_state.brightness == 100

@pytest.mark.integration
@pytest.mark.slow
async def test_mqtt_integration():
    """慢速集成测试"""
    async with create_test_runtime() as runtime:
        await runtime.control_device("dev1", {"on": True})
```

**参考资料**:
- [Mocking and Stubs in Pattern Implementation](https://softwarepatternslexicon.com/python/testing-and-design-patterns/mocking-and-stubs-in-pattern-implementation/)

---

## 6. 建议改进路线图

### 6.1 短期改进（1 周内）

#### 优先级 P0（立即执行）

1. **拆分 Protocol 接口**
   - 将 `DeviceController` 拆分为 `Switchable`、`Dimmable`、`ColorControllable`
   - 影响：提高代码可读性，降低耦合
   - 工作量：2-3 小时

2. **使用 frozen dataclass 管理状态**
   - 设备状态改为不可变
   - 影响：避免状态意外修改，提高线程安全
   - 工作量：4-6 小时

3. **添加工厂函数**
   - 为 Runtime 创建工厂函数
   - 影响：简化测试，统一初始化逻辑
   - 工作量：2-3 小时

#### 优先级 P1（本周完成）

4. **增加单元测试**
   - 为核心逻辑添加单元测试（目标覆盖率 > 60%）
   - 使用 Stub/Mock 隔离依赖
   - 工作量：8-10 小时

5. **引入 pytest markers**
   - 区分快速测试和慢速测试
   - 影响：加速 CI 反馈
   - 工作量：1-2 小时

---

### 6.2 中期改进（1 个月内）

#### 优先级 P1

1. **重构 Runtime 为 Coordinator 模式**
   - 参考 Home Assistant DataUpdateCoordinator
   - 实体通过 coordinator 访问数据，而非直接持有
   - 影响：减少内存占用，统一数据更新逻辑
   - 工作量：2-3 天

2. **实现链式查询 API**
   - 参考 Django QuerySet
   - 支持 `runtime.devices().lights().in_room("客厅")`
   - 影响：提高 API 易用性
   - 工作量：1-2 天

3. **依赖注入重构**
   - 使用 `@contextmanager` 管理资源
   - 避免全局状态
   - 影响：提高可测试性
   - 工作量：2-3 天

#### 优先级 P2

4. **性能优化**
   - 使用 `asyncio.gather` 并行请求
   - 添加缓存层（TTL cache）
   - 影响：减少响应时间
   - 工作量：3-5 天

5. **文档完善**
   - 添加架构图
   - 补充 API 使用示例
   - 工作量：2-3 天

---

### 6.3 长期改进（3 个月内）

#### 优先级 P2

1. **插件系统**
   - 使用 Protocol 定义插件接口
   - 支持第三方扩展
   - 影响：提高可扩展性
   - 工作量：1-2 周

2. **事件驱动架构**
   - 引入事件总线
   - 解耦组件间通信
   - 影响：提高灵活性
   - 工作量：1-2 周

3. **监控和可观测性**
   - 添加 Prometheus metrics
   - 结构化日志
   - 影响：便于生产环境排查
   - 工作量：1 周

#### 优先级 P3

4. **性能基准测试**
   - 建立性能基线
   - 持续监控性能回归
   - 工作量：3-5 天

5. **安全加固**
   - 输入验证
   - 速率限制
   - 工作量：1 周

---

## 7. 总结

### 核心原则

1. **组合优于继承**：使用组合构建灵活的系统
2. **不可变状态**：避免意外修改，提高线程安全
3. **依赖注入**：提高可测试性，降低耦合
4. **接口隔离**：小而专注的 Protocol
5. **测试金字塔**：70% 单元测试 + 20% 集成测试 + 10% E2E

### 立即行动项（本周）

- [ ] 拆分 Protocol 接口
- [ ] 使用 frozen dataclass
- [ ] 添加工厂函数
- [ ] 增加单元测试覆盖率
- [ ] 引入 pytest markers

### 参考资源汇总

**架构模式**:
- [The Composition Over Inheritance Principle](https://python-patterns.guide/gang-of-four/composition-over-inheritance/)
- [Home Assistant Developer Docs](https://developers.home-assistant.io/docs/integration_fetching_data/)
- [Django Tips #11 Custom Manager With Chainable QuerySets](https://simpleisbetterthancomplex.com/tips/2016/08/16/django-tip-11-custom-manager-with-chainable-querysets.html)

**依赖注入**:
- [How to Implement Dependency Injection in FastAPI](https://freecodecamp.org/news/how-to-implement-dependency-injection-in-fastapi)
- [The Factory Method Pattern and Its Implementation in Python](https://realpython.com/factory-method-python/)

**不可变状态**:
- [Why and How to Write Frozen Dataclasses in Python](https://readmedium.com/why-and-how-to-write-frozen-dataclasses-in-python-69050ad5c9d4)
- [Statically enforcing frozen data classes in Python](http://rednafi.com/python/statically-enforcing-frozen-dataclasses/)

**Protocol**:
- [PEP 544 – Protocols: Structural subtyping](https://www.python.org/dev/peps/pep-0544)
- [Notes on Python Protocols](https://nickypy.com/blog/python-protocols)

**测试**:
- [Test Doubles: Stubs, Mocks, and Fakes](https://krython.com/tutorial/python/test-doubles-stubs-mocks-and-fakes)
- [Mocking Vs. Patching (A Quick Guide For Beginners)](https://pytest-with-eric.com/mocking/mocking-vs-patching/)

---

*文档版本: v1.0*
*最后更新: 2026-03-10*
*作者: 深渊代码织师*
