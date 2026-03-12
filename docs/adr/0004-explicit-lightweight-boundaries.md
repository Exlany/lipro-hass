# ADR-0004: 保持显式、轻量、可审计的边界

- **Status**: Accepted
- **Date**: 2026-03-12
- **Owners**: Architecture / developer experience

## 背景

本项目已经形成一套适合 Home Assistant 集成的轻量架构：`DataUpdateCoordinator` 作为适配根，`RuntimeContext` 做显式注入，`dataclasses` + TypedDict/类型别名承载领域模型，`uv + ruff + mypy + pytest` 组成质量基线。

在这种规模下，最常见的“升级冲动”不是能力不足，而是过早引入重型框架，例如通用 DI 容器、事件总线、全域 `pydantic`、额外仓储层。它们会增加抽象层次，却未必降低真实复杂度。

## 决策

1. 保持显式依赖方向：`Entity -> Service -> Runtime -> Client`
2. 保持 `RuntimeContext` 作为 coordinator 回调注入协议
3. 保持 `dataclasses` + TypedDict / 类型别名作为默认类型建模方式
4. 保持 `uv + ruff + mypy + pytest` 作为默认验证栈
5. 重型技术只允许在边界层、且必须有明确触发条件时再评估

## 取舍

### 收益

- 代码路径更显式，适合排查 Home Assistant 场景中的运行时问题
- 工具链足够轻量，新成员理解与参与成本更低
- 文档、类型检查、测试能够围绕同一条显式调用链展开

### 代价

- 某些高级能力需要用约束和文档来补，而不是靠框架自动获得
- 边界层校验与可观测性需要后续逐步增强，不能指望框架一次性解决

## 明确拒绝的替代方案

- 通用 DI 容器：当前依赖图规模不足以证明收益
- 事件总线替代显式调用链：会削弱可追踪性与可调试性
- 全域 `pydantic` 化：样板与运行时成本偏高，不适合当前体量
- 本地状态持久化 / 仓储模式：当前以内存协调状态为主，复杂度不匹配

## 后果

- 架构仍有提升空间，但优先级应落在 ADR、契约测试、可观测性、边界 schema，而不是大规模技术换血
- 若未来要引入更强类型库，例如 `pydantic v2` 或 `msgspec`，应限定在外部协议边界，而非全域替换
- 若 `core/api/client.py` 的 mixin façade 继续膨胀，可再新增 ADR 讨论 API client 收敛方案

## 重议触发器

只有在以下情况之一出现时，才应重新讨论该决策：

1. 外部 payload 复杂度显著上升，手写校验与 TypedDict 成本持续超标
2. 运行时依赖图扩大到显式 wiring 已明显降低可维护性
3. 可观测性、类型安全、模块解耦的真实痛点已经被证明确实无法在现有轻量架构内解决
