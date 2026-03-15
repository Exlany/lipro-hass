# ARCHITECTURE
> Snapshot: `2026-03-15`
> Repository: `/var/tmp/coolvibe/worktrees/edf26778937a-/lipro-hass`
> Focus: `arch`
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、协作与局部审阅。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本图谱必须同步回写或标记为过时。

## 1. Arbitration Sources
本图谱以以下真源为裁决顺序基础，并已交叉核对实现与测试：
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/STATE.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/baseline/TARGET_TOPOLOGY.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `docs/developer_architecture.md`
- `custom_components/lipro/**`
- `tests/**`

## 2. Formal Production Mainline
正式主链已经收敛为单条 Home Assistant → control → runtime → protocol → vendor 的链路：

```text
Home Assistant entry / flow / service / entity
  -> custom_components/lipro/__init__.py
  -> custom_components/lipro/control/entry_lifecycle_controller.py
  -> custom_components/lipro/control/service_registry.py
  -> custom_components/lipro/coordinator_entry.py
  -> custom_components/lipro/core/coordinator/coordinator.py
  -> custom_components/lipro/core/coordinator/orchestrator.py
  -> custom_components/lipro/core/coordinator/services/*.py
  -> custom_components/lipro/core/protocol/facade.py
      -> custom_components/lipro/core/api/client.py
      -> custom_components/lipro/core/mqtt/mqtt_client.py
  -> custom_components/lipro/core/protocol/contracts.py
  -> custom_components/lipro/core/protocol/boundary/*.py
  -> vendor REST / IoT / MQTT
```

主链上的正式 owner：
- Control root：`custom_components/lipro/control/entry_lifecycle_controller.py`、`custom_components/lipro/control/service_registry.py`
- Runtime root：`custom_components/lipro/coordinator_entry.py`、`custom_components/lipro/core/coordinator/coordinator.py`
- Runtime wiring：`custom_components/lipro/core/coordinator/orchestrator.py`、`custom_components/lipro/core/coordinator/runtime_context.py`、`custom_components/lipro/core/coordinator/factory.py`
- Protocol root：`custom_components/lipro/core/protocol/facade.py`
- Canonical contract / boundary：`custom_components/lipro/core/protocol/contracts.py`、`custom_components/lipro/core/protocol/boundary/rest_decoder.py`、`custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`
- Domain truth：`custom_components/lipro/core/capability/registry.py`、`custom_components/lipro/core/device/device.py`、`custom_components/lipro/core/device/state.py`
- Assurance truth：`custom_components/lipro/core/telemetry/exporter.py`、`tests/meta/*.py`、`tests/harness/**`

## 3. Five-Plane Mapping
| Plane | 正式根 / 正式集合 | 目录归属 | 当前判断 |
|---|---|---|---|
| Control | `EntryLifecycleController`、`ServiceRegistry`、control surfaces | `custom_components/lipro/control/`、`custom_components/lipro/__init__.py`、`custom_components/lipro/config_flow.py`、`custom_components/lipro/diagnostics.py`、`custom_components/lipro/system_health.py` | 已形成单一控制面 home；HA 根模块基本保持 thin adapter |
| Runtime | `Coordinator`、`RuntimeOrchestrator`、`RuntimeContext`、runtime services | `custom_components/lipro/coordinator_entry.py`、`custom_components/lipro/core/coordinator/` | 唯一正式编排根明确；`CoordinatorProtocolService` 已收口 protocol-facing ops |
| Protocol | `LiproProtocolFacade`、`LiproRestFacade`、`LiproMqttFacade`、canonical contracts | `custom_components/lipro/core/protocol/`、`custom_components/lipro/core/api/`、`custom_components/lipro/core/mqtt/` | 正式根固定；`core/api/` 与 `core/mqtt/` 是 child façade / transport slice，不再是第二 root |
| Domain | `CapabilityRegistry`、`CapabilitySnapshot`、`LiproDevice` explicit surface、entity/platform projections | `custom_components/lipro/core/capability/`、`custom_components/lipro/core/device/`、`custom_components/lipro/entities/`、platform 根文件 | 动态委托已清退；领域真源与平台投影基本分离 |
| Assurance | telemetry exporter、boundary fixtures、replay、meta guards、ledgers | `custom_components/lipro/core/telemetry/`、`tests/`、`.planning/`、`docs/` | 观测/回放/治理已成正式保障面，且被明确限制为 pull-only / observer-only |

