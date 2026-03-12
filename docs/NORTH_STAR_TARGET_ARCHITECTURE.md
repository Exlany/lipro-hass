# Lipro 北极星目标架构（North Star Target Architecture）

> **Last Updated**: 2026-03-12
> **Status**: Target State / Active Reference
> **Role**: 定义“什么是正确终态”，不被历史债、迁移成本、临时兼容层左右。

## 1. 架构定位

北极星目标架构不是“当前实现说明”，也不是“现有代码的美化版解释”，而是整个仓库的**终态设计基准**：

- 先定义正确终态，再安排迁移路径
- 历史债只影响排期，不影响架构判断
- 任何偏离终态的实现，都视为待收敛偏差，而不是第二套合法架构
- 任何“为了兼容现状而保留的例外”，都必须有清理路径、失效条件与最终删除目标

## 2. 北极星法则

### 2.1 全层同标

所有层共享同一套设计法则：

1. **显式组合优于继承聚合**
2. **单一正式主链优于多入口并存**
3. **边界归一化优于内部到处兼容供应商形态**
4. **领域真源优于平台/实体重复表达**
5. **控制面、运行面、协议面、领域面、保障面分离**
6. **可验证、可观测、可仲裁优于“看起来能跑”**
7. **迁移残留必须收口，不得长期并行合法化**

### 2.2 依赖方向法则

北极星终态中的依赖方向必须清晰、单向、可验证：

- **Platform / Entity** → 只依赖 `Domain`、`Service Surface`、`Control Contracts`
- **Service Surface** → 只依赖 `Runtime Public Surface`
- **Runtime Plane** → 可依赖 `Domain`、`Protocol Contracts`、`Assurance Hooks`
- **Control Plane** → 可依赖 `Runtime Public Surface` 与 `Assurance`
- **Protocol Plane** → 负责对外 IO、协议恢复、边界归一化，不反向依赖 `Runtime` / `Entity`
- **Assurance Plane** → 可以观测所有层，但不主导业务编排

禁止的反向依赖：

- `Entity / Platform` 直连 `Client / MQTT / Runtime internals`
- `Protocol` 感知 `Coordinator` 或 HA 平台语义
- `Compatibility layer` 反向定义正式 public surface

### 2.3 明确禁止

以下模式不属于北极星终态：

- 任意层以 `mixin` 聚合作为正式设计
- 同一能力存在两条正式主链
- 通过历史兼容层长期维持双标准
- 通过全局事件总线、全局单例、隐式回调替代显式边界
- 让原始供应商 payload 穿透协议边界进入运行面、领域面、实体面
- 用“临时适配”规避正式设计，而不写明清理条件

## 3. 五大平面与参考设计

### 3.1 Protocol Plane

负责外部协议、认证恢复、请求策略、边界归一化与兼容迁移。

**终态正式组件**：

- `LiproProtocolFacade`：唯一正式 protocol-plane root
- `LiproRestFacade`：REST / IoT 子门面
- `LiproMqttFacade`：MQTT 子门面
- `TransportGateway`：统一 HTTP/IoT 请求执行
- `AuthSession`：token、refresh、reauth 恢复状态
- `RequestPolicy`：超时、限流、重试、幂等等策略
- `EndpointCollaborators`：按域划分的 endpoint 处理器
- `PayloadNormalizers`：把供应商形态归一化为 canonical contracts
- `CompatAdapters`：仅迁移期存在，负责旧接口到新 contracts 的桥接

**终态不变量**：

- 对外协议入口最终只从 `LiproProtocolFacade` 暴露
- `LiproRestFacade` / `LiproMqttFacade` 是协议平面下的子门面，而不是彼此割裂的根
- `LiproApiFacade` 若在 Phase 2 出现，只是收敛 REST 主链的中间台阶，不是绝对终态
- `LiproClient` 不属于终态正式设计；若迁移期仍存在，也只能是短期 compat adapter / shell
- 端点协作者不再通过多重继承聚合行为
- 401 / 429 / connection error 恢复链路在 protocol plane 内闭环
- canonical contract 在 protocol plane 边界完成，运行面不消费原始供应商形态
- `CompatAdapters` 必须是显式、可计数、可删除的临时残留

