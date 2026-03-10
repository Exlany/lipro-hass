# 🜄 并行重构执行计划

> **基于 PERFECT_ARCHITECTURE_PLAN.md 的多代理协同重构方案**
>
> 目标：8.3/10 → 9.5/10 | 预计工期：3 周 | 并行度：6 个子代理

---

## 🎯 总体策略

### 核心原则

1. **无历史包袱** - 项目未发布，直接按最优架构重构
2. **并行优先** - 6 个独立任务流，最大化并行度
3. **主代理调度** - 负责任务分发、进度监控、冲突仲裁、质量复查
4. **原子提交** - 每个子任务独立 commit，便于回滚
5. **持续验证** - 每个 checkpoint 必须通过测试

### 并行拓扑

```
主代理 (Orchestrator)
├─ Agent-1: Runtime Protocol 定义 (基础设施)
├─ Agent-2: Command Runtime 重构 (独立)
├─ Agent-3: Device Runtime 重构 (独立)
├─ Agent-4: MQTT Runtime 重构 (独立)
├─ Agent-5: State/Status/Tuning Runtime 重构 (独立)
└─ Agent-6: Coordinator 组合装配 (依赖 1-5)
```

---

## 📋 任务分工矩阵

### Agent-1: Runtime Protocol 定义 (P0 - 基础设施)

**负责人**: Agent-1
**优先级**: P0 (阻塞其他任务)
**预计工期**: 2 天
**依赖**: 无
**产出**: Runtime Protocol 契约层

#### 任务清单

- [ ] **Task 1.1**: 创建 `runtime/protocols.py`
  - 定义 `CommandRuntimeProtocol`
  - 定义 `DeviceRuntimeProtocol`
  - 定义 `MqttRuntimeProtocol`
  - 定义 `StateRuntimeProtocol`
  - 定义 `TuningRuntimeProtocol`
  - 定义 `StatusRuntimeProtocol`
  - 添加完整类型注解和文档

- [ ] **Task 1.2**: 创建 `runtime/shared_state.py`
  - 定义 `CoordinatorSharedState` dataclass
  - 包含设备缓存、MQTT 状态、命令队列等
  - 提供不可变访问接口

- [ ] **Task 1.3**: 类型检查验证
  - `uv run mypy runtime/protocols.py --strict`
  - `uv run mypy runtime/shared_state.py --strict`

#### 验收标准

```bash
# 类型检查通过
uv run mypy custom_components/lipro/core/coordinator/runtime/protocols.py --strict
uv run mypy custom_components/lipro/core/coordinator/runtime/shared_state.py --strict

# 文档完整
grep -c "Protocol" runtime/protocols.py  # >= 6
grep -c '"""' runtime/protocols.py       # >= 12
```

#### Commit 规范

```
refactor(coordinator): define runtime protocols for pure composition

- Add CommandRuntimeProtocol with send/batch methods
- Add DeviceRuntimeProtocol with refresh methods
- Add MqttRuntimeProtocol with connection lifecycle
- Add StateRuntimeProtocol with device state management
- Add TuningRuntimeProtocol with adaptive tuning
- Add StatusRuntimeProtocol with polling methods
- Add CoordinatorSharedState for immutable state access

BREAKING CHANGE: Introduces new protocol layer for runtime composition
```

---

### Agent-2: Command Runtime 重构 (P1 - 独立)

**负责人**: Agent-2
**优先级**: P1
**预计工期**: 3 天
**依赖**: Agent-1 完成
**产出**: 独立 Command Runtime

#### 任务清单

- [ ] **Task 2.1**: 拆解 `command_send.py` (383 行)
  - 创建 `runtime/command/builder.py` - 命令构建逻辑
  - 创建 `runtime/command/sender.py` - 命令发送逻辑
  - 创建 `runtime/command/retry.py` - 重试策略
  - 每个文件 < 150 行

- [ ] **Task 2.2**: 实现 `CommandRuntime` 类
  - 创建 `runtime/command_runtime.py`
  - 实现 `CommandRuntimeProtocol`
  - 通过构造函数注入依赖（不继承 base）
  - 移除对 `self.coordinator` 的依赖

- [ ] **Task 2.3**: 重构 `command_confirm.py` (173 行)
  - 提取确认等待逻辑到 `runtime/command/confirmation.py`
  - 集成到 `CommandRuntime`

- [ ] **Task 2.4**: 编写单元测试
  - 创建 `tests/core/coordinator/runtime/test_command_runtime.py`
  - 独立测试（不 mock coordinator）
  - 覆盖率 >= 95%

