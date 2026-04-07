# Phase 04: Capability Model 统一 - Context

**Gathered:** 2026-03-12
**Status:** Active (`04-01` completed, `04-02/04-03` pending)
**Decision mode:** North-star arbitration by default
**Source:** `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/baseline/TARGET_TOPOLOGY.md`, `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/FILE_MATRIX.md`, `.planning/reviews/RESIDUAL_LEDGER.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, current domain/device/entity/platform slice inspection

## Phase Boundary

本阶段的唯一目标是：

**把设备能力语义收敛到单一 formal source-of-truth，并让平台、实体、命令、属性描述围绕同一 capability model 演进。**

本阶段必须完成：
- 建立 `CapabilityRegistry / CapabilitySnapshot` 的正式领域面；
- 把 `core/device` 中的能力判断退化为对 canonical capability truth 的消费；
- 让 entity / platform / helper 只消费 capability snapshot 或基于它的 projection；
- 把仍然存在的双轨能力规则、旧 helper、compat 访问面登记到治理台账并逐步清退。

本阶段明确**不做**：
- runtime invariants、MQTT 生命周期、command confirmation 的最终加固（属于 Phase 5）；
- assurance plane / CI gates 的体系化正式化（属于 Phase 6）；
- compat / docs / shadow module 的全仓最终清零（属于 Phase 7）。

## Current Structural Tension

当前 capability truth 的重复来源至少存在以下几类：
- `custom_components/lipro/core/device/capabilities.py`：类别与能力布尔集合；
- `custom_components/lipro/core/device/device_views.py`：`category()` / `platforms()` 的重复推导；
- `custom_components/lipro/core/device/profile.py`：`resolve_platforms()` 与类型解析；
- `custom_components/lipro/core/device/state_accessors.py`：`supports_color_temp()` 的状态侧重复表达；
- 平台与实体层：大量直接消费 `device.is_light` / `device.supports_color_temp` / `device.max_fan_gear` / `device.platforms`。

这些重复表达尚未都删除，但 `04-01` 已先建立 formal capability root，后续计划围绕它迁移与清退。

## Locked Decisions

- `custom_components/lipro/core/capability/` 是 capability truth 的正式 home。
- `CapabilityRegistry` 是 capability snapshot 的唯一正式构造入口。
- `CapabilitySnapshot` 是平台 / 实体 / helper / 命令侧可消费的稳定快照。
- `custom_components/lipro/core/device/capabilities.py` 只允许作为 compat bridge 存在，不能继续定义第二套规则。
- `device_views` / `device_snapshots` 必须消费 canonical capability truth，而不是各自重算。
- `04-01` 不做大规模 consumer migration 与删除动作；这些动作顺延到 `04-02` / `04-03`。

## Upstream Inputs

进入本 phase 前，以下上游输入已经满足：
- `Phase 1 / 1.5`：目标拓扑、public surfaces、verification contract 已 formalize；
- `Phase 2 / 2.5 / 2.6`：protocol root 与 external boundary truth 已收口；
- `Phase 3`：control plane 已形成稳定 consumer 边界，不再反向塑造 capability truth。

当前 `Phase 4` 可以直接把 capability model 当作 domain plane 的正式下一块拼图，而不需要再等待 protocol/control 的阻塞项。