### 3.2 Runtime Plane

负责编排、刷新、状态一致性、命令确认与 MQTT 生命周期。

**终态正式组件**：

- `Coordinator`：唯一编排根
- `RuntimeOrchestrator`：唯一 wiring / 装配根
- `RuntimeContext`：唯一回调注入协议
- `CommandRuntime` / `DeviceRuntime` / `StateRuntime` / `StatusRuntime` / `MqttRuntime` / `TuningRuntime`

**终态不变量**：

- 命令、刷新、状态写入、MQTT 生命周期都只有一条正式路径
- 运行时协作只通过显式依赖与公开 primitives 完成
- 任何旁路刷新、旁路写状态、旁路 MQTT 应用路径都属于回归

### 3.3 Domain Plane

负责设备能力、身份、状态视图、命令模型、属性描述与平台投影。

**终态正式组件**：

- `DeviceAggregate` / `LiproDevice`：设备聚合根（命名可演进，职责不可漂移）
- `CapabilityRegistry`：单一能力真源
- `CapabilitySnapshot`：供平台/实体消费的稳定快照
- `Command Model`：命令对象与写侧能力语义
- `Platform Projections`：平台适配层，只做投影，不二次定义领域规则

**终态不变量**：

- 能力、属性、命令、平台差异围绕同一能力真源演进
- 平台层不重复持有“另一份规则系统”
- 领域模型不泄漏 HA 平台细节，也不承担协议恢复逻辑

### 3.4 Control Plane

负责接入、配置、诊断、服务注册、支持面与生命周期治理。

**终态正式组件**：

- `EntryLifecycleController`：setup / unload / reload / reauth / options
- `ServiceRegistry`：HA services 的唯一注册与撤销边界
- `DiagnosticsSurface`：诊断导出与 support payload
- `SystemHealthSurface`：健康度与依赖探针
- `ConfigFlow / OptionsFlow`：显式的接入与配置故事线

**终态不变量**：

- 控制面和运行面解耦，但通过稳定 public surface 对接
- `diagnostics` / `system_health` / `service wiring` / `entry lifecycle` 属于同一控制面叙事
- 控制面改动必须有 lifecycle / flow / diagnostics 验收

### 3.5 Assurance Plane

负责契约测试、可观测性、架构守卫、质量门禁与审计证据。

**终态正式组件**：

- `Contract Suite`：golden fixtures + canonical assertions
- `Architecture Rules`：依赖方向、双主链、跨层直连守卫
- `Telemetry Hooks`：命令确认、刷新耗时、MQTT 恢复、auth recovery
- `Verification Matrix`：把 phase / requirement / tests / docs 对齐
- `CI Gates`：lint / types / tests / architecture checks

**终态不变量**：

- 不只验证功能，还验证边界、依赖方向、恢复链路与架构不变量
- 可观测性是正式能力，不是调试临时品
- 任何架构回退都应由自动化护栏发现，而不是靠再次人工审计

## 4. 目标态目录映射

```text
custom_components/lipro/
├── core/
│   ├── coordinator/           # Runtime plane
│   ├── api/                   # Protocol plane (explicit facade + collaborators)
│   ├── mqtt/                  # Protocol transport
│   ├── device/                # Domain plane
│   ├── command/               # Domain write-side helpers
│   └── telemetry/             # Assurance runtime metrics (target)
├── entities/                  # Domain → HA adapter
├── helpers/                   # Declarative builders / rule helpers
├── services/                  # Control plane / HA service surface
├── flow/                      # Control plane config flows
├── diagnostics.py             # Control plane diagnostics export
├── system_health.py           # Control plane health surface
└── tests/                     # Assurance plane
```

