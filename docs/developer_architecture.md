# Lipro Home Assistant Integration - Developer Architecture

> **Last Updated**: 2026-03-10  \
> **Version**: 2.x
>
> ⚠️ 本文档仅描述“架构与模块边界”，不在此硬编码评分/覆盖率/通过率等易失真指标。  \
> 质量验收与重构收口进度请以 `docs/refactor_completion_plan.md` 的回填记录为准。

## 📌 快速导航

- 组件入口：`custom_components/lipro/__init__.py`
- Coordinator（HA glue + 编排）：`custom_components/lipro/core/coordinator/coordinator.py`
- Runtime 组件（组合式）：`custom_components/lipro/core/coordinator/runtime/`
- Coordinator 服务层（适配/门面）：`custom_components/lipro/core/coordinator/services/`
- 设备薄 facade：`custom_components/lipro/core/device/device.py`
- API client：`custom_components/lipro/core/api/client.py`
- MQTT client：`custom_components/lipro/core/mqtt/mqtt_client.py`

## Overview

Lipro 集成将 Lipro 设备接入 Home Assistant，当前支持的平台（与代码保持一致）见：`custom_components/lipro/__init__.py` 中的 `PLATFORMS`：

- `light`, `cover`, `switch`, `fan`, `climate`, `binary_sensor`, `sensor`, `select`, `update`

通信与状态更新采用“MQTT 推送 + REST 兜底轮询”的混合模型：

- MQTT：用于实时属性变更与在线状态更新
- REST：用于设备列表/状态轮询与 MQTT 不可用时的降级兜底

## Architecture Principles

### 1) 组合优于继承（Composition over Mixins）

Coordinator 不再依赖 mixin 聚合，而是将职责拆成可独立测试/替换的 runtime 组件（command/status/state/device/mqtt/tuning）。

### 2) 边界清晰：Entity → Coordinator → Runtime/Service → Client

- **Entities**：只承载 HA 平台胶水与 UI 表现，不直接做 API/MQTT 细节
- **Coordinator**：编排、缓存与更新节奏，作为 HA `DataUpdateCoordinator` 的对接层
- **Runtime/Service**：业务能力与协议细节的承载处（可单测）
- **Client（API/MQTT）**：外部 IO 与协议封装

### 3) 依赖注入（Dependency Injection）

runtime/service 通过构造注入依赖，以便单测替换。

### 4) “只写已验证事实”的文档策略

- 本文档不维护“质量评分/覆盖率百分比/测试数量”等会快速过期的数字
- 若需要指标，请以 CI 或本地命令输出为准，并回填到 `docs/refactor_completion_plan.md`

## Core Components

### Coordinator（`core/coordinator/coordinator.py`）

职责：

- 维护运行时状态容器（devices / entity registry / identity index）
- 组装并注入 runtime 组件
- 对接 HA 的更新循环（`_async_update_data`）
- 作为 service 层门面：对 Entity 暴露稳定调用面

关键 runtime 组件（均位于 `core/coordinator/runtime/`）：

- `StateRuntime`：设备查找、属性更新、实体注册索引
- `DeviceRuntime`：设备列表刷新、过滤策略、设备增删对齐
- `StatusRuntime`：REST 状态轮询（批次与并发）
- `MqttRuntime`：MQTT 生命周期管理与消息分发
- `CommandRuntime`：命令发送、确认跟踪、post-refresh 策略
- `TuningRuntime`：批次大小/窗口等调参逻辑

### API Client（`core/api/`）

- `client.py`：`LiproClient`（端点 mixin + transport mixin 的组合入口）
- `transport_core.py` / `transport_retry.py` / `transport_signing.py`：请求核心/重试/签名拆分
- `endpoints/`：按域拆分端点（auth/status/devices/commands/...）

### MQTT Client（`core/mqtt/`）

- `mqtt_client.py`：`LiproMqttClient` 薄门面
- `client_runtime.py`：运行时桥接（把“厚逻辑”留在 helper 内）
- `payload.py` / `topics.py` / `subscription_manager.py`：payload 解析、topic 生成、订阅同步

