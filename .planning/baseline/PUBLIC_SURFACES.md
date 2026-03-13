# Public Surfaces

**Purpose:** 定义各平面的 canonical public surfaces、过渡公开面与禁止作为正式入口的对象。
**Status:** Formal baseline asset (`BASE-01` public-surface truth source)
**Updated:** 2026-03-13

## Formal Role

- 本文件是 canonical / transitional / forbidden public surfaces 的唯一 baseline 清单。
- canonical public surface 必须映射回 `TARGET_TOPOLOGY.md` 中已声明的 formal root / root set；compat shell 不得反向提升为 architecture truth。
- transitional public surface 只是带退出条件的临时允许面，不构成第二套正式 root 语义。
- `.planning/baseline/ARCHITECTURE_POLICY.md` 负责把这些 public-surface truth 映射成可执行 rule ids 与 targeted regression bans。

## Canonical Public Surfaces

| Plane / Scope | Canonical Surface | Formal Role | Notes |
|---------------|-------------------|-------------|-------|
| Protocol | `LiproProtocolFacade` | target-state formal protocol root | 终态唯一正式协议根 |
| Protocol (Phase 2) | `LiproRestFacade` | phase-local canonical REST sub-facade | Phase 2 可直接引用的正式 REST surface，但必须收敛到 `LiproProtocolFacade` |
| Runtime | `Coordinator` + runtime services/public surface | runtime orchestration root + stable service surface | 运行面唯一正式编排出口 |
| Domain | `CapabilityRegistry` / `CapabilitySnapshot` / command contracts | domain truth surface family | `custom_components/lipro/core/capability/` 为统一能力真源与投影来源 |
| Control | `EntryLifecycleController`, `ServiceRegistry`, `DiagnosticsSurface`, `SystemHealthSurface` | control-plane formal surface set | `custom_components/lipro/control/` 为正式内部控制面 home；HA 根模块只保留 adapter 职责 |
| Assurance | contract suites, invariant suites, meta guards, ledgers | assurance arbitration surface set | 保障面的正式裁决面 |

## Transitional Public Surfaces

| Surface | Allowed Until | Exit Condition |
|---------|---------------|----------------|
| `LiproClient` compat shell | Phase 2 / 2.5 migration only | production constructors / runtime-facing consumers 已切到 `LiproProtocolFacade`，仅剩显式 compat alias / wrapper 可删除 |
| `LiproMqttClient` compat shell | Phase 2.5 / 7 cleanup only | 仅剩 transport-level compat/export seam；runtime/control 正式入口不再感知它是 public root |
| legacy wrapper outputs | active migration only | 新 canonical contracts 覆盖旧 consumers |
| `DeviceCapabilities` compat alias | Phase 4 / 7 cleanup only | `core/device/capabilities.py` 的旧导入点迁移到 `CapabilitySnapshot` / `CapabilityRegistry` |
| cluster-level `FILE_MATRIX` | pre-Phase 7 | 升级为 file-level governance view |

## Forbidden As Formal Roots

- mixin-based mega client
- direct transport/auth objects exposed to entity/control plane
- MQTT client object as runtime/entity public truth
- raw vendor payloads as domain/runtime public contracts
- `core/protocol/boundary/*` decoder package as runtime/control/domain/entity public surface
- ad-hoc helper exports that bypass formal plane roots

## Architecture Policy Mapping

| Rule ID | Enforces | Notes |
|--------|----------|-------|
| `ENF-SURFACE-COORDINATOR-ENTRY` | `coordinator_entry.py` 只暴露 runtime root symbol | 单一 runtime root |
| `ENF-SURFACE-API-EXPORTS` | `core/api/__init__.py` 不导出 transport / auth / policy internals | compat shell 不能扩成新 root |
| `ENF-SURFACE-PROTOCOL-EXPORTS` | `core/protocol/__init__.py` 不导出 boundary decoder internals | `boundary/*` 维持 protocol-local collaborator 身份 |
| `ENF-BACKDOOR-COORDINATOR-PROPERTIES` | `Coordinator` 不暴露 runtime internals properties | 防止 runtime surface 变宽 |
| `ENF-BACKDOOR-SERVICE-AUTH` | service execution 不再回退到 coordinator 私有 auth seam | backdoor ban |

## Update Rule

若某 phase：
- 新建了正式 public surface
- 删除了旧 public surface
- 降级了某 compat shell
- 新增或修改了 `ARCHITECTURE_POLICY.md` 中的 surface / backdoor rules

则必须同步更新：
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/ARCHITECTURE_POLICY.md`

---
*Used by: API/runtime/control/capability phase planning, public-surface guards, and targeted regression bans*
