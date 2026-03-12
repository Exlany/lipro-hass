# File Matrix

**Python files total:** 378

## Phase Ownership by Cluster

| Cluster | Python files | Primary phase | Status |
|---------|--------------|---------------|--------|
| `custom_components/lipro/core/api` | 33 | Phase 2 | `02-01` matrix locked |
| `tests/core/api` | 14 | Phase 2 | `02-01` matrix locked |
| `tests/snapshots` | 5 | Phase 1 / 2 / 6 | Phase 01 baseline locked |
| `custom_components/lipro/core/coordinator` | 56 | Phase 5 | Pending |
| `custom_components/lipro/core/device` | 23 | Phase 4 | Pending |
| `custom_components/lipro/core/mqtt` | 12 | Phase 2 / 5 / 6 | Pending |
| `custom_components/lipro/services` | 11 | Phase 3 | Pending |
| `custom_components/lipro/flow` + entry files | 8 | Phase 3 | Pending |
| `custom_components/lipro/entities` + platform modules | 13 | Phase 4 | Pending |
| Remaining helpers / scripts / tests | remainder | Cross-cutting | Pending |

## Current Focus Slice

### Phase 2 Slice

- `custom_components/lipro/core/api/**/*.py`
- `tests/core/api/**/*.py`
- `tests/snapshots/test_api_snapshots.py`
- `tests/flows/test_config_flow.py`
- direct consumer tests that directly `import custom_components.lipro.core.api...`、patch `core.api` 私有路径，或直接 spec/patch/实例化 `LiproClient`

### Direct Consumer Scope Notes

- `02-01` 的 direct consumer set 只覆盖 **直接依赖 API slice** 的测试文件；不把整个 runtime / control-plane 测试簇都算进来。
- `tests/test_coordinator_runtime.py` 与 `tests/platforms/test_update_task_callback.py` 仍是 Phase 2 邻接验证，但它们未直接消费 `core.api`，因此本次不新增 file-level 条目。
- `tests/meta/test_public_surface_guards.py` 属于治理护栏，不与 compat/direct consumer tests 混为一类；它继续由 baseline asset pack 管理。

## Classification Vocabulary

- `保留`：符合北极星终态，仅做轻微整理
- `重构`：保留职责，但必须按新架构重写内部实现
- `迁移适配`：阶段性桥接层，必须登记删除条件
- `删除`：不进入终态，待消费者清零后移除

## Phase 02 Detailed Governance Matrix (`02-01`)

### `custom_components/lipro/core/api` Public Surface 与主链

| File | 分类 | `02-01` 裁决 |
|------|------|--------------|
| `custom_components/lipro/core/api/__init__.py` | 重构 | canonical export 必须转向 `LiproRestFacade`；`LiproClient` 仅保留 transitional compat 语义 |
| `custom_components/lipro/core/api/client.py` | 迁移适配 | 保留为 compat shell；正式协议逻辑迁出，legacy wrappers 只允许短期存在 |
| `custom_components/lipro/core/api/errors.py` | 保留 | API error taxonomy 继续作为正式 public surface |
| `custom_components/lipro/core/api/types.py` | 保留 | typed payload contracts 继续作为 canonical protocol types |

### `custom_components/lipro/core/api` Mixin Spine 与删除候选

| File | 分类 | `02-01` 裁决 |
|------|------|--------------|
| `custom_components/lipro/core/api/client_base.py` | 删除 | 仅为 mixin 继承链提供 typing 基座；随 demixin 一并退出 |
| `custom_components/lipro/core/api/client_pacing.py` | 删除 | pacing / busy-retry 状态迁入 `RequestPolicy` 与显式 transport collaborators |
| `custom_components/lipro/core/api/client_auth_recovery.py` | 删除 | 由 `AuthRecoveryCoordinator` 接管 auth classification / refresh / replay |
| `custom_components/lipro/core/api/client_transport.py` | 删除 | 以 `TransportExecutor` + `TransportCore` 显式组合替代 mixin 入口 |
| `custom_components/lipro/core/api/endpoints/__init__.py` | 删除 | `_ClientEndpointsMixin` 聚合根不进入终态，只保留显式 endpoint collaborators |

### `custom_components/lipro/core/api` Explicit Collaborators 与 Helper 基座