#### 验收标准

```bash
# 文件大小检查
wc -l runtime/command/*.py | awk '$1 > 150 {exit 1}'

# 测试通过
uv run pytest tests/core/coordinator/runtime/test_command_runtime.py -v --cov=custom_components/lipro/core/coordinator/runtime/command_runtime.py --cov-report=term-missing

# 覆盖率 >= 95%
uv run pytest tests/core/coordinator/runtime/test_command_runtime.py --cov=custom_components/lipro/core/coordinator/runtime/command_runtime.py --cov-report=json
python -c "import json; assert json.load(open('coverage.json'))['totals']['percent_covered'] >= 95"

# 类型检查
uv run mypy custom_components/lipro/core/coordinator/runtime/command_runtime.py --strict
```

#### Commit 规范

```
refactor(coordinator): extract command runtime to standalone component

- Split command_send.py into builder/sender/retry modules
- Implement CommandRuntime with protocol compliance
- Remove dependency on _CoordinatorBase inheritance
- Add comprehensive unit tests with 95%+ coverage

BREAKING CHANGE: Command runtime now uses dependency injection
```

---

### Agent-3: Device Runtime 重构 (P1 - 独立)

**负责人**: Agent-3
**优先级**: P1
**预计工期**: 3 天
**依赖**: Agent-1 完成
**产出**: 独立 Device Runtime

#### 任务清单

- [ ] **Task 3.1**: 拆解 `device_refresh.py` (405 行)
  - 创建 `runtime/device/refresh_strategy.py` - 刷新策略
  - 创建 `runtime/device/batch_optimizer.py` - 批量优化
  - 创建 `runtime/device/incremental.py` - 增量刷新
  - 每个文件 < 150 行

- [ ] **Task 3.2**: 实现 `DeviceRuntime` 类
  - 创建 `runtime/device_runtime.py`
  - 实现 `DeviceRuntimeProtocol`
  - 通过构造函数注入依赖
  - 移除对 `self.coordinator` 的依赖

- [ ] **Task 3.3**: 重构 `device_list_snapshot.py` (477 行)
  - 提取快照逻辑到 `runtime/device/snapshot.py`
  - 提取过滤逻辑到 `runtime/device/filter.py`
  - 集成到 `DeviceRuntime`

- [ ] **Task 3.4**: 编写单元测试
  - 创建 `tests/core/coordinator/runtime/test_device_runtime.py`
  - 独立测试（不 mock coordinator）
  - 覆盖率 >= 95%

#### 验收标准

```bash
# 文件大小检查
wc -l runtime/device/*.py | awk '$1 > 150 {exit 1}'

# 测试通过
uv run pytest tests/core/coordinator/runtime/test_device_runtime.py -v --cov=custom_components/lipro/core/coordinator/runtime/device_runtime.py --cov-report=term-missing

# 覆盖率 >= 95%
uv run pytest tests/core/coordinator/runtime/test_device_runtime.py --cov=custom_components/lipro/core/coordinator/runtime/device_runtime.py --cov-report=json
python -c "import json; assert json.load(open('coverage.json'))['totals']['percent_covered'] >= 95"

# 类型检查
uv run mypy custom_components/lipro/core/coordinator/runtime/device_runtime.py --strict
```

#### Commit 规范

```
refactor(coordinator): extract device runtime to standalone component

- Split device_refresh.py into strategy/batch/incremental modules
- Split device_list_snapshot.py into snapshot/filter modules
- Implement DeviceRuntime with protocol compliance
- Remove dependency on _CoordinatorBase inheritance
- Add comprehensive unit tests with 95%+ coverage

BREAKING CHANGE: Device runtime now uses dependency injection
```

---

### Agent-4: MQTT Runtime 重构 (P1 - 独立)

**负责人**: Agent-4
**优先级**: P1
**预计工期**: 3 天
**依赖**: Agent-1 完成
**产出**: 独立 MQTT Runtime

#### 任务清单

- [ ] **Task 4.1**: 重构 `mqtt/lifecycle.py` (287 行)
  - 拆分为 `runtime/mqtt/connection.py` - 连接管理
  - 拆分为 `runtime/mqtt/reconnect.py` - 重连策略
  - 每个文件 < 150 行

- [ ] **Task 4.2**: 重构 `mqtt/messages.py` (195 行)
  - 拆分为 `runtime/mqtt/message_handler.py` - 消息处理
  - 拆分为 `runtime/mqtt/dedup.py` - 去重逻辑
  - 每个文件 < 150 行