### Device Model（`core/device/`）

- `device.py`：`LiproDevice`（薄 facade），尽量只保留结构化字段与少量门面方法
- `state.py`：`DeviceState`（可变状态视图 + derived accessors）
- `device_views.py` / `extras.py` / `device_runtime.py`：派生视图、补充能力与兼容逻辑

### Entities（`entities/`）

平台实体实现尽量遵循：

- 不直接访问 API/MQTT 细节
- 通过 Coordinator/service 层下发命令、请求刷新
- 对“乐观更新/防抖/锁”等并发语义集中在公共基类中维护

## Data Flow

### 1) 状态更新（MQTT / REST）

```
┌──────────────┐
│ MQTT Message │ ──┐
└──────────────┘   │
                   ├──→ ┌─────────────────┐
┌──────────────┐   │    │   MqttRuntime   │
│ REST Polling │ ──┘    │ (normalize/app) │
└──────────────┘        └─────────────────┘
                               ↓
                        ┌─────────────────┐
                        │  StateRuntime   │
                        │ (apply + index) │
                        └─────────────────┘
                               ↓
                        ┌─────────────────┐
                        │  LiproDevice    │
                        │ (properties)    │
                        └─────────────────┘
                               ↓
                        ┌─────────────────┐
                        │ Entity 更新 HA  │
                        └─────────────────┘
```

### 2) 命令执行（Entity → Coordinator → API → 确认/刷新）

```
┌──────────────┐
│ User Action  │
└──────────────┘
       ↓
┌──────────────────┐
│ Entity.async_*() │
└──────────────────┘
       ↓
┌──────────────────────┐
│ Coordinator.send()   │
└──────────────────────┘
       ↓
┌──────────────────────┐
│ CommandRuntime       │
│ (build/send/verify)  │
└──────────────────────┘
       ↓
┌──────────────────────┐
│ ConfirmationTracker  │
│ + post-refresh       │
└──────────────────────┘
       ↓
┌──────────────────────┐
│ State reconciliation │
└──────────────────────┘
```

### 3) 认证（AuthManager → API client 401 recovery）

- `core/auth/manager.py` 负责 token 生命周期、refresh、必要时触发 reauth
- API transport 层负责在 401 时触发 refresh 回调，并重试请求

## Module Map（目录结构）

（只列关键路径，避免文档随代码拆分频繁过期）

- `custom_components/lipro/core/coordinator/`
  - `coordinator.py`：HA glue + runtime 编排
  - `runtime/`：可组合 runtime（state/device/status/mqtt/command/...）
  - `services/`：协调器服务层（稳定调用面）
- `custom_components/lipro/core/api/`
  - `client.py`、`client_base.py`、`client_transport.py`、`transport_*.py`
  - `endpoints/`：按域拆分端点
- `custom_components/lipro/core/mqtt/`
  - `mqtt_client.py`、`client_runtime.py`、`payload.py`、`topics.py`
- `custom_components/lipro/core/device/`
  - `device.py`、`state.py`、`device_views.py`、`extras.py`
- `custom_components/lipro/entities/`
  - `base.py` + 各平台实体实现

## Verification（本地验证）

统一使用 `uv`，避免环境漂移：

- `uv run ruff check .`
- `uv run --extra dev mypy custom_components/lipro tests`
- `uv run pytest -q`

生成物策略：

- `pytest-benchmark` 等工具可能产生 `.benchmarks/`、`benchmark_results.json`，应保持在 `.gitignore` 中（避免误入库）。

## Contributing（贡献约定）

- 保持“组合式 runtime + 薄 facade + service 委托”的方向，不回退到 mixin 拼装
- 对外能力（Entity/Service 使用的 API）优先通过协议与类型契约固化，而不是散落 `cast`
- 任何新增/改动：优先补齐单测，并确保 ruff/mypy/pytest 通过

## References

- Home Assistant Developer Docs: https://developers.home-assistant.io/
- `CODE_QUALITY_REVIEW.md`
- `docs/refactor_completion_plan.md`
- `CHANGELOG.md`
