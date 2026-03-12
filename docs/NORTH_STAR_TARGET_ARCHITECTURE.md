# Lipro 北极星目标架构（North Star Target Architecture）

> **Last Updated**: 2026-03-12
> **Status**: Target State / Active Reference
> **Role**: 定义“什么是正确终态”，不被历史债、迁移成本、临时兼容层左右。

## 1. 目标定义

北极星目标架构不是另一套“当前实现说明”，而是整个仓库的**终态设计基准**：

- 先定义正确的终态，再安排迁移路径
- 历史债只影响排期，不影响架构判断
- 任何偏离终态的实现，都应视为待收敛偏差，而不是第二套合法架构

## 2. 北极星原则

### 2.1 全层同标

所有层共享同一套设计原则：

1. **显式组合优于继承聚合**
2. **单一正式主链优于多入口并存**
3. **边界契约优于隐式约定**
4. **可观测、可验证优于经验调试**
5. **控制面、运行面、协议面、领域面分离**

### 2.2 明确禁止

以下模式不属于北极星终态：

- 任意层以 mixin 聚合作为正式设计
- 同一能力存在两条正式主链
- Entity / Platform 直连 Runtime / Client
- 通过历史兼容层长期维持双标准
- 用事件总线、全局单例、隐式回调替代显式依赖边界

## 3. 五大平面

### 3.1 Runtime Plane

负责运行中编排与状态一致性：

- `Coordinator`：唯一编排根
- `RuntimeOrchestrator`：统一 wiring / DI
- `RuntimeContext`：唯一回调注入协议
- `CommandRuntime` / `DeviceRuntime` / `StateRuntime` / `StatusRuntime` / `MqttRuntime` / `TuningRuntime`

**北极星要求**：
- 命令、刷新、状态写入、MQTT 生命周期都只有一个正式入口
- Runtime 之间只通过显式依赖与正式回调协作

### 3.2 Protocol Plane

负责外部协议、边界校验与协议恢复：

- REST transport
- MQTT transport
- Auth / token lifecycle
- Payload schemas / codecs / signing
- API facade / endpoint collaborators

**北极星要求**：
- `API Client` 采用显式 facade + collaborators，不保留 mixin 聚合作为正式终态
- 所有外部 payload 入口都可被 schema、golden fixtures、contract tests 覆盖
- 401 / rate limit / connection error 等恢复链路明确且可观测

### 3.3 Domain Plane

负责设备能力、命令模型、属性描述与平台映射：

- `LiproDevice` 与 device views
- capabilities / identity / state / extras
- descriptors / commands / platform rules

**北极星要求**：
- 设备能力有单一 source-of-truth
- 平台规则、命令对象、属性描述符围绕统一 capability model 演进
- 平台层不重复表达领域规则

### 3.4 Control Plane

负责接入、配置、诊断、服务注册与运行支持：

- `__init__.py` / config entry lifecycle
- `config_flow.py` / `entry_options.py`
- `diagnostics.py` / `system_health.py`
- services registry / registrations / diagnostics package

**北极星要求**：
- 控制面与运行面解耦，但边界清晰
- diagnostics / system health / options / reauth 归入同一控制面叙事，而不是散落辅助文件
- 所有控制面入口都有显式生命周期与验收标准

### 3.5 Assurance Plane

负责验证、观测、约束执行与回归保护：

- unit / integration / contract / snapshot tests
- observability metrics
- architecture rules / dependency enforcement
- lint / types / CI checks

**北极星要求**：
- 不只验证功能，还验证边界、依赖方向与协议契约
- 架构约束可自动化检查，不能只靠文档提醒
- 关键运行信号可量化：命令确认、刷新耗时、MQTT 恢复、auth recovery

## 4. 目标态目录映射

```text
custom_components/lipro/
├── core/
│   ├── coordinator/           # Runtime plane
│   ├── api/                   # Protocol plane (explicit facade + collaborators)
│   ├── mqtt/                  # Protocol plane / transport
│   ├── auth/                  # Protocol + control support
│   ├── device/                # Domain plane
│   ├── command/               # Domain write-side helpers
│   └── telemetry/             # Assurance plane runtime metrics (target)
├── entities/                  # Domain → HA adapter
├── helpers/                   # Declarative builders / rules helpers
├── services/                  # Control plane / HA service surface
├── flow/                      # Control plane config flows
├── diagnostics.py             # Control plane diagnostics export
├── system_health.py           # Control plane health surface
└── tests/                     # Assurance plane
```

## 5. Definition of Done

只有满足以下条件，才算真正收敛到北极星目标架构：

1. **全层显式组合**：不存在被文档认可的 mixin 聚合例外
2. **单一正式主链**：命令、刷新、状态写入、接入生命周期都只有一条正式路径
3. **边界契约化**：REST / MQTT / diagnostics / services 都有明确契约与回归保护
4. **控制面成体系**：config entry / options / diagnostics / system health 形成清晰 control-plane 文档与实现
5. **可观测可仲裁**：关键运行指标、错误恢复、回退路径可解释、可测、可观测
6. **架构规则自动化**：依赖方向和关键 invariants 由测试或静态规则守护

## 6. 不追求的“伪先进”

北极星目标架构**不等于**：

- 更复杂的框架堆叠
- 通用 DI 容器
- 全局事件总线
- 全域 `pydantic`
- 为“现代感”而新增的抽象层

真正先进的是：

- 设计一套长期稳定、边界清晰、可审计、可演进的系统
- 让每一层遵循同一套标准，不制造例外
- 让迁移方向明确，不再被历史残留绑架

## 7. 当前最优先推进方向

1. `API Client` 去 mixin 化，统一全层标准
2. Protocol boundary 契约测试化
3. Runtime / control-plane / support-plane 边界文档与实现对齐
4. 统一 capability model，消除平台/领域的重复表达
5. observability + architecture enforcement 成为正式平面