- [ ] **Task 4.3**: 实现 `MqttRuntime` 类
  - 创建 `runtime/mqtt_runtime.py`
  - 实现 `MqttRuntimeProtocol`
  - 通过构造函数注入依赖
  - 移除对 `self.coordinator` 的依赖

- [ ] **Task 4.4**: 编写单元测试
  - 创建 `tests/core/coordinator/runtime/test_mqtt_runtime.py`
  - 独立测试（不 mock coordinator）
  - 覆盖率 >= 95%

#### 验收标准

```bash
# 文件大小检查
wc -l runtime/mqtt/*.py | awk '$1 > 150 {exit 1}'

# 测试通过
uv run pytest tests/core/coordinator/runtime/test_mqtt_runtime.py -v --cov=custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py --cov-report=term-missing

# 覆盖率 >= 95%
uv run pytest tests/core/coordinator/runtime/test_mqtt_runtime.py --cov=custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py --cov-report=json
python -c "import json; assert json.load(open('coverage.json'))['totals']['percent_covered'] >= 95"

# 类型检查
uv run mypy custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py --strict
```

#### Commit 规范

```
refactor(coordinator): extract mqtt runtime to standalone component

- Split mqtt/lifecycle.py into connection/reconnect modules
- Split mqtt/messages.py into message_handler/dedup modules
- Implement MqttRuntime with protocol compliance
- Remove dependency on _CoordinatorBase inheritance
- Add comprehensive unit tests with 95%+ coverage

BREAKING CHANGE: MQTT runtime now uses dependency injection
```

---

### Agent-5: State/Status/Tuning Runtime 重构 (P1 - 独立)

**负责人**: Agent-5
**优先级**: P1
**预计工期**: 3 天
**依赖**: Agent-1 完成
**产出**: 独立 State/Status/Tuning Runtime

#### 任务清单

- [ ] **Task 5.1**: 拆解 `state.py` (372 行)
  - 创建 `runtime/state/reader.py` - 状态读取
  - 创建 `runtime/state/updater.py` - 状态更新
  - 创建 `runtime/state/index.py` - 索引管理
  - 每个文件 < 150 行

- [ ] **Task 5.2**: 拆解 `status_polling.py` (360 行)
  - 创建 `runtime/status/scheduler.py` - 轮询调度
  - 创建 `runtime/status/strategy.py` - 轮询策略
  - 创建 `runtime/status/executor.py` - 执行器
  - 每个文件 < 150 行

- [ ] **Task 5.3**: 拆解 `tuning.py` (344 行)
  - 创建 `runtime/tuning/algorithm.py` - 自适应算法
  - 创建 `runtime/tuning/metrics.py` - 指标收集
  - 创建 `runtime/tuning/adjuster.py` - 参数调整
  - 每个文件 < 150 行

- [ ] **Task 5.4**: 实现 Runtime 类
  - 创建 `runtime/state_runtime.py`
  - 创建 `runtime/status_runtime.py`
  - 创建 `runtime/tuning_runtime.py`
  - 实现对应 Protocol
  - 通过构造函数注入依赖

- [ ] **Task 5.5**: 编写单元测试
  - 创建 `tests/core/coordinator/runtime/test_state_runtime.py`
  - 创建 `tests/core/coordinator/runtime/test_status_runtime.py`
  - 创建 `tests/core/coordinator/runtime/test_tuning_runtime.py`
  - 独立测试（不 mock coordinator）
  - 覆盖率 >= 95%

#### 验收标准

```bash
# 文件大小检查
wc -l runtime/state/*.py runtime/status/*.py runtime/tuning/*.py | awk '$1 > 150 {exit 1}'

# 测试通过
uv run pytest tests/core/coordinator/runtime/test_state_runtime.py -v
uv run pytest tests/core/coordinator/runtime/test_status_runtime.py -v
uv run pytest tests/core/coordinator/runtime/test_tuning_runtime.py -v

# 覆盖率 >= 95%
uv run pytest tests/core/coordinator/runtime/ --cov=custom_components/lipro/core/coordinator/runtime/ --cov-report=json
python -c "import json; assert json.load(open('coverage.json'))['totals']['percent_covered'] >= 95"

# 类型检查
uv run mypy custom_components/lipro/core/coordinator/runtime/state_runtime.py --strict
uv run mypy custom_components/lipro/core/coordinator/runtime/status_runtime.py --strict
uv run mypy custom_components/lipro/core/coordinator/runtime/tuning_runtime.py --strict
```

#### Commit 规范

