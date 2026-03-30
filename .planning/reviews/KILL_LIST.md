# Kill List

## Candidate Removals (Phase 02 Registered)

| Target | Current carrier | Owner | Earliest delete phase | Delete when | `02-01` status |
|--------|------------------|-------|-----------------------|-------------|----------------|
| `_ClientBase` | `custom_components/lipro/core/api/session_state.py` | `02-02 façade + transport rewrite` | Phase 2 | 生产与测试都不再需要 mixin typing spine | 已关闭（Phase 17：retired to `RestSessionState` formal state home） |
| `_ClientPacingMixin` | `custom_components/lipro/core/api/client_pacing.py` | `02-02 façade + transport rewrite` | Phase 2 | pacing / busy-retry 状态归入 `RequestPolicy` / transport chain，测试不再实例化 mixin host | 已关闭（Phase 17：compat shell removed, only timing helpers remain） |
| `_ClientAuthRecoveryMixin` | `custom_components/lipro/core/api/auth_recovery.py` | `02-02 façade + transport rewrite` | Phase 2 | auth classification / refresh / replay 迁入 `RestAuthRecoveryCoordinator`，私有路径不再被 patch | 已关闭（Phase 17：compat shell removed, coordinator retained） |
| `_ClientTransportMixin` | `custom_components/lipro/core/api/transport_executor.py` | `02-02 façade + transport rewrite` | Phase 2 | transport 入口完全改为 `RestTransportExecutor` + `TransportCore` 显式组合 | 已关闭（Phase 17：compat shell removed, `RestTransportExecutor` retained） |
| `_ClientEndpointsMixin` | `custom_components/lipro/core/api/endpoints/__init__.py` | `02-03 endpoint collaborator migration` | Phase 2 | façade 只装配显式 endpoint collaborators，不再继承聚合 mixin | 已关闭（Phase 11：aggregate endpoint mixin export removed） |
| legacy endpoint mixin classes | `custom_components/lipro/core/api/endpoints/{auth,commands,devices,misc,payloads,schedule,status}.py` | `02-03 endpoint collaborator migration` | Phase 2 | 各 endpoint / payload helper 已迁成 explicit collaborators / normalizers | 已关闭（Phase 17：legacy mixin family retired to explicit collaborators + local ports） |
| `_build_compat_list_payload` | `custom_components/lipro/core/api/client.py` | `02-04 compat shell cleanup` | Phase 2 | direct consumers 不再要求 `{"data": [...]}` envelope | 已关闭（Phase 12：compat payload helper removed） |
| legacy compat wrapper methods | `custom_components/lipro/core/api/client.py::{get_device_list,query_iot_devices,query_outlet_devices,query_group_devices}` | `02-04 compat shell cleanup` | Phase 2 | runtime / tests 改用 canonical façade outputs 或统一 compat adapter | 已关闭（Phase 12：compat wrapper methods removed） |
| `LiproClient` 作为 legacy constructor name | `custom_components/lipro/core/api/__init__.py` | `02-04 public-surface demotion`（与 Phase 9 handoff 对齐） | Phase 9+ | 只剩 `core.api` 显式 compat shell；direct tests/consumers 完成迁移后删除 | 已关闭（Phase 12：compat shell removed） |
| `LiproMqttClient` 作为 legacy transport root name | `custom_components/lipro/core/mqtt/transport.py`（`LiproMqttFacade.raw_client` seam 已在 Phase 12 删除） | `02.5 unified-root closeout` | Phase 9+ | integration/tests 不再需要 concrete transport object，且 direct transport legacy naming 完成收口 | 已关闭（Phase 17：canonical naming unified to `MqttTransport`） |
| `LiproMqttFacade.raw_client` compat seam | `custom_components/lipro/core/protocol/facade.py` | `09 residual surface closure` | Phase 9+ | runtime/integration assertions 改用 formal child façade，不再需要 concrete transport object | 已关闭（Phase 12：compat seam removed） |
| split-root protocol public semantics | runtime / tests 中并行感知 `LiproRestFacade` 与 `LiproMqttClient` 的入口语义 | `02.5 unified-root closeout` | Phase 2.5 | `PUBLIC_SURFACES.md` 与 runtime-facing consumers 只承认 `LiproProtocolFacade` 为正式协议根 | 已关闭（Phase 9：implicit root delegation and package-level MQTT root export removed） |
| 多行 power payload 的 compat wrapping | `custom_components/lipro/core/api/power_service.py` | `02-04 compat shell cleanup` | Phase 2 | power helper 只返回 canonical rows；兼容 envelope 仅存在于 compat shell | 已关闭（Phase 17：formal helper contract is explicit row/list only） |
| `services/wiring.py` compat shell | `custom_components/lipro/services/wiring.py` | `11 control-router formalization` | Phase 11+ | formal router ownership 收口后删除 compat shell | 已关闭（Phase 11：compat shell removed） |
| coordinator 私有 auth hook seam | `custom_components/lipro/services/execution.py` | `03/05 runtime-auth hardening` | Phase 5 | service execution 只通过正式 runtime/auth contract 获取 auth context | 已关闭（Phase 5） |
| `DeviceCapabilities` legacy public name | `custom_components/lipro/core/device/capabilities.py` | `04-03 capability compat cleanup` | Phase 4 / 7 | 直接导入点已迁到 `custom_components/lipro/core/capability`，device facade 不再依赖 legacy alias | 已关闭（Phase 12：compat alias removed） |
| `device_delegation.py` dynamic delegation carrier | `custom_components/lipro/core/device/device_delegation.py` | `13 explicit domain surface` | Phase 13 | device/state 正式表面已改成显式 property / method surface，不再需要独立 delegation carrier | 已关闭（Phase 13：file removed） |
| `LiproDevice.__getattr__` / `DeviceState.__getattr__` | `custom_components/lipro/core/device/{device.py,state.py}` | `13 explicit domain surface` | Phase 13 | focused tests 锁定 no-`__getattr__` contract，device/state surface 只由显式 façade 定义 | 已关闭（Phase 13：dynamic delegation removed） |

