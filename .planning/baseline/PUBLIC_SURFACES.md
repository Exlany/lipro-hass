# Public Surfaces

**Purpose:** 定义各平面的 canonical public surfaces、过渡公开面与禁止作为正式入口的对象。
**Status:** Formal baseline asset (`BASE-01` public-surface truth source)
**Updated:** 2026-03-20 (Phase 43 control/runtime/service boundary aligned)

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
| Runtime | `Coordinator` + runtime services/public surface | runtime orchestration root + stable service surface | protocol-facing runtime ops 统一经 `CoordinatorProtocolService` / `coordinator.protocol_service` 收口；schedule / diagnostics / OTA consumers 不再经 coordinator 顶层 passthrough operations 取能力；`devices` 只允许以 read-only mapping 暴露；outlet power 真源收口到 `LiproDevice.outlet_power_info` |
| Domain | `CapabilityRegistry` / `CapabilitySnapshot` / `LiproDevice` + `DeviceState` explicit surface / command contracts | domain truth surface family | `custom_components/lipro/core/capability/` 与 `custom_components/lipro/core/device/` 共同定义显式设备域真源；动态 `__getattr__` 不再合法化；HA platform strings / config-entry projection 只允许停留在 adapter seams |
| Control | `EntryLifecycleController`、`ServiceRegistry`、`service_router`、`DiagnosticsSurface`、`SystemHealthSurface`、`telemetry_surface` bridge helpers | control-plane formal surface set | `custom_components/lipro/control/` 为正式内部控制面 home；HA 根模块只保留 adapter 职责 |
| Assurance | contract suites、invariant suites、meta guards、ledgers、`RuntimeTelemetryExporter` / telemetry contracts、replay harness/report surfaces、`V1_1_EVIDENCE_INDEX.md`、`V1_2_EVIDENCE_INDEX.md`、`tests/harness/evidence_pack/*`、`scripts/export_ai_debug_evidence_pack.py`、`v1.2-MILESTONE-AUDIT.md`、`v1.3-HANDOFF.md` | assurance arbitration surface set | exporter / replay / evidence index / milestone audit / handoff tooling 只作为 assurance-only 或 pull-only truth consumers，不得反向成为 runtime/control/public root |

## Assurance-only Extension Rules

- `custom_components/lipro/core/telemetry/*` 与 `custom_components/lipro/control/telemetry_surface.py` 只承担 observer-only telemetry truth 输出与 control bridge 角色；control-plane bridge 只能通过 `runtime_access` + `Coordinator.protocol` / `telemetry_service` pull 正式 telemetry truth，runtime / entity / platform 不得把它们当成第二条业务主链。
- `tests/harness/protocol/*`、`tests/fixtures/protocol_replay/*`、`tests/integration/test_protocol_replay_harness.py` 与 replay run summary 只属于 assurance-only replay surfaces；生产路径只能被它们验证，不能反向依赖它们。
- `.planning/reviews/V1_1_EVIDENCE_INDEX.md`、`.planning/reviews/V1_2_EVIDENCE_INDEX.md` 与 milestone closeout evidence 入口都必须是 pull-only evidence pointers：只能索引正式真源，不得重新扫描仓库拼出第二套事实。
- `tests/harness/evidence_pack/*`、`scripts/export_ai_debug_evidence_pack.py` 与生成的 `ai_debug_evidence_pack.json` / `ai_debug_evidence_pack.index.md` 只属于 assurance-only evidence-pack surfaces；AI / tooling 可以消费它们，但 runtime / control / entity 不得反向依赖它们。

## Phase 40 Governance Truth Surface Notes

- `.planning/baseline/GOVERNANCE_REGISTRY.json` 是 governance-only 的 machine-readable baseline asset：它只承载 active governance facts（版本、安装、support routing、release trust、continuity），不是 runtime / control / protocol 的 public API。
- `.planning/MILESTONES.md`、`.planning/milestones/*.md`、`.planning/v1.5-MILESTONE-AUDIT.md` 与 `V1_5_EVIDENCE_INDEX.md` 继续只承担 archive / audit / handoff 身份；它们可以作为历史证据被引用，但不得回流为 current governance truth。
- `custom_components/lipro/control/runtime_access.py` 是 control/services 读取 runtime entry 枚举、device lookup 与 snapshot projection 的唯一正式 read-model home。
- `custom_components/lipro/services/execution.py` 同时保持 `formal shared service execution facade` 身份；`schedule.py` 复用它的 shared executor，而不是维护第二条 auth/error 执行链。
- `docs/README.md` 只负责解释当前可读入口与 active-vs-archive 边界，不得把 milestone snapshots 或 phase workspace assets 重新讲成对外 current source。

