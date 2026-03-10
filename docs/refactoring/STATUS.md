# Refactoring Status

> 最后更新：2026-03-10
>
> 本状态表用于对照 `docs/refactoring/tasks/*.json`；以下结论仅基于当前工作区与已执行校验命令。

## 已完成要点

- 运行时入口已固定切换到 `CoordinatorV2`，不再保留 `V1/V2` 环境开关路径
- 设备模型已拆为薄外观 + 工厂/视图/运行时/快照/状态/额外能力模块，`custom_components/lipro/core/device/device.py` 当前为 `87` 行
- MQTT 客户端已拆为薄外观 + runtime/connection/subscription/topic/message 组件，`custom_components/lipro/core/mqtt/client.py` 当前为 `150` 行
- 类型热点已收口：
  - `custom_components/lipro/core/api/diagnostics_service.py`：`Any = 0`
  - `custom_components/lipro/services/diagnostics_service.py`：`Any = 0`
  - `custom_components/lipro/core/api/schedule_service.py`：`Any = 0`
  - `custom_components/lipro/core/command/result.py`：`Any = 0`
- 快照、benchmark、类型专项测试、覆盖率差异工具、重构工具与 CI 已全部落地
- benchmark 基线已清理为单份：`.benchmarks/Linux-CPython-3.13-64bit/0001_baseline.json`

## Checkpoint Matrix

| Task File | Checkpoint | Status | Notes |
|---|---|---|---|
| `agent-1-exceptions.json` | `cp-1-1` | Done | `custom_components/lipro/core/exceptions.py` 已建立共享异常层次 |
| `agent-1-exceptions.json` | `cp-1-2` ~ `cp-1-5` | Done | MQTT 热路径宽泛异常已收窄并外提到连接/回调管理组件 |
| `agent-1-exceptions.json` | `cp-1-6` | Done | `uv run ruff check custom_components/lipro/core/mqtt/ --select BLE001` 通过；剩余 `except Exception` 仅保留在回调/卸载/边界保护层 |
| `agent-2-types.json` | `cp-2-1` | Done | `custom_components/lipro/core/api/types.py` 已集中承载 TypedDict 合同 |
| `agent-2-types.json` | `cp-2-2` | Done | `custom_components/lipro/core/command/result.py` 已完成类型收口 |
| `agent-2-types.json` | `cp-2-3` | Done | `custom_components/lipro/services/diagnostics_service.py` 已补齐 `Protocol`/`TypedDict` |
| `agent-2-types.json` | `cp-2-4` | Done | `custom_components/lipro/core/api/diagnostics_service.py` 已移除热点 `Any` |
| `agent-2-types.json` | `cp-2-5` | Done | `custom_components/lipro/core/api/schedule_service.py` 已完成类型合同整理 |
| `agent-2-types.json` | `cp-2-6` | Done | `tests/type_checking/` 已接入，目标热点模块 `mypy --strict` 通过 |
| `agent-3-architecture.json` | `cp-3-1` | Done | `Protocol` 服务边界已存在 |
| `agent-3-architecture.json` | `cp-3-2` | Done | `CoordinatorMqttService` 已承担协调器对 MQTT 的公开编排入口 |
| `agent-3-architecture.json` | `cp-3-3` | Done | `CoordinatorCommandService` 已承担命令发送公开入口 |
| `agent-3-architecture.json` | `cp-3-4` | Done | `CoordinatorDeviceRefreshService` 已承担刷新公开入口 |
| `agent-3-architecture.json` | `cp-3-5` | Done | `CoordinatorV2` 已落地并作为当前 `entry.runtime_data` |
| `agent-3-architecture.json` | `cp-3-6` | Done | 依据“未发布、直接上最终架构”原则，已改为固定 V2 路径验证 |
| `agent-3-architecture.json` | `cp-3-7` | Done | `docs/refactoring/ARCHITECTURE_COMPARISON.md` 与本状态表已同步最新结论 |
| `agent-4-device-model.json` | `cp-4-1` ~ `cp-4-4` | Done | `DeviceIdentity` / `DeviceState` / `DeviceCapabilities` / `DeviceNetworkInfo` 均已落地 |
| `agent-4-device-model.json` | `cp-4-5` | Done | `LiproDevice` 已成为薄 facade + 委托外观 |
| `agent-4-device-model.json` | `cp-4-6` | Done | 快照与目录化测试均已存在 |
| `agent-4-device-model.json` | `cp-4-7` | Done | `docs/refactoring/DEVICE_MODEL_REPORT.md` 已按当前结构回填 |
| `agent-5-mqtt-client.json` | `cp-5-1` | Done | `message_processor.py` 已落地 |
| `agent-5-mqtt-client.json` | `cp-5-2` | Done | `topic_builder.py` 已落地 |
| `agent-5-mqtt-client.json` | `cp-5-3` | Done | `connection_manager.py` 已落地 |
| `agent-5-mqtt-client.json` | `cp-5-4` | Done | `client.py` 已瘦身为 `150` 行组合外观 |
| `agent-5-mqtt-client.json` | `cp-5-5` | Done | MQTT 新结构已接入当前协调器/runtime 路径 |
| `agent-5-mqtt-client.json` | `cp-5-6` | Done | MQTT 单元/集成测试已落地并通过 |
| `agent-5-mqtt-client.json` | `cp-5-7` | Done | `docs/refactoring/MQTT_CLIENT_REPORT.md` 已按当前数据回填 |
| `agent-6-testing.json` | `cp-6-1` | Done | `tests/snapshots/` 与 `.ambr` 基线已落地 |
| `agent-6-testing.json` | `cp-6-2` | Done | `tests/benchmarks/` 已落地，benchmark 基线已清理为单份 |
| `agent-6-testing.json` | `cp-6-3` | Done | `tests/type_checking/` 已落地 |
| `agent-6-testing.json` | `cp-6-4` | Done | `scripts/coverage_diff.py` 已落地 |
| `agent-6-testing.json` | `cp-6-5` | Done | `scripts/refactor_tools.py` 与其测试已落地 |
| `agent-6-testing.json` | `cp-6-6` | Done | CI 已覆盖 Ruff / mypy / type-checking / coverage diff / snapshot / benchmark |
| `agent-6-testing.json` | `cp-6-7` | Done | `docs/refactoring/TESTING_INFRASTRUCTURE.md` 与 `docs/developer_testing_guide.md` 已回填最新事实 |

## 当前验收口径

```bash
uv run ruff check .
uv run mypy --hide-error-context --no-error-summary
uv run pytest tests/type_checking/ -v
uv run mypy tests/type_checking/ --strict
uv run pytest tests/snapshots/ -v
uv run pytest tests/ --ignore=tests/benchmarks -q
uv run pytest tests/benchmarks/ -v --benchmark-only --benchmark-save=baseline
uv run pytest tests/ --ignore=tests/benchmarks --cov=custom_components/lipro --cov-report=json -q
uv run python scripts/coverage_diff.py coverage.json --minimum 95
uv run python scripts/refactor_tools.py --coverage-json coverage.json --minimum-coverage 95
```

## 备注

- 当前仍有少数相对较大的功能文件，但已不再属于本轮 checklist 定义的“超大类/类型热点/继承链扩散”问题
- 旧 mixin 实现现仅作为内部实现细节保留；对外运行时、文档与新增代码路径统一面向 `CoordinatorV2` 与显式 service 边界
- 本轮目标已从“兼容旧架构”明确切换为“直接落到最终架构”，因此不再保留旧开关与双跑路径