| File | 分类 | `02-01` 裁决 |
|------|------|--------------|
| `custom_components/lipro/core/api/auth_service.py` | 重构 | auth endpoint helper 保留职责，但不得继续通过 `Any + _smart_home_request` 绑定旧 client |
| `custom_components/lipro/core/api/command_api_service.py` | 重构 | 保留命令编码/重试语义，移除 “`LiproClient`-compatible call” 假设 |
| `custom_components/lipro/core/api/diagnostics_api_service.py` | 保留 | 继续作为 canonical diagnostics collaborator；不承载 compat shell 语义 |
| `custom_components/lipro/core/api/mqtt_api_service.py` | 保留 | Phase 2 不重写 MQTT，但保留 canonical helper 与 contract seam |
| `custom_components/lipro/core/api/observability.py` | 保留 | 继续作为 auth/transport telemetry hook surface |
| `custom_components/lipro/core/api/power_service.py` | 重构 | helper 可保留，但多行 `{"data": ...}` compat shaping 必须收口到 compat shell / normalizer boundary |
| `custom_components/lipro/core/api/request_codec.py` | 保留 | 作为 request encoding helper 保持稳定 |
| `custom_components/lipro/core/api/request_policy.py` | 保留 | backoff / pacing / retry policy 作为显式 collaborator 保留 |
| `custom_components/lipro/core/api/response_safety.py` | 保留 | response masking / code normalization 继续作为 boundary safety 基座 |
| `custom_components/lipro/core/api/schedule_codec.py` | 保留 | canonical schedule payload parsing 保留 |
| `custom_components/lipro/core/api/schedule_endpoint.py` | 保留 | schedule body builders 保留为 collaborator helper |
| `custom_components/lipro/core/api/schedule_service.py` | 重构 | schedule collaborator 保留职责，但不得继续依赖 client 私有协议方法 |
| `custom_components/lipro/core/api/status_service.py` | 保留 | status batching / fallback helpers 继续作为 explicit service seam |
| `custom_components/lipro/core/api/transport_core.py` | 保留 | 作为 HTTP execution primitive 并入 `TransportExecutor` |
| `custom_components/lipro/core/api/transport_retry.py` | 保留 | rate-limit / retry primitive 继续保留 |
| `custom_components/lipro/core/api/transport_signing.py` | 保留 | signing primitive 继续保留 |

### `custom_components/lipro/core/api/endpoints` Modules

| File | 分类 | `02-01` 裁决 |
|------|------|--------------|
| `custom_components/lipro/core/api/endpoints/auth.py` | 重构 | auth endpoint methods 从 mixin class 改为显式 collaborator |
| `custom_components/lipro/core/api/endpoints/commands.py` | 重构 | command endpoint methods 从 mixin class 改为显式 collaborator |
| `custom_components/lipro/core/api/endpoints/connect_status.py` | 保留 | 纯 coercion helper，可直接留在 normalizer/helper 层 |
| `custom_components/lipro/core/api/endpoints/devices.py` | 重构 | device endpoint methods 从 mixin class 改为显式 collaborator |
| `custom_components/lipro/core/api/endpoints/misc.py` | 重构 | misc endpoint methods 从 mixin class 改为显式 collaborator |
| `custom_components/lipro/core/api/endpoints/payloads.py` | 重构 | payload helpers 去 mixin 化，转入 canonical normalizers / shared helper seam |
| `custom_components/lipro/core/api/endpoints/schedule.py` | 重构 | schedule endpoint methods 从 mixin class 改为显式 collaborator |
| `custom_components/lipro/core/api/endpoints/status.py` | 重构 | status endpoint methods 从 mixin class 改为显式 collaborator |

### `tests/core/api` Suites

| File | 分类 | `02-01` 裁决 |
|------|------|--------------|
| `tests/core/api/__init__.py` | 保留 | test package marker，无迁移语义 |
| `tests/core/api/test_api.py` | 重构 | mega-client suite 必须拆分为 facade / collaborator / compat shell 三类测试 |
| `tests/core/api/test_api_client_transport.py` | 重构 | 取消 `_ClientTransportMixin` dummy host，改测 explicit transport chain |
| `tests/core/api/test_api_command_service.py` | 保留 | helper-level command contract 继续保留 |
| `tests/core/api/test_api_diagnostics_service.py` | 保留 | diagnostics collaborator contracts 继续保留 |
| `tests/core/api/test_api_schedule_endpoints.py` | 重构 | 旧 mixin endpoint helpers 改测显式 schedule collaborator/normalizer seam |
| `tests/core/api/test_api_schedule_service.py` | 重构 | schedule service tests 去除 client 私有协议假设 |
| `tests/core/api/test_api_status_service.py` | 保留 | status batching / fallback contract 继续保留 |
| `tests/core/api/test_api_types_smoke.py` | 保留 | typed payload smoke guards 继续保留 |
| `tests/core/api/test_helper_modules.py` | 重构 | `_ClientPacingMixin` 与 compat helper 断言需要迁至 request policy / compat shell tests |
| `tests/core/api/test_protocol_contract_matrix.py` | 保留 | Phase 1 protocol truth 护栏，Phase 2 不得回退 |
| `tests/core/api/test_request_codec.py` | 保留 | request codec contract 继续保留 |
| `tests/core/api/test_schedule_codec.py` | 保留 | canonical schedule codec guard 继续保留 |
| `tests/core/api/test_schedule_endpoint.py` | 保留 | pure endpoint body builders 继续保留 |

### Direct Consumer Tests

