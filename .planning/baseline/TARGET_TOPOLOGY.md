# Target Topology

**Purpose:** 定义北极星终态的五平面拓扑、正式组件、目标目录映射与非目标归属。
**Status:** Formal baseline asset (`BASE-01` topology truth source)
**Updated:** 2026-03-27 (Phase 85 terminal audit aligned)
**Alignment:** `v1.23 / Phase 85` current-route truth verified on `2026-03-27`

## Formal Role

- 本文件是五平面拓扑、formal root / root set、目标目录意图的正式 baseline 真源。
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 负责裁决北极星原则；本文件把该原则翻译成后续 phases 可直接引用的 topology 语义。
- 后续 phase 若要新增、降级或替换 formal root / root set，必须先回写本文件，再更新实现、测试与 phase 文档。

## Five-Plane Topology

| Plane | Formal Root / Root Set | Key Components | Target Ownership |
|-------|-------------|----------------|------------------|
| Protocol | `LiproProtocolFacade` | `LiproRestFacade`, `LiproMqttFacade`, `RestAuthRecoveryCoordinator`, `RequestPolicy`, boundary helpers/collaborators | `custom_components/lipro/core/protocol/`, `custom_components/lipro/core/api/`, `custom_components/lipro/core/mqtt/` |
| Runtime | `Coordinator` | `RuntimeOrchestrator`, `RuntimeContext`, runtimes, services/public surface | `custom_components/lipro/core/coordinator/` |
| Domain | `CapabilityRegistry` + `CapabilitySnapshot` | capability truth, device aggregate, command contracts, state views, projections | `custom_components/lipro/core/capability/`, `custom_components/lipro/core/device/`, `custom_components/lipro/entities/`, platform modules |
| Control | `EntryLifecycleController` + control surface set | `ServiceRegistry`, `ServiceRouter`, `RuntimeAccess`, `DiagnosticsSurface`, `SystemHealthSurface`, root thin adapters | `custom_components/lipro/control/`, root thin adapters, `custom_components/lipro/services/`, `custom_components/lipro/runtime_infra.py` |
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
| `custom_components/lipro/core/protocol/` | Protocol formal root home | `LiproProtocolFacade`、canonical contracts、protocol-owned diagnostics/session truth |
| `custom_components/lipro/core/api/` | Protocol REST child-façade slice | `LiproRestFacade` collaborator family；稳定导入入口保留在 `core/api/client.py` |
| `custom_components/lipro/core/mqtt/` | Protocol MQTT child-façade slice | `LiproMqttFacade` 与 localized direct transport 归属于统一协议根之下 |
| `custom_components/lipro/core/coordinator/` | Runtime spine | Phase 5 做 invariant-level 正式化 |
| `custom_components/lipro/core/capability/` | Domain truth root | Phase 4 的正式 capability registry / snapshot home |
| `custom_components/lipro/core/device/` | Domain device aggregate | 聚合 facade、identity/state/extras 与 device views/support helpers |
| `custom_components/lipro/entities/` + platform modules | Domain projections | 只做 projection，不再定义第二套规则 |
| `custom_components/lipro/control/` | Control formal home | lifecycle、service router、runtime access、diagnostics/system-health formal ownership |
| `custom_components/lipro/services/` + root thin adapters | Control helpers / adapters | service declarations、request shaping、thin adapter helpers；不得讲成第二 control root |
| `custom_components/lipro/runtime_infra.py` | Shared runtime-infra ownership | device-registry listener、pending reload coordination、shared runtime bootstrap；不是替代 control formal home 的第二根 |
| `tests/` | Assurance implementation | 测试结构必须跟随正式架构迁移 |

## Non-Goals by Plane

- **Protocol plane** 不拥有 HA entity/control 语义
- **Runtime plane** 不拥有 vendor payload 编解码与签名恢复细节
- **Domain plane** 不拥有 auth/retry/network recovery
- **Control plane** 不反向定义 runtime internals
- **Assurance plane** 观察与仲裁，但不承载业务编排

## Transitional Residue Rules

- legacy client names（`LiproClient` / `LiproMqttClient`）不属于 target topology，必须继续保持删除或禁回流状态，不能再被写成 current public/formal root
- 任何 mixin client、影子 helper、旧 public names 都不属于终态拓扑
- 迁移残留必须在 `RESIDUAL_LEDGER` 和 `KILL_LIST` 同步记录

---
*Used by: Phase 1.5+ planning, design review, and verification*
