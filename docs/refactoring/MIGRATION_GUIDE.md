# Refactoring Migration Guide

## 当前可用的新边界

### Device

- `DeviceIdentity`：承载不可变身份信息
- `DeviceState`：承载可变属性解析与派生状态
- `DeviceCapabilities`：承载能力与分类判断
- `DeviceNetworkInfo`：承载网络诊断信息
- `LiproDevice`：保留兼容外壳，逐步退化为组合入口

### MQTT

- `MqttMessageProcessor`：承载消息解析与路由前处理
- `LiproMqttClient`：保留客户端外壳，逐步退化为组合入口

### Coordinator

- `CoordinatorStateService`
- `CoordinatorCommandService`
- `CoordinatorDeviceRefreshService`
- `CoordinatorMqttService`

当前原则是：**公开入口先收束到 service，复杂 runtime 再逐步下沉**。

## 推荐写法

### 新代码优先依赖 service 边界

优先通过以下边界组织新逻辑：

- 状态读取 → `state_service`
- 命令发送 → `command_service`
- 设备刷新 → `device_refresh_service`
- MQTT 生命周期 → `mqtt_service`

### 避免继续扩散旧模式

不要再新增新的 coordinator mixin。
不要再把新的公开入口直接塞回超大类。
不要再在 `LiproDevice` / `LiproMqttClient` 中堆叠横向职责。

## 迁移顺序建议

1. 先把公开入口迁到 service
2. 再把 runtime 细节从 mixin 内部逐块下沉到 service
3. 最后再评估是否落地真正的 `CoordinatorV2`

## 当前仍保留的兼容层

以下对象当前仍然存在，但应视为迁移过渡层：

- `custom_components/lipro/core/device/device.py`
- `custom_components/lipro/core/mqtt/client.py`
- `custom_components/lipro/core/coordinator/command_send.py`
- `custom_components/lipro/core/coordinator/status_polling.py`
- `custom_components/lipro/core/coordinator/mqtt/lifecycle.py`

## 验证建议

每次迁移后至少执行：

```bash
uv run ruff check .
uv run mypy --hide-error-context --no-error-summary
uv run pytest tests/core/coordinator/services -q
```

涉及设备或 MQTT 时，再补：

```bash
uv run pytest tests/core/test_device.py tests/core/test_device_state.py -q
uv run pytest tests/core/mqtt/test_mqtt.py tests/core/mqtt/test_message_processor.py -q
```