## Phase 43 Control / Runtime Boundary Notes

- `custom_components/lipro/control/runtime_access.py` 现在同时固定 typed diagnostics/system-health projection 与 entry-scoped runtime lookup；control consumers 不再混搭 coordinator internals / ad-hoc mapping reads。
- `custom_components/lipro/control/service_router_support.py` 是 service callback 热路径里唯一正式 `(device, coordinator)` bridge；`custom_components/lipro/services/device_lookup.py` 只保留 service-facing `device_id` resolution，不再拥有 runtime truth。
- `custom_components/lipro/runtime_infra.py` 成为 device-registry listener、pending reload task cleanup 与 reload coordination 的正式 home；`custom_components/lipro/services/maintenance.py` 只保留 `refresh_devices` thin adapter。
- `custom_components/lipro/control/service_router.py` 继续是 public callback home；`services/registrations.py` 仅做 HA service declaration binding，没有第二条 service-ownership story。

## Transitional Public Surfaces

| Surface | Allowed Until | Exit Condition |
|---------|---------------|----------------|
| cluster-level `FILE_MATRIX` | pre-Phase 7 | 升级为 file-level governance view |

## Phase 25.2 Telemetry Formal-Surface Closure Notes

- `runtime_types.LiproCoordinator` 现显式暴露 bridge 真正需要的 `protocol` 与 `telemetry_service`；`Coordinator.client` 不再被视为 control-plane formal surface。
- `custom_components/lipro/control/telemetry_surface.py` 现在只通过 `runtime_access.get_entry_runtime_coordinator()` + `Coordinator.protocol` 构建 protocol telemetry source，不再合法化 legacy protocol-handle seam (`Coordinator.client`)。
- 本 phase 只关闭 source-binding honesty seam；`RuntimeTelemetryExporter` schema / sink payload 保持稳定，未引入第二条 telemetry root。

## Phase 35 Protocol Hotspot Final Slimming Notes

- `LiproRestFacade` 仍是唯一 canonical REST child façade；`client.py` 只保留 stable import home，request pipeline / endpoint-operation 复杂度已正式下沉到 `request_gateway.py`、`transport_executor.py` 与 `endpoint_surface.py`，它们只是 localized collaborators，不是新 public roots。
- `LiproProtocolFacade` 继续是唯一 protocol-plane root；`rest_port.py` 只是 typed REST child-façade port，`mqtt_facade.py` 只是 MQTT child façade home，二者都不得被上层当作 package-level alternative root。
- 本 phase 只切薄 formal root / child façade body，不新增 package export、不回流 `__getattr__` 式隐式扩面，也不改变外部 formal import story。

## Phase 36 Runtime Root / Polling Surface Notes

- `Coordinator` 仍是唯一 runtime orchestration root；`CoordinatorPollingService` 只是 runtime/service seam 的 helper home，用于承接 polling / snapshot / outlet power orchestration，不能被 control/entity/platform 直接当作新 public surface 消费。
- runtime public surface 仍以 `Coordinator`、`CoordinatorProtocolService`、`CoordinatorMqttService`、`CoordinatorStateService` 与正式 service homes 为准；typed exception arbitration 只是 root/service behavior hardening，不构成第二条 runtime story。
- `command_service.py`、`mqtt_lifecycle.py`、`device_runtime.py`、`mqtt_runtime.py` 与 `snapshot.py` 的 typed failure 语义属于 runtime internal contracts；外部公开面没有新增 broad-catch escape hatch。

## Phase 37 Test Topology / Derived-Truth Notes

