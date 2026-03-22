# Dependency Matrix

**Purpose:** 定义允许/禁止的跨平面依赖方向，并作为 architecture guards 的语义真源。
**Status:** Baseline reference
**Updated:** 2026-03-20 (Phase 43 control/service/runtime boundary aligned)

## Formal Role

- 本文件定义 allowed / forbidden dependency direction 的 baseline truth。
- `.planning/baseline/ARCHITECTURE_POLICY.md` 把这些语义规则翻译成可执行的 rule ids 与 enforcement chain；两者必须同步演进，不能各写各的 seed 文案。

## Allowed Dependencies

| From | May Depend On | Why |
|------|----------------|-----|
| Entity / Platform | Domain, Runtime public surface, Control contracts | 实体与平台只消费稳定投影与服务面 |
| Services / Control surfaces | Runtime public surface, Domain, Assurance hooks | 控制面与服务面要经正式公开边界协作 |
| Runtime | Domain, Protocol canonical public surface (`LiproProtocolFacade` + canonical contracts), Assurance hooks | 运行面编排只消费统一协议根与归一化 contracts；不得直接依赖 `core/protocol/boundary/*` decoder internals |
| Protocol | protocol-local collaborators, transport, auth, codecs | 协议边界内部闭环恢复与归一化 |
| Assurance | All planes (read/observe only) | 用于测试、审计、CI 守卫 |

## Forbidden Dependencies

| From | Must Not Depend On | Why |
|------|--------------------|-----|
| Entity / Platform | raw protocol internals, `core/protocol/boundary/*`, concrete MQTT transport, REST transport | 破坏边界与测试隔离 |
| Control plane | protocol internals, `core/protocol/boundary/*`, runtime internals bypassing public surface | 容易形成 backdoor 与 split-root 回流；`control/` 只能通过正式 runtime/public surfaces 协作，且不得依赖 child façade roots |
| Domain | HA lifecycle, auth/retry/network recovery | 会污染领域真源 |
| Protocol | coordinator, entity, platform, diagnostics UI semantics | 协议层不应感知宿主上层语义 |
| Compat shell | 反向定义正式 public surface | compat 只能跟随，不可主导 |

## Phase 40 Governance Truth Boundary

- `.planning/baseline/GOVERNANCE_REGISTRY.json` 只允许被 governance docs / contributor templates / meta guards pull 取；production code、runtime orchestration 与 service execution 不得把它当作运行时配置源。
- `custom_components/lipro/control/runtime_access.py` 继续是 control/runtime typed read-model 的唯一 helper home；diagnostics / service_router_support / maintenance 不得散落 `runtime_data`、ad hoc coordinator iteration 或 direct device mapping 读取。
- `custom_components/lipro/services/device_lookup.py` 只允许处理 service-facing target → device-id resolution；最终 `(device, coordinator)` bridge 必须由 `custom_components/lipro/control/service_router_support.py` 通过 `RuntimeAccess` 完成。
- `custom_components/lipro/services/maintenance.py` 只允许通过 `runtime_access.iter_runtime_entry_coordinators()` 实现 `refresh_devices`；device-registry listener / pending reload task ownership 必须固定在 `custom_components/lipro/runtime_infra.py`。
- `custom_components/lipro/services/execution.py` 是唯一 shared auth/error execution home；`custom_components/lipro/services/schedule.py` 只允许提供 schedule-specific 参数封装、日志与翻译 key，不得复制独立 coordinator auth chain 或 reauth story。

## Phase 43 Control / Service Boundary Clarifications

- Control → services 只允许 pull service-facing shaping helpers；services 不得通过 helper surface 反向定义 runtime truth、control ownership 或 lifecycle listener 归属。
- `custom_components/lipro/control/diagnostics_surface.py` 只能消费 typed runtime projection 与 entry-scoped runtime lookup；`custom_components/lipro/control/service_router_support.py` 只能组合 service target resolution + runtime_access bridge；`custom_components/lipro/runtime_infra.py` 负责 listener/reload lifecycle。
- `custom_components/lipro/services/device_lookup.py` 与 `custom_components/lipro/services/maintenance.py` 都不得重新长回最终 `(device, coordinator)` 裁决、listener/pending-task state 或 direct coordinator traversal story。

