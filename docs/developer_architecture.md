# Lipro Home Assistant Integration - Developer Architecture

> **Last aligned through**: `v1.43 archived / evidence-ready` (`2026-04-04`)
> **Current route alignment**: `no active milestone route / latest archived baseline = v1.43` (`2026-04-04`, archived / evidence-ready (2026-04-04))
> **Default next command**: `$gsd-new-milestone`
> **Latest archived evidence path**: `.planning/reviews/V1_43_EVIDENCE_INDEX.md`
> **Latest archived audit path**: `.planning/v1.43-MILESTONE-AUDIT.md`
> **Role**: 描述当前正式实现拓扑、目录归属与开发者入口。
>
> 本文档是 **current-topology guide**，不是 phase 日志、评分快照或覆盖率公告板。  
> 北极星终态裁决请见 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`。  
> 当前治理真源请以 `.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 为准。  
> `.planning/codebase/*.md` 属于 `derived collaboration maps / 协作图谱 / 派生视图`，帮助协作与定位，但不构成新的 authority chain。

## 阅读顺序

- 先看下方的“快速导航”“五大平面”“当前正式主链”，这是 current-topology first hop。
- historical freeze / typed-boundary / sanitizer / assurance notes 已下沉到 `docs/architecture_archive.md`，作为 pull-only appendix 供回溯，不再占据当前开发入口主线。
- predecessor archive selector notes 已全部下沉到 `docs/architecture_archive.md`；当前 first hop 不再混入 retired route tokens。

## Current Route Compression

- `v1.43` 已从 closeout-ready route 冻结为 latest archived baseline：当前 developer first hop 只保留已交付的 REST/protocol second-pass slimming、release/governance freshness、control/runtime narrowing 与 device aggregate hardening 结果，不再假装仍有 active milestone 正在执行。
- `custom_components/lipro/core/api/rest_facade.py` 与 `custom_components/lipro/core/protocol/rest_port.py` 继续保持 canonical formal-home 身份；`rest_facade_internal_methods.py` 与 `rest_port_bindings.py` 只承担 inward support / binding mechanics，不是第二 root。
- `Phase 141` 的 service-router public shell、entry-root explicit factory wiring、runtime local projection 与 `device_runtime.py` side-car bookkeeping 已共同冻结为 archived evidence；nested worktree 下 `gsd-tools` root detection 不是 live truth authority。
- 如需继续演进，请先读取 `.planning/reviews/V1_43_EVIDENCE_INDEX.md`、`.planning/v1.43-MILESTONE-AUDIT.md` 与 `.planning/PROJECT.md`，再显式开启新 milestone；不要回流为第二条 active / planning-only 叙事。

## 快速导航

| Area | Path | Role |
|---|---|---|
| HA integration entry | `custom_components/lipro/__init__.py` | thin adapter，装配 control-plane 与 runtime root |
| Protocol root | `custom_components/lipro/core/protocol/facade.py` | `LiproProtocolFacade`，唯一正式 protocol-plane root |
| REST child façade | `custom_components/lipro/core/api/rest_facade.py` | `LiproRestFacade` 显式组合根 |
| REST stable import home | `custom_components/lipro/core/api/client.py` | `LiproRestFacade` 稳定导入入口 |
| MQTT transport façade | `custom_components/lipro/core/protocol/mqtt_facade.py` | protocol-plane MQTT child façade |
| Runtime root | `custom_components/lipro/core/coordinator/coordinator.py` | `Coordinator`，唯一正式 runtime orchestration root |
| Runtime collaborators | `custom_components/lipro/core/coordinator/runtime/` | device/status/mqtt/command/tuning runtimes |
| Runtime service layer | `custom_components/lipro/core/coordinator/services/` | runtime-facing public collaborators |
| Domain truth | `custom_components/lipro/core/device/`, `custom_components/lipro/core/capability/` | device aggregate 与 capability truth |
| Control formal home | `custom_components/lipro/control/` | lifecycle / service router / runtime access / diagnostics / system health |
| Shared runtime infra | `custom_components/lipro/runtime_infra.py` | device-registry listener / pending reload / shared runtime bootstrap ownership |
| Root runtime contracts | `custom_components/lipro/runtime_types.py`, `custom_components/lipro/service_types.py` | typed runtime coordinator / service contract home |
| Auth/bootstrap root helper | `custom_components/lipro/entry_auth.py` | config-entry auth seed / token persistence / setup-exception home |
| Control service adapters | `custom_components/lipro/services/` | service declarations、request shaping、thin service helpers |
| Platform adapters | `custom_components/lipro/*.py` platform files | entity projection / HA platform binding |
| Assurance | `tests/`, `scripts/`, `.planning/baseline/`, `.planning/reviews/` | tests / guards / governance truth |