## 4. Entry Points And Wiring
### 4.1 Home Assistant root adapters
- `custom_components/lipro/__init__.py` 只暴露 `async_setup()`、`async_setup_entry()`、`async_unload_entry()`、`async_reload_entry()`，并在调用时构造 `EntryLifecycleController` 与 `ServiceRegistry`。
- `custom_components/lipro/coordinator_entry.py` 只导出 `Coordinator`；`tests/meta/test_public_surface_guards.py` 与 `tests/meta/test_modularization_surfaces.py` 明确禁止从 `custom_components/lipro/core/__init__.py` 回流 runtime root。
- `custom_components/lipro/diagnostics.py` 与 `custom_components/lipro/system_health.py` 是 control surface 的 thin adapter；`tests/core/test_diagnostics.py`、`tests/core/test_system_health.py` 验证它们保持 adapter 身份。
- `custom_components/lipro/config_flow.py`、`custom_components/lipro/entry_auth.py`、`custom_components/lipro/flow/*.py` 组成接入入口，直接使用 `LiproProtocolFacade` 与 `LiproAuthManager`，不再回流 legacy client 名称。

### 4.2 Platform entrypoints
- `custom_components/lipro/light.py`、`switch.py`、`sensor.py`、`binary_sensor.py`、`fan.py`、`climate.py`、`cover.py`、`select.py`、`update.py` 都只暴露 `async_setup_entry()` 并通过 `custom_components/lipro/helpers/platform.py` / `custom_components/lipro/entities/base.py` 构造实体。
- `.planning/baseline/ARCHITECTURE_POLICY.md` 与 `tests/meta/test_dependency_guards.py` 禁止这些平台模块直接依赖 `custom_components.lipro.core.api`、`custom_components.lipro.core.mqtt` 或 `custom_components.lipro.core.protocol.boundary`。

### 4.3 Service entrypoints
- `custom_components/lipro/services/registrations.py` 只维护 HA service 声明表，handler 全部落在 `custom_components/lipro/control/service_router.py`。
- `custom_components/lipro/control/developer_router_support.py` 已承接 developer-report、optional capability、sensor-history 等私有 glue；`tests/services/test_services_registry.py` 确认 registration handler 模块归属仍是 `service_router.py`。

## 5. Data Flow
### 5.1 Setup / unload flow
1. `custom_components/lipro/__init__.py` 创建 `EntryLifecycleController`。
2. `custom_components/lipro/control/entry_lifecycle_controller.py` 通过 `custom_components/lipro/entry_auth.py` 组装 `LiproProtocolFacade` + `LiproAuthManager`。
3. controller 构造 `custom_components/lipro/core/coordinator/coordinator.py::Coordinator`，首次刷新成功后把实例写入 `entry.runtime_data`。
4. controller 再转发平台 setup，并调用 `ServiceRegistry.async_sync_with_lock()` 统一注册服务。
5. unload/reload 仍由 `EntryLifecycleController` 单点编排；`tests/core/test_control_plane.py` 与 `tests/core/test_init.py` 都锁定了这一故事线。

### 5.2 Refresh / state ingress flow
1. `Coordinator._async_update_data()` 与 `Coordinator.async_refresh_devices()` 是正式刷新入口。
2. runtime 通过 `custom_components/lipro/core/coordinator/services/device_refresh_service.py`、`status` runtime、`custom_components/lipro/core/device/device_factory.py` 构造或更新 `LiproDevice` 聚合。
3. 高漂移 REST 载荷先经 `custom_components/lipro/core/protocol/contracts.py` 与 `custom_components/lipro/core/protocol/boundary/rest_decoder.py` canonicalize，再进入 runtime/domain。
4. `Coordinator.devices` 只暴露 read-only mapping；`.planning/baseline/PUBLIC_SURFACES.md` 与 `tests/meta/test_public_surface_guards.py` 明确禁止把 live mutable registry 提升为 public truth。

### 5.3 Command flow
1. HA entity 从 `custom_components/lipro/entities/base.py` 发起 `async_send_command()` 或 `async_change_state()`。
2. `Coordinator.async_send_command()` 转交 `custom_components/lipro/core/coordinator/services/command_service.py`。
3. runtime 通过 `custom_components/lipro/core/protocol/facade.py` 调用 REST/MQTT child façade。
4. 命令确认、重试与状态过滤落在 `custom_components/lipro/core/command/` 与 `custom_components/lipro/core/coordinator/runtime/command/**`。
5. 最终状态写入统一经 `Coordinator._apply_properties_update()` 进入 `StateRuntime`；`docs/developer_architecture.md` 与 `tests/core/test_command_*` 系列共同锁定此路径。

### 5.4 MQTT flow
1. `Coordinator.async_setup_mqtt()` 通过 `LiproProtocolFacade.build_mqtt_facade()` 建立 protocol child façade。
2. `custom_components/lipro/core/mqtt/mqtt_client.py` 仍是 concrete transport class，但只能作为 `LiproMqttFacade` 内部协作者。
3. MQTT payload 先经 `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py` 与 `CanonicalProtocolContracts` 归一化。
4. runtime 再由 `custom_components/lipro/core/coordinator/runtime/mqtt/**` 与 `mqtt_lifecycle.py` 应用到设备状态。
5. `tests/core/mqtt/test_protocol_replay_mqtt.py` 与 `tests/core/api/test_protocol_contract_matrix.py` 明确要求走 boundary public path，而非 runtime 自解码。

