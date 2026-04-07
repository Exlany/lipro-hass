# Phase 10 Research

**Phase:** `10 API Drift Isolation & Core Boundary Prep`
**Source inputs:** architecture review, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `docs/developer_architecture.md`
**Date:** 2026-03-14

## Findings

### 1. 当前最大的真实风险不是 import 越界，而是 vendor payload shape 仍在上浮

`Phase 7.1` ~ `Phase 9` 已显著加强 plane/root/surface/public export 的边界，但当前守卫更擅长阻止“谁 import 了谁”，还不够擅长阻止“谁开始重新理解 vendor envelope / field alias / pagination shape”。

这意味着一旦逆向 API 发生大范围变化，最先受冲击的不会是 entity/platform import graph，而是：

- `core/protocol` 与 `core/api` 的高漂移 endpoint 处理；
- `core/coordinator` / `runtime/device snapshot` 对 `data` / `hasMore` / `iotId` / `deviceId` / `properties` 等形态的兼容逻辑；
- `config_flow` / `entry_auth` / control adapters 直接消费 login/result dict 的路径。

因此 `Phase 10` 的根因修复目标应是 **payload-shape isolation**，而不是先讨论物理 shared-core 抽离。

### 2. `core` 现在是“逻辑收口 home”，不是“可直接独立的跨平台 core”

当前北极星与 roadmap 口径都支持把 protocol/runtime/domain truth 继续压回 `custom_components/lipro/core/*`，但并未把“跨平台 SDK / second root”定义为本里程碑目标。

对未来可复用性的正确裁决应是：

- **可被提纯的 nucleus**：`LiproProtocolFacade`、canonical contracts、auth/session/result contracts、device aggregate/capability truth；
- **不该在本 phase 抽离的部分**：`Coordinator`、HA lifecycle、config flow、system health、diagnostics、service wiring、platform/entity glue。

所以本 phase 的正确定位是 **core-boundary prep**，不是 **physical package extraction**。

### 3. `config_flow` / `entry_auth` 是 API 漂移向 HA adapter 传导的高风险面

当前 HA adapter 已明显变薄，但 `config_flow` 与部分 entry-auth 流程仍直接 new `LiproProtocolFacade` 并消费登录结果 shape。这类路径的风险在于：

- 只要 login/result contract 改名、嵌套、分层或 envelope 变化，control adapter 会直接破；
- 这会把原本应该封死在 protocol plane 的变化，传播到 HA setup / reauth / reconfigure 主线；
- 未来 CLI / 其他宿主若复用同一协议真相，也无法稳定复用这条路径。

因此 `Phase 10` 必须把这些 adapter 改为只依赖 **formal auth/result contract** 或显式 use case。

### 4. `core` formal surface 仍需要继续去 HA runtime 叙事化

`coordinator_entry.py` 已是正确的 HA runtime public home，但 `core/__init__.py` 仍把 `Coordinator` 当作 `core` 顶层 public export 的一部分。这会模糊两件事：

- 什么是 host-neutral core truth；
- 什么是 HA-specific runtime root。

`Phase 10` 不一定要完全删除所有 convenience import，但必须把正式叙事继续收窄：

- `Coordinator` 的对外 home 应继续固定在 `coordinator_entry.py`；
- `core` 顶层应更偏向 protocol/domain/auth/contracts，而不是混出 HA runtime root。

### 5. 文档与治理回写必须成为 phase deliverable，而不是收尾补票

契约者已明确要求“以上要求也记得完善到文档”。这和北极星完全一致：

- 如果只改代码、不改 roadmap/requirements/context/research/validation/verification/governance，Phase 10 的边界就无法被后续 reviewer / agent / future host 继承；
- 若未来 CLI / other host 真要建立在 formal boundary 之上，文档必须先能回答“哪些能复用、哪些不能复用、为什么”。

因此 `ISO-04` 不应被视为文档杂项，而是本 phase 的主交付之一。

## Recommended Outputs

### 1. Planning artifacts

建议至少生成：

- `10-ARCHITECTURE.md` — 锁定本 phase 的边界裁决与 non-goals
- `10-RESEARCH.md` — 本研究文件
- `10-VALIDATION.md` — Nyquist 验证策略
- `10-01-PLAN.md` — 高漂移 protocol boundary canonicalization
- `10-02-PLAN.md` — host-neutral auth/result contracts + adapter migration
- `10-03-PLAN.md` — `core` formal surface / runtime home demotion
- `10-04-PLAN.md` — docs/governance/replay/meta guard sync

### 2. Likely production files

高概率涉及：

- `custom_components/lipro/core/protocol/contracts.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/api/endpoints/*`
- `custom_components/lipro/core/coordinator/orchestrator.py`
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`
- `custom_components/lipro/config_flow.py`
- `custom_components/lipro/entry_auth.py`
- `custom_components/lipro/core/__init__.py`
- `custom_components/lipro/coordinator_entry.py`
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/telemetry_surface.py`

### 3. Likely tests / guards / fixtures

高概率涉及：

- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/core/api/test_api_status_endpoints.py`
- `tests/core/api/test_protocol_replay_rest.py`
- `tests/core/mqtt/test_protocol_replay_mqtt.py`
- `tests/flows/test_config_flow.py`
- `tests/core/test_auth.py`
- `tests/test_coordinator_public.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_protocol_replay_assets.py`
- `tests/fixtures/api_contracts/**`
- `tests/fixtures/protocol_replay/**`

## Validation Architecture

### Validation dimensions

1. **Boundary closure**：高漂移 REST/MQTT 输入是否都先落 canonical contract，再进入 runtime/domain/control
2. **Adapter decoupling**：`config_flow` / `entry_auth` / control adapters 是否只消费 formal result/use case
3. **Core surface demotion**：`Coordinator` 是否继续固定在 HA runtime home，而不是混入 host-neutral core truth
4. **Replay fidelity**：新增/更新的 contracts 是否有 replay/fixture/authority 证明
5. **Governance sync**：roadmap / requirements / validation / guards / residual docs 是否与代码事实一致

### Recommended quick run

- `uv run pytest -q -x tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_status_endpoints.py tests/flows/test_config_flow.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py`

### Recommended full suite

- `uv run ruff check custom_components/lipro tests`
- `uv run pytest -q -x tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/flows/test_config_flow.py tests/core/test_auth.py tests/test_coordinator_public.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_protocol_replay_assets.py`

### Phase-specific proof expectations

- 每个被正式 canonicalized 的高漂移 endpoint 都要有 contract / replay / regression proof；
- 每个被迁出的 adapter dependency 都要有 flow/auth regression proof；
- `core` surface demotion 不能打破当前 HA 运行时主链；
- 所有新/改动的 guards 与 phase docs 必须在同一轮回写。

## Final Arbitration

`Phase 10` 的最优实现不是“把整个 `core` 抽出去”，而是：

- 先把 **API drift** 关在 protocol boundary 里；
- 再把 **HA adapter** 改成只吃 formal contract；
- 再继续收窄 **`core` vs HA runtime home** 的正式叙事；
- 最后用 docs / governance / replay / guards 把这套边界固定下来。

若未来真的要做 CLI / 其他宿主，这一 phase 应产出的不是 shared SDK 本身，而是 **足够稳定、足够可裁决的 host-neutral nucleus**。
