# Public Surfaces

**Purpose:** 定义各平面的 canonical public surfaces、过渡公开面与禁止作为正式入口的对象。
**Status:** Formal baseline asset (`BASE-01` public-surface truth source)
**Updated:** 2026-03-14

## Formal Role

- 本文件是 canonical / transitional / forbidden public surfaces 的唯一 baseline 清单。
- canonical public surface 必须映射回 `TARGET_TOPOLOGY.md` 中已声明的 formal root / root set；compat shell 不得反向提升为 architecture truth。
- transitional public surface 只是带退出条件的临时允许面，不构成第二套正式 root 语义。
- `.planning/baseline/ARCHITECTURE_POLICY.md` 负责把这些 public-surface truth 映射成可执行 rule ids 与 targeted regression bans。

## Canonical Public Surfaces

| Plane / Scope | Canonical Surface | Formal Role | Notes |
|---------------|-------------------|-------------|-------|
| Protocol | `LiproProtocolFacade` | target-state formal protocol root | 终态唯一正式协议根；formal contract 由显式 methods/properties 定义，不再由 child `__getattr__` / `__dir__` 隐式扩面 |
| Protocol (Phase 2) | `LiproRestFacade` | phase-local canonical REST sub-facade | Phase 2 可直接引用的正式 REST surface，但必须收敛到 `LiproProtocolFacade` |
| Runtime | `Coordinator` + runtime services/public surface | runtime orchestration root + stable service surface | 运行面唯一正式编排出口；`devices` 只允许以 read-only mapping 暴露，outlet power 真源收口到 `LiproDevice.outlet_power_info` |
| Domain | `CapabilityRegistry` / `CapabilitySnapshot` / command contracts | domain truth surface family | `custom_components/lipro/core/capability/` 为统一能力真源与投影来源 |
| Control | `EntryLifecycleController`, `ServiceRegistry`, `service_router`, `DiagnosticsSurface`, `SystemHealthSurface`, `telemetry_surface` bridge helpers | control-plane formal surface set | `custom_components/lipro/control/` 为正式内部控制面 home；`control/service_router.py` 是 service callback formal home；HA 根模块只保留 adapter 职责，telemetry bridge 只负责定位 exporter |
| Assurance | contract suites, invariant suites, meta guards, ledgers, `RuntimeTelemetryExporter` / telemetry contracts, replay harness/report surfaces, `V1_1_EVIDENCE_INDEX.md`, `tests/harness/evidence_pack/*`, `scripts/export_ai_debug_evidence_pack.py` | assurance arbitration surface set | exporter / replay / evidence index / evidence-pack tooling 只作为 assurance-only 或 pull-only truth consumers，不得反向成为 runtime/control/public root |

## Assurance-only Extension Rules

- `custom_components/lipro/core/telemetry/*` 与 `custom_components/lipro/control/telemetry_surface.py` 只承担 observer-only telemetry truth 输出与 control bridge 角色；runtime / entity / platform 不得把它们当成第二条业务主链。
- `tests/harness/protocol/*`、`tests/fixtures/protocol_replay/*`、`tests/integration/test_protocol_replay_harness.py` 与 replay run summary 只属于 assurance-only replay surfaces；生产路径只能被它们验证，不能反向依赖它们。
- `.planning/reviews/V1_1_EVIDENCE_INDEX.md` 以及后续 `Phase 8` evidence pack 入口都必须是 pull-only evidence pointers：只能索引正式真源，不得重新扫描仓库拼出第二套事实。
- `tests/harness/evidence_pack/*`、`scripts/export_ai_debug_evidence_pack.py` 与生成的 `ai_debug_evidence_pack.json` / `ai_debug_evidence_pack.index.md` 只属于 assurance-only evidence-pack surfaces；AI / tooling 可以消费它们，但 runtime / control / entity 不得反向依赖它们。

## Transitional Public Surfaces

| Surface | Allowed Until | Exit Condition |
|---------|---------------|----------------|
| `core.api.LiproClient` compat shell | Phase 9+ cleanup only | 仅保留 `custom_components.lipro.core.api` 显式 compat shell；root / flow / core 包级再导出已收口 |
| `LiproMqttClient` compat shell | Phase 9+ cleanup only | 仅剩 direct transport module 与 `LiproMqttFacade.raw_client` 测试 seam；包级 public export 已收口 |
| `LiproProtocolFacade.get_device_list` compat wrapper | active migration only | wrapper 仍保留显式 compat 语义，但正式真源已切到 `rest.device-list@v1` + `CanonicalProtocolContracts.normalize_device_list_page`；direct consumers 清零后删除 |
| `DeviceCapabilities` compat alias | Phase 4 / 7 cleanup only | `core/device/capabilities.py` 的旧导入点迁移到 `CapabilitySnapshot` / `CapabilityRegistry` |
| `services/wiring.py` compat shell | Phase 11+ cleanup only | 仓库内 tests/production 已切离；remaining downstream imports 清零后删除 compat shell |
| cluster-level `FILE_MATRIX` | pre-Phase 7 | 升级为 file-level governance view |