## Phase 85 Routed Delete Gates

| Target | Current carrier | Owner | Earliest delete phase | Delete when | Phase 85 verdict |
|--------|------------------|-------|-----------------------|-------------|------------------|
_None currently registered._

> **Phase 88 freeze note:** routed delete gates 为空是显式 closeout verdict，不是遗漏登记。若未来出现新的 file-level delete campaign，必须重新登记 target、owner、exit condition 与 evidence。

## Deletion Gate

删除前必须满足：
1. 下游消费者已迁移。
2. contract / regression tests 通过。
3. residual ledger 已关闭对应条目。
4. summary 明确记录是“正式删除”还是“仅登记、不删除”。

## Phase 110 Status Update

- 本 phase **无新增 active kill target**；主要工作是 snapshot inward split、governance closeout 与 evidence chain 收口，不新增 file-level delete campaign。
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` 与 `snapshot_support.py` 均保留为 formal/inward homes，不被误登记为 future delete target。
- `no active milestone route / latest archived baseline = v1.30` 已生效；下一步稳定为 `$gsd-new-milestone`。

## Phase 109 Status Update

- 本 phase **无新增 active kill target**；当前收口的是 anonymous-share manager inward decomposition、focused regressions 与 governance projection，而不是新的 file-level delete campaign。
- `custom_components/lipro/core/anonymous_share/manager.py`、`manager_scope.py` 与 `manager_support.py` 都继续保留为 formal/support homes；本轮只允许 inward decomposition，不把它们叙述成 future delete target。
- `no active milestone route / latest archived baseline = v1.30` 已生效；下一步稳定为 `$gsd-new-milestone`，而不是把 Phase 109 再回写成 active story。

## Phase 108 Status Update

- 本 phase **无新增 active kill target**；MQTT transport/runtime explicit owner/state contract、focused regressions 与 governance projection 现在作为 predecessor bundle 保持可见性，而不是新的 file-level delete campaign。
- `custom_components/lipro/core/mqtt/transport.py` 与 `custom_components/lipro/core/mqtt/transport_runtime.py` 都继续保留为 formal/private homes；本轮只允许 predecessor visibility，不把它们叙述成 future delete target。
- `no active milestone route / latest archived baseline = v1.30` 已生效；`Phase 108` 现在只承担 predecessor visibility，而不是 current-route handoff owner。

## Phase 107 Status Update

- 本 phase **无新增 active kill target**；REST child-façade assembly、status fallback helper decomposition 与 request-policy pacing-cache localization 现在作为 completed predecessor bundle 保持可见性，而不是新的 file-level delete campaign。
- `custom_components/lipro/core/api/rest_facade.py`、`custom_components/lipro/core/api/status_fallback_support.py` 与 `custom_components/lipro/core/api/request_policy_support.py` 都继续保留为 formal/support homes；本轮只允许 predecessor visibility，不把它们叙述成 future delete target。
- `no active milestone route / latest archived baseline = v1.30` 已生效；下一步稳定为 `$gsd-new-milestone`，而不是把 Phase 107 再回写成 active story。

## Phase 105 Status Update

- 本 phase **无新增 active kill target**；它现在承担 latest-archived closeout visibility，而不是 current-route selector。
- `tests/meta/governance_followup_route_specs.py` 与 `scripts/check_file_matrix_registry_*` 继续保留为 formal governance truth，不被误登记为 future delete target。
- `Phase 103` / `Phase 104` predecessor bundle 与 `Phase 105` promoted closeout bundle 已分别通过 focused guards 与 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 固定身份；当前已进入 archived-only route。

## Phase 65 Status Update

- 本 phase **无新增 file-level kill target**：本轮收口的是 `runtime_access_support.py` 反射味、runtime alias sidecar 与 anonymous-share bool-only submit bridge，这些都在原正式 home 内被消解，而不是通过新增删除门槛维持。
- `RESIDUAL_LEDGER.md` 已同步登记三个 closeout family；`KILL_LIST` 继续保持“无新增待删文件”的 truthful 状态。

## Phase 70 Status Update

- 本 phase **无新增 file-level kill target**：`runtime_access_support_{members,telemetry,views,devices}.py`、`share_client_{ports,refresh,submit}.py` 与 `core/ota/query_support.py` 都是既有 formal homes 的 inward helper cluster，不是 future delete campaign 的权宜 compat shell。
- archive/version/governance 的收口通过 authority / tests / docs freeze 完成，没有为了“看起来在清理”而伪造新的 delete gate。

## Phase 01 Closeout Review

- 已检查 kill list 与 Phase 01 baseline 产物的关系，本次**无新增删除项**。
- `_Client*Mixin` 与 compat wrappers 仍是后续 Phase 2 的主要清理对象；Phase 01 只补足它们必须遵守的 contract baseline。
- canonical snapshots、immutable constraints 与 phase summaries 属于治理资产，不进入删除候选。

## Phase 02 / `02-01` Registration Note

- 本计划只做 kill candidate 登记与删除门槛澄清，不执行任何生产代码删除。
- mixin inheritance、compat wrappers、legacy public names 已从“口头债务”升级为文件级 kill targets。
- 若后续 `02-02` ~ `02-04` 没有实际删除动作，summary 必须说明仍阻塞于哪个 direct consumer / public surface。


## Phase 02 / `02-04` Status Update

- `_ClientEndpointsMixin` aggregate export 已从 `custom_components/lipro/core/api/endpoints/__init__.py` 删除；remaining delete-gated scope 已收缩为 legacy endpoint mixin helper classes 本身。
- `_ClientBase`、`_ClientAuthRecoveryMixin`、`_ClientTransportMixin` 不再按整文件删除理解；需要删除的是残余 compat spine，同时保留 `RestSessionState` / `RestAuthRecoveryCoordinator` / `RestTransportExecutor` 等正式组件。
- `LiproClient` 已完成 formal-root demotion，但 top-level factory / flow seam 仍保留过渡存在；删除动作交由 `Phase 2.5+` 随 unified root 继续推进。

## Phase 02.5 / `02.5-01` Registration Note

- 已把 `LiproMqttClient` formal-root 语义与 split-root protocol public semantics 升格为 file-level kill targets。
- `Phase 2.5` 的删除目标不是盲删 MQTT helpers，而是删除“两个正式协议根并存”的语义。

## Phase 02.5 / `02.5-02 ~ 02.5-03` Status Update

- `LiproMqttClient` 已完成 formal-root demotion：真实生产主链现在通过 `LiproMqttFacade` 作为 protocol child façade 接入，旧 concrete transport 只剩 compat/export 语义。
- split-root protocol public semantics 已从 runtime-facing production path 清退；剩余删除门槛集中在 `core/mqtt/__init__.py` 旧导出与 compat tests/aliases 的最终清零。
- `LiproClient` 仍保留显式 compat alias，但 `custom_components/lipro/__init__.py` / `config_flow.py` / coordinator MQTT path 已全部切到 `LiproProtocolFacade`。


## Phase 03 / `03-02 ~ 03-03` Status Update

- `custom_components/lipro/services/wiring.py` 已在 Phase 11 删除；formal control-plane service ownership 现仅归属 `custom_components/lipro/control/service_router.py`。
- `custom_components/lipro/services/execution.py` 的 coordinator 私有 auth hook seam 已在 Phase 5 收口；当前保留的是正式 service execution facade，而不是 active kill target。
- `custom_components/lipro/diagnostics.py`、`system_health.py` 与 `__init__.py` 不再进入 kill list：它们保留为 HA adapter 薄层，终态角色已被明确保留。


## Phase 04 Status Update

- `custom_components/lipro/core/device/capabilities.py` 已缩减为显式 compat alias，生产主链不再依赖它。
- `DeviceCapabilities` legacy public name kill target 继续保留，删除时机后移到 `Phase 7` 的 compat/legacy sweep。
- `04-02 / 04-03` 已完成 duplicate-rule 清退，因此本 phase 不再保留新的 file-level delete target。


## Phase 05 Status Update

- `custom_components/lipro/services/execution.py` 的 coordinator 私有 auth hook seam 已关闭；不再作为 active kill target。
- Phase 5 新增的 signal formalization 与 shadow cleanup 不引入新的 file-level kill target。

## Phase 07.5 Status Update

- `07.5` 只完成 governance / closeout arbitration：本 phase **无新增 file-level kill target**，也不把 evidence index、telemetry exporter 或 replay harness 误登记为删除候选。
- 现有 delete gates 维持不变：legacy protocol public names 与 `DeviceCapabilities` compat alias 仍按既有 gate 收口。
- `V1_1_EVIDENCE_INDEX.md`、`07.5-SUMMARY.md` 与 phase summaries 属于 closeout governance artifacts，不进入 kill list。

## Phase 08 Status Update

- `08` 只新增 assurance-only evidence-pack tooling：本 phase **无新增 file-level kill target**，也不把 `tests/harness/evidence_pack/*`、`scripts/export_ai_debug_evidence_pack.py` 或导出产物误登记为删除候选。
- 现有 delete gates 维持不变：legacy protocol public names 与 `DeviceCapabilities` compat alias 继续按既有条件收口。
- `ai_debug_evidence_pack.json` / `ai_debug_evidence_pack.index.md` 属于可再生 assurance outputs；其 formal home 是 tooling/export chain，而不是 kill list target。

## Phase 09 Status Update

- `custom_components/lipro/__init__.py`、`config_flow.py`、`core/__init__.py` 与 `core/mqtt/__init__.py` 的 legacy public-name / export chain 已关闭；它们不再是 active kill target，只保留正式 adapter / helper 角色。
- remaining protocol delete targets 只剩 `core.api.LiproClient`、`LiproProtocolFacade.get_device_list` compat seam 与 `LiproMqttFacade.raw_client` explicit seam。
- `LiproMqttClient` kill target 已缩窄到 direct transport class 与 `LiproMqttFacade.raw_client` compat seam；删除门槛是 integration/tests 不再需要 concrete transport object。
- `raw_client` 已显式登记为 future kill target；本 phase 没有引入新的无 gate compat，剩余 delete target 都是显式、可计数、可回归验证的 seam。

## Phase 10 Status Update

- `custom_components/lipro/core/__init__.py` 的 runtime-home export chain 已关闭；它不再是 active kill target，只保留 host-neutral core export 角色。
- `AuthSessionSnapshot` / `LiproAuthManager` 已成为 formal auth/session contract home；`get_auth_data()` fallback 仍是 compat/test seam，但本 phase 不把它提升为新的 file-level kill target。
- remaining protocol delete targets 维持不变：`core.api.LiproClient`、`LiproProtocolFacade.get_device_list` compat seam 与 `LiproMqttFacade.raw_client` explicit seam 继续按既有 gate 收口。
- 本 phase 没有引入新的 file-level kill target；future host work 必须复用 boundary-first nucleus，而不是重开 shared-core / runtime-root 抽离。

## Phase 11 Status Update

- `custom_components/lipro/services/wiring.py` compat shell 已物理删除；相关 kill target 已关闭。
- `_ClientEndpointsMixin` aggregate export 已删除；API mixin inheritance delete gate 继续收缩到 remaining helper mixin consumers。
- remaining active kill targets 现主要集中在 `LiproMqttClient` legacy naming 与 remaining helper mixin / typing spine。


## Phase 12 Status Update

- 已删除：`core.api.LiproClient` compat shell。
- 已删除：`LiproProtocolFacade.get_device_list` compat wrapper。
- 已删除：`LiproMqttFacade.raw_client` compat seam。
- 已删除：`DeviceCapabilities` legacy public name 与 `custom_components/lipro/core/device/capabilities.py`。
- 保留但降格：`_ClientBase` 仅作为 internal typing contract，不再作为 active public skeleton。

## Phase 13 Status Update

- 已删除：`custom_components/lipro/core/device/device_delegation.py` dynamic delegation carrier。
- 已删除：`LiproDevice.__getattr__` / `DeviceState.__getattr__` 动态领域扩面。
- formal device/domain surface 现由显式 property / method 集合与 focused tests 共同锁定。
- remaining active delete gates 与 Phase 13 无新增长尾 compat。


## Phase 14 Status Update

- 本 phase **无新增 file-level kill target**；`ScheduleApiService` 已退出正式 schedule 主链，但不需要作为独立 kill target 继续登记。
- `custom_components/lipro/core/api/status_fallback.py` 与 `custom_components/lipro/control/developer_router_support.py` 属于 focused helper homes，不进入 kill list。
- remaining active delete gates 继续集中在 `_ClientBase` / helper mixin family、`LiproMqttClient` legacy naming 与少量 helper-level compatibility envelope。


## Phase 15 Status Update

- 本 phase **无新增 file-level kill target**；developer feedback/upload truth、governance/source-path truth 与 tooling semantics 只做裁决与收口。
- `_ClientBase` 与 `LiproMqttClient` 的 delete gate 维持不变，但 `FILE_MATRIX` / `PUBLIC_SURFACES` / `RESIDUAL_LEDGER` 现已明确写出 locality / ownership。
- `coverage_diff.py` 被保留为 coverage floor + optional baseline diff 工具；benchmark baseline/threshold lane 与 dev `pip-audit` 都已有明确治理语义，不进入 kill list。

## Phase 16 Status Update

- `custom_components/lipro/services/execution.py` 的 coordinator 私有 auth hook seam 继续维持关闭；本 phase 明确禁止把它重新登记成 active kill target。
- remaining active delete gates 仍集中在 `_ClientBase` / helper mixin family、`LiproMqttClient` legacy naming 与少量 helper-level compatibility envelope。
- Final closeout audit (`2026-03-15`) 未发现新的 file-level kill target；repo-wide residual counts 为 `Any=711`、`except Exception=36`、`type: ignore=12`、dead pytest markers `=0`，全部继续受现有 delete gate 约束。

| Item | Current status | Owner | Delete gate | Evidence |
|------|----------------|-------|-------------|----------|
| `_ClientBase` / helper mixin family | 已登记，未删除 | `core/api` | helper consumers 不再依赖 legacy mixin spine，且 import guards / tests 已迁出 | `custom_components/lipro/core/api/session_state.py`, `.planning/reviews/RESIDUAL_LEDGER.md` |
| `LiproMqttClient` legacy naming | 已登记，未删除 | `core/mqtt` | direct transport legacy name 不再出现在 tests / child façade imports / documentation 中 | `custom_components/lipro/core/mqtt/transport.py`, `.planning/reviews/RESIDUAL_LEDGER.md` |
| helper-level power compatibility envelope | 已登记，未删除 | `core/api` | outlet power / service callers 仅消费单一正式 payload shape 后删除 | `custom_components/lipro/core/api/power_service.py`, `custom_components/lipro/core/coordinator/outlet_power.py` |


## Phase 17 Status Update

- 已关闭：`_ClientBase` / `_ClientPacingMixin` / `_ClientAuthRecoveryMixin` / `_ClientTransportMixin` 及 endpoint legacy mixin family 的 active delete gate；production truth 只保留 `RestSessionState`、`RestAuthRecoveryCoordinator` 与 `RestTransportExecutor` 等正式组件。
- 已关闭：`LiproMqttClient` legacy transport root name；canonical concrete naming 统一为 `MqttTransport`，且 package/root public-surface bans 已同步。
- 已关闭：`get_auth_data()` fallback 与 helper-level power compatibility envelope；token persistence / outlet-power helper contract 均已收口到单一正式 typed truth。
- 当前 kill list 仅保留明确 de-scope / out-of-scope cleanup 议题，不再保留 Phase 16 carry-forward residual 作为 active delete gate。

## Phase 18 Status Update

- 本 phase **无新增 active kill target**；`core/auth/bootstrap.py`、`flow/login.py::ConfigEntryLoginProjection` 与 `helpers/platform.py` 都是正式 helper / adapter homes，而不是新的 compat shell。
- `CATEGORY_TO_PLATFORMS`、`get_platforms_for_category()`、`CapabilitySnapshot.platforms`、`supports_platform()` 与 `device_views.platforms()` 已从治理真源退场；其回流风险由 Phase 18 targeted bans 负责阻断，而非留作新的 delete-gated carry-forward。
- `entry_auth.py` 与 `config_flow.py` 已统一复用 shared auth bootstrap wiring；后续若再优化，只允许继续收窄 adapter 语义，不得重建第二套 auth bootstrap truth。

## Phase 19 Status Update

- 本 phase **无新增 active kill target**；`custom_components/lipro/headless/boot.py`、`tests/harness/headless_consumer.py` 与平台 thin setup shells 都是正式 proof/helper/adapter homes，而不是新的 compat shell。
- `build_password_login_seed()` 已从 `flow/login.py` 退出，headless proof 不再需要经由 HA flow 包复用 host-neutral seed helper。
- authority 继续维持 **no-change**：未新增 truth-source family、未改变 authority precedence、未改变 sync owner；proof outputs 只消费 authority path，不反向成为 authority path。

## Phase 20 Status Update

- 本 phase **无新增 active kill target**；remaining boundary family completion 的主线是 authority / fixture / replay / guard 收口，不是新增 compat shell 或 file-level cleanup story。
- `mqtt.topic.v1`、`mqtt.message-envelope.v1` 与 remaining REST family 的 closeout 只能压缩 active residual / replay gap，不得借机把 `topics.py`、`message_processor.py`、`payload.py`、fixture README 或 replay docs 重新合法化为第二 authority root。
- `20-VERIFICATION.md` 与 `.planning/{ROADMAP,REQUIREMENTS,STATE}.md` 的完成态已在 full gate 通过后同步；Phase 20 不再保留“等待 final gate”的 carry-forward 说明。


## Phase 21 Status Update

- 本 phase **无新增 active kill target**；replay harness、evidence pack、failure taxonomy helper 与 telemetry sink 都是正式 assurance / contract homes，不应被误登记为待删对象。
- broad-catch 收紧的目标是改正 arbitration 语义，而不是制造一轮 rename-or-delete campaign；remaining `except Exception` 只作为 future sustainment typed hardening backlog 记录。
- `failure_summary` / `error_category` / `error_type` contract 现由 shared telemetry truth 锁定，后续 phase 只能消费它，不能把它重新降格成临时 compatibility wrapper。

## Phase 22 Status Update

- 本 phase **无新增 active kill target**；diagnostics / system health / developer report / evidence consumer convergence 是 contract closure，不是 file-level cleanup campaign。
- `failure_entries` 聚合与 diagnostics-service `last_error` payload 继续保留正式 consumer/home 身份；legacy `build_developer_report()` compat / test seam 已移除。
- 后续 docs / release closeout 只能继续消费 shared `failure_summary` truth，不得以“文档清理”为名把这些 consumer surfaces 重新写回 helper folklore。

## Phase 23 Status Update

- 本 phase **无新增 active kill target**；`V1_2_EVIDENCE_INDEX.md`、README / SUPPORT / TROUBLESHOOTING / runbook / template 同步都属于长期治理资产，而不是可删临时文件。
- release workflow 继续复用 `.github/workflows/ci.yml`；未新增第二套 gate，因此也没有新的 workflow-level kill target。
- 若未来更新 contributor/release docs，只允许沿既有 authority / verification chain 收口，不得重新造“phase-specific temp checklist”文件族。

## Phase 24 Status Update

- 本 phase **无新增 active kill target**；`v1.2-MILESTONE-AUDIT.md`、`V1_2_EVIDENCE_INDEX.md`、`v1.3-HANDOFF.md` 与 `MILESTONES.md` 都是正式 closeout / handoff assets。
- final repo audit 仅把 distributed tech debt 转化为显式 backlog / retain disposition，没有为“看起来更整洁”而追加新的 file-level kill target。
- `v1.2` 当前只差外层 archival workflow；closeout bundle 本身不得再被误判为 short-lived temp artifact。

## Phase 39 Status Update

- 已关闭：`custom_components/lipro/core/protocol/compat.py` dead shell；该 kill target 不再保留为 future delete gate。
- 本 phase **无新增 active kill target**；control-home clarification、governance current-story convergence 与 mega-test topicization 都是 formal truth / evidence closeout，不是新的 delete campaign。
- `39-SUMMARY.md` 与 `39-VERIFICATION.md` 已作为 Phase 39 closeout evidence promoted；`39-VALIDATION.md`、`39-PRD.md`、`39-CONTEXT.md` 与 `39-0*-PLAN.md` 继续保持 execution-trace 身份。


## Phase 40 Status Update

- `custom_components/lipro/services/execution.py` 明确保留为 formal service execution facade；Phase 40 只允许围绕 shared execution contract 收口，不得把它重新登记为 active kill target。
- 本 phase **无新增 active kill target**；`runtime_access` helpers、governance registry truth 与 endpoint-operations wording 都是 formal truth closure，不是新的 delete campaign。

## Phase 43 Status Update

- 本 phase **无新增 active kill target**；typed runtime projection、maintenance demotion 与 service-router boundary 收敛都是 formal truth closeout，不是新增 delete campaign。
- `custom_components/lipro/services/device_lookup.py` 与 `custom_components/lipro/services/maintenance.py` 继续保留，但仅作为 service-facing helper / thin adapter；它们不是 future kill target，也不得回流为 runtime/control ownership home。
- `custom_components/lipro/runtime_infra.py` 与 `custom_components/lipro/control/service_router_support.py` 当前是正式 ownership homes；后续若继续优化，只能做局部收敛，不能重新打开第二条 helper-owned listener/runtime story。

## Phase 44 Status Update

- 本 phase **无新增 active kill target**；`README.md` / `README_zh.md`、`CONTRIBUTING.md`、`docs/README.md`、`SUPPORT.md`、`SECURITY.md` 与 PR template 都是正式入口契约，不是临时治理脚手架。
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 继续明确保持 promoted allowlist 身份；`44-SUMMARY.md` 与 `44-VERIFICATION.md` 被提升为长期证据，其余 `44-0x-SUMMARY.md` 与 plan/context/research 资产继续保持 execution-trace 身份。
- 旧术语的剩余承载点现只允许停留在 residual / archive 语境；这是一条 boundary hygiene contract，不是新的 file-delete campaign。

## Phase 45 Status Update

- 本 phase **无新增 active kill target**；decoder hotspot slimming、typed outcome vocabulary 收口与 benchmark governance hardening 都是 formal home refinement，不是新的 delete campaign。
- `scripts/check_benchmark_baseline.py` 与 `tests/benchmarks/benchmark_baselines.json` 现已被确认为正式 benchmark governance artifacts，不是临时实验脚手架。
- `45-SUMMARY.md` 与 `45-VERIFICATION.md` 已提升为长期证据；其余 `45-0x-SUMMARY.md` 与 plan/context/research 资产继续保持 execution-trace 身份。


## Phase 47 Status Update

- 本 phase **无新增 active kill target**；docs index formalization、signature-regex tighten 与 verification-matrix drift guard 都属于 current-truth hardening，不是新的 delete campaign。
- `scripts/agent_worker.py` 与 `scripts/orchestrator.py` 暂仍保留，因为维护中的文档 / 自动化仍需要这些名称提供显式失败与迁移指引；delete after maintained docs and automation no longer rely on the stub names as migration hints。它们不是 active tooling，也不得继续被当作成功路径。

## Phase 52 Status Update

- 本 phase **无新增 active kill target**；`protocol_facade_rest_methods.py`、`ProtocolRestPortFamily`、`RequestPolicy`、`RestRequestGateway` 与 `RestTransportExecutor` 的当前动作都是 formal ownership / boundary closure，而不是新的 delete campaign。
- `Generic backoff helper leak` 已在 `RESIDUAL_LEDGER.md` 中登记为 deferred residual，但它当前不是 file-level kill target；后续若继续收口，只允许迁往更诚实的 shared backoff home，不得借机把现有 protocol/API homes 误删或降格。

## Phase 54 Status Update

- 本 phase **无新增 active kill target**；`manager_support.py`、`share_client_support.py`、`helper_support.py` 与 `request_policy_support.py` 都属于 support-only inward decomposition，不是新的 delete campaign。
- `Generic backoff helper leak` 在本 phase 只完成了 companion formalization 与 residual honesty 冻结；它仍不是 file-level kill target，后续只允许迁往更诚实的 shared backoff home。



## Phase 56 Status Update

- 本 phase **无新增 active kill target**；`custom_components/lipro/core/utils/backoff.py` 是正式 neutral helper home，不是新的 delete campaign。
- `Generic backoff helper leak` 已在 Phase 56 关闭：动作是 owner-truth 纠偏与 neutral helper migration，而不是删除 `RequestPolicy` / `RetryStrategy` / `MqttSetupBackoff` 这些 formal homes。
- 后续若继续优化 retry semantics，只允许围绕 plane-local semantics 或 typed outcome 收敛，不能以“共享 helper”名义重新打开 file-level delete folklore。

## Phase 57 Status Update

- 本 phase **无新增 active kill target**；typed command-result contract hardening 属于 formal-home convergence，不是新的 delete campaign。
- `Command-result stringly-typed outcome contract` 已在 Phase 57 关闭：动作是 typed vocabulary convergence，而不是删除 `result_policy.py` / `result.py` / runtime sender / diagnostics handlers 这些 formal homes。
- 后续若继续优化 retry budgets 或 broader outcome reuse，只允许围绕 shared contract 继续收口，不能以 typed cleanup 名义重新打开 file-level delete folklore。


## Phase 58 Status Update

- 本 phase **无新增 active kill target**；repo-wide refreshed audit 关注的是 verdict refresh、route synthesis 与 truth freeze，不是新的 delete campaign。
- 后续若继续处理 megaguards / tooling hotspots / thick formal homes，只能以 inward decomposition、topicization 或 naming clarity 方式推进，不得虚构 file-level delete folklore。

## Phase 59 Status Update

- 本 phase **无新增 active kill target**；verification topicization 与 current-story freeze 都属于 formal truth closeout，不是新的 delete campaign。
- `tests/core/test_device_refresh.py` 的退场已在本 phase 完成，后续若继续优化 verification topology，只允许围绕当前 focused suites 收口，不得再恢复新的 mega-suite folklore。
- thin-shell meta roots 与 truth-family submodules 现已是正式 verification topology；后续若继续拆分，只能延续 same-story inward decomposition，而不能重新长出 second governance story。


## Phase 60 Status Update

- 本 phase **无新增 active kill target**；tooling hotspot 通过 inward decomposition closeout，而不是 file deletion campaign。
- `scripts/check_file_matrix.py` / `tests/meta/test_toolchain_truth.py` 继续保留 formal root 身份；新 sibling modules 只缩窄 ownership，不制造新的 delete folklore。


## Phase 66 Status Update

- 本 phase **无新增 active kill target**；release-target fidelity、adapter-root cleanup 与 focused protocol coverage hardening 都沿现有正式 home 收口，没有再造临时 delete-gated 第三故事线。
- `custom_components/lipro/__init__.py` 的 duplicated runtime-loaded stub block 与 `sensor.py` / `select.py` 的 runtime-only dynamic import folklore 已完成退场，不再保留为 carry-forward delete gate。
- stale release-example / active-route drift 已作为治理真相问题关闭；后续若再变更 release/docs/current-story，只允许沿现有 authority chain 更新，不得重新创造临时 cleanup backlog。


## Phase 68 Status Update

- 本 phase **无新增 active kill target**；hotspot inward split、MQTT authority 收束与 docs/metadata truth sync 都沿现有正式 home / governance chain 完成，没有制造新的 delete-gated 过渡物。
- `custom_components/lipro/core/telemetry/outcomes.py`、`custom_components/lipro/core/telemetry/json_payloads.py` 与 `custom_components/lipro/control/runtime_access_support.py` 都只是 localized helper seams，不是未来 delete campaign 的权宜故事线。
- docs/current-story drift 已通过 README/docs/manifest/pyproject/meta guards 同轮关闭；后续若再变更 public contract，只允许沿既有 authority chain 同步更新。


## Phase 69 Status Update

- 本 phase **无新增 active kill target**；typed runtime-access wrappers、schedule/protocol service narrowing、checker balance hardening 与 current-story governance freeze 都沿既有正式 home 收口，没有制造新的 delete-gated 过渡物。
- `custom_components/lipro/control/runtime_access_support.py`、`custom_components/lipro/runtime_infra.py` 与 related helper mirrors 继续只承担 localized support seam 身份，不是未来 cleanup campaign 的临时借口。
- `v1.18` archive promotion 已完成；当前无 active milestone route，且不得把 `Phase 70` 结果回退成 planned residual。


## Phase 76 Status Update

- 本 phase **无新增 active kill target**；治理真相修复采用 contract/block/guard 收口，而不是 file-level cleanup campaign。
- historical milestone prose 继续保留 archive/audit 身份；被关闭的是 parser-visible shadow，而不是历史证据本身。

## Phase 77 Status Update

- 本 phase **无新增 active kill target**；shared helper 已回到诚实 helper home，focused bootstrap smoke 已冻结成长期 no-growth concern。
- `test_governance_closeout_guards.py` 不再承担跨 suite helper API 身份；被关闭的是误导性 topology，而不是 closeout smoke anchor。

## Phase 78 Status Update

- 本 phase **无新增 active kill target**；closeout-ready route handoff 只前推 live truth、fast-path smoke 与 review ledgers，不新增 file-level delete gate。
- 后续唯一正式下一步是 `$gsd-complete-milestone v1.21`；不得再以“补 current story”为名重开隐性 phase。

## Phase 79 Status Update

- 本 phase **无新增 active kill target**；治理工具链热点拆分与 release-contract topicization 只收口维护性与 current-truth honesty，不新增 file-level delete gate。
- 后续唯一正式下一步是 `$gsd-complete-milestone v1.21`；不得再以“补 current story”或“临时 topic shell”为名重开隐性 phase。

## Phase 80 Status Update

- 本 phase **无新增 active kill target**；治理 typing closure 与 giant-test topicization 只收口维护性与 current-truth honesty，不新增 file-level delete gate。
- 后续唯一正式下一步是 `$gsd-complete-milestone v1.21`；不得再以“补 mypy”或“补测试拆分”为名重开隐性 phase。



## Phase 81 Status Update

- 本 phase **无新增 active kill target**；public first-hop convergence 与 contributor change-map publication 收口的是 docs-entry drift，而不是 file-level delete campaign。
- maintainer appendix 继续保持 maintainer-only 身份；后续 docs 优化只能沿现有入口矩阵同步，不得制造临时 route shell。

## Phase 82 Status Update

- 本 phase **无新增 active kill target**；release route / archived evidence chain formalization 通过 docs / guards 收口，不需要新增 delete-gated 过渡物。
- latest archived pointer 与 milestone audit 继续保持 historical-only 身份；后续 release 工作只能沿既有 maintainer route 加强验证，不得回流平行 release folklore。

## Phase 83 Status Update

- 本 phase **无新增 active kill target**；evidence-first intake 与 stewardship contract 收口的是模板 / 文档 / registry drift，而不是 file-level cleanup campaign。
- `.github/CODEOWNERS` 继续是唯一 owner / custody truth source；issue / PR / support / security surfaces 只能投影它，不能暗示 hidden delegate、backup maintainer 或 public security fallback。

## Phase 84 Status Update

- 本 phase **无新增 active kill target**；focused guard coverage 与 current-route closeout-ready freeze 收口的是 governance truth / docs-entry / promoted-evidence drift，而不是 file-level cleanup campaign。
- `v1.22` 当前已进入 `Phase 84 complete / closeout-ready`；后续唯一正式下一步是 `$gsd-new-milestone`，不得再以“补 guard”“补 starter truth”之名重开隐性 phase。

## v1.21 Milestone Closeout Status

- 本次里程碑 closeout **无新增 active kill target**；被关闭的是隐式 active-route story，而不是任何需要回头删除的临时壳层。
- 后续唯一正式下一步是 `$gsd-new-milestone`；不得再以“补 closeout story”“补 archive pointer”或“补 final governance topicization”为名重开隐性 phase。

## Phase 85 Status Update

- 本 phase **无新增 file-level kill target**；repo-wide terminal audit 冻结的是 verdict / routing truth，不是新的 file-delete campaign。
- `custom_components/lipro/core/anonymous_share/share_client.py` 的 `_safe_read_json()` alias 与 `submit_share_payload()` bool shim 已在 `Phase 86` 关闭；文件本身继续是正式 anonymous-share worker client home。
- `custom_components/lipro/runtime_infra.py` 已在 `Phase 86` 完成 inward split closeout；giant assurance carriers（`tests/core/api/test_api_diagnostics_service.py`、`tests/core/api/test_protocol_contract_matrix.py`、`tests/core/coordinator/runtime/test_mqtt_runtime.py`）继续只允许沿 `Phase 87` 做 topicization，不得被叙述成未来 file-level kill target。


## Phase 90 Status Update

- 本 phase **无新增 active kill target**；hotspot routing freeze 纠偏的是 ownership / delete-gate wording，而不是启动新的 file-level delete campaign。
- `custom_components/lipro/core/coordinator/runtime/command_runtime.py`、`custom_components/lipro/core/api/rest_facade.py`、`custom_components/lipro/core/api/request_policy.py`、`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` 与 `custom_components/lipro/core/anonymous_share/manager.py` 在本 phase 被明确确认为 formal homes，不得再被写成 future kill target。
- `custom_components/lipro/__init__.py`、`custom_components/lipro/control/runtime_access.py`、`custom_components/lipro/entities/base.py` 与 `custom_components/lipro/entities/firmware_update.py` 继续只承担 protected thin shell / projection 身份；后续 phase 若继续收口，只允许 inward split / typed narrowing，不得靠 delete folklore 重新叙述这些 outward shells。


## Phase 91 Status Update

- 本 phase **无新增 active kill target**；typed-boundary hardening 与 protocol/runtime canonicalization 是 inward contract closure，不是 file-level delete campaign。
- `custom_components/lipro/core/protocol/protocol_facade_rest_methods.py`、`custom_components/lipro/core/protocol/rest_port.py`、`custom_components/lipro/runtime_types.py` 与 `custom_components/lipro/core/coordinator/types.py` 现已明确写为 formal typed-boundary / live-canonicalization homes，不得被重新叙述成 temporary kill target。
- `custom_components/lipro/__init__.py`、`custom_components/lipro/control/runtime_access.py`、`custom_components/lipro/entities/base.py` 与 `custom_components/lipro/entities/firmware_update.py` 继续保持 protected thin shell / projection posture；Phase 91 只允许 typed narrowing，不允许 orchestration 回流。


## Phase 92 Status Update

- 无新增 active kill target；Phase 92 是 contract convergence / topicization closeout，不是隐性 delete campaign。
- 任何后续想删除的 localized sanitizer / topical shell，仍必须给出显式 kill gate 与 evidence pointer，不能 retroactively 借本 phase 背书。


## Phase 93 Status Update

- 无新增 active kill target；Phase 93 是 assurance freeze / closeout proof，相当于把前序收口结果转成可持续验证的 current-route truth，而不是新一轮 delete campaign。
- 任何未来的测试重拆、治理脚本重生或 closeout 资产清理，仍必须显式给出 kill gate 与证据链，不能借“只是派生文档”之名绕过治理。
## Phase 98 Status Update

- 本 phase **无新增 active kill target**；被关闭的是 `outlet_power` legacy side-car fallback carry-forward 叙事，而不是启动新的 file-level delete campaign。
- `Phase 98` 现在作为 completed predecessor 保留；其 closeout evidence 继续存在，但不再承担 current-route selector 职责。

## Phase 99 Status Update

- 本 phase **无新增 active kill target**；`status_fallback_support.py` 与 `command_runtime_support.py` 代表的是 inward decomposition，不是新的 file-level delete campaign。
- `custom_components/lipro/core/api/status_fallback.py` 与 `custom_components/lipro/core/coordinator/runtime/command_runtime.py` 继续冻结为 formal homes；remaining large formal homes 仍只允许 inward split / typed narrowing，不得被 retroactively 写成 future kill target。

## Phase 100 Status Update

- 本 phase **无新增 active kill target**；`schedule_service_support.py` 与 `mqtt_runtime_support.py` 代表的是 inward decomposition，不是新的 file-level delete campaign。
- `custom_components/lipro/core/api/schedule_service.py` 与 `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` 继续冻结为 formal homes；remaining large formal homes 仍只允许 inward split / typed narrowing，不得被 retroactively 写成 future kill target。

## Phase 101 Status Update

- 本 phase **无新增 active kill target**；`manager_submission.py`、`manager_support.py`、`rest_decoder_support.py` 与 `mqtt_api_service.py` 代表的是 inward decomposition / boundary truth cleanup，不是新的 file-level delete campaign。
- `custom_components/lipro/core/anonymous_share/manager.py` 与 `custom_components/lipro/core/protocol/boundary/rest_decoder.py` 继续冻结为 formal homes；remaining large formal homes 仍只允许 inward split / typed narrowing，不得被 retroactively 写成 future kill target。

## Phase 103 Status Update

- `custom_components/lipro/__init__.py` 不再承担 lazy-load / entry-auth giant-root 叙事；对应支撑已下沉到 `control/entry_root_support.py`。
- `tests/conftest.py` 不再继续吸附 topicized collection hooks 与 `_CoordinatorDouble` 细节；delete gate 改为防止这些职责回流到 giant fixture root。

## Phase 104 Status Update

- `custom_components/lipro/control/service_router_handlers.py` 不再继续作为 mixed family hotspot；它现在只保留 family index / import surface 角色。
- `custom_components/lipro/core/coordinator/runtime/command_runtime.py` 继续冻结为 formal orchestration home；outcome bookkeeping / reauth handling 的 delete gate 改为防止这些职责重新长回正式 root。

## Phase 102 Status Update

- 本 phase **无新增 active kill target**；它处理的是 archived-only governance/docs/evidence hardening，不是新的 file-level delete campaign。
- latest archived pointer、verification stratification 与 docs-first continuity wording 必须继续沿现有 maintainer route / planning governance truth 演进，不得被 retroactively 写成“未来删除后就没问题”的临时 folklore。