## Architecture Policy Mapping

| Rule ID | Enforces | Notes |
|--------|----------|-------|
| `ENF-IMP-ENTITY-PROTOCOL-INTERNALS` | Entity / Platform 不直连 `core.api`、`core.mqtt`、`core.protocol.boundary` internals | 结构性 import 规则 |
| `ENF-IMP-CONTROL-NO-BYPASS` | Control surface 不直连 protocol internals 或 runtime internals bypass | 阻断 backdoor / split-root 回流 |
| `ENF-IMP-BOUNDARY-LOCALITY` | `core/protocol/boundary/*` 仅限 protocol-plane internal collaborators 合法消费 | future assurance-only 例外必须先登记 |
| `ENF-IMP-NUCLEUS-NO-HOMEASSISTANT-IMPORT` | `core/auth` / `core/capability` / `core/device` nucleus homes 不吸入 `homeassistant` imports | host-neutral truth 不得宿主化 |
| `ENF-IMP-NUCLEUS-NO-PLATFORM-BACKFLOW` | nucleus homes 不反向依赖 `helpers/platform.py` | HA platform projection 必须停留在 adapter seam |
| `ENF-IMP-HEADLESS-PROOF-LOCALITY` | headless boot seam 不得吸入 `homeassistant` / control / runtime / platform projection imports | proof consumer 不得长成第二 root |
| `ENF-IMP-PLATFORM-SHELL-NO-CONTROL-LOCATOR` | platform setup shell 不得依赖 `control/runtime_access.py` | platform adapter 必须保持 headless setup shell 身份 |

## Guard Chain

| Rule | Initial Enforcement | Full Enforcement Target |
|------|---------------------|--------------------------|
| Entity 不直连 protocol internals / boundary decoders | `scripts/check_architecture_policy.py` + `tests/meta/test_dependency_guards.py` | local-fast + CI fail-fast |
| Control 只走 runtime public surface | `scripts/check_architecture_policy.py` + `tests/meta/test_dependency_guards.py` | local-fast + CI fail-fast |
| Host-neutral nucleus 不 import `homeassistant` | `scripts/check_architecture_policy.py` + `tests/meta/test_dependency_guards.py` | local-fast + CI fail-fast |
| Host-neutral nucleus 不依赖 adapter platform projection | `scripts/check_architecture_policy.py` + `tests/meta/test_dependency_guards.py` | local-fast + CI fail-fast |
| Protocol 不依赖 coordinator/entity | import scan + reviewer checklist | future protocol/root checks |
| Compat 不成为 public truth | `ARCHITECTURE_POLICY.md` + public-surface guards | residual kill gate |
| Runtime/control 不直连 child façade roots | protocol/root contract tests + integration proof | stronger dependency guards |

## Phase 07.3 Observer-Only Telemetry Surface

- `custom_components/lipro/core/telemetry/*` 只允许 pull `ProtocolTelemetrySource` / `RuntimeTelemetrySource` ports、pure models 与 sink projections；不得反向依赖 `control/*`、`Coordinator` internals 或 child façade internals。
- `custom_components/lipro/control/telemetry_surface.py` 是 control-plane 唯一 bridge：可以装配 `RuntimeTelemetryExporter`，但 diagnostics / system-health consumers 不得绕过它回退到 runtime private fields。
- exporter family 属于 `observer-only surface`：允许读取正式 runtime / protocol telemetry truth，不得获得编排权、服务注册权或第二套事件总线语义。

## Phase 10 Control / Core Boundary Clarifications

- `custom_components/lipro/control/runtime_access.py` 是 control plane 读取 runtime-home `Coordinator` 的唯一 helper；`entry.runtime_data.coordinator` 不得在 adapter / control surface 中散落读取。
- `custom_components/lipro/control/telemetry_surface.py` 必须通过 `runtime_access.get_entry_runtime_coordinator()` 定位 runtime root；telemetry bridge 不能重新承担 runtime-home 叙事。
- `custom_components/lipro/config_flow.py`、`custom_components/lipro/entry_auth.py` 允许依赖 `LiproAuthManager` / `AuthSessionSnapshot` 这类 host-neutral contract；不允许依赖 raw login/result payload 或 boundary decoder internals。

## Phase 25.2 Telemetry Formal-Surface Closure Clarifications

