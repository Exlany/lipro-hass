# Target Topology

**Purpose:** 定义北极星终态的五平面拓扑、正式组件、目标目录映射与非目标归属。
**Status:** Formal baseline asset (`BASE-01` topology truth source)
**Updated:** 2026-03-12

## Formal Role

- 本文件是五平面拓扑、formal root / root set、目标目录意图的正式 baseline 真源。
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 负责裁决北极星原则；本文件把该原则翻译成后续 phases 可直接引用的 topology 语义。
- 后续 phase 若要新增、降级或替换 formal root / root set，必须先回写本文件，再更新实现、测试与 phase 文档。

## Five-Plane Topology

| Plane | Formal Root / Root Set | Key Components | Target Ownership |
|-------|-------------|----------------|------------------|
| Protocol | `LiproProtocolFacade` | `LiproRestFacade`, `LiproMqttFacade`, `AuthSession`, `RequestPolicy`, `PayloadNormalizers`, collaborators | `custom_components/lipro/core/api/`, `custom_components/lipro/core/mqtt/` |
| Runtime | `Coordinator` | `RuntimeOrchestrator`, `RuntimeContext`, runtimes, services/public surface | `custom_components/lipro/core/coordinator/` |
| Domain | `CapabilityRegistry` + `CapabilitySnapshot` | device aggregate, command contracts, state views, projections | `custom_components/lipro/core/device/`, `custom_components/lipro/entities/`, platform modules |
| Control | `EntryLifecycleController` + control surface set | `ServiceRegistry`, `DiagnosticsSurface`, `SystemHealthSurface`, flows | `custom_components/lipro/__init__.py`, flow/support/service surfaces |
| Assurance | verification / governance stack | contracts, invariants, meta guards, ledgers, CI gates, ADR/docs | `tests/`, `.planning/`, `docs/`, `.github/workflows/` |

## Canonical Direction

```text
HA entry / flows / services / entities
  -> Control Plane + Runtime public surface + Domain projections
  -> Runtime Plane
  -> Protocol Plane
  -> Vendor REST / IoT / MQTT

Assurance Plane observes all layers and guards regressions.
```

## Target Directory Intent

| Current Area | Target Role | Notes |
|--------------|-------------|-------|
| `custom_components/lipro/core/api/` | Protocol REST slice | Phase 2 先收敛为 `LiproRestFacade` |
| `custom_components/lipro/core/mqtt/` | Protocol MQTT slice | Phase 2.5 归并为统一协议根的子门面 |
| `custom_components/lipro/core/coordinator/` | Runtime spine | Phase 5 做 invariant-level 正式化 |
| `custom_components/lipro/core/device/` | Domain core | Phase 4 统一 capability 真源 |
| `custom_components/lipro/entities/` + platform modules | Domain projections | 只做 projection，不再定义第二套规则 |
| `custom_components/lipro/services/` + entry/control files | Control plane surfaces | Phase 3 形成清晰控制面故事线 |
| `tests/` | Assurance implementation | 测试结构必须跟随正式架构迁移 |

## Non-Goals by Plane

- **Protocol plane** 不拥有 HA entity/control 语义
- **Runtime plane** 不拥有 vendor payload 编解码与签名恢复细节
- **Domain plane** 不拥有 auth/retry/network recovery
- **Control plane** 不反向定义 runtime internals
- **Assurance plane** 观察与仲裁，但不承载业务编排

## Transitional Residue Rules

- `LiproClient` 只能作为短期 compat shell，不能作为 target topology 的正式根
- 任何 mixin client、影子 helper、旧 public names 都不属于终态拓扑
- 迁移残留必须在 `RESIDUAL_LEDGER` 和 `KILL_LIST` 同步记录

---
*Used by: Phase 1.5+ planning, design review, and verification*
