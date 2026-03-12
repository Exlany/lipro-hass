# ADR-0003: 外部状态写入先确认再落状态

- **Status**: Accepted
- **Date**: 2026-03-12
- **Owners**: Command / state consistency

## 背景

当前系统同时接收来自 MQTT 推送、REST 轮询、命令后的确认回流。若这些状态源直接写入设备状态，会出现：

- 新命令刚发出，旧状态回流立刻把乐观状态覆盖掉
- 命令确认延迟不可学习，post-refresh 与保护窗口无法收敛
- MQTT / REST 的乱序与重复消息在不同入口被重复处理

## 决策

1. 所有外部状态写入统一经过 `Coordinator._apply_properties_update()`
2. 先执行 `CommandRuntime.filter_pending_state_properties()` 过滤 stale 属性
3. 再执行 `CommandRuntime.observe_state_confirmation()` 学习确认延迟与确认命中
4. 最后才进入 `StateRuntime.apply_properties_update()` 更新设备内存态

## 取舍

### 收益

- 确认学习、stale 过滤、状态落库顺序得到统一
- MQTT 与 REST 不再各自拥有不同的状态裁决规则
- 命令后的 post-refresh 可以和 confirmation tracker 形成闭环

### 代价

- 状态入口被显式收紧，旁路写状态会被视为架构违规
- 某些调试式捷径需要删除，必须通过正式主链验证行为

## 明确拒绝的替代方案

- MQTT 直接写 `StateRuntime`、REST 走另一套入口：会导致裁决规则分裂
- 仅靠时间窗口做去重，不做 confirmation 学习：无法持续调优
- 命令服务层单独再做 fallback refresh：会和 confirmation manager 重复调度

## 后果

- 若未来引入新的状态源，也必须接入这条统一状态写入链
- 任何优化都应围绕“过滤 -> 观察 -> 落状态”的顺序，而不是跳过其中任一步
- 测试应优先覆盖乱序、重复消息、命令确认超时与回流覆盖场景

## 重议触发器

只有在以下情况之一出现时，才应重新讨论该决策：

1. 上游开始提供可信的事件版本号 / 逻辑时钟，足以替代当前 confirmation 裁决
2. 当前确认链成本过高，且可被更强的一致性协议安全替换
3. 系统新增离线持久化状态层，需要重新定义状态进入内存态前的裁决方式