- `tests/core/test_init_service_handlers*.py`、`tests/core/test_init_runtime*.py` 与 `tests/meta/test_governance_phase_history*.py` 属于 assurance topology topicization，不是 production public surface 的扩张。
- 聚合测试文件现在只保留 shared helper / topic root 身份；`test_init_service_handlers.py`、`test_init_runtime_behavior.py` 与 `test_governance_phase_history.py` 不再承担所有子主题。
- `.planning/codebase/*` 继续只是 derived collaboration maps；Phase 37 关闭的是 topology drift，而不是抬升派生文档为 authority。

## Phase 27 Hotspot Slimming & Residual-Honesty Notes

- `runtime_types.LiproCoordinator` 现显式暴露 `protocol_service`：schedule / diagnostics / OTA capability consumers 只能 pull `coordinator.protocol_service`，不再把 coordinator 顶层 `async_*` passthrough operations 当 formal runtime surface。
- `custom_components/lipro/core/coordinator/coordinator.py` 已删除 schedule / diagnostics / OTA / outlet-power passthrough operation cluster；保留的 `get_device` / `register_entity` / `get_device_lock` 仍属于 entity-facing runtime helper，而不是 protocol passthrough。
- runtime 正式代码已清理 `Phase C` / `Phase H4` 这类历史迁移叙事；若未来继续切薄 hotspot，必须沿现有 service / child-façade home 下沉，而不是新增第二 root。

## Phase 17 Final Residual Retirement Notes

- `custom_components/lipro/core/api/session_state.py` 现在只保留 `RestSessionState` formal REST session state；`_ClientBase` 已从 production truth 退场。
- `custom_components/lipro/core/api/transport_executor.py` 现在只保留 `RestTransportExecutor` / explicit transport helpers；`_ClientTransportMixin` 已退场。
- REST endpoint legacy inheritance-aggregate family 已退场；formal collaborator set 固定为 `AuthEndpoints`、`CommandEndpoints`、`DeviceEndpoints`、`MiscEndpoints`、`ScheduleEndpoints`、`StatusEndpoints` 与 `_EndpointAdapter` local typed port。
- `MqttTransport` 是 canonical MQTT concrete transport，但不是 public surface；只允许停留在 `core/mqtt` + `core/protocol`。
- token persistence 只消费 `AuthSessionSnapshot`；`get_auth_data()` compatibility projection 已从正式路径退场。
- outlet-power 正式 contract 只承认 `OutletPowerInfoRow | list[OutletPowerInfoRow]`；synthetic `{"data": rows}` 已退出 formal path。

## Phase 18 Host-Neutral Nucleus Notes

- `custom_components/lipro/core/auth/bootstrap.py` 现在是 host-neutral auth/bootstrap helper home：`config_flow.py` 与 `entry_auth.py` 只允许通过它装配 protocol/auth collaborators，不得把它误判成新的 protocol 或 control root。
- `custom_components/lipro/flow/login.py::ConfigEntryLoginProjection` 是 HA config-entry projection home；`AuthSessionSnapshot` 继续是唯一正式 auth/session truth。
- `custom_components/lipro/helpers/platform.py` 是唯一 HA platform projection home；`DeviceCategory`、`CapabilitySnapshot`、`CapabilityRegistry`、`LiproDevice` 与 `device_views` 继续保持 host-neutral nucleus 身份。
- `CATEGORY_TO_PLATFORMS`、`get_platforms_for_category()`、`CapabilitySnapshot.platforms`、`supports_platform()` 与 `device_views.platforms()` 已从 nucleus truth 退场，并由 targeted bans 阻断回流。


## Phase 16 Governance Calibration Notes

- `custom_components/lipro/services/execution.py` 继续保留为正式 shared service execution facade；schedule 等控制面服务必须复用它，不得重新长出第二条 auth/error 执行链。
- `custom_components/lipro/services/execution.py` 同时保持 `formal shared service execution facade` 身份；它不是 active residual，也不是 active kill target。
- `.planning/codebase/*.md` 只承担 derived collaboration map 角色；它们可以解释 public surface locality，但不能反向定义 canonical / transitional / forbidden surface truth。

## Phase 15 Surface Closure Notes

