# ADR-0001: Coordinator 作为唯一编排根

- **Status**: Accepted
- **Date**: 2026-03-12
- **Owners**: Core architecture

## 背景

Home Assistant 集成天然以 `DataUpdateCoordinator` 为运行时中心，但历史演进中，命令、刷新、状态写入、服务编排容易向 `Entity`、`Platform`、helper 或临时 facade 扩散。这样会带来三类问题：

1. 主链分叉，难以判断哪里才是正式入口
2. 运行时策略散落，测试与回归验证成本升高
3. 边界被打穿后，后续重构会回到“牵一发而动全身”的状态

## 决策

1. `Coordinator` 作为唯一编排根，统一承载运行时主链调度
2. `Entity` 只负责 HA 平台胶水与 UI 表现，不直接编排 Runtime
3. `Service` 负责稳定边界与跨 Runtime 协调，不直接承接底层 IO
4. `Runtime` 负责业务能力与策略，不暴露给 `Entity` 直接依赖
5. `Client` 负责 REST / MQTT / 上游协议 IO，不承载上层编排策略

## 取舍

### 收益

- 主链更单一，命令、刷新、状态同步都可围绕 coordinator 收口
- 依赖方向更清晰，便于通过 `RuntimeContext` 做显式注入
- 测试可以按层切分：Entity、Service、Runtime、Client 各自验证

### 代价

- `Coordinator` 会保留一定编排复杂度，不能追求过度瘦身
- 需要通过文档与测试持续守边界，否则容易重新渗透

## 明确拒绝的替代方案

- `Entity -> Runtime` 直连：会让平台层重新承担编排职责
- 事件总线式隐式编排：可追踪性下降，调试成本上升
- 通用 DI 容器：对当前规模而言引入成本高于收益

## 后果

- 新增运行时能力时，应优先扩展 `Runtime` + `Coordinator` public API，而不是给 Entity 加私有捷径
- 新增平台时，应复用现有 Service / Runtime 主链，而不是复制编排逻辑
- 审计或重构结论若要推翻此边界，必须新增 ADR，而不是只在 PR 中口头说明

## 重议触发器

只有在以下情况之一出现时，才应重新讨论该决策：

1. `Coordinator` 已无法保持可测试性，且拆分后仍能保留清晰主链
2. 新运行时模型要求多个并行编排根，且单根设计已明显成为瓶颈
3. Home Assistant 官方运行模型发生重大变化，现有 coordinator 模式不再契合
