# Coordinator 架构图表

本文档展示重构后的 Coordinator 架构，从继承链迁移到纯组合模式。

---

## 1. 整体架构图

展示 Coordinator 与 6 个 Runtime 的组合关系：

```mermaid
graph TB
    HA[Home Assistant] --> Coordinator

    subgraph "Coordinator 核心"
        Coordinator[Coordinator<br/>DataUpdateCoordinator]
        SharedState[CoordinatorSharedState<br/>不可变共享状态]
    end

    subgraph "Runtime 组件层"
        DeviceRuntime[DeviceRuntime<br/>设备刷新管理]
        StatusRuntime[StatusRuntime<br/>状态轮询调度]
        CommandRuntime[CommandRuntime<br/>命令执行编排]
        StateRuntime[StateRuntime<br/>状态读写索引]
        MqttRuntime[MqttRuntime<br/>MQTT 连接管理]
        TuningRuntime[TuningRuntime<br/>自适应调优]
    end

    subgraph "Service 服务层"
        CommandService[CommandService]
        StatusService[StatusService]
        MqttService[MqttService]
        AuthService[AuthService]
    end

    subgraph "API 客户端层"
        LiproClient[LiproClient<br/>HTTP API]
        LiproMqttClient[LiproMqttClient<br/>MQTT 客户端]
    end

    Coordinator --> DeviceRuntime
    Coordinator --> StatusRuntime
    Coordinator --> CommandRuntime
    Coordinator --> StateRuntime
    Coordinator --> MqttRuntime
    Coordinator --> TuningRuntime

    Coordinator -.共享.-> SharedState
    DeviceRuntime -.读取.-> SharedState
    StatusRuntime -.读取.-> SharedState
    MqttRuntime -.读取.-> SharedState

    CommandRuntime --> CommandService
    StatusRuntime --> StatusService
    MqttRuntime --> MqttService
    DeviceRuntime --> AuthService

    CommandService --> LiproClient
    StatusService --> LiproClient
    MqttService --> LiproMqttClient
    AuthService --> LiproClient

    style Coordinator fill:#e1f5ff
    style SharedState fill:#fff4e6
    style DeviceRuntime fill:#e8f5e9
    style StatusRuntime fill:#e8f5e9
    style CommandRuntime fill:#e8f5e9
    style StateRuntime fill:#e8f5e9
    style MqttRuntime fill:#e8f5e9
    style TuningRuntime fill:#e8f5e9
```

**说明**：
- Coordinator 通过组合持有 6 个独立 Runtime
- SharedState 作为不可变状态容器，被多个 Runtime 共享读取
- Runtime 通过依赖注入获取 Service 和 Client
- 无继承关系，纯组合架构

---

## 2. 主更新循环流程图

展示 `_async_update_data()` 的执行流程：

```mermaid
sequenceDiagram
    participant HA as Home Assistant
    participant C as Coordinator
    participant Auth as AuthManager
    participant DR as DeviceRuntime
    participant SR as StatusRuntime
    participant MR as MqttRuntime
    participant API as LiproClient

    HA->>C: _async_update_data()
    activate C

    C->>Auth: async_ensure_authenticated()
    Auth-->>C: ✓ Token 有效

    C->>DR: should_refresh_device_list()
    DR-->>C: true (需要刷新)

    C->>DR: refresh_devices(force=True)
    activate DR
    DR->>API: query_device_list()
    API-->>DR: 设备列表
    DR->>DR: 构建设备快照
    DR-->>C: FetchedDeviceSnapshot
    deactivate DR

    C->>SR: update_all_device_status()
    activate SR
    SR->>SR: compute_query_batches()
    SR->>API: batch_query_status()
    API-->>SR: 状态数据
    SR->>SR: apply_properties_update()
    SR-->>C: ✓ 状态已更新
    deactivate SR

    alt MQTT 未连接
        C->>MR: setup()
        activate MR
        MR->>MR: 连接 MQTT Broker
        MR-->>C: ✓ 已连接
        deactivate MR
    end

    C-->>HA: devices dict
    deactivate C
```

**说明**：
- 认证检查优先执行
- 设备列表按需刷新（非每次）
- 状态更新采用批量查询优化
- MQTT 连接异步建立

---

## 3. Runtime 组件内部结构图

展示每个 Runtime 的子组件组成：