- `get_developer_report` local debug view 与 developer-feedback upload projector 现在明确分家：上传 shaping 固定在 `core/anonymous_share/report_builder.py`，而不是回流到 `service_router.py`。
- `control/service_router.py` 继续保留 public handler home 身份；`developer_router_support.py` 与 `runtime_access.py` 承接 diagnostics glue 与 host-side typing follow-through。
- `runtime_types.LiproCoordinator` 现在同时承接 diagnostics capability 与 runtime auth/command 正式 contract；developer diagnostics 不再维护第二套平级 coordinator truth。
- Phase 15 只完成 locality / ownership wording；Phase 17 已完成最后一批 API / MQTT residual 的物理清退与命名收口。

## Phase 14 Surface Closure Notes

- `Coordinator` 的 protocol-facing runtime ops 已收口到 `CoordinatorProtocolService`；control 与 runtime 不得再通过 protocol façade 直取 concrete transport。
- `status_fallback.py` 与 `developer_router_support.py` 已成为 focused helper homes；`status_service.py` 与 `service_router.py` 仅保留 public orchestration / handler 身份。
- `DeviceCapabilities` compat alias 与 `core/device/capabilities.py` 已删除；能力真源固定在 `core/capability/CapabilityRegistry` / `CapabilitySnapshot`。

## Phase 09 Surface Closure Notes

- `custom_components/lipro/core/protocol/facade.py` 已改为显式 root contract：`LiproProtocolFacade` 与 `LiproMqttFacade` 不再通过 `__getattr__` / `__dir__` 扩面，child surface 不再反向定义 root。
- `custom_components/lipro/__init__.py`、`custom_components/lipro/config_flow.py`、`custom_components/lipro/core/__init__.py` 与 `custom_components/lipro/core/mqtt/__init__.py` 的 legacy public-name / compat export 已在 Phase 09 收口；`core.api.LiproClient` compat shell 已在 Phase 12 正式删除。
- `Coordinator.devices` 现在只暴露 read-only mapping；live mutable runtime registry 继续留在 coordinator internal state，不再作为 formal public surface。
- `custom_components/lipro/control/runtime_access.py` 是 control/services 读取 runtime entry 枚举、device lookup 与 snapshot projection 的唯一正式 read-model home。
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

- inheritance-driven mega aggregate
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
| `ENF-IMP-API-LEGACY-SPINE-LOCALITY` | `session_state.py` / `client_pacing.py` / `auth_recovery.py` / `transport_executor.py` 只能继续局部停留在 `core/api` | local helper/session modules 不得扩散到生产其它平面 |
| `ENF-IMP-MQTT-TRANSPORT-LOCALITY` | `MqttTransport` 不能新增 direct production consumers | concrete transport 继续局限在 protocol/mqtt seam |
| `ENF-IMP-NUCLEUS-NO-HOMEASSISTANT-IMPORT` | `core/auth` / `core/capability` / `core/device` nucleus homes 不得直接 import `homeassistant` | host-neutral nucleus 不得吸入宿主生命周期语义 |
| `ENF-IMP-NUCLEUS-NO-PLATFORM-BACKFLOW` | nucleus homes 不得反向依赖 `helpers/platform.py` | adapter-only HA platform projection 不能定义 domain truth |
| `ENF-IMP-ASSURANCE-NO-PRODUCTION-BACKFLOW` | assurance-only artifacts 不得被 production path 反向依赖 | replay / evidence 继续保持 pull-only / assurance-only |
| `ENF-GOV-RELEASE-CI-REUSE` | `release.yml` 必须复用 `ci.yml` 并保持 validate gate | 发布链不得旁路治理与版本守卫 |
| `ENF-COMPAT-ROOT-NO-LEGACY-CLIENT` | root adapter 不得重新绑定 legacy names 或 concrete transport exports | `LiproClient` / `LiproMqttClient` / `MqttTransport` 都不得回流 |
| `ENF-COMPAT-CONFIG-FLOW-NO-LEGACY-CLIENT` | config flow 只使用 `LiproProtocolFacade`，不得回流 legacy client names 或 concrete transport | Phase 9 compat export ban + Phase 17 no-concrete-export follow-through |
| `ENF-COMPAT-CORE-PACKAGE-NO-LEGACY-CLIENTS` | `core/__init__.py` 不得重新导出 legacy client names、`Coordinator` 或 concrete transport | package-level compat/runtime-home demotion guard |
| `ENF-COMPAT-MQTT-PACKAGE-NO-LEGACY-CLIENT` | `core/mqtt/__init__.py` 不得重新暴露 `LiproMqttClient` 或 `MqttTransport` | MQTT package no-concrete-transport-export guard |
| `ENF-ADAPTER-CONFIG-FLOW-USES-AUTH-PROJECTION` | `config_flow.py` 必须通过 shared auth bootstrap + entry projection 组织登录路径 | HA adapter 不得重建第二套 auth truth |
| `ENF-ADAPTER-ENTRY-AUTH-USES-BOOTSTRAP` | `entry_auth.py` 必须复用 shared bootstrap wiring，而不是手工拼装 token / credential glue | outward seam 稳定，内部装配统一 |
| `ENF-HOSTPROJ-CATEGORIES-NO-HA-PLATFORMS` | `const/categories.py` 不得重新长回 HA platform mapping symbols | category truth 保持 host-neutral |
| `ENF-HOSTPROJ-CAPABILITY-NO-PLATFORM-FIELD` | `CapabilitySnapshot` 不得重新携带 `platforms` / `supports_platform()` | capability truth 保持 host-neutral |
| `ENF-HOSTPROJ-DEVICE-VIEWS-NO-PLATFORM-PROJECTION` | `device_views.py` 不得重新提供 `platforms()` projection helper | device views 只保留 host-neutral read-only surfaces |

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