- `custom_components/lipro/control/telemetry_surface.py` 现在只允许 pull `Coordinator.protocol` 与 `telemetry_service` 这两个正式 observer surfaces；`coordinator.client` 不再是 allowed dependency / bridge input。
- `runtime_types.LiproCoordinator` 已显式承认 telemetry bridge 真实需要的 `protocol` / `telemetry_service` surfaces；任何 consumer 若继续依赖 `Coordinator.client`、`entry.runtime_data` 或 coordinator private fields，应视为 regression。
- `.planning/codebase/STRUCTURE.md` 等 codebase maps 继续只是 derived collaboration views；它们可以记录 telemetry bridge wiring，但不能重新定义 authority/dependency truth。

## Phase 48 Formal-Root Decomposition Clarifications

- `custom_components/lipro/control/runtime_access_support.py` 只是 `runtime_access.py` 的 support-only helper cluster；control / diagnostics / system-health / telemetry consumers 仍必须经 `runtime_access.py` 读取正式 runtime truth。
- `custom_components/lipro/control/telemetry_surface.py` 只能通过 `runtime_access.build_entry_telemetry_exporter()` 取得 exporter；它不得重新导入 private support helper、直接 coordinator lookup 或 `entry.runtime_data`。
- `custom_components/lipro/core/coordinator/lifecycle.py` 可以承接 `CoordinatorUpdateCycle` 这类 internal collaborator，但 `Coordinator` 仍是唯一 runtime orchestration root；lifecycle helper 不得变成第二入口或 package export。
- `custom_components/lipro/__init__.py` 继续只保留 lazy alias seam 与 `_build_entry_lifecycle_controller()` 组装入口；`EntryLifecycleController` 仍是 setup / unload / reload 的唯一 control-plane owner。

## Phase 27 Protocol-Service Convergence Clarifications

- `custom_components/lipro/services/schedule.py`、`custom_components/lipro/services/diagnostics/*` 与 `custom_components/lipro/entities/firmware_update.py` 现在只允许 pull `runtime_types.LiproCoordinator.protocol_service` 这一个 runtime-owned protocol capability port；不得继续依赖 coordinator 顶层 schedule / diagnostics / OTA passthrough operations。
- `custom_components/lipro/core/coordinator/services/protocol_service.py` 是 runtime 与 protocol root 之间的唯一 formal capability bridge；它可以依赖 `LiproProtocolFacade`，但 control/entity/platform 不得反向绕过它摸 runtime internals。
- outlet-power polling 允许在 coordinator 内部通过 `self.protocol_service.async_fetch_outlet_power_info` 完成 runtime wiring；这属于 runtime 内部实现，不构成新的 external public surface。

## Phase 18 Host-Neutral Nucleus / Adapter Projection Clarifications

- `custom_components/lipro/core/auth/bootstrap.py`、`custom_components/lipro/core/capability/*` 与 `custom_components/lipro/core/device/*` 共同构成 host-neutral nucleus helper/contract family；这些 homes 可以被 HA adapter 消费，但不得直接 import `homeassistant`。
- `custom_components/lipro/helpers/platform.py` 是 adapter-only HA platform projection home；entities / platform setup 可以消费它，但 nucleus homes 不得反向依赖它来定义 category/capability/device truth。
- `custom_components/lipro/config_flow.py`、`custom_components/lipro/entry_auth.py` 与 `custom_components/lipro/flow/login.py` 只承担 HA adapter / projection 角色：`AuthSessionSnapshot` 继续是 formal auth truth，`ConfigEntryLoginProjection` 只是 config-entry payload projection。

## Phase 35 Protocol Hotspot Clarifications

- `custom_components/lipro/core/api/client.py` 只保留 `LiproRestFacade` stable import home；`custom_components/lipro/core/api/rest_facade.py` 允许 inward 依赖 `request_gateway.py`、`transport_executor.py` 与 `endpoint_surface.py`，但 runtime/control/tests 不得把这些 collaborators 当作对外 contract。
- `custom_components/lipro/core/protocol/facade.py` 允许 inward 依赖 `rest_port.py` 与 `mqtt_facade.py`；`_RestFacadePort` 只是 typed child-façade port，`LiproMqttFacade` 只是 protocol root 下的 MQTT child façade，control/runtime 不得绕过 `LiproProtocolFacade` 直摸这些 internals。
- protocol hotspot slimming 允许 root/body 继续变薄，但不允许把 endpoint-operation glue 迁移成新的 external package export 或 dependency shortcut。

