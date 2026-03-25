# Lipro Home Assistant Integration - Developer Architecture

> **Last aligned through**: `Phase 43` (`2026-03-20`)
> **Role**: 描述当前正式实现拓扑、目录归属与开发者入口。
>
> 本文档是 **current-topology guide**，不是 phase 日志、评分快照或覆盖率公告板。  
> 北极星终态裁决请见 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`。  
> 当前治理真源请以 `.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 为准。  
> `.planning/codebase/*.md` 属于 `derived collaboration maps / 协作图谱 / 派生视图`，帮助协作与定位，但不构成新的 authority chain。

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
| Control service adapters | `custom_components/lipro/services/` | service declarations、request shaping、thin service helpers |
| Platform adapters | `custom_components/lipro/*.py` platform files | entity projection / HA platform binding |
| Assurance | `tests/`, `scripts/`, `.planning/baseline/`, `.planning/reviews/` | tests / guards / governance truth |

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
│   └── anonymous_share/       # protocol-adjacent anonymous-share support
├── control/                   # formal control-plane home
├── services/                  # control-plane service declarations / adapters / handler helpers
├── entities/                  # domain -> HA entity adapters
├── helpers/                   # platform projection builders / rules
├── diagnostics.py             # thin adapter -> control.diagnostics_surface
├── system_health.py           # thin adapter -> control.system_health_surface
├── config_flow.py             # control-plane flow adapter
└── runtime_*.py               # typed HA runtime glue
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

1. HA service declaration 由 `custom_components/lipro/control/service_registry.py` 作为正式 owner 注册；`custom_components/lipro/services/registrations.py` 仅保留 compat import shell
2. `control/service_router.py` 接管 public callback
3. `control/service_router_handlers.py` / support helpers 组合 request shaping、runtime lookup、error translation
4. runtime formal surface 完成实际行为

## 为什么 `control/` 与 `services/` 同时存在

- `control/` 负责 **formal ownership**：callback home、runtime access、diagnostics/system-health surfaces、lifecycle orchestration。
- `services/` 负责 **service adapter helpers**：schema/contract constants、request shaping、diagnostics/share/schedule helper implementations；service registration formal owner 已收口到 `control/service_registry.py`。
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

## 常用命令

- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run python scripts/check_translations.py`
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