## Sanctioned Root-level Homes

- `custom_components/lipro/runtime_infra.py`：shared runtime infra / device-registry listener / pending reload ownership 的 sanctioned root-level home。
- `custom_components/lipro/runtime_types.py` + `custom_components/lipro/service_types.py`：typed runtime coordinator / service contract 的 sanctioned root-level homes；它们是 formal contract entry，不是 accidental helper。
- `custom_components/lipro/entry_auth.py`：config-entry auth/bootstrap seed、token persistence、setup-exception mapping 的 sanctioned root-level home。

## Phase 127 Execution Notes

- `custom_components/lipro/control/runtime_access.py` 已直接消费 typed `SystemHealthTelemetryView`；control-plane runtime snapshot 不再先 materialize stringly dict surrogate。
- `custom_components/lipro/control/runtime_access_support_views.py` 已切回显式 member/helper narrowing；slot-backed ports 继续支持，但 `type(...).__getattribute__` 不再是正式主链。
- `v1.36` 已完成 milestone closeout 并前推为 latest archived baseline：runtime-access hotspot、readiness honesty、benchmark/coverage gates 与 continuity governance contract 现只作为 pull-only archived evidence 提供后续路线引用。

## Phase 126 Execution Notes

- `custom_components/lipro/services/diagnostics/handlers.py` 现在直接消费 `helper_support.py` 的 pure mechanics helper；`helpers.py` 继续保留 stable outward helper home，但不再承担未使用 duplicate capability collector。
- `custom_components/lipro/control/developer_router_support.py` 的 non-entry-specific developer report branch 已复用 `build_developer_runtime_coordinator_iterator()`，保持 runtime iterator freezing 的单一 control-local story。
- `Phase 126` 现只保留 predecessor-visible diagnostics helper shell thinning proof，不再作为 current runtime hotspot owner。

## Phase 125 Execution Notes