## Phase 36 Runtime Root / Exception Clarifications

- `custom_components/lipro/core/coordinator/coordinator.py` 允许 inward 依赖 `services/polling_service.py`；`CoordinatorPollingService` 只属于 runtime internal helper home，不得被 control/entity/platform 当作 bypass seam。
- `services/polling_service.py` 可以依赖 `CoordinatorProtocolService`、`CoordinatorMqttService`、runtime state/status/tuning homes；这些依赖只在 runtime plane 内合法，不代表 external public dependency growth。
- typed arbitration 只允许沿 runtime 主链 inward 收口；control/service/docs/test 不得通过新增 broad catch 或 raw internal exception type 建立第二套 failure story。

## Phase 37 Test Topology / Derived-Truth Clarifications

- `tests/core/test_init_service_handlers*.py`、`tests/core/test_init_runtime*.py` 与 `tests/meta/test_governance_phase_history*.py` 的 split 只改变 assurance topology，不改变 production dependency direction。
- `.planning/codebase/*` 可以记录这些 topic suites 的新布局，但它们仍不得反向定义 dependency / authority truth；真正的依赖仲裁继续以 baseline + guards 为准。
- governance/toolchain tests 允许依赖 split topical suites 与 generated file-matrix truth；production planes 不得反向依赖测试拓扑或派生映射。

## Phase 52 Request-Policy / Protocol-Root Clarifications

- `custom_components/lipro/core/protocol/facade.py` 可以 inward 依赖 `protocol_facade_rest_methods.py`、`rest_port.py` 与 `mqtt_facade.py`；它们分别只承担 support-only bound methods、typed REST child ports 与 MQTT child façade home，不得被 runtime/control/tests 讲成 alternative root。
- `custom_components/lipro/core/api/rest_facade.py` 与 `rest_facade_request_methods.py` 允许 inward 依赖 `request_gateway.py`、`transport_executor.py` 与 `request_policy.py`；其中 `RequestPolicy` 持有 `429` / busy / pacing truth，`RestRequestGateway` 持有 mapping/auth-aware retry-context orchestration，`RestTransportExecutor` 只保留 signed transport execution / response normalization，不得反向长回 second request owner。
- `custom_components/lipro/core/api/transport_retry.py` 只允许通过 injected `handle_rate_limit` 回调向 `RequestPolicy` 请求决策；`compute_exponential_retry_wait_time()` 若仍被 strict request-policy family 之外的 protocol/runtime/MQTT helpers 共享，必须继续在 residual ledger 中显式登记，直到迁入更诚实的 shared backoff home。

## Review Checklist

- [ ] 新增依赖是否符合 allowed matrix
- [ ] 是否引入了新的跨平面 shortcut
- [ ] 是否把 compat 层误提升为正式 public surface
- [ ] 是否需要同步更新 `PUBLIC_SURFACES.md`、`ARCHITECTURE_POLICY.md` 与 `VERIFICATION_MATRIX.md`

---
*Used by: Phase 1.5 seed guards, Phase 7.2 architecture policy, and CI-level dependency enforcement*

- `custom_components/lipro/headless/boot.py` 是 local proof seam：它只能依赖 host-neutral auth/protocol truth，不能导入 `homeassistant`、`Coordinator`、`custom_components/lipro/control/*` 或 `helpers/platform.py`。
- platform `async_setup_entry()` 壳只允许通过 `helpers/platform.add_entry_entities()` 把 `entry.runtime_data` 投影为实体列表；它们不得导入 `custom_components/lipro/control/runtime_access.py` 或其他 control locator。



## Phase 53 Runtime / Entry-Root Clarifications

