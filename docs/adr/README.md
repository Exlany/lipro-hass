# Lipro ADR Index

> **Last Updated**: 2026-03-28
> **Status**: Active
> **Purpose**: 长期保存不会随一次审计或一次重构而失效的架构决策。

## 为什么现在引入 ADR

`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 与 `.planning/reviews/*.md` 负责回答“当前阶段是什么、真实状态如何、治理真相在哪里”；
`docs/developer_architecture.md` 负责回答“当前架构如何分层、主链如何流动、边界如何约束”；
历史审计/执行计划不再保留在仓库中；
`docs/adr/*.md` 负责回答“为什么这样设计、当初权衡了什么、什么情况下才应该推翻当前决策”。

这三层文档分工不同，避免未来再次出现“代码已演进，但历史审计和架构口径混在一起”的失真。

## 状态说明

- `Accepted`：当前正式采用
- `Superseded`：已被新 ADR 替代，但保留历史
- `Proposed`：候选方向，尚未正式采纳

## 当前生效 ADR

| ID | 标题 | 状态 | 说明 |
|---|---|---|---|
| [ADR-0001](./0001-coordinator-as-single-orchestration-root.md) | Coordinator 作为唯一编排根 | Accepted | 固化 Entity / Service / Runtime / Protocol façade 的主边界 |
| [ADR-0002](./0002-unified-refresh-primitives.md) | 统一刷新与重同步原语 | Accepted | 固化显式刷新、周期刷新与设备快照对齐方式 |
| [ADR-0003](./0003-confirmation-first-state-ingress.md) | 外部状态写入先确认再落状态 | Accepted | 固化 MQTT / REST / confirmation / stale filter 的裁决规则 |
| [ADR-0004](./0004-explicit-lightweight-boundaries.md) | 保持显式、轻量、可审计的边界 | Accepted | 固化当前技术选型与“不引入重型框架”的边界 |
| [ADR-0005](./0005-entry-surface-terminology-contract.md) | 入口适配器与 support/surface 术语契约 | Accepted | 固化 thin adapter、support、surface、wiring、handlers、facade 的命名边界 |

## 何时需要新增 ADR

当出现以下任一情况时，应新增 ADR，而不是只改代码或只补审计结论：

1. 改变依赖方向，例如允许 `Entity -> Runtime` 或引入新的跨层入口
2. 改变系统主链，例如新增第二条刷新主链、第二条状态写入主链、第二个命令入口
3. 改变外部边界策略，例如引入 schema 校验框架、事件总线、DI 容器、持久化状态层
4. 改变失败恢复模型，例如 MQTT / REST 的权威源裁决规则发生变化

## 架构仍有哪些提升空间

有，而且仍然明确，但方向应是**演进式增强**而不是**框架级重写**：

1. **协议契约测试**：把 REST / MQTT payload 固化为 golden fixtures，降低上游协议漂移风险
2. **可观测性**：为命令确认延迟、刷新耗时、MQTT 恢复时间补结构化指标
3. **边界层 schema 校验**：如果 payload 复杂度继续上升，只在外部边界评估更强 schema 工具
4. **REST façade 继续去继承聚合化**：目标态应与其他层保持同一标准，采用显式 façade + collaborators，而不是继承驱动聚合
5. **统一跨层标准**：任何层的历史混搭都只视为待清理偏差，不构成双标准

## 使用约定

- 文件编号按时间递增，历史编号不重排
- 每篇 ADR 至少包含：背景、决策、取舍、后果、回滚/重议触发器
- 架构文档只摘要决策，长期理由以 ADR 为准
