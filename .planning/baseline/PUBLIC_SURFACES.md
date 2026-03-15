# Public Surfaces

**Purpose:** 定义各平面的 canonical public surfaces、过渡公开面与禁止作为正式入口的对象。
**Status:** Formal baseline asset (`BASE-01` public-surface truth source)
**Updated:** 2026-03-15 (Phase 17 final residual retirement)

## Formal Role

- 本文件是 canonical / transitional / forbidden public surfaces 的唯一 baseline 清单。
- canonical public surface 必须映射回 `TARGET_TOPOLOGY.md` 中已声明的 formal root / root set；compat shell 不得反向提升为 architecture truth。
- transitional public surface 只是带退出条件的临时允许面，不构成第二套正式 root 语义。
- `.planning/baseline/ARCHITECTURE_POLICY.md` 负责把这些 public-surface truth 映射成可执行 rule ids 与 targeted regression bans。
- `.planning/codebase/*.md` 只允许作为 derived collaboration maps / 协作图谱；它们可以解释 locality，但不能升级成平行 authority chain。

## Canonical Public Surfaces

| Plane / Scope | Canonical Surface | Formal Role | Notes |
|---------------|-------------------|-------------|-------|
| Protocol | `LiproProtocolFacade` | target-state formal protocol root | 终态唯一正式协议根；formal contract 由显式 methods/properties 定义，不再由 child `__getattr__` / `__dir__` 隐式扩面 |
| Protocol (REST child) | `LiproRestFacade` | canonical REST child façade | formal REST child surface；必须始终收敛到 `LiproProtocolFacade` |
| Runtime | `Coordinator` + runtime services/public surface | runtime orchestration root + stable service surface | protocol-facing runtime ops 统一经 `CoordinatorProtocolService` 收口；`devices` 只允许以 read-only mapping 暴露；outlet power 真源收口到 `LiproDevice.outlet_power_info` |
| Domain | `CapabilityRegistry` / `CapabilitySnapshot` / `LiproDevice` + `DeviceState` explicit surface / command contracts | domain truth surface family | `custom_components/lipro/core/capability/` 与 `custom_components/lipro/core/device/` 共同定义显式设备域真源；动态 `__getattr__` 不再合法化 |
| Control | `EntryLifecycleController`、`ServiceRegistry`、`service_router`、`DiagnosticsSurface`、`SystemHealthSurface`、`telemetry_surface` bridge helpers | control-plane formal surface set | `custom_components/lipro/control/` 为正式内部控制面 home；HA 根模块只保留 adapter 职责 |
| Assurance | contract suites、invariant suites、meta guards、ledgers、`RuntimeTelemetryExporter` / telemetry contracts、replay harness/report surfaces、`V1_1_EVIDENCE_INDEX.md`、`tests/harness/evidence_pack/*`、`scripts/export_ai_debug_evidence_pack.py` | assurance arbitration surface set | exporter / replay / evidence index / evidence-pack tooling 只作为 assurance-only 或 pull-only truth consumers，不得反向成为 runtime/control/public root |

## Assurance-only Extension Rules

- `custom_components/lipro/core/telemetry/*` 与 `custom_components/lipro/control/telemetry_surface.py` 只承担 observer-only telemetry truth 输出与 control bridge 角色；runtime / entity / platform 不得把它们当成第二条业务主链。
- `tests/harness/protocol/*`、`tests/fixtures/protocol_replay/*`、`tests/integration/test_protocol_replay_harness.py` 与 replay run summary 只属于 assurance-only replay surfaces；生产路径只能被它们验证，不能反向依赖它们。
- `.planning/reviews/V1_1_EVIDENCE_INDEX.md` 与 Phase 8 evidence-pack 入口都必须是 pull-only evidence pointers：只能索引正式真源，不得重新扫描仓库拼出第二套事实。
- `tests/harness/evidence_pack/*`、`scripts/export_ai_debug_evidence_pack.py` 与生成的 `ai_debug_evidence_pack.json` / `ai_debug_evidence_pack.index.md` 只属于 assurance-only evidence-pack surfaces；AI / tooling 可以消费它们，但 runtime / control / entity 不得反向依赖它们。

