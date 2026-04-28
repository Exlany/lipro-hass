# Lipro 北极星目标架构（North Star Target Architecture）

> **Last Updated**: `2026-03-19`
> **Status**: Target State / Active Reference
> **Role**: 定义“什么是正确终态”，用于裁决架构正确性，而不是复述任一临时实现。

## 1. 架构定位

北极星目标架构定义的是 **终态正确性**：

- 先定义正确终态，再安排迁移路径
- 历史兼容成本不改变架构裁决
- 任何偏离终态的实现都属于待收敛偏差，而不是第二套合法架构
- 迁移残留只能显式登记、可计数、可删除，不能长期合法化

## 2. 北极星法则

1. **显式组合优于继承聚合**
2. **单一正式主链优于多入口并存**
3. **边界归一化优于内部到处兼容供应商形态**
4. **领域真源优于平台/实体重复表达**
5. **控制面 / 运行面 / 协议面 / 领域面 / 保障面分离**
6. **可验证、可观测、可仲裁优于“看起来能跑”**
7. **迁移残留必须持续收口，不得长期并行合法化**

## 3. 依赖方向法则

- Platform / entity 只依赖 domain truth、runtime public surface、control contracts
- Control plane 只依赖 runtime public surface 与 assurance truth
- Runtime plane 可依赖 domain、protocol contracts、assurance hooks
- Protocol plane 负责外部 IO、boundary normalization、auth recovery、request policy
- Assurance plane 可以观测所有层，但不主导业务编排

**禁止：**

- entity / platform 直连 protocol internals、MQTT concrete transport、runtime private state
- protocol 感知 coordinator / Home Assistant lifecycle semantics
- compatibility layer 反向定义正式 public surface
- 用 empty shell、全局单例、隐式回调、事件总线替代正式边界

## 4. 五大平面

### 4.1 Protocol Plane

**Formal components**

- `LiproProtocolFacade`：唯一正式 protocol-plane root
- `LiproRestFacade`：REST child façade
- `LiproMqttFacade`：MQTT child façade
- `RequestPolicy`：超时、速率、重试等策略真源
- canonical contracts / payload normalizers / endpoint collaborators

**Invariants**

- 对外协议入口只从 `LiproProtocolFacade` 暴露
- canonical contracts 必须在 protocol boundary 完成
- 401 / 429 / connection recovery 在 protocol plane 内闭环
- `LiproClient`、`LiproMqttClient`、`raw_client`、旧 compat wrappers 不得回流

### 4.2 Runtime Plane

**Formal components**

- `Coordinator`：唯一 runtime orchestration root
- `RuntimeOrchestrator`：唯一 wiring root
- `RuntimeContext`：正式 callback injection contract
- runtime collaborators: `DeviceRuntime` / `StateRuntime` / `StatusRuntime` / `MqttRuntime` / `CommandRuntime` / `TuningRuntime`
- runtime services: polling / state / command / telemetry / mqtt / device-refresh service layer

**Invariants**

- 命令、刷新、状态写入、MQTT lifecycle 只有一条正式路径
- 不允许 bypass refresh、旁路写状态、旁路 MQTT apply path

### 4.3 Domain Plane

**Formal components**

- `LiproDevice`：device aggregate façade
- `CapabilityRegistry` / `CapabilitySnapshot`：唯一能力真源
- device views / command models / platform projections

**Invariants**

- 平台层只做 projection，不二次定义 capability truth
- domain 不承担 protocol recovery / HA lifecycle 语义

### 4.4 Control Plane

**Formal home**

- `custom_components/lipro/control/`

**Formal components**

- `EntryLifecycleController`
- `ServiceRouter`
- `ServiceRegistry`
- `RuntimeAccess`
- `DiagnosticsSurface`
- `SystemHealthSurface`
- `Redaction`
- `ConfigFlow / OptionsFlow`（thin adapter + flow contracts）

**Support helpers, not alternate roots**

- `custom_components/lipro/services/`：service declarations、request shaping、lookup、error translation、diagnostics/share/schedule helper modules
- 根层 `__init__.py`、`diagnostics.py`、`system_health.py`、`config_flow.py`：thin adapters

**Invariants**

- control plane 与 runtime plane 解耦，但只通过稳定 public surface 对接
- `services/` 不得再被叙述为 legacy carrier 或第二 control root
- `service wiring` 不是当前正式概念；正式概念是 `service callback home + adapter helpers`

### 4.5 Assurance Plane

**Formal components**

- architecture policy / file matrix / residual ledger / kill list / verification matrix
- contract tests / replay tests / governance tests / CI gates
- telemetry / diagnostics / replay evidence

**Invariants**

- 不只验证功能，也验证边界、依赖方向、authority truth 与 closeout story
- 任何架构回退都应由自动化护栏发现，而不是靠再次人工审计

## 5. 目标态目录映射

```text
custom_components/lipro/
├── core/
│   ├── protocol/              # protocol root + canonical contracts + diagnostics context
│   ├── api/                   # REST child façade collaborators / request policy / endpoint surface
│   ├── mqtt/                  # concrete MQTT transport / payload/topic helpers
│   ├── coordinator/           # runtime root + runtimes + runtime services
│   ├── capability/            # domain capability truth
│   ├── device/                # domain device aggregate
│   ├── command/               # domain write-side helpers
│   └── anonymous_share/       # protocol-adjacent support
├── control/                   # control plane formal home
├── services/                  # control service adapters / declarations / helpers
├── entities/                  # domain -> HA entity adapters
├── helpers/                   # projection / builder helpers
├── diagnostics.py             # thin control adapter
├── system_health.py           # thin control adapter
└── tests/                     # assurance plane
```

## 6. Definition of Done

只有同时满足以下条件，才可视为逼近北极星终态：

1. 全层显式组合，不依赖正式 mixin 继承链
2. protocol / runtime / control 都只有一条正式主链
3. vendor payload 不穿透 protocol boundary
4. capability / device / command / projection 围绕同一 domain truth 演进
5. control plane 形成单一叙事：lifecycle / router / diagnostics / health / flow / runtime access
6. assurance plane 由自动化护栏守护，而非只靠口头约定
7. 全仓文件都有归属与残留裁决
8. 历史残留可以清零，不能长期漂浮

## 7. 当前最高优先级

1. 维持 `control/`、`runtime/`、`protocol/`、`domain/`、`assurance/` 的单一主链，不接受第二 story 回流
2. 维持已关闭 compat seams 的关闭状态：`LiproClient`、`LiproMqttClient`、`raw_client`、`get_device_list` compat wrappers 不得回流
3. 保持治理真源与 machine-checkable guards 同步，不允许 stale prose 重新定义“当前现状”
4. 继续把 dead shell、误导性命名与巨石测试收口为更干净、更可维护的正式资产

## 8. 北极星 2.0（AI Debug Ready, HA-only）

北极星 2.0 不是换技术栈，而是在不破坏单主链的前提下，把 **可观测 / 可回放 / 可给 AI 分析的证据链**升级为正式能力：

- telemetry truth 单一：protocol/runtime telemetry sources → exporter/surfaces → diagnostics/system-health/developer/CI consumers
- replay 只复用 formal public path，不复制第二实现
- diagnostics/support 输出必须走正式 redaction / authority contract

## 9. 治理产物

- `tests/meta/` 与 `scripts/check_*.py`：自动化结构与边界守卫
- `CONTRIBUTING.md`、`docs/README.md`、`docs/developer_architecture.md`：当前公开协作入口与开发者说明
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`：维护者发版与连续性说明
- `docs/adr/*.md`：长期保留的架构决策记录
