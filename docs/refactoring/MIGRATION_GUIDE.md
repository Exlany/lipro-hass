# Refactoring Migration Guide

## 当前运行时边界

### Coordinator

- `entry.runtime_data` 固定为 `CoordinatorV2`
- 新代码应优先依赖显式 service 能力，而不是旧 mixin 细节

### Device

- `DeviceIdentity`：不可变身份信息
- `DeviceState`：可变状态与派生值
- `DeviceCapabilities`：能力与类别判断
- `DeviceNetworkInfo`：网络诊断信息
- `LiproDevice`：薄外观与兼容入口

### MQTT

- `MqttMessageProcessor`：消息解析与前处理
- `MqttConnectionManager`：连接生命周期与后台任务
- `MqttSubscriptionManager`：订阅同步
- `MqttTopicBuilder`：topic 构建与批处理
- `LiproMqttClient`：薄外观与组装入口

## 新代码推荐写法

- 状态读取 → `state_service`
- 命令发送 → `command_service`
- 设备刷新 → `device_refresh_service`
- MQTT 生命周期 → `mqtt_service`
- 设备模型扩展 → 对应 `core/device/*` 聚焦模块
- MQTT 行为扩展 → 对应 `core/mqtt/*` 聚焦模块

## 不再推荐的写法

- 不再新增 coordinator mixin
- 不再引入运行时开关切换新旧 coordinator
- 不再把新职责堆回 `LiproDevice` / `LiproMqttClient` 超壳
- 不再围绕旧兼容路径设计新代码

## 验证建议

每次涉及架构边界调整后至少执行：

```bash
uv run ruff check .
uv run mypy --hide-error-context --no-error-summary
uv run pytest tests/ --ignore=tests/benchmarks -q
```

若涉及覆盖率门槛与重构工具，再补：

```bash
uv run pytest tests/ --ignore=tests/benchmarks --cov=custom_components/lipro --cov-report=json -q
uv run python scripts/coverage_diff.py coverage.json --minimum 95
uv run python scripts/refactor_tools.py --coverage-json coverage.json --minimum-coverage 95
```

## 结论

迁移已经完成。后续开发默认站在当前结构之上，不再需要为旧架构保留额外兼容设计。