## Transitional Public Surfaces

| Surface | Allowed Until | Exit Condition |
|---------|---------------|----------------|
| cluster-level `FILE_MATRIX` | pre-Phase 7 | 升级为 file-level governance view |

## Phase 17 Final Residual Retirement Notes

- `custom_components/lipro/core/api/client_base.py` 现在只保留 `ClientSessionState` formal REST session state；`_ClientBase` 已从 production truth 退场。
- `custom_components/lipro/core/api/client_transport.py` 现在只保留 `TransportExecutor` / explicit transport helpers；`_ClientTransportMixin` 已退场。
- REST endpoint legacy mixin family 已退场；formal collaborator set 固定为 `AuthEndpoints`、`CommandEndpoints`、`DeviceEndpoints`、`MiscEndpoints`、`ScheduleEndpoints`、`StatusEndpoints` 与 `_EndpointAdapter` local typed port。
- `MqttTransportClient` 是 canonical MQTT concrete transport，但不是 public surface；只允许停留在 `core/mqtt` + `core/protocol`。
- token persistence 只消费 `AuthSessionSnapshot`；`get_auth_data()` compatibility projection 已从正式路径退场。
- outlet-power 正式 contract 只承认 `OutletPowerInfoRow | list[OutletPowerInfoRow]`；synthetic `{"data": rows}` 已退出 formal path。

## Phase 16 Governance Calibration Notes

- `custom_components/lipro/services/execution.py` 继续保留为正式 service execution facade；coordinator 私有 auth seam 已在 Phase 5 关闭，不得重新登记为 active public residual。
- `.planning/codebase/*.md` 只承担 derived collaboration map 角色；它们可以解释 public surface locality，但不能反向定义 canonical / transitional / forbidden surface truth。

## Phase 15 Surface Closure Notes

- `get_developer_report` local debug view 与 developer-feedback upload projector 现在明确分家：上传 shaping 固定在 `core/anonymous_share/report_builder.py`，而不是回流到 `service_router.py`。
- `control/service_router.py` 继续保留 public handler home 身份；`developer_router_support.py` 与 `runtime_access.py` 承接 diagnostics glue 与 host-side typing follow-through。
- Phase 15 只完成 locality / ownership wording；Phase 17 已完成最后一批 API / MQTT residual 的物理清退与命名收口。

## Phase 14 Surface Closure Notes

- `Coordinator` 的 protocol-facing runtime ops 已收口到 `CoordinatorProtocolService`；control 与 runtime 不得再通过 protocol façade 直取 concrete transport。
- `status_fallback.py` 与 `developer_router_support.py` 已成为 focused helper homes；`status_service.py` 与 `service_router.py` 仅保留 public orchestration / handler 身份。
- `DeviceCapabilities` compat alias 与 `core/device/capabilities.py` 已删除；能力真源固定在 `core/capability/CapabilityRegistry` / `CapabilitySnapshot`。

## Phase 09 Surface Closure Notes

- `custom_components/lipro/core/protocol/facade.py` 已改为显式 root contract：`LiproProtocolFacade` 与 `LiproMqttFacade` 不再通过 `__getattr__` / `__dir__` 扩面，child surface 不再反向定义 root。
- `custom_components/lipro/__init__.py`、`custom_components/lipro/config_flow.py`、`custom_components/lipro/core/__init__.py` 与 `custom_components/lipro/core/mqtt/__init__.py` 的 legacy public-name / compat export 已在 Phase 09 收口；`core.api.LiproClient` compat shell 已在 Phase 12 正式删除。
- `Coordinator.devices` 现在只暴露 read-only mapping；live mutable runtime registry 继续留在 coordinator internal state，不再作为 formal public surface。
- `custom_components/lipro/core/device/device.py` 中的 `LiproDevice.outlet_power_info` 已成为 outlet power 单一正式 primitive；`extra_data["power_info"]` 仅允许作为 legacy read fallback，不再承担正式 truth 角色。

