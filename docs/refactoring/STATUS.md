# Refactoring Status

> 最后更新：2026-03-09
>
> 本状态表用于主代理逐项对照 `docs/refactoring/tasks/*.json`，避免重构遗漏。

## 本轮已完成

- 修复 `docs/refactoring/tasks/*.json` 的可解析性，当前全部任务清单均可被 `jq` 正常解析
- 收窄 MQTT 客户端热路径宽泛异常
- 降低命令结果与部分 API 模块的类型热点
- 完成 `LiproDevice` 的 `DeviceIdentity` / `DeviceState` / `DeviceCapabilities` / `DeviceNetworkInfo` 抽离
- 提取 `MqttMessageProcessor` 并接入 `LiproMqttClient`
- 为 Coordinator 引入并注入 `CommandService` / `DeviceRefreshService` / `MqttService` / `StateService`
- 新增 `CoordinatorV2` 组合外观与基础测试
- 将 `async_send_command` / `async_refresh_devices` / `async_setup_mqtt` / `async_stop_mqtt` / `async_sync_mqtt_subscriptions` 的公开入口收束到服务层
- 补齐服务层与设备拆分的单元测试

## Checkpoint Matrix

| Task File | Checkpoint | Status | Notes |
|---|---|---|---|
| `agent-1-exceptions.json` | `cp-1-1` | Partial | 尚未引入完整异常层次，但 MQTT 热路径已收窄 |
| `agent-1-exceptions.json` | `cp-1-2` ~ `cp-1-5` | Done | `custom_components/lipro/core/mqtt/client.py` 热路径宽泛异常已处理 |
| `agent-1-exceptions.json` | `cp-1-6` | Partial | 当前已完成热点清理，尚未形成全局“零裸异常”证明 |
| `agent-2-types.json` | `cp-2-1` | Partial | 尚未系统化补齐所有 `TypedDict` |
| `agent-2-types.json` | `cp-2-2` | Done | `custom_components/lipro/core/command/result.py` 已重点收敛 |
| `agent-2-types.json` | `cp-2-3` | Partial | 诊断服务仍有余量 |
| `agent-2-types.json` | `cp-2-4` | Partial | API 诊断模块仍有余量 |
| `agent-2-types.json` | `cp-2-5` | Partial | `schedule_service` 已补局部类型与 mypy 阻塞 |
| `agent-2-types.json` | `cp-2-6` | Partial | 当前局部类型检查通过，尚未形成专项类型测试目录 |
| `agent-3-architecture.json` | `cp-3-1` | Done | `StateManagementProtocol` / `MqttServiceProtocol` / `CommandServiceProtocol` / `DeviceRefreshServiceProtocol` 已齐备 |
| `agent-3-architecture.json` | `cp-3-2` | Partial | `MqttService` 已接管公开入口，核心 runtime 逻辑仍在 bridge 中 |
| `agent-3-architecture.json` | `cp-3-3` | Partial | `CommandService` 已接管公开入口，确认/队列逻辑仍在 bridge 中 |
| `agent-3-architecture.json` | `cp-3-4` | Partial | `DeviceRefreshService` 已接管公开入口，刷新策略与批量优化仍主要在现有 runtime 中 |
| `agent-3-architecture.json` | `cp-3-5` | Partial | `custom_components/lipro/coordinator_v2.py` 与 `tests/test_coordinator_v2.py` 已落地，仍未替代现网主协调器 |
| `agent-3-architecture.json` | `cp-3-6` | Not Started | V1/V2 双跑开关与兼容性矩阵尚未落地 |
| `agent-3-architecture.json` | `cp-3-7` | Done | `docs/refactoring/ARCHITECTURE_COMPARISON.md` 已补齐 |
| `agent-4-device-model.json` | `cp-4-1` | Done | `DeviceIdentity` 已落地并有测试 |
| `agent-4-device-model.json` | `cp-4-2` | Done | `DeviceState` 已落地并有测试 |
| `agent-4-device-model.json` | `cp-4-3` | Done | `DeviceCapabilities` 已落地并有测试 |
| `agent-4-device-model.json` | `cp-4-4` | Done | `DeviceNetworkInfo` 已落地并有测试 |
| `agent-4-device-model.json` | `cp-4-5` | Partial | `LiproDevice` 已组合这些组件，但主体仍偏大 |
| `agent-4-device-model.json` | `cp-4-6` ~ `cp-4-7` | Not Started | 快照测试与设备重构报告尚未补 |
| `agent-5-mqtt-client.json` | `cp-5-1` | Done | `MqttMessageProcessor` 已落地并接入客户端 |
| `agent-5-mqtt-client.json` | `cp-5-2` ~ `cp-5-3` | Not Started | Topic / Connection manager 尚未拆出 |
| `agent-5-mqtt-client.json` | `cp-5-4` ~ `cp-5-6` | Partial | 客户端已开始服务化，但未完成完整组合化与专项集成收口 |
| `agent-5-mqtt-client.json` | `cp-5-7` | Not Started | MQTT 重构报告尚未补 |
| `agent-6-testing.json` | `cp-6-1` ~ `cp-6-7` | Not Started | 当前以现有单元测试/静态检查为主，尚未建立快照/基准/专项工具链 |

## 当前默认验收口径

- Python / pytest / mypy / ruff 命令统一使用 `uv run ...`
- 先做最小范围验证，再逐步扩大到波次级验证
- `tasks/*.json` 中个别 `--cov=<file path>` 命令更适合作为“意图说明”而非覆盖率精确口径；实际执行时可用等价的模块级 `--cov` 参数替代

## 下一步建议

1. 继续完成 `agent-3` 的 `cp-3-2` / `cp-3-3` / `cp-3-4`，把 bridge 内的核心 runtime 逻辑进一步下沉到 service
2. 决定是否直接推进 `cp-3-5`：落地 `CoordinatorV2`
3. 为 `agent-4` / `agent-5` 补快照、集成测试与重构报告
4. 在波次结束后执行更大范围的 `pytest` / `mypy` / `ruff check`