- `custom_components/lipro/core/coordinator/runtime_wiring.py` 可以依赖 runtime services / lifecycle collaborators 以承接 bootstrapping mechanics，但它不能成为第二 runtime root、package export 或 control-facing capability surface。
- `custom_components/lipro/control/entry_lifecycle_support.py` 只能被 `EntryLifecycleController` inward 使用；`runtime_infra.py` 继续只承载 shared infra/listener truth，不能反向接管 lifecycle ownership。
- `custom_components/lipro/control/entry_root_wiring.py` 只能被 `custom_components/lipro/__init__.py` 作为 lazy wiring helper 使用；HA root adapter 继续保持 lazy alias seam，不得回退到 eager binding / singleton controller story。

## Phase 54 Helper-Hotspot Clarifications

- `custom_components/lipro/core/anonymous_share/registry.py`、diagnostics services 与 share-service flows 只允许经 `manager.py` / `share_client.py` / `helpers.py` 读取正式 story；`manager_support.py`、`share_client_support.py` 与 `helper_support.py` 只能被对应 formal homes inward 依赖。
- `custom_components/lipro/core/api/request_policy.py` 可以 inward 依赖 `request_policy_support.py` 承接 pacing/backoff mechanics；`transport_retry.py`、`core/command/result_policy.py`、`core/coordinator/runtime/command/retry.py` 与 `core/mqtt/setup_backoff.py` 若仍复用 `compute_exponential_retry_wait_time()`，只能继续经 `request_policy.py` 这一 compat surface 读取，不得直连 `request_policy_support.py`。
- `custom_components/lipro/control/service_router.py` 的 diagnostics callback truth 不变；helpers/support splitting 不得让 services / tests / docs 绕过 router 讲出第二 public callback story。


## Phase 56 Neutral Backoff Clarifications

- `custom_components/lipro/core/utils/backoff.py` 是 neutral shared exponential-backoff primitive home；它只承接 pure delay math，不承担 plane-local retry policy。
- `custom_components/lipro/core/api/request_policy.py` 已停止导出 `compute_exponential_retry_wait_time()`；API plane 只保留 `429` / busy / pacing decision truth。
- `custom_components/lipro/core/command/result_policy.py`、`custom_components/lipro/core/coordinator/runtime/command/retry.py` 与 `custom_components/lipro/core/mqtt/setup_backoff.py` 现统一从 `core/utils/backoff.py` import primitive，同时继续保留各自的 local retry semantics。

## Phase 57 Typed Command-Result Contract Clarifications

- `custom_components/lipro/core/command/result_policy.py` 与 `custom_components/lipro/core/command/result.py` 共同组成 command-result formal contract family：前者负责 classification / polling / typed state truth，后者负责 failure arbitration / stable export truth。
- `custom_components/lipro/core/coordinator/runtime/command/sender.py` 只能经 `custom_components/lipro/core/command/result.py` 读取 shared typed command-result contract，不得维护本地 duplicated literals。
- `custom_components/lipro/services/diagnostics/types.py` 与 diagnostics handlers 只允许复用 shared command-result state contract；diagnostics `query_command_result` response 不得继续把 `state` 讲成 bare `str` folklore。

## Phase 58 Repository Audit Refresh Clarifications

- `Phase 58` 不引入新的 dependency-direction rule；它确认当前 `protocol -> runtime -> control/adapter` 主线仍成立。
- next-wave route 优先处理的是 guard/test localization 与 tooling maintainability，而不是用 dependency-law 名义重做已关闭主线。

## Phase 62 Naming / Discoverability Clarifications

- `custom_components/lipro/core/device/extras_payloads.py` 与 `extras_features.py` 允许 inward 依赖 `extras_support.py` 承接 payload / panel parsing helpers；其他 domain/runtime/platform consumers 不得把它当作对外 contract。
- `custom_components/lipro/core/api/endpoint_surface.py` 继续允许被 `rest_facade.py` inward 依赖承接 endpoint operations collaborator mechanics；runtime/control/tests/docs 不得把它讲成 public route 或第二 façade。
- diagnostics services / tests / docs 继续只能经 `helpers.py` 与 router/public callback story 读取正式 diagnostics import truth；`feedback_handlers.py`、`command_result_handlers.py`、`capability_handlers.py` 与 `helper_support.py` 只允许由 diagnostics formal homes inward 依赖。
- `manager_submission.py`、`share_client_flows.py`、`candidate_support.py` 与 `select_internal/gear.py` 的 inward-only posture 在 Phase 62 继续保持；命名 / discoverability 收口不得把它们提升成第二 formal root。