## Phase 10 Surface Boundary Notes

- `custom_components/lipro/core/__init__.py` 现在只保留 host-neutral exports：`LiproProtocolFacade`、`LiproMqttFacade`、`LiproRestFacade`、`AuthSessionSnapshot` 等；`Coordinator` 不再从这里导出。
- `custom_components/lipro/coordinator_entry.py` 继续是 `Coordinator` 的唯一 runtime-home public surface；HA adapters 应通过该 home 或 `custom_components/lipro/control/runtime_access.py` 读取 runtime root。
- `custom_components/lipro/control/telemetry_surface.py` 现在必须经 `runtime_access.get_entry_runtime_coordinator()` 定位 runtime home，避免 `entry.runtime_data` 访问在 control plane 四处蔓延。
- `custom_components/lipro/config_flow.py` 与 `custom_components/lipro/entry_auth.py` 已切到 `AuthSessionSnapshot` / auth manager formal contract，不再把 raw login/result dict 当 public surface。

## Phase 11 Control / Surface Closeout Notes

- `custom_components/lipro/control/service_router.py` 已成为 control-plane 唯一正式 service callback home；`custom_components/lipro/services/registrations.py` 只做 HA service declaration 绑定。
- legacy wiring compat shell 已正式删除，不再属于 transitional public surface，也不得作为 patch / import truth 回流。
- `custom_components/lipro/control/runtime_access.py` 继续是 control-plane runtime locator；control adapters 不得再旁路读取 coordinator internals。

## Forbidden As Formal Roots

- mixin-based mega client
- direct transport/auth objects exposed to entity/control plane
- concrete MQTT transport object as runtime/entity public truth
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
| `ENF-IMP-API-LEGACY-SPINE-LOCALITY` | `client_base.py` / `client_pacing.py` / `client_auth_recovery.py` / `client_transport.py` 只能继续局部停留在 `core/api` | local helper/session modules 不得扩散到生产其它平面 |
| `ENF-IMP-MQTT-TRANSPORT-LOCALITY` | `MqttTransportClient` 不能新增 direct production consumers | concrete transport 继续局限在 protocol/mqtt seam |
| `ENF-IMP-ASSURANCE-NO-PRODUCTION-BACKFLOW` | assurance-only artifacts 不得被 production path 反向依赖 | replay / evidence 继续保持 pull-only / assurance-only |
| `ENF-GOV-RELEASE-CI-REUSE` | `release.yml` 必须复用 `ci.yml` 并保持 validate gate | 发布链不得旁路治理与版本守卫 |
| `ENF-COMPAT-ROOT-NO-LEGACY-CLIENT` | root adapter 不得重新绑定 legacy names 或 concrete transport exports | `LiproClient` / `LiproMqttClient` / `MqttTransportClient` 都不得回流 |
| `ENF-COMPAT-CONFIG-FLOW-NO-LEGACY-CLIENT` | config flow 只使用 `LiproProtocolFacade`，不得回流 legacy client names 或 concrete transport | Phase 9 compat export ban + Phase 17 no-concrete-export follow-through |
| `ENF-COMPAT-CORE-PACKAGE-NO-LEGACY-CLIENTS` | `core/__init__.py` 不得重新导出 legacy client names、`Coordinator` 或 concrete transport | package-level compat/runtime-home demotion guard |
| `ENF-COMPAT-MQTT-PACKAGE-NO-LEGACY-CLIENT` | `core/mqtt/__init__.py` 不得重新暴露 `LiproMqttClient` 或 `MqttTransportClient` | MQTT package no-concrete-transport-export guard |

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