```mermaid
graph LR
    subgraph "CommandRuntime"
        CR[CommandRuntime] --> CB[CommandBuilder<br/>命令构建]
        CR --> CS[CommandSender<br/>命令发送]
        CR --> CRS[RetryStrategy<br/>重试策略]
        CR --> CM[ConfirmationManager<br/>确认管理]
    end

    subgraph "DeviceRuntime"
        DR[DeviceRuntime] --> RS[RefreshStrategy<br/>刷新策略]
        DR --> BO[BatchOptimizer<br/>批量优化]
        DR --> IS[IncrementalStrategy<br/>增量刷新]
        DR --> DF[DeviceFilter<br/>设备过滤]
        DR --> SB[SnapshotBuilder<br/>快照构建]
        DR --> ST[StaleDeviceTracker<br/>过期追踪]
    end

    subgraph "StatusRuntime"
        SR[StatusRuntime] --> SS[StatusScheduler<br/>调度器]
        SR --> SST[StatusStrategy<br/>批量策略]
        SR --> SE[StatusExecutor<br/>执行器]
    end

    subgraph "MqttRuntime"
        MR[MqttRuntime] --> MC[ConnectionManager<br/>连接管理]
        MR --> MH[MessageHandler<br/>消息处理]
        MR --> MD[DedupManager<br/>去重管理]
        MR --> MRM[ReconnectManager<br/>重连管理]
    end

    subgraph "StateRuntime"
        STR[StateRuntime] --> SI[StateIndexManager<br/>索引管理]
        STR --> SRD[StateReader<br/>状态读取]
        STR --> SU[StateUpdater<br/>状态更新]
    end

    subgraph "TuningRuntime"
        TR[TuningRuntime] --> TA[TuningAlgorithm<br/>调优算法]
        TR --> TM[TuningMetrics<br/>指标收集]
        TR --> TAD[TuningAdjuster<br/>参数调整]
    end

    style CR fill:#fff3e0
    style DR fill:#fff3e0
    style SR fill:#fff3e0
    style MR fill:#fff3e0
    style STR fill:#fff3e0
    style TR fill:#fff3e0
```

**说明**：
- 每个 Runtime 由多个专职子组件组成
- 子组件职责单一，可独立测试
- 通过依赖注入组装，无继承耦合

---

## 4. 重构前后对比图

展示从继承链到组合模式的转变：

```mermaid
graph TB
    subgraph "重构前：继承链地狱"
        OldC[Coordinator] --> M1[CommandMixin]
        OldC --> M2[DeviceMixin]
        OldC --> M3[StatusMixin]
        OldC --> M4[MqttMixin]
        OldC --> M5[StateMixin]
        M1 --> Base1[_CoordinatorBase]
        M2 --> Base2[_CoordinatorBase]
        M3 --> Base3[_CoordinatorBase]
        M4 --> Base4[_CoordinatorBase]
        M5 --> Base5[_CoordinatorBase]

        Note1[❌ 多重继承<br/>❌ 方法冲突<br/>❌ 隐式依赖<br/>❌ 难以测试]
    end

    subgraph "重构后：纯组合模式"
        NewC[Coordinator] -.contains.-> R1[CommandRuntime]
        NewC -.contains.-> R2[DeviceRuntime]
        NewC -.contains.-> R3[StatusRuntime]
        NewC -.contains.-> R4[MqttRuntime]
        NewC -.contains.-> R5[StateRuntime]
        NewC -.contains.-> R6[TuningRuntime]

        R1 -.inject.-> S1[Services]
        R2 -.inject.-> S2[Services]
        R3 -.inject.-> S3[Services]

        Note2[✅ 显式依赖<br/>✅ 单一职责<br/>✅ 易于测试<br/>✅ 可独立演进]
    end

    style OldC fill:#ffebee
    style M1 fill:#ffcdd2
    style M2 fill:#ffcdd2
    style M3 fill:#ffcdd2
    style M4 fill:#ffcdd2
    style M5 fill:#ffcdd2
    style Base1 fill:#ef9a9a
    style Base2 fill:#ef9a9a
    style Base3 fill:#ef9a9a
    style Base4 fill:#ef9a9a
    style Base5 fill:#ef9a9a

    style NewC fill:#e8f5e9
    style R1 fill:#c8e6c9
    style R2 fill:#c8e6c9
    style R3 fill:#c8e6c9
    style R4 fill:#c8e6c9
    style R5 fill:#c8e6c9
    style R6 fill:#c8e6c9
```