## 5. 技术选型边界

北极星的“先进”不是追求更重的框架，而是追求**长期稳定、结构透明、边界清晰、可验证**。

### 5.1 当前最优技术立场

- **保留 Home Assistant custom integration + Python async 主栈**：不为“换血”而换血
- **在 HA 生命周期内正式使用 `ConfigEntry.runtime_data` 承载 typed runtime roots**：让 setup / unload / diagnostics / strict typing 一致
- **优先 `TypedDict + dataclass(slots=True) + Protocol`**：分别承担 contract、状态承载、边界协定，而不是一上来引入重型 schema 框架
- **优先长期复用的 `aiohttp.ClientSession` 与显式 transport executor**：不按请求创建 session
- **优先 `TraceConfig` 或等价轻量 hooks 做 request telemetry**：不引入全局事件总线
- **优先显式 wiring**：不引入通用 DI 容器

### 5.2 工程标准

- `Protocol` 主要用于静态边界，不在热路径滥用 runtime protocol checks
- middleware 若存在，必须单一职责、顺序明确、循环有界
- retry / auth recovery / rate limit 必须是显式、可测、可观测的协作者关系
- diagnostics 必须走正式脱敏出口，不把 token / account data 暴露到支持面

### 5.3 未来可评估但非当前前提

只有当复杂度继续上升且现有轻量模式不再足够时，才评估：

- 边界 schema 工具（例如更强的结构化 payload 校验）
- 依赖规则工具（例如更严格的 import / layer enforcement）
- 更细粒度的 protocol collaborator 分层

评估标准不是“是否更现代”，而是：

1. 是否显著提升可维护性与可验证性
2. 是否降低边界漂移与理解成本
3. 是否不会引入新的双标准与隐式魔法

## 6. 全仓代码审视与重构治理

北极星不是只改热点文件，而是要对**全部 Python 文件**建立正式治理：

- 每个 `*.py` 文件都必须被归类为：`保留` / `重构` / `迁移适配` / `删除`
- 每个 phase 都要明确本轮审视范围、触达文件簇、残留清单、删除清单
- 历史兼容层必须进入 `residual ledger`，不能散落在实现里“自然存在”
- 文档、代码、测试、phase plan 必须形成可追踪闭环

建议工作产物：

- `.planning/reviews/FILE_MATRIX.md`：全仓文件分类矩阵
- `.planning/reviews/RESIDUAL_LEDGER.md`：历史残留与删除时机
- `.planning/reviews/KILL_LIST.md`：明确待删除模块/适配层
- `.planning/phases/*`：每个阶段的上下文、研究、执行计划、总结

## 7. Definition of Done

只有满足以下条件，才算真正收敛到北极星目标架构：

1. **全层显式组合**：不存在被文档认可的 `mixin` 聚合例外
2. **单一正式主链**：命令、刷新、状态写入、接入生命周期只有一条正式路径
3. **边界归一化**：供应商 payload 不穿透 protocol plane
4. **领域单一真源**：能力、属性、命令、平台差异围绕同一模型演进
5. **控制面成体系**：entry lifecycle、flows、diagnostics、services 形成单一叙事
6. **保障面正式化**：contract、observability、architecture rules 成为自动化护栏
7. **全仓已分类治理**：所有 Python 文件都有归类与去向
8. **历史残留可清零**：compat adapters 仅剩显式、有限、可删除的迁移桥

## 8. 当前最高优先级

1. 完成协议契约基线，锁定 protocol boundary 真相
2. 重建 `API Client` 为显式 facade + collaborators
3. 建立全仓文件治理矩阵，防止重构过程再次产生双标准
4. 收敛 control plane、domain plane、runtime plane 的正式 public surface
5. 把 assurance plane 从“补充项”升级为正式平面