- `custom_components/lipro/runtime_types.py` + `custom_components/lipro/service_types.py` 继续保持 sanctioned root-level contract homes；`ScheduleMeshDeviceLike`、`CommandProperties`、`DeviceRefreshServiceLike` 与 service-facing failure/property shapes 已回收到同一正式真源，不再在下游 runtime/service 文件里重复定义。
- `custom_components/lipro/config_flow.py` 继续只保留 Home Assistant entry-point glue；`custom_components/lipro/flow/step_handlers.py` 现在直接消费 `_show_*` / `_get_*` / `_async_*` private helper seam，不再借由 public pass-through wrapper 中转。
- `custom_components/lipro/entry_auth.py` 继续承担 persisted auth-seed / token persistence / setup-exception formal home；单次中转 helper 已被压平，没有重新长出第二套 bootstrap story。
- 当前治理 current-route truth 已 canonicalize 到 `.planning/baseline/GOVERNANCE_REGISTRY.json` 的 `planning_route`；`PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 只保留 projection / consistency target 身份。

## 五大平面

| Plane | Formal home | Core truth |
|---|---|---|
| Protocol | `custom_components/lipro/core/protocol/`, `custom_components/lipro/core/api/`, `custom_components/lipro/core/mqtt/` | canonical contracts、auth recovery、transport policy、boundary normalization |
| Runtime | `custom_components/lipro/core/coordinator/` | polling、command confirmation、snapshot refresh、MQTT lifecycle |
| Domain | `custom_components/lipro/core/device/`, `custom_components/lipro/core/capability/`, `custom_components/lipro/core/command/` | device identity、capability truth、write-side intent |
| Control | `custom_components/lipro/control/`, `custom_components/lipro/services/`, root thin adapters | entry lifecycle、service callbacks、support/diagnostics surfaces |
| Assurance | `tests/`, `scripts/`, `.planning/` | architecture policy、traceability、observability、replay/fixture truth |

## 当前正式主链

### Protocol plane

- `LiproProtocolFacade` 是唯一正式 protocol-plane root。
- `LiproRestFacade` 与 `LiproMqttFacade` 是 child façades；它们协作，但不构成第二 root。
- canonical contract 必须在 protocol boundary 完成；runtime / domain / entities 不消费 raw vendor payload。
- `MqttTransport` 是 localized concrete transport，不是 public protocol root。

### Runtime plane

- `Coordinator` 是唯一正式 runtime root。
- `RuntimeOrchestrator` + `RuntimeContext` + runtime service layer 负责把 runtime collaborators 组合成一条正式执行路径。
- 命令、轮询、MQTT 消息应用、snapshot refresh 都只允许走显式 runtime service / runtime collaborator path。

### Domain plane

- `LiproDevice` 是 device aggregate façade；能力真源固定在 `CapabilityRegistry` / `CapabilitySnapshot`。
- 平台文件只做 projection，不二次定义 capability truth。
- Domain 不承担 protocol recovery / Home Assistant lifecycle 语义。

### Control plane

- `custom_components/lipro/control/` 是 formal home。
- `ServiceRouter` 是 service callback home；`RuntimeAccess` 是 control → runtime 的 typed read-model 与 runtime locator。
- `DiagnosticsSurface` / `SystemHealthSurface` / `EntryLifecycleController` 是 formal control collaborators。
- `custom_components/lipro/runtime_infra.py` 是 device-registry listener、pending reload coordination 与 runtime listener ownership 的正式 home。
- `custom_components/lipro/runtime_types.py` + `custom_components/lipro/service_types.py` 共同承接 root-level typed runtime/service contract truth；runtime root 不再反向依赖 `services/contracts.py` 的 service schema home。
- `custom_components/lipro/entry_auth.py` 是 config-entry auth/bootstrap 的正式 home；它复用 shared bootstrap / auth contract，而不是第二 control root。
- 根层 `__init__.py`、`diagnostics.py`、`system_health.py`、`config_flow.py` 继续保持 thin adapter 身份。
- `custom_components/lipro/services/` 不再承载“legacy carrier”身份；它的正式角色是：
  - HA service declaration / registration
  - request shaping / device-id resolution / error translation helpers
  - diagnostics/share/schedule/maintenance thin adapters
- `services/device_lookup.py` 只负责 service-facing target → `device_id` 解析；最终 `(device, coordinator)` 裁决只允许停留在 `control/service_router_support.py`。
- `services/maintenance.py` 只负责 `refresh_devices` service adapter；device-registry listener 不得回流到 services。

### Assurance plane

- `tests/meta/`、`scripts/check_*.py`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 共同守护结构、真相与 traceability。
- replay / fixture / contract / governance tests 先守边界与 authority，再守行为。

## 依赖规则

### 允许的方向

- Platform / entity → domain truth + control/runtime public surface
- Control → runtime public surface + assurance helpers
- Runtime → domain + protocol contracts + assurance hooks
- Protocol → external IO + canonical contracts + telemetry
- Assurance → 可以观测所有层，但不回写业务控制流

### 禁止的方向

- Entity / platform 直连 protocol internals、MQTT concrete transport、runtime private state
- Protocol 感知 coordinator / HA runtime semantics
- control / platform / entity 把 `services/` 或 helper 层重新讲成第二主链
- compat / legacy naming 反向定义 current public truth

## 目录与归属

```text
custom_components/lipro/
├── core/
│   ├── protocol/              # formal protocol root + canonical contracts + diagnostics context
│   ├── api/                   # REST child façade collaborators / request policy / endpoint surface
│   ├── mqtt/                  # concrete MQTT transport / payload/topic helpers
│   ├── coordinator/           # runtime root + runtimes + runtime services
│   ├── device/                # device aggregate / normalization helpers
│   ├── capability/            # capability truth
│   ├── command/               # write-side helpers
│   └── anonymous_share/       # anonymous-share formal home + inward collaborators
├── control/                   # formal control-plane home
├── services/                  # control-plane service declarations / adapters / handler helpers
├── entities/                  # domain -> HA entity adapters
├── helpers/                   # platform projection builders / rules
├── diagnostics.py             # thin adapter -> control.diagnostics_surface
├── system_health.py           # thin adapter -> control.system_health_surface
├── config_flow.py             # control-plane flow thin adapter
├── runtime_infra.py           # sanctioned root-level runtime infra / listener ownership home
├── runtime_types.py           # sanctioned root-level typed runtime contract home
├── service_types.py           # shared service-facing command/failure typed contract home
└── entry_auth.py              # sanctioned root-level config-entry auth/bootstrap home
```

## 关键数据流

### 1. 状态更新

1. Protocol plane 获取 canonical payload / MQTT message
2. Runtime collaborators 归并、过滤、确认 pending command expectations
3. `StateRuntime` 更新 device aggregate
4. `Coordinator` 发布更新给 entities / platforms

### 2. 命令执行

1. User / service callback 进入 entity 或 control callback
2. Runtime service / command runtime 发送正式命令
3. protocol plane 执行 request / retry / auth recovery / pacing
4. runtime 记录 confirmation / refresh strategy / telemetry

### 3. 控制面调用

1. HA service declaration 由 `custom_components/lipro/control/service_registry.py` 作为唯一正式 owner 注册；HA 根适配器只能通过该模块装配服务注册，已不存在额外的 `services/registrations.py` compat import shell
2. `control/service_router.py` 接管 public callback
3. `control/service_router_handlers.py` 作为非 diagnostics callback family home 组合 request shaping、runtime lookup、error translation；developer / diagnostics callbacks 继续留在 `control/service_router_diagnostics_handlers.py`
4. runtime formal surface 完成实际行为

## 为什么 `control/` 与 `services/` 同时存在

- `control/` 负责 **formal ownership**：callback home、runtime access、diagnostics/system-health surfaces、lifecycle orchestration。
- `services/` 负责 **service adapter helpers**：schema/contract constants、request shaping、diagnostics/share/schedule helper implementations；service registration formal owner 已收口到 `control/service_registry.py`，`__init__.py` 也不再直连 `services/registry.py`。
- 两者不是“双主链”，而是 **formal home + helper surface** 的关系；任何文档或测试不得再把 `services/` 讲成 legacy carrier 或第二 control root。

## 演进约束

- 不重开 `LiproClient`、`LiproMqttClient`、`raw_client`、`get_device_list` compat seam。
- 不新增第二 runtime root、全局事件总线、通用 DI 容器。
- 不让 replay / docs / planning prose 比实际 guards 更“有权威”。
- 不把 empty shell / stale alias 留在正式目录中“等待以后再说”。

## 最小验证矩阵

| Touched area | Minimum verification |
|---|---|
| `core/protocol/**`, `core/api/**`, replay/fixture changes | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/meta/test_protocol_replay_assets.py tests/core/api/test_protocol_replay_rest.py tests/integration/test_protocol_replay_harness.py` |
| `core/coordinator/**`, runtime service changes | `uv run pytest -q tests/core/coordinator/test_runtime_root.py tests/integration/test_mqtt_coordinator_integration.py` |
| `control/**`, `services/**`, governance truth | `uv run pytest -q tests/meta/test_governance*.py tests/services` |
| `config_flow.py`, flow schemas, runtime glue | `uv run pytest -q tests/flows tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_setup_entry_failures.py` |
| massive test topicization only | run the touched topical suites + `uv run pytest -q tests/core tests/flows tests/meta` |
| docs / governance only | `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py` |

## Phase 93 Assurance Freeze Notes

- `FILE_MATRIX.md`、`TESTING.md`、`VERIFICATION_MATRIX.md` 与 route smoke tests 共同构成 assurance freeze proof；任何派生投影滞后都属于 current-route regression，而不是可忽略的文档噪音。
- `tests/meta/test_phase31_runtime_budget_guards.py` 继续是 repo-wide typing-budget freeze home；quality-freeze closeout does not introduce a second public root。

## 常用命令

- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run python scripts/check_translations.py`
- `uv run python scripts/check_markdown_links.py`
- `uv run pytest -q tests/ --ignore=tests/benchmarks`

## 协作图谱身份

- `.planning/codebase/*.md` 是 `derived collaboration maps / 协作图谱 / 派生视图`。
- 它们用于解释代码地图与协作入口，不直接决定结构仲裁。
- 发生冲突时，服从 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` → `.planning/ROADMAP.md` → `.planning/REQUIREMENTS.md` → `.planning/STATE.md` → baseline/reviews 的顺序。

## 参考文档

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/ARCHITECTURE_POLICY.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

## Historical Architecture Archive

- 历史 phase notes / appendix 已移至 `docs/architecture_archive.md`。
- `docs/developer_architecture.md` 只保留 current developer guidance；archive appendix 不再承担 current-route selector 身份。
