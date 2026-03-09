# Architecture Comparison

## 旧形态

### Coordinator

- 以深层 mixin 继承链组织行为
- 状态通过基类共享属性横向扩散
- 公开入口与 runtime 细节耦合在同一类层级

### Device / MQTT

- 超大类承载多种职责
- 可测试边界有限
- 局部优化存在，但收敛点不足

## 新形态（当前阶段）

### Coordinator

- 已引入 `Protocol` + `Service` 边界
- 公开入口开始收束到 service
- runtime 逻辑仍部分留在 bridge/mixin 中，处于“半收敛”阶段

### Device / MQTT

- `LiproDevice` 已拆出身份 / 状态 / 能力 / 网络信息
- `LiproMqttClient` 已拆出 `MqttMessageProcessor`
- 组合方向明确，外部行为保持稳定

## 目标形态

### Coordinator

- service 持有核心业务编排
- mixin 仅保留极少数过渡桥，最终可删除
- 状态管理、命令、刷新、MQTT 生命周期边界清晰

### Device / MQTT

- 外壳类只负责组装与少量兼容逻辑
- 纯逻辑尽量下沉到小型可测试组件

## 当前结论

当前代码已从“全靠继承链”进入“服务边界 + 兼容桥并存”的中间态。
下一阶段重点不是继续加新 mixin，而是把 bridge 内 runtime 继续向 service 下沉。