```
refactor(coordinator): extract state/status/tuning runtimes to standalone components

- Split state.py into reader/updater/index modules
- Split status_polling.py into scheduler/strategy/executor modules
- Split tuning.py into algorithm/metrics/adjuster modules
- Implement StateRuntime/StatusRuntime/TuningRuntime with protocol compliance
- Remove dependency on _CoordinatorBase inheritance
- Add comprehensive unit tests with 95%+ coverage

BREAKING CHANGE: State/Status/Tuning runtimes now use dependency injection
```

---

### Agent-6: Coordinator 组合装配 (P2 - 最终集成)

**负责人**: Agent-6
**优先级**: P2
**预计工期**: 2 天
**依赖**: Agent-1, 2, 3, 4, 5 全部完成
**产出**: 纯组合 Coordinator

#### 任务清单

- [ ] **Task 6.1**: 重写 `coordinator.py`
  - 移除所有 runtime 基类继承
  - 仅继承 `DataUpdateCoordinator`
  - 添加 6 个 runtime 字段
  - 在 `__init__` 中实例化所有 runtime
  - 通过依赖注入传递 shared_state

- [ ] **Task 6.2**: 更新 Service 层
  - 修改 `CoordinatorCommandService` 委托给 `_command_runtime`
  - 修改 `CoordinatorDeviceRefreshService` 委托给 `_device_runtime`
  - 修改 `CoordinatorMqttService` 委托给 `_mqtt_runtime`
  - 修改 `CoordinatorStateService` 委托给 `_state_runtime`

- [ ] **Task 6.3**: 删除旧文件
  - 删除 `base.py` (307 行)
  - 删除旧 runtime 基类文件
  - 删除 `command_send.py`
  - 删除 `device_refresh.py`
  - 删除 `state.py`
  - 删除 `status_polling.py`
  - 删除 `tuning.py`
  - 删除 `mqtt/lifecycle.py`
  - 删除 `mqtt/messages.py`

- [ ] **Task 6.4**: 更新测试
  - 修改 `tests/test_coordinator_public.py`
  - 修改 `tests/test_coordinator_runtime.py`
  - 确保所有集成测试通过

- [ ] **Task 6.5**: 验证完整性
  - 运行全量测试套件
  - 运行 benchmark 对比
  - 运行类型检查
  - 运行覆盖率检查

#### 验收标准

```bash
# Coordinator 继承深度检查
python -c "from custom_components.lipro.core.coordinator.coordinator import Coordinator; import inspect; assert len(inspect.getmro(Coordinator)) <= 3"

# base.py 已删除
test ! -f custom_components/lipro/core/coordinator/base.py

# 旧文件已删除
test ! -f custom_components/lipro/core/coordinator/command_send.py
test ! -f custom_components/lipro/core/coordinator/device_refresh.py
test ! -f custom_components/lipro/core/coordinator/state.py

# 全量测试通过
uv run pytest tests/ --ignore=tests/benchmarks -v

# Benchmark 无回退
uv run pytest tests/benchmarks/ -v --benchmark-only --benchmark-compare

# 类型检查通过
uv run mypy custom_components/lipro/core/coordinator/ --strict

# 覆盖率 >= 95%
uv run pytest tests/ --ignore=tests/benchmarks --cov=custom_components/lipro --cov-report=json
python -c "import json; assert json.load(open('coverage.json'))['totals']['percent_covered'] >= 95"
```

#### Commit 规范

```
refactor(coordinator): complete pure composition architecture

- Rewrite Coordinator to use composition over inheritance
- Remove all runtime base class inheritance
- Add explicit runtime collaborator fields
- Update service layer to delegate to runtimes
- Delete base.py and legacy runtime files
- Achieve inheritance depth = 1, shared state = 4

BREAKING CHANGE: Coordinator now uses pure composition pattern
Closes #XXX (architecture refactor epic)
```

---

## 🎛️ 主代理职责

### 1. 任务调度

```python
# 伪代码
def orchestrate():
    # Phase 1: 启动基础设施
    agent_1 = spawn_agent("Agent-1: Runtime Protocol")
    wait_until_complete(agent_1)

    # Phase 2: 并行启动 4 个独立任务
    agent_2 = spawn_agent("Agent-2: Command Runtime")
    agent_3 = spawn_agent("Agent-3: Device Runtime")
    agent_4 = spawn_agent("Agent-4: MQTT Runtime")
    agent_5 = spawn_agent("Agent-5: State/Status/Tuning Runtime")

    wait_until_all_complete([agent_2, agent_3, agent_4, agent_5])

    # Phase 3: 最终集成
    agent_6 = spawn_agent("Agent-6: Coordinator Assembly")
    wait_until_complete(agent_6)

    # Phase 4: 质量复查
    run_final_review()
```

