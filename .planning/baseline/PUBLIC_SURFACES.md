# Public Surfaces

**Purpose:** 定义各平面的 canonical public surfaces、过渡公开面与禁止作为正式入口的对象。
**Status:** Formal baseline asset (`BASE-01` public-surface truth source)
**Updated:** 2026-03-12

## Formal Role

- 本文件是 canonical / transitional / forbidden public surfaces 的唯一 baseline 清单。
- canonical public surface 必须映射回 `TARGET_TOPOLOGY.md` 中已声明的 formal root / root set；compat shell 不得反向提升为 architecture truth。
- transitional public surface 只是带退出条件的临时允许面，不构成第二套正式 root 语义。

## Canonical Public Surfaces

| Plane / Scope | Canonical Surface | Formal Role | Notes |
|---------------|-------------------|-------------|-------|
| Protocol | `LiproProtocolFacade` | target-state formal protocol root | 终态唯一正式协议根 |
| Protocol (Phase 2) | `LiproRestFacade` | phase-local canonical REST sub-facade | Phase 2 可直接引用的正式 REST surface，但必须收敛到 `LiproProtocolFacade` |
| Runtime | `Coordinator` + runtime services/public surface | runtime orchestration root + stable service surface | 运行面唯一正式编排出口 |
| Domain | `CapabilityRegistry` / `CapabilitySnapshot` / command contracts | domain truth surface family | 统一能力真源与投影来源 |
| Control | `EntryLifecycleController`, `ServiceRegistry`, `DiagnosticsSurface`, `SystemHealthSurface` | control-plane formal surface set | 控制面正式组件 |
| Assurance | contract suites, invariant suites, meta guards, ledgers | assurance arbitration surface set | 保障面的正式裁决面 |

## Transitional Public Surfaces

| Surface | Allowed Until | Exit Condition |
|---------|---------------|----------------|
| `LiproClient` compat shell | Phase 2 / 2.5 migration only | `LiproProtocolFacade` 接管正式入口且调用方迁移完成 |
| legacy wrapper outputs | active migration only | 新 canonical contracts 覆盖旧 consumers |
| cluster-level `FILE_MATRIX` | pre-Phase 7 | 升级为 file-level 378/378 视图 |

## Forbidden As Formal Roots

- mixin-based mega client
- direct transport/auth objects exposed to entity/control plane
- MQTT client object as runtime/entity public truth
- raw vendor payloads as domain/runtime public contracts
- ad-hoc helper exports that bypass formal plane roots

## Update Rule

若某 phase：
- 新建了正式 public surface
- 删除了旧 public surface
- 降级了某 compat shell

则必须同步更新：
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`

Phase `01.5-02` seed scope：`tests/meta/test_public_surface_guards.py` 当前只守住三件事——`Coordinator` 保持窄 runtime surface、`LiproClient` 仍被归类为 transitional compat shell、`custom_components.lipro.core.api` 不得重新导出 transport internals/legacy helper names。

---
*Used by: API/runtime/control/capability phase planning and meta guard design*