| File | 直接依赖 | 分类 | `02-01` 裁决 |
|------|----------|------|--------------|
| `tests/snapshots/test_api_snapshots.py` | diagnostics/mqtt/types helpers | 保留 | Phase 1 canonical snapshot baseline，继续作为 Phase 2 contract truth |
| `tests/flows/test_config_flow.py` | `LiproApiError` / `LiproAuthError`；patch `config_flow.LiproClient` | 迁移适配 | 保留错误语义断言，但 constructor seam 后续需从 legacy public name 脱钩 |
| `tests/core/test_anonymous_share.py` | `LiproClient`、`observability`、patch `client_auth_recovery._record_api_error` | 重构 | 改测 facade/auth-recovery observability seam，不再 patch mixin-era 私有路径 |
| `tests/core/test_auth.py` | `LiproClient`、auth errors | 迁移适配 | auth manager 不能长期依赖 legacy public root 作为 spec 类型 |
| `tests/core/test_boundary_conditions.py` | public errors；局部直接实例化 `LiproClient` | 迁移适配 | 剩余 constructor edge cases 收敛到 compat shell / façade split tests |
| `tests/core/test_command_dispatch.py` | `LiproApiError` | 保留 | 仅验证 public error mapping |
| `tests/core/test_command_trace.py` | `LiproApiError` | 保留 | 仅验证 public error tracing |
| `tests/core/test_coordinator.py` | `LiproAuthError` / `LiproConnectionError` | 保留 | 继续消费正式错误 surface，不绑定 mixin 细节 |
| `tests/core/test_coordinator_integration.py` | API error family | 保留 | 继续消费正式错误 surface，不绑定 mixin 细节 |
| `tests/core/test_exceptions.py` | `errors.py` public hierarchy | 保留 | 继续锁定 shared exception layering |
| `tests/core/test_outlet_power.py` | API error family | 保留 | 仅验证 public error / helper behavior |
| `tests/core/test_outlet_power_runtime.py` | `LiproApiError` | 保留 | 仅验证 runtime error propagation |
| `tests/core/coordinator/runtime/test_command_runtime.py` | `LiproApiError` / `LiproAuthError` | 保留 | 继续消费正式错误 surface |
| `tests/core/coordinator/runtime/test_device_runtime.py` | `LiproClient` spec + compat methods | 迁移适配 | runtime 仍依赖 `get_device_list/query_*_devices` compat surface，必须在 Phase 2 清点后迁移 |
| `tests/core/coordinator/services/test_command_service.py` | `LiproApiError` | 保留 | 仅验证 public error mapping |
| `tests/meta/test_modularization_surfaces.py` | `custom_components.lipro.core.api` symbol surface | 保留 | 继续约束 canonical helper symbols，不与 compat consumer 混淆 |

### Direct Consumer Test Support / Legacy Public-Name Consumers

| File | 直接依赖 | 分类 | `02-01` 裁决 |
|------|----------|------|--------------|
| `tests/conftest.py` | patch `config_flow.LiproClient`、shared auth/connection mocks | 迁移适配 | 共享夹具仍承载 legacy constructor 假设，后续需切换到 façade-aware factory seam |
| `tests/core/test_device_refresh.py` | compat methods `get_device_list/query_iot_devices/query_group_devices/query_outlet_devices` | 迁移适配 | 视作 compat wrapper 高风险消费者，在 wrapper 删除前必须先迁移 |
| `tests/core/test_init.py` | top-level `LiproClient` patch / factory wiring | 迁移适配 | 入口装配仍假设 legacy public name，需与 control/runtime handoff 同步迁移 |
| `tests/core/test_token_persistence.py` | `LiproClient` 作为 auth/client factory | 迁移适配 | token persistence factory seam 后续需从 legacy public name 脱钩 |

## Phase 01 Closeout Review

- 已检查 `tests/fixtures/api_contracts/**`、`tests/core/api/test_protocol_contract_matrix.py` 与 `tests/snapshots/test_api_snapshots.py`，确认它们构成 Phase 01 的 baseline 资产面。
- 本次未调整文件归属：协议实现与大多数 API 测试仍归后续 Phase 2 收口；Phase 01 只负责锁定 contract baseline。
- `tests/snapshots` 状态更新为 `Phase 01 baseline locked`，表示已有 canonical contract 观察面，但后续 Phase 2 / 6 仍可在同一承载面继续扩展。

## Phase 02 / `02-01` Governance Delta

- `custom_components/lipro/core/api/**/*.py`、`tests/core/api/**/*.py` 与 direct consumer tests 已补齐 file-level target fate，不再只停留在 cluster 级别。
- `LiproClient`、compat wrappers、mixin spine 与 legacy public-name consumers 已被明确标成 `迁移适配` / `删除` / `重构`，为 `02-02` ~ `02-04` 提供可执行边界。
- 本次只做治理归档，不修改业务代码、不改测试实现。