## Phase 19 Headless Proof & Adapter Shell Notes

- `custom_components/lipro/headless/boot.py` 是 local proof-only boot seam：它只复用 `AuthBootstrapSeed` / `AuthSessionSnapshot` / `build_protocol_auth_context()`，不构成 canonical 或 transitional public surface。
- `custom_components/lipro/headless/__init__.py` 必须保持 no-export package 身份；`HeadlessBootContext`、`build_headless_boot_context()` 与 `build_password_boot_seed()` 只能通过具体文件路径被 proof/adapter 使用。
- `tests/harness/headless_consumer.py` 与 `tests/integration/test_headless_consumer_proof.py` 只属于 proof-only assurance consumer：允许证明 `auth -> device -> replay/evidence` 共用同一 nucleus，但不得升级成 authority source、runtime root 或 contributor-facing product surface。
- `config_flow.py` 与 `entry_auth.py` 现在共同 inward 到 `build_headless_boot_context()`；`ConfigEntryLoginProjection` 继续只属于 HA config-entry projection，`AuthSessionSnapshot` 继续是唯一正式 auth/session truth。
- `helpers/platform.py` 继续是唯一 HA platform projection home；各平台 `async_setup_entry()` 现在只保留 thin headless setup shell，`control/runtime_access.py` 仍是 control-plane locator，不得成为 platform/entity bridge。
- Phase 19 enforcement 由 `ENF-IMP-HEADLESS-PROOF-LOCALITY`、`ENF-IMP-PLATFORM-SHELL-NO-CONTROL-LOCATOR`、`ENF-PROOF-HEADLESS-PACKAGE-NO-EXPORTS` 与 `ENF-PROOF-HEADLESS-BOOT-NO-SECOND-ROOT-BACKFLOW` 共同负责。



## Phase 21-24 Closeout Notes

- shared `failure_summary` / `failure_entries` 语义属于 assurance/control consumer contract 的投影结果，不构成新的 public root，也不允许绕过 exporter / telemetry truth 直接定义正式 surface。
- `V1_2_EVIDENCE_INDEX.md`、`v1.2-MILESTONE-AUDIT.md` 与 `v1.3-HANDOFF.md` 都是 pull-only governance / handoff assets：它们消费既有 north-star / baseline / review truth，但不替代这些真源。
- `Phase 21-24` 对 public surfaces 的裁决是 **no new root / no new authority**：closeout 只允许同步 story 与 consumer wording，不允许把 replay、evidence、runbook 或 handoff 提升为第二业务入口。
