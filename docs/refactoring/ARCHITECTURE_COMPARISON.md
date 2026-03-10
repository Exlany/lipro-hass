# Architecture Comparison

## 旧形态

### Coordinator

- 以深层 mixin 继承链组织行为
- 状态通过基类共享属性横向扩散
- 公开入口与 runtime 细节耦合在同一类层级
- 运行时边界与扩展点不清晰，新增逻辑容易继续堆入 mixin

### Device / MQTT

- 超大类承载多种职责
- 可测试边界有限
- 局部优化存在，但收敛点不足

## 新形态

### Runtime 入口

- `custom_components/lipro/__init__.py` 运行时已直接实例化 `CoordinatorV2`
- `custom_components/lipro/runtime_types.py` 统一将运行时类型收口到 `CoordinatorV2`
- 不再保留 `V1/V2` 双跑、配置开关或 facade 包装层

### Coordinator

- 公开编排边界已显式落到 `CoordinatorStateService`、`CoordinatorCommandService`、`CoordinatorDeviceRefreshService`、`CoordinatorMqttService`
- `CoordinatorV2` 现已成为原生运行时主体，旧 mixin 不再是推荐扩展点
- `CoordinatorV2` 现已成为原生运行时入口；旧类名仅保留为别名，不再承担独立运行时角色

### Device / MQTT

- `LiproDevice` 已拆成薄外观 + 工厂 / 视图 / 委托 / 运行时 / 快照 / 状态 / extras 模块
- `LiproMqttClient` 已拆成薄外观 + runtime / connection / subscription / topic / message 组件
- 测试边界已与模块边界对齐，便于单测、快照与 benchmark 验证

## 核心指标变化

| 指标 | 旧形态 | 当前形态 |
|---|---:|---:|
| Coordinator 运行时入口层级 | 13 层 mixin 链直接暴露 | `CoordinatorV2` 作为唯一入口，内部仍保留 mixin 链 |
| Coordinator 对外共享状态面 | 62 个共享属性 | 4 个显式 service 依赖 |
| `LiproDevice` 主文件行数 | 742 | 87 |
| `LiproMqttClient` 主文件行数 | 601 | 150 |
| 类型热点 `Any` | 高频集中 | 目标热点清零 |

## 为什么现在更优

- 新功能落点明确：优先写在 service 或聚焦组件，而不是再加 mixin 或继续膨胀超大类
- 调试链路更短：设备、MQTT、命令、刷新职责均有清晰入口
- 类型合同更稳：热点 `Any` 已清零，类型测试进入 CI
- 运行时更干净：未发布项目直接切到最终运行时路径，不再背负双实现维护成本

## 当前结论

当前工作区已完成从“深层继承 + 超大类”到“薄外观 + 显式服务/组件边界”的迁移。后续新增逻辑应继续沿着 `CoordinatorV2`、service 边界与小组件方向演进，而不是回退到旧的 mixin 扩散模式。