## Phase 09 Surface Closure Notes

- `custom_components/lipro/core/protocol/facade.py` 已改为显式 root contract：`LiproProtocolFacade` 与 `LiproMqttFacade` 不再通过 `__getattr__` / `__dir__` 扩面，child surface 不再反向定义 root。
- `custom_components/lipro/__init__.py`、`custom_components/lipro/config_flow.py`、`custom_components/lipro/core/__init__.py` 与 `custom_components/lipro/core/mqtt/__init__.py` 的 legacy public-name / compat export 已收口；`custom_components/lipro/core/api/__init__.py` 中的 `LiproClient` 是唯一仍登记的显式 compat shell。
- `Coordinator.devices` 现在只暴露 read-only mapping；live mutable runtime registry 继续留在 coordinator internal state，不再作为 formal public surface。
- `custom_components/lipro/core/device/device.py` 中的 `LiproDevice.outlet_power_info` 已成为 outlet power 单一正式 primitive；`extra_data["power_info"]` 仅允许作为 legacy read fallback，不再承担正式 truth 角色。

## Phase 10 Surface Boundary Notes

- `custom_components/lipro/core/__init__.py` 现在只保留 host-neutral exports：`LiproProtocolFacade`、`LiproMqttFacade`、`LiproRestFacade`、`AuthSessionSnapshot` 等；`Coordinator` 不再从这里导出。
- `custom_components/lipro/coordinator_entry.py` 继续是 `Coordinator` 的唯一 runtime-home public surface；HA adapters 应通过该 home 或 `custom_components/lipro/control/runtime_access.py` 读取 runtime root。
- `custom_components/lipro/control/telemetry_surface.py` 现在必须经 `runtime_access.get_entry_runtime_coordinator()` 定位 runtime home，避免 `entry.runtime_data` 访问在 control plane 四处蔓延。
- `custom_components/lipro/config_flow.py` 与 `custom_components/lipro/entry_auth.py` 已切到 `AuthSessionSnapshot` / auth manager formal contract，不再把 raw login/result dict 当 public surface。

## Forbidden As Formal Roots

- mixin-based mega client
- direct transport/auth objects exposed to entity/control plane
- MQTT client object as runtime/entity public truth
- raw vendor payloads as domain/runtime public contracts
- `core/protocol/boundary/*` decoder package as runtime/control/domain/entity public surface
- ad-hoc helper exports that bypass formal plane roots
- `tests/harness/protocol/*` / replay reports / evidence index / `tests/harness/evidence_pack/*` / `scripts/export_ai_debug_evidence_pack.py` / generated evidence pack outputs 被当作 runtime、control、entity public surface

## Architecture Policy Mapping

| Rule ID | Enforces | Notes |
|--------|----------|-------|
| `ENF-SURFACE-COORDINATOR-ENTRY` | `coordinator_entry.py` 只暴露 runtime root symbol | 单一 runtime root |
| `ENF-SURFACE-API-EXPORTS` | `core/api/__init__.py` 不导出 transport / auth / policy internals | compat shell 不能扩成新 root |
| `ENF-SURFACE-PROTOCOL-EXPORTS` | `core/protocol/__init__.py` 不导出 boundary decoder internals | `boundary/*` 维持 protocol-local collaborator 身份 |
| `ENF-BACKDOOR-COORDINATOR-PROPERTIES` | `Coordinator` 不暴露 runtime internals properties | 防止 runtime surface 变宽 |
| `ENF-BACKDOOR-SERVICE-AUTH` | service execution 不再回退到 coordinator 私有 auth seam | backdoor ban |
| `ENF-COMPAT-ROOT-NO-LEGACY-CLIENT` | root adapter 不得重新绑定 `LiproClient` / `LiproMqttClient` | Phase 9 compat export ban |
| `ENF-COMPAT-CONFIG-FLOW-NO-LEGACY-CLIENT` | config flow 只使用 `LiproProtocolFacade`，不得回流 legacy client names | Phase 9 compat export ban |
| `ENF-COMPAT-CORE-PACKAGE-NO-LEGACY-CLIENTS` | `core/__init__.py` 不得重新导出 legacy client names 或 `Coordinator` | package-level compat/runtime-home demotion guard |
| `ENF-COMPAT-MQTT-PACKAGE-NO-LEGACY-CLIENT` | `core/mqtt/__init__.py` 不得重新暴露 `LiproMqttClient` | MQTT package compat demotion guard |

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
