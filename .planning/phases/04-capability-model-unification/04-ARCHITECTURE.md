# Phase 04: Capability Model 统一 - Architecture

**Status:** Active (`04-01` landed)
**Updated:** 2026-03-12

## Architectural Goal

让 domain plane 的 capability truth 从“散落在 device/profile/platform/helper 中的隐式规则集合”，升级为“拥有正式 home、正式 owner、正式 snapshot contract 的领域能力面”。

## Formal Components

### 1. `CapabilityRegistry`

**Owns**:
- `device_type_hex -> category/platforms` 的 canonical 映射入口；
- color temperature、fan gear 等能力边界的归一化；
- `device aggregate -> capability snapshot` 的正式构造。

**Must not own**:
- protocol payload normalization；
- runtime lifecycle / refresh orchestration；
- HA entity 细节或 service wiring。

### 2. `CapabilitySnapshot`

**Owns**:
- category、platforms、capability flags、边界值；
- 供 platform/entity/helper 安全消费的稳定只读投影。

**Must not own**:
- vendor payload 解码；
- 动态 runtime state；
- command execution。

### 3. `DeviceCapabilities` compat bridge

**Role**:
- 保留历史 `core.device` 导入路径；
- 允许现有测试与少量消费者平滑迁移；
- 明确声明自己不是 formal owner。

**Delete gate**:
- `04-02` consumer migration 完成；
- `04-03` 旧能力访问面清退完成；
- 无生产路径继续把它当作 architecture truth。

## Canonical Direction

```text
LiproDevice / profile metadata
  -> CapabilityRegistry
  -> CapabilitySnapshot
  -> device facade / entity descriptors / platform modules / command model
```

任何 category / platforms / supports_color_temp / max_fan_gear 的正式判断，都必须从这条主链得出。

## Phase 4 Execution Shape

### `04-01` — registry / snapshot / compat bridge
- 建立 `core/capability/`；
- 把 `core/device/capabilities.py` 降级为 compat bridge；
- 让 `device_snapshots.py` / `device_views.py` 走 canonical capability truth；
- 新增 registry tests；
- 回写治理与 baseline docs。

### `04-02` — consumer migration
- entity descriptors、platform modules、projection helpers 统一消费 snapshot / projection；
- 减少 `device` facade 对“能力语义字段”作为隐式规则系统的承载；
- 为 command model 对 capability truth 的消费建立明确接缝。

### `04-03` — duplicate rule cleanup
- 删除旧 helper / 影子判断 / 多点重复规则；
- 把 compat 访问面缩到最小；
- 完成 residual / kill updates，并准备向 Phase 5 handoff。

## File Treatment

### Formal Home
- `custom_components/lipro/core/capability/__init__.py`
- `custom_components/lipro/core/capability/models.py`
- `custom_components/lipro/core/capability/registry.py`

### Compatibility Bridge
- `custom_components/lipro/core/device/capabilities.py`

### Early Consumers
- `custom_components/lipro/core/device/device_snapshots.py`
- `custom_components/lipro/core/device/device_views.py`
- `custom_components/lipro/core/device/device.pyi`

### Next-Wave Consumers (`04-02`)
- `custom_components/lipro/entities/**/*.py`
- `custom_components/lipro/{light,fan,binary_sensor,cover,climate,select}.py`
- `custom_components/lipro/helpers/platform.py`

## Handoff to Later Phases

- **To Phase 5**：runtime plane 可以把 capability truth 当作稳定领域输入，而不必再兜底解释设备类别与平台差异；
- **To Phase 6**：meta guards 可进一步禁止 platform/entity 自建第二套 capability rules；
- **To Phase 7**：compat bridge、旧 helper、重复规则具备明确 kill targets。