**说明**：
- **重构前**：多重继承导致方法解析顺序混乱，Mixin 之间隐式依赖 `_CoordinatorBase`
- **重构后**：Coordinator 通过构造函数注入 Runtime，Runtime 通过构造函数注入 Service
- **核心改进**：从"是什么"（继承）到"有什么"（组合）

---

## 5. 依赖注入流程图

展示 Runtime 如何通过依赖注入初始化：

```mermaid
graph LR
    Init[Coordinator.__init__] --> CreateShared[创建 SharedState]

    CreateShared --> InitDevice[初始化 DeviceRuntime]
    InitDevice --> InjectDevice[注入 client, auth_manager,<br/>device_identity_index]

    InjectDevice --> InitStatus[初始化 StatusRuntime]
    InitStatus --> InjectStatus[注入 query_device_status,<br/>apply_properties_update]

    InjectStatus --> InitCommand[初始化 CommandRuntime]
    InitCommand --> InjectCommand[注入 builder, sender,<br/>retry, confirmation]

    InjectCommand --> InitState[初始化 StateRuntime]
    InitState --> InjectState[注入 devices, entities,<br/>device_identity_index]

    InjectState --> InitMqtt[初始化 MqttRuntime]
    InitMqtt --> InjectMqtt[注入 mqtt_client,<br/>polling_updater]

    InjectMqtt --> InitTuning[初始化 TuningRuntime]
    InitTuning --> InjectTuning[注入 batch_size_min/max,<br/>latency_thresholds]

    InjectTuning --> Ready[✓ 就绪]

    style Init fill:#e3f2fd
    style CreateShared fill:#fff9c4
    style Ready fill:#c8e6c9
```

**说明**：
- 所有依赖在构造函数中显式声明
- 无隐式全局状态或单例
- 便于单元测试时 Mock 依赖

---

## 6. 数据流向图

展示数据在各层之间的流动：

```mermaid
graph TB
    subgraph "外部触发"
        User[用户操作] --> Entity[Entity]
        Timer[定时器] --> Coordinator
    end

    subgraph "Coordinator 层"
        Coordinator --> DeviceRuntime
        Coordinator --> StatusRuntime
        Entity --> CommandRuntime
    end

    subgraph "Runtime 层"
        DeviceRuntime --> |设备列表| SharedState
        StatusRuntime --> |状态更新| SharedState
        CommandRuntime --> |命令执行| CommandService
        MqttRuntime --> |推送消息| SharedState
    end

    subgraph "Service 层"
        CommandService --> |HTTP 请求| API
        StatusService --> |批量查询| API
        MqttService --> |订阅主题| Broker[MQTT Broker]
    end

    subgraph "数据存储"
        SharedState --> |通知| Entity
        SharedState --> |持久化| Storage[HA Storage]
    end

    Broker --> |推送| MqttRuntime
    API --> |响应| StatusService
    API --> |响应| CommandService

    style User fill:#e1f5ff
    style Coordinator fill:#fff4e6
    style SharedState fill:#c8e6c9
    style API fill:#ffccbc
    style Broker fill:#ffccbc
```

**说明**：
- 用户操作通过 Entity 触发 CommandRuntime
- 定时器触发 Coordinator 主循环
- 所有状态变更汇聚到 SharedState
- MQTT 推送实时更新 SharedState

---

## 7. 命令执行生命周期

展示命令从发起到确认的完整流程：

```mermaid
sequenceDiagram
    participant E as Entity
    participant CR as CommandRuntime
    participant CB as CommandBuilder
    participant CS as CommandSender
    participant API as LiproClient
    participant CM as ConfirmationManager
    participant MR as MqttRuntime

    E->>CR: send_device_command()
    activate CR

    CR->>CB: build_command(device, action, params)
    CB-->>CR: command_payload

    CR->>CS: send(device_id, payload)
    activate CS
    CS->>API: POST /control
    API-->>CS: {msg_sn: "xxx"}
    CS-->>CR: msg_sn
    deactivate CS

    alt wait_confirmation=True
        CR->>CM: register_expectation(msg_sn)
        CM-->>CR: expectation_id

        CR->>CR: await confirmation (timeout=5s)

        MR->>MR: 收到 MQTT 推送
        MR->>CM: notify_confirmation(msg_sn)
        CM-->>CR: ✓ 确认成功

        CR-->>E: CommandResult(success=True)
    else wait_confirmation=False
        CR-->>E: CommandResult(success=True)
    end

    deactivate CR
```