### 5.5 Diagnostics / system health / telemetry flow
- `custom_components/lipro/diagnostics.py` -> `custom_components/lipro/control/diagnostics_surface.py` -> `custom_components/lipro/control/runtime_access.py` + `custom_components/lipro/control/telemetry_surface.py`
- `custom_components/lipro/system_health.py` -> `custom_components/lipro/control/system_health_surface.py` -> `runtime_access.py` + telemetry projection
- `custom_components/lipro/core/telemetry/exporter.py` 是 observer-only truth，`tests/integration/test_telemetry_exporter_integration.py` 与 `.planning/reviews/V1_1_EVIDENCE_INDEX.md` 明确其只可被 diagnostics/system-health/evidence 消费，不得反向成为业务主链。

### 5.6 External-boundary / evidence flow
- firmware truth：`custom_components/lipro/firmware_support_manifest.json` 是 local trust root，`tests/meta/test_firmware_support_manifest_repo_asset.py` 强制其可解析且包含 certified rows。
- diagnostics/support/share truth：`tests/fixtures/external_boundaries/**` + `tests/helpers/external_boundary_fixtures.py` + `tests/meta/test_external_boundary_authority.py` / `test_external_boundary_fixtures.py` 锁定外部边界真源。
- replay/evidence truth：`tests/fixtures/protocol_replay/**`、`tests/harness/protocol/**`、`tests/harness/evidence_pack/**`、`scripts/export_ai_debug_evidence_pack.py` 只属于 assurance-only surface。

## 6. Public Surface Inventory
正式 public surface 由 baseline 与 meta guards 共同限定：
- Runtime home：`custom_components/lipro/coordinator_entry.py` 只导出 `Coordinator`
- Protocol package：`custom_components/lipro/core/protocol/__init__.py` 只导出 root、contracts、session、telemetry，不导出 boundary internals
- REST package：`custom_components/lipro/core/api/__init__.py` 只导出 `LiproRestFacade`、errors、typed rows
- Control package：`custom_components/lipro/control/__init__.py` 只导出 control-plane formal surfaces 与 runtime locator/snapshot helpers
- Domain projection：`custom_components/lipro/entities/base.py`、`custom_components/lipro/helpers/platform.py`、各 platform 根文件只暴露 HA 投影入口
- Guard proof：`tests/meta/test_public_surface_guards.py`、`tests/meta/test_modularization_surfaces.py`、`tests/meta/test_governance_guards.py`

## 7. Compatibility Residuals And Leftovers
正式登记且仍活跃的残留主要有（不含已关闭 seam）：
- `_ClientBase` 与 `_Client*Mixin` helper spine：`custom_components/lipro/core/api/client_base.py`、`custom_components/lipro/core/api/client_*.py`、`custom_components/lipro/core/api/endpoints/*.py`
- `LiproMqttClient` legacy naming：`custom_components/lipro/core/mqtt/mqtt_client.py`
- helper-level compatibility envelope：`custom_components/lipro/core/api/power_service.py`

与治理文档一致的判断：
- `.planning/reviews/RESIDUAL_LEDGER.md` 把上述对象定义为显式 residual family，而不是正式 root；`custom_components/lipro/services/execution.py` 的 coordinator 私有 auth seam 已在 Phase 5 关闭，当前只保留正式 service execution facade。
- `.planning/reviews/KILL_LIST.md` 继续把 `_ClientBase`、legacy endpoint mixin classes、`LiproMqttClient` naming 维持为 active delete gate。
- `custom_components/lipro/core/api/status_fallback.py` 与 `custom_components/lipro/control/developer_router_support.py` 已被治理文档明确定义为 helper home，不属于 public surface，也不属于新的正式 root。

额外的代码级观察：
- `custom_components/lipro/services/execution.py` 现在只保留正式 service execution home 身份；旧 private auth seam 已在 Phase 5 关闭，后续不应再被写回 active residual。
- `custom_components/lipro/control/telemetry_surface.py` 仍通过 `client` 属性探测 protocol telemetry，而 `Coordinator` 的正式术语已经在 `custom_components/lipro/core/coordinator/coordinator.py` 收口为 `protocol`；`tests/integration/test_telemetry_exporter_integration.py` 目前也以 `client` stub 驱动该桥。这是命名层的残留接缝，不改变主链归属，但会增加维护认知成本。

## 8. Architecture Verdict
结论不是“仓库仍有多条合法故事线”，而是：
- 正式主链已经稳定：`control -> runtime -> protocol -> canonical boundary -> vendor`
- 目录归属已经与五平面基本对齐：control、runtime、protocol、domain、assurance 各有明确 home
- public surface 已由 baseline + meta guards 固化，不再依赖历史导出习惯
- 兼容层已被压缩到少量可计数 residual：`_ClientBase` family、`LiproMqttClient` naming、少数 helper-level seams

一句话裁决：**`lipro-hass` 当前是“正式主链成立、兼容残留可数、保障面强约束”的北极星收尾态，而不是仍处于双架构并存态。**