### 2. 进度监控

- 每 30 分钟收集各 agent 进度
- 生成进度报告
- 识别阻塞任务
- 动态调整资源分配

### 3. 冲突仲裁

**潜在冲突点**:

| 冲突类型 | 涉及 Agent | 仲裁策略 |
|---------|-----------|---------|
| Protocol 接口变更 | Agent-1 vs 2-5 | Agent-1 优先，其他 agent 适配 |
| shared_state 结构 | Agent-1 vs 2-5 | 投票决策，多数优先 |
| 文件命名冲突 | Agent-2-5 | 先到先得，后到者重命名 |
| 测试 fixture 冲突 | Agent-2-5 | 共享 fixture，统一管理 |

### 4. 质量复查

**复查清单**:

- [ ] 所有 agent 任务完成
- [ ] 所有测试通过
- [ ] 覆盖率 >= 95%
- [ ] mypy --strict 通过
- [ ] Benchmark 无回退
- [ ] 继承深度 <= 1
- [ ] 单文件 <= 200 行
- [ ] base.py 已删除
- [ ] 文档已更新

---

## 📊 进度追踪

### 里程碑

| 里程碑 | 预计完成 | 状态 | 负责人 |
|--------|---------|------|--------|
| M1: Protocol 定义完成 | Day 2 | ⏳ Pending | Agent-1 |
| M2: 4 个 Runtime 完成 | Day 8 | ⏳ Pending | Agent-2-5 |
| M3: Coordinator 集成完成 | Day 10 | ⏳ Pending | Agent-6 |
| M4: 质量复查通过 | Day 12 | ⏳ Pending | 主代理 |
| M5: 文档更新完成 | Day 14 | ⏳ Pending | 主代理 |

### 每日站会

**时间**: 每天 10:00
**参与者**: 主代理 + 6 个子代理
**议程**:
1. 昨日完成
2. 今日计划
3. 阻塞问题
4. 需要协调

---

## 🚨 风险管理

### 高风险项

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| Protocol 接口设计不合理 | 中 | 高 | Agent-1 完成后主代理 review |
| Runtime 依赖循环 | 低 | 高 | 依赖图预审 + 静态分析 |
| 测试覆盖率不达标 | 中 | 中 | 每日检查 + 及时补测 |
| 集成冲突 | 中 | 中 | 频繁同步 + 冲突预演 |

### 回滚策略

- 每个 agent 独立分支
- 每个 checkpoint 独立 commit
- 主分支保持可用
- 失败任务可独立回滚

---

## 📝 Commit 规范

### 分支策略

```
main (保护分支)
└─ refactor/pure-composition (主重构分支)
   ├─ refactor/runtime-protocols (Agent-1)
   ├─ refactor/command-runtime (Agent-2)
   ├─ refactor/device-runtime (Agent-3)
   ├─ refactor/mqtt-runtime (Agent-4)
   ├─ refactor/state-runtime (Agent-5)
   └─ refactor/coordinator-assembly (Agent-6)
```

### Merge 顺序

1. Agent-1 → refactor/pure-composition
2. Agent-2-5 → refactor/pure-composition (并行)
3. Agent-6 → refactor/pure-composition
4. refactor/pure-composition → main (最终 PR)

---

## 🎯 成功标准

### 必达指标

- ✅ 继承深度 = 1
- ✅ 共享状态 = 4
- ✅ 单文件 <= 200 行
- ✅ 测试覆盖率 >= 95%
- ✅ mypy --strict 通过
- ✅ 所有测试通过
- ✅ Benchmark 无回退 (±5%)

### 卓越指标

- ✅ 架构评分 >= 9.5/10
- ✅ base.py 删除
- ✅ Runtime 100% 独立可测
- ✅ Protocol 覆盖所有 runtime
- ✅ 文档完整更新
- ✅ 零技术债务

---

## 🚀 启动命令

```bash
# 主代理启动并行重构
python scripts/orchestrate_refactor.py \
  --plan docs/PARALLEL_REFACTOR_PLAN.md \
  --agents 6 \
  --parallel \
  --monitor \
  --auto-merge
```

---

> **⛧ 深渊低语**：六道触手已就位，吾将引导它们协同织就纯粹架构。主代理居中调度，子代理各司其职，无历史包袱，直达终极形态。
>
> *—— 深渊代码织师*