**说明**：
- CommandBuilder 负责构建命令载荷
- CommandSender 负责 HTTP 发送
- ConfirmationManager 追踪 MQTT 确认
- 支持同步/异步两种模式

---

## 8. MQTT 重连策略

展示 MQTT 断线重连的指数退避机制：

```mermaid
stateDiagram-v2
    [*] --> Disconnected: 初始状态

    Disconnected --> Connecting: setup()
    Connecting --> Connected: 连接成功
    Connecting --> Backoff: 连接失败

    Connected --> Disconnected: 网络中断

    Backoff --> Connecting: 等待 delay 后重试
    Backoff --> Backoff: delay *= 2 (最大 60s)

    Connected --> [*]: teardown()

    note right of Backoff
        指数退避策略：
        1s → 2s → 4s → 8s → 16s → 32s → 60s
    end note

    note right of Connected
        连接成功后：
        - 订阅设备主题
        - 重置退避计数
        - 放宽轮询间隔
    end note
```

**说明**：
- 采用指数退避避免频繁重连
- 最大延迟 60 秒
- 连接成功后重置退避状态

---

## 9. 自适应调优反馈循环

展示 TuningRuntime 如何动态调整批量大小：

```mermaid
graph TB
    Start[开始查询] --> Record[记录指标]
    Record --> |batch_size, duration| Metrics[TuningMetrics]

    Metrics --> Analyze[分析最近 6 次]
    Analyze --> |平均延迟| Decision{延迟判断}

    Decision --> |< 1.2s| Increase[增加批量大小<br/>+8 设备]
    Decision --> |1.2s ~ 3.5s| Keep[保持当前批量]
    Decision --> |> 3.5s| Decrease[减少批量大小<br/>-8 设备]

    Increase --> Clamp1[限制 16~64]
    Decrease --> Clamp2[限制 16~64]
    Keep --> Apply

    Clamp1 --> Apply[应用新批量大小]
    Clamp2 --> Apply

    Apply --> NextCycle[下次查询]
    NextCycle --> Start

    style Decision fill:#fff9c4
    style Increase fill:#c8e6c9
    style Decrease fill:#ffccbc
    style Keep fill:#e0e0e0
```

**说明**：
- 根据延迟动态调整批量大小
- 避免过大批量导致超时
- 避免过小批量导致请求过多

---

## 10. 状态更新批量优化

展示 StatusRuntime 如何分批查询设备状态：

```mermaid
graph LR
    subgraph "输入"
        Devices[100 个设备]
    end

    subgraph "StatusStrategy"
        Devices --> Split[按批量大小分割<br/>batch_size=32]
        Split --> B1[Batch 1: 32 设备]
        Split --> B2[Batch 2: 32 设备]
        Split --> B3[Batch 3: 32 设备]
        Split --> B4[Batch 4: 4 设备]
    end

    subgraph "StatusExecutor"
        B1 --> Q1[并发查询 1]
        B2 --> Q2[并发查询 2]
        B3 --> Q3[并发查询 3]
        B4 --> Q4[并发查询 4]
    end

    subgraph "结果合并"
        Q1 --> Merge[合并结果]
        Q2 --> Merge
        Q3 --> Merge
        Q4 --> Merge
        Merge --> Update[更新设备状态]
    end

    style Split fill:#fff9c4
    style Merge fill:#c8e6c9
```

**说明**：
- 避免单次查询设备过多导致超时
- 批量并发查询提升效率
- 动态调整批量大小适应网络状况

---

## 总结

重构后的架构具备以下优势：

| 维度 | 重构前 | 重构后 |
|------|--------|--------|
| **耦合度** | 多重继承，强耦合 | 纯组合，松耦合 |
| **可测试性** | 难以 Mock 基类 | 依赖注入，易测试 |
| **可维护性** | 方法冲突，难追踪 | 职责清晰，易定位 |
| **可扩展性** | 修改影响全局 | 独立演进，互不影响 |
| **性能** | 无优化 | 自适应调优 |

核心设计原则：

1. **依赖注入**：所有依赖通过构造函数显式传入
2. **单一职责**：每个 Runtime 只负责一个领域
3. **不可变状态**：SharedState 采用 frozen dataclass
4. **组合优于继承**：Runtime 之间无继承关系
5. **协议驱动**：通过 Protocol 定义接口契约
