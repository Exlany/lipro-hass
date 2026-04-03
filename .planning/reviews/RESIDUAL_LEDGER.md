# Residual Ledger

## Current Residual Posture

- `v1.43` 已显式保持为 active milestone route；当前 closeout verdict 已承认 `Phase 141 complete / closeout-ready`，不再留下 planning-ready 幻觉。
- `Phase 141` 未新增 active residual family：service-router seam narrowing、entry-root explicit factory wiring、runtime contract inward decomposition、device aggregate/runtime side-car hardening 与 governance closeout sync 现已收束为同一 closeout bundle。
- 当前 active residual posture = `zero active residual family`；若未来 reopen follow-up，必须登记新 family / owner / exit condition，而不是复用已关闭的 `Phase 141` route。

## Phase 141 Residual Delta

- `Phase 141` 未新增 active residual family；本轮完成的是 service-router seam narrowing、entry-root explicit factory wiring、runtime contract inward decomposition、device aggregate/runtime side-car hardening 与 governance closeout sync 的一次性收口。
- `runtime_types.py` 继续保持 shared runtime contract 的唯一 sanctioned outward root；control/service/device 本地 projections 仅承担 inward helper 身份。
- `LiproDevice` outward façade 未改名、未改 public call shape；MQTT freshness 与 outlet-power bookkeeping 已回收到 `device_runtime.py`，`diagnostics_surface.py` 继续只消费 formal primitive。

## Phase 140 Residual Delta

- `Phase 140` 未新增 active residual family；本轮 formalize 的是 governance/docs freshness 收口，而不是新的 structural residual campaign。
- stale verification lane、`CHANGELOG.md` public-summary scope、runbook access-mode wording 与 route/ledger sync 现已进入 closed bundle，不再作为 silent carry-forward 漂浮；`tests/meta/test_phase140_governance_source_freshness_guards.py` 负责冻结这条 freshness guard chain。
- nested worktree 下 `gsd-tools` root detection 继续不作为 live truth authority；route proof 以 selector family、registry、focused guards 与 `140-*` phase assets 为准。
- sanctioned follow-up 已在 `Phase 141` 被完整消费并收口：`service_router`、`runtime_types.py`、`core/device/device.py` 与 `entry_root_support.py` 的 narrowing owner 现已回流到 closeout bundle，不再保留 planning-ready carry-forward 幻觉。

## Phase 139 Residual Delta

- `Phase 139` 未新增 active residual family；canonical roots 仍是 `custom_components/lipro/core/api/rest_facade.py` 与 `custom_components/lipro/core/protocol/rest_port.py`。
- schedule `group_id` forwarding honesty 已进入 closed bundle，不再作为“后续某轮也许要查”的 silent behavioral carry-forward。
- 当前作为 predecessor 保留的是 Phase 139 的 protocol/root second-pass slimming 闭环，而不是新的 protocol/root residual；governance/docs freshness 已在 Phase 140 关闭。

## Active Residual Families

| Family | Current example | Owner phase | Residual owner | Exit condition |
|--------|------------------|-------------|----------------|----------------|
_None currently registered._

> **Phase 88 freeze note:** 这里的 zero-active posture 是显式 closeout verdict，而不是尚未清点完成的空白。若未来出现新 residual，必须以新的 family 重新登记 owner、exit condition 与 evidence。


## Phase 132 Residual Delta

- `Phase 132` 未新增 active residual family；本轮完成的是 current selector、archive/history boundary、developer/runbook first-hop 与 route-marker helper ownership 的收口，而不是新的 lingering exception。
- `v1.38` closeout 后，remaining concern 只保留为 future milestone 显式 reopen 的 sanctioned hotspot breadth（如 `runtime_types.py`、`request_policy.py`、`dispatch.py`、`auth/manager.py`、`firmware_update.py`）；它们不是 active residual family。
- archive-era governance mega-suite topicization 仍有继续减压空间，但 `Phase 132` 已把 current route / latest archived pointer / promoted-asset ownership 的职责混装消除，不再留下 live-route residual。

## Phase 131 Residual Delta

- `Phase 131` 未新增 active residual family；本轮收口的是 repo-wide terminal audit、docs/toolchain/governance selector truth 与 closeout evidence chain，而不是新的 lingering exception。
- repo-external continuity / private fallback 仍被保留为 honest governance boundary：仓内文档、registry 与 runbook 已冻结 single-maintainer / no-hidden-delegate / no-guaranteed-non-GitHub-private-fallback posture，但它们不是 active residual family。
- sanctioned hotspot breadth 继续作为 future optimization candidate（如 `rest_facade.py`、`runtime_types.py`、`request_policy.py`、`dispatch.py`、`auth/manager.py`、`firmware_update.py`），当前不被误登记为 residual delete campaign。

## Phase 130 Residual Delta

- `Phase 130` 未新增 active residual family；`command_runtime.py` 与 `entities/firmware_update.py` 的 sanctioned hotspot 已继续 inward slimming，并通过 focused runtime/firmware/OTA/meta proofs 冻结住当前收口结果。
- `command_runtime.py` 继续保持 formal runtime orchestration home，`firmware_update.py` 继续保持 protected thin OTA projection shell；新增 support helpers 只是 inward seam，不是新的 residual backdoor。
- 当前 remaining live concern 已收束到 `Phase 131`：repo-wide terminal audit closeout、final report synthesis 与 governance continuity decision boundary 仍待最终 codify；`131-CONTEXT.md` / `131-RESEARCH.md` 已就位，route truth 不再停在 Phase 130 placeholder。

## Phase 129 Residual Delta

- `Phase 129` 未新增 active residual family；`rest_facade.py` 与 `status_fallback_support.py` 的 sanctioned hotspot 已继续 inward slimming，并通过 focused regressions / meta guards 冻结住当前收口结果。
- 当前 remaining live concern 已显式前推到 `Phase 130` 与 `Phase 131`：`command_runtime.py` / `entities/firmware_update.py` 的 multi-topic hotspot 仍待继续 inward split，repo-wide terminal audit / continuity decision boundary 仍待 final closeout。
- queued `Phase 130` / `Phase 131` 目录已登记，current-route inventory 不再因为缺少 phase 目录而失真。

## Phase 128 Residual Delta

- `Phase 128` 未新增 active residual family；本轮是把 readiness honesty、coverage baseline diff、benchmark smoke 与 continuity limits 正式 codify 为 closeout-ready governance contract。
- 仍未闭环的 repo-external 现实限制（documented delegate 仍不存在、non-GitHub private fallback 仍未建立）已被诚实写入 docs / templates / registry，而不是被伪装成仓内已解决 residual。
- 更深层 architecture / stewardship debt 已明确移交后续 milestone；`Phase 128` 自身没有留下新的 active residual。

## Phase 127 Residual Delta

- `Phase 127` 未新增 active residual family；`runtime_access` stringly system-health surrogate 与 `runtime_access_support_views.py` reflective narrowing seam 已一起收口。
- `custom_components/lipro/control/runtime_access.py` 继续保持 protected thin runtime read-model home；后续若继续切薄，只允许 inward decomposition / typed narrowing，不得把 runtime internals 重新合法化。
- 当前 remaining live concern 已前移到 `Phase 128`：open-source readiness honesty、benchmark / coverage diff gate 与 single-maintainer continuity / security fallback contract。

## Phase 126 Residual Delta

- `Phase 126` 未新增 active residual family；diagnostics helper shell thinning 只是把 mechanics 指回 canonical helper home，没有创造新的 lingering exception。
- `services/diagnostics/helpers.py` 仍保留 outward stable helper home 身份，但 duplicate capability collector 已删除，不再承担第二套 mechanics truth。
- `Phase 126` 关闭后，remaining hotspot 已显式前推给 `Phase 127` 与 `Phase 128`，没有 orphan residual family 留在当前 route。

## Phase 125 Residual Delta

- `Phase 125` 未新增 active residual family；machine-readable governance current-route truth 已收敛到 `.planning/baseline/GOVERNANCE_REGISTRY.json::planning_route`，selector docs 只保留 projection 身份。
- `runtime_types.py` 继续保持 outward formal home，但 `ScheduleMeshDeviceLike`、`CommandProperties` 与 `DeviceRefreshServiceLike` 的 shadow duplicates 已被消解；当前剩余风险是 breadth，而不是 duplicated truth。
- `config_flow.py` / `flow/step_handlers.py` / `entry_auth.py` 已进一步删掉 public pass-through wrapper 与单次中转 helper；本轮没有创造新的 auth/flow lingering exception。

## Phase 124 Residual Delta

- `Phase 124` 未新增 active residual family：auth-flow-schedule carry-forward 已被收口到正式 homes，而不是被登记为新的 lingering exception。
- stale `biz_id` / `remember_password_hash` revival 已关闭；`entry_auth.py` 现在承担 persisted auth-seed single-source truth，不再由 flow projection 与 token callback 各自解释。
- schedule direct-call normalization / result typing 已收敛到 `services/contracts.py`，因此没有新的 schedule residual family 需要继续登记。


## Phase 110 Residual Delta

- `Phase 110` 未新增 active residual family：snapshot helper inward split、governance guards 与 evidence chain 收口均已落入 formal homes。
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` 继续保持唯一 outward snapshot orchestration home；`snapshot_support.py` 仅是 inward helper，不是 residual backdoor。
- `Phase 107` / `108` / `109` 继续保持 predecessor-visible evidence；`.planning/reviews/V1_30_EVIDENCE_INDEX.md` 与 `.planning/v1.30-MILESTONE-AUDIT.md` 已接入 closeout chain。

## Phase 109 Residual Delta

- `Phase 109` 没有创造新的无主 active residual family；anonymous-share manager hotspot 已被正式收口为 predecessor-visible完成态。
- `core/coordinator/runtime/device/snapshot.py` 仍是唯一 live follow-up，并已显式路由到 `Phase 110`，属于有 owner 的 continuation，而不是 orphan residual。
- `Phase 108` predecessor bundle、`Phase 107` predecessor bundle、`Phase 105` promoted closeout bundle 与 `v1.29` latest archived baseline 继续保持可审计可见性，不会被当前 route 误清理或误回写。

## Phase 108 Residual Delta

- `Phase 108` 没有创造新的无主 active residual family；MQTT transport/runtime private-state reach-through 现作为 completed predecessor bundle 保持可见性，而不再承担 current-route owner 身份。
- `Phase 109` 已接管 current-route hotspot convergence；当前只剩 `Phase 110` 继续承担 snapshot surface reduction / milestone closeout，而不是把 predecessor proof 回流成 residual family。
- `Phase 107` predecessor bundle、`Phase 105` promoted closeout bundle 与 `v1.29` latest archived baseline 继续保持可审计可见性，不会被当前 route 误清理或误回写。

## Phase 107 Residual Delta

- `Phase 107` 没有创造新的无主 active residual family；REST/auth/status hotspot 现在作为 completed predecessor bundle 保持可见性，不再承担 live current-route selector 身份。
- `Phase 109` 已接管 current-route hotspot convergence；`Phase 110` 继续承担 remaining continuation scope，而不是把 predecessor proof 回流成 residual family。
- `v1.29` latest archived baseline、`Phase 105` promoted closeout bundle 与 `Phase 103/104` predecessor bundles 继续保持可审计可见性，不会被当前 route 误清理或误回写。

## Phase 105 Residual Delta

- `v1.29` archived closeout 继续保持 zero-active archived posture；`Phase 105` 现在承担的是 latest-archived closeout visibility，而不是 current-route selector。
- `tests/meta/governance_followup_route_specs.py`、`scripts/check_file_matrix_registry_shared.py` 与 `scripts/check_file_matrix_registry_classifiers.py` 继续承担共享规则真源；它们是 formal governance truth，不是新的 residual family。
- `Phase 103` / `Phase 104` predecessor bundles 继续保留可见性，但不会重新升级为 active residual；`v1.28` closeout bundle 继续保持 pull-only previous archived baseline 身份。

## Phase 85 Audit-Routed Carry-Forward

> 下列条目是 `v1.23 / Phase 85` repo-wide terminal audit 明确登记的 carry-forward，并非重新打开已关闭 residual family。

| Finding | Scope | Verdict | Owner phase | Exit condition | Evidence |
|--------|-------|---------|-------------|----------------|----------|
| giant assurance carriers (`test_api_diagnostics_service.py`, `test_protocol_contract_matrix.py`, `test_mqtt_runtime.py`) | Assurance | closed in Phase 87 | Phase 87 | concern-local suites、thin roots 与 focused no-regrowth guards 已落地 | `.planning/reviews/V1_23_TERMINAL_AUDIT.md`; `.planning/phases/87-assurance-hotspot-decomposition-and-no-regrowth-guards/{87-01-SUMMARY.md,87-02-SUMMARY.md,87-03-SUMMARY.md}`; `tests/meta/test_phase87_assurance_hotspot_guards.py` |

- `ShareWorkerClient` compat submit / JSON aliases 已在 `Phase 86` 关闭：`_safe_read_json()` alias 与 bool `submit_share_payload()` shim 已删除；production/tests 只承认 `safe_read_json()` 与 `submit_share_payload_with_outcome()`。
- `runtime_infra.py` orchestration hotspot 已在 `Phase 86` 关闭：`runtime_infra.py` 继续是 outward formal home，`runtime_infra_device_registry.py` 仅承担 support-only inward helper 身份。

- `TARGET_TOPOLOGY.md`、`DEPENDENCY_MATRIX.md`、`ARCHITECTURE_POLICY.md` 与 `docs/developer_architecture.md` 的 `Phase 85 close now` 真源同步，已记录在 `.planning/reviews/V1_23_TERMINAL_AUDIT.md`；它们属于当前 phase 的 close-now truth sync，不是新的 active residual family。
- `.planning/reviews/V1_22_EVIDENCE_INDEX.md` 与 `.planning/v1.22-MILESTONE-AUDIT.md` 继续是 explicitly-keep historical evidence；后续 phase 只能 pull 其结论，不得把 archived-only truth 回写成 active debt。
- `Phase 85`~`87` 的 closeout summaries 现已由 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` allowlist 明确提升为长期治理证据；本节继续只承担 historical carry-forward closure 说明。

## Closed Residual Families

- `Runtime-access mixed helper cluster` 已在 Phase 70 关闭：`custom_components/lipro/control/runtime_access_support.py` 已 inward split 为 `runtime_access_support_{members,telemetry,views,devices}.py`，而 `runtime_access.py` 继续保持唯一 outward runtime read home。

- `Anonymous-share / OTA duplicated query-selection choreography` 已在 Phase 70 关闭：`share_client_flows.py` 现仅保留薄 orchestration shell，`share_client_{ports,refresh,submit}.py` 与 `core/ota/query_support.py` 吸收了 shared submit/refresh/query truth，`firmware_update.py` 也不再保留 entity-local OTA arbitration choreography。

- `Archive-vs-current version truth drift and governance mega-test sprawl` 已在 Phase 70 关闭：`test_version_sync.py` 不再读取 archived phase/evidence 内容，`governance_contract_helpers.py` 与 topicized current-milestone/archive suites 继续把 latest-evidence pointer 与 active-route truth 固定到 current docs / runbook / registry。

- `Runtime-access reflective probing` 已在 Phase 65 关闭：`custom_components/lipro/control/runtime_access_support.py` 现只承认显式 instance/class members 与 typed runtime views，`MagicMock` 幽灵成员不再定义生产真相。

- `Runtime identity alias extras sidecar` 已在 Phase 65 关闭：`custom_components/lipro/core/coordinator/runtime/device/snapshot.py` 现把 alias 真相投影为 `FetchedDeviceSnapshot.identity_aliases_by_serial`，`state/index.py` 也不再读取 `device.extra_data["identity_aliases"]`。

- `Anonymous-share bool-only submit bridge` 已在 Phase 65 关闭：`custom_components/lipro/core/anonymous_share/{manager.py,manager_submission.py}` 现统一走 `OperationOutcome` submit contract，aggregate/scoped submit 也不再以 bool-only 路径充当主真相。

- `Command-result stringly-typed outcome contract` 已在 Phase 57 关闭：`custom_components/lipro/core/command/result_policy.py` / `result.py` 现已共享 typed state / verification / failure-reason vocabulary，runtime sender 与 diagnostics `query_command_result` response typing 也不再依赖 scattered raw strings。

- `Generic backoff helper leak` 已在 Phase 56 关闭：`compute_exponential_retry_wait_time()` 现已迁到 `custom_components/lipro/core/utils/backoff.py`，command/runtime/MQTT callers 不再从 `request_policy.py` 取用 generic helper，而 `RequestPolicy` 只继续拥有 API-local `429` / busy / pacing truth；它也是被显式 carry-forward 到 `Phase 56+` 的唯一 helper-home residual，现已完成 closeout。

- `External-boundary advisory naming` 已在 Phase 38 关闭：firmware external-boundary 现统一为 local trust-root / remote advisory 语义；历史资产文件名 `firmware_support_manifest.json` 被保留，但不再被表述成 advisory truth。

- `Legacy public names` 已在 Phase 12 关闭：`core.api.LiproClient` compat shell 已删除，legacy constructor name 不再作为生产 public surface 存在。
- `Capability compat public name` 已在 Phase 12 关闭：`DeviceCapabilities` 与 `custom_components/lipro/core/device/capabilities.py` 已删除。
- `Domain dynamic delegation` 已在 Phase 13 关闭：`LiproDevice.__getattr__` / `DeviceState.__getattr__` 已移除，`custom_components/lipro/core/device/device_delegation.py` 已删除。
- `Control-plane scatter` 已在 Phase 11 关闭：formal router、runtime locator 与 HA adapter 边界已固定，control plane 不再以散落 helper / wiring 叙事存在。
- `Legacy service wiring carrier` 已在 Phase 11 关闭：`custom_components/lipro/services/wiring.py` 已正式删除，control-plane formal router truth 收口到 `custom_components/lipro/control/service_router.py`。
- `Private runtime auth seam` 已在 Phase 5 关闭：`custom_components/lipro/services/execution.py` 只保留正式 service execution facade 身份，不再作为 active residual family。
- `API aggregate endpoint mixin` 已在 Phase 11 关闭：`custom_components/lipro/core/api/endpoints/__init__.py` 不再导出 `_ClientEndpointsMixin`，active residual 只剩 endpoint helper-class-level demixin cleanup。

- `API compat wrappers` 已在 Phase 17 关闭：`power_service.py` 与 outlet-power runtime/protocol formal path 只承认 explicit row/list contract，synthetic `{"data": rows}` envelope 已退场。

- `API mixin inheritance` 已在 Phase 17 关闭：`_ClientBase`、`_ClientPacingMixin`、`_ClientAuthRecoveryMixin`、`_ClientTransportMixin` 与 endpoint legacy mixin family 已完成 physical retirement 或 truthful demotion。

- `Split-root protocol surfaces` 已在 Phase 17 关闭：legacy `LiproMqttClient` naming 已退场，`MqttTransport` 仅保留为 localized concrete transport。

- `Auth/session compat projection` 已在 Phase 17 关闭：token persistence 只消费 `AuthSessionSnapshot`，`get_auth_data()` compat projection 已删除。

- `Protocol-boundary family coverage` 已在 Phase 20 关闭：`rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 现全部完成 registry-backed boundary formalization，不再保留为 active residual family。

- `Replay scenario coverage` 已在 Phase 21 关闭：remaining families 现已获得 explicit replay / evidence assurance coverage，不再保留 v1.1 de-scope carry-forward 叙事。

- `Release-target / active-route freshness drift` 已在 Phase 66 关闭：`.github/workflows/{ci,release}.yml`、`README*`、`docs/README.md`、baseline/review docs 与 `tests/meta/test_governance_release_contract.py` 现在共同承认同一 tagged ref / current-story truth。

- `Adapter-root duplicated stub and dynamic-import folklore` 已在 Phase 66 关闭：`custom_components/lipro/__init__.py` 删除 duplicated Protocol stub block，`sensor.py` / `select.py` 改为显式导入 `entities.base.LiproEntity` formal home。

- `Protocol seam focused-coverage gap` 已在 Phase 66 关闭：`RestTransportExecutor`、`CoordinatorProtocolService`、`LiproProtocolFacade` 与 `LiproMqttFacade` 现拥有 dedicated focused regression suites，不再主要依赖 mega-matrix tests 才能发现 seam 破坏。

- `MQTT authority ambiguity` 已在 Phase 68 关闭：`custom_components/lipro/core/mqtt/topics.py` 现只保留 boundary-backed adapter 身份，`custom_components/lipro/core/protocol/boundary/mqtt_decoder.py` 继续是唯一 canonical MQTT topic/payload decode authority。

- `Hotspot regrowth risk in telemetry/share/runtime/docs contracts` 已在 Phase 68 关闭：`telemetry/models.py`、`share_client_flows.py`、`diagnostics_api_ota.py`、`runtime_infra.py` 与 docs/metadata surfaces 已完成 inward split / truth sync，并由 focused guards + repo-wide gates 冻结。

## Phase 66 Residual Delta

- 无新增 active residual family。
- 本 phase 显式关闭了 stale release-example / active-route drift、adapter-root duplicated stub folklore 与 protocol seam focused-coverage gap。
- 若后续 closeout audit 再发现问题，只允许以新的 explicit residual family 重新登记，不得借 archive/docs wording 静默回流。

## Rules

- 新发现的 residual 必须登记，不能只在对话中提到。
- 每条 residual 至少要给出 **当前样本、owner、exit condition**，否则不算正式登记。
- 任何 residual 若进入第二个 phase 仍未收敛，必须解释为何继续存在。
- compat / mixin / legacy public-name residual 只允许存在于显式 compat shell / adapters 中，不得继续散落在正式 public surface 与业务逻辑内部。
- 本账本允许保留 legacy `Client` / `Mixin` / compat symbol 名称，但仅用于 archive / delete-gate / symbol-identity 说明；它们不得回流为当前架构术语。

## Phase 01 Closeout Review

- 已复核当前 residual families 与 Phase 01 baseline 的关系：本阶段只锁定 protocol boundary truth，不试图提前消除 residual。
- 本次**无新增 residual family**；canonical snapshots 与 immutable constraints 没有引入新的桥接层或临时兼容结构。
- `API compat wrappers` 与 `API mixin inheritance` 继续由 Phase 2 负责清理；Phase 01 仅为其提供不可漂移的 contract 输入边界。

## Phase 02 / `02-01` Residual Delta

- 为 `API compat wrappers`、`API mixin inheritance` 补齐了明确 owner 与 file-level current examples。
- 新增 `Legacy public names` residual family，用于约束 `LiproClient` 作为 public root name 的过渡存在方式。
- 本计划只做登记，不关闭 residual；真正清退动作留给 `02-02` ~ `02-04`。


## Phase 02 / `02-04` Residual Delta

- `API mixin inheritance` 已从正式生产主链中退出，但仍以 helper-test / patch seam / typing anchor 的形式受控残留。
- `Legacy public names` 已完成 public-surface demotion：正式叙事与内部类型依赖改为 `LiproRestFacade`，保留 `LiproClient` 只为过渡工厂与兼容包装。
- `API compat wrappers` 暂未删除；其删除门槛明确交给 direct consumer migration / unified protocol root 相位继续完成。

## Phase 02.5 / `02.5-01` Residual Delta

- 新增 `Split-root protocol surfaces` residual family，专门约束 `REST root + MQTT root` 双入口语义。
- `LiproClient` 的 public-root demotion 已完成，但 `LiproMqttClient` 与 runtime-facing protocol entry 仍需在 `Phase 2.5` 继续收口。
- 后续所有 protocol-plane 清理动作都必须以 `LiproProtocolFacade` 为唯一 exit target。

## Phase 02.5 / `02.5-02 ~ 02.5-03` Residual Delta

- `Split-root protocol surfaces` 已从生产主链中清出：runtime/control 构造点、MQTT lifecycle 与 coordinator-facing seams 都只承认 `LiproProtocolFacade` 为正式协议根。
- `Legacy public names` residual 继续存在，但已缩窄为显式 compat alias / wrapper：`LiproClient` 与 `LiproMqttClient` 不再承担 formal-root 语义，只剩测试/导出/过渡层使用。
- `API compat wrappers` 仍未删除；其后续退出条件保持不变，但 unified root 已把 direct consumer 迁移主线切换完成。


## Phase 02.6 Residual Delta

- 新增 `External-boundary advisory naming` residual family：authority 已被矫正，但 remote advisory 与 generated payload 的部分命名仍需在 cleanup phase 统一为更诚实的术语。
- external-boundary 真相已经从实现代码迁出到 authority matrix / inventory / fixtures / meta guards；因此 Phase 2.6 不再保留“隐式 boundary folklore”这类未登记残留。

## Phase 03 Residual Delta

- `Control-plane scatter` residual 已从生产主链显著缩小：正式 owner 已迁入 `custom_components/lipro/control/`，剩余问题集中在 legacy carrier 与少量 private seam。
- 本 phase 曾新增 `Legacy service wiring carrier` residual family；该 residual 已在 Phase 11 随 `services/wiring.py` 删除而关闭。
- `custom_components/lipro/services/execution.py` 的私有 auth hook seam 已在 Phase 5 关闭：service execution 现在只消费正式 `auth_service` contract。


## Phase 04 Residual Delta

- `Capability duplication` 已从生产主链关闭：platform/entity/device/state 的正式能力判断现在都围绕 canonical capability truth。
- `DeviceCapabilities` residual 继续存在，但已被明确缩减为旧 public-name compat alias；它不再定义任何正式 capability 语义。


## Phase 05 Residual Delta

- `Private runtime auth seam` 已关闭：`custom_components/lipro/services/execution.py` 不再依赖 coordinator 私有 auth hook，而只通过正式 `auth_service` contract 获取认证上下文。
- runtime signal ports 已 formalize；`connect-status` shadow chain 未被 resurrect，相关 dead modules 已转入 Phase 7 治理 closeout。


## Phase 07.1 / `07.1-03` Residual Delta

- 新增 `Protocol-boundary family coverage` residual family：`rest.mqtt-config@v1` 与 `mqtt.properties@v1` 已接入 registry，但 inventory 中其余 family 仍待收口或裁决。
- `tests/fixtures/protocol_boundary/` 已建立 replay-ready evidence family；因此后续 phase 不得绕过这些 fixtures 另造 decoder/replay 真源。
- 本计划没有新增 compat shell；残留只描述尚未完成 family coverage，而不是允许 boundary truth 重新散落。

## Phase 07.2 Residual Delta

- 本 phase **无新增 residual family**；`ARCHITECTURE_POLICY.md` 只是把既有 baseline truth formalize 成单一 enforcement baseline，而不是引入第二真源。
- future `observer-only surface` / `assurance-only boundary consumer` 例外必须先回写 `ARCHITECTURE_POLICY.md` 与 baseline docs，再进入 helper / script / tests allowlist。
- targeted regression bans 只封堵已知 backdoor / export / property regression，不构成新的正式 public surface 或新 root。

## Phase 07.3 / `07.3-01` Residual Delta

- 新增 `Telemetry consumer convergence` residual family：本计划只完成 exporter formal home、contracts、ports 与 control bridge，consumer 全量收口明确留给 `07.3-02`。
- 本计划**无新增 compat shell**；`core/telemetry/*` 与 `control/telemetry_surface.py` 是正式 observer-only surface，不得被解释为第二条 runtime/control 主链。
- 后续 replay / evidence phases 只能 pull `07.3` exporter truth；若需要新增 sink/collector，必须先复用现有 contracts，而不是另立 telemetry 真源。

## Phase 07.3 / `07.3-02` Residual Delta

- `Telemetry consumer convergence` residual family 已关闭：diagnostics / system health / developer / CI sinks 的生产路径现在都统一 pull exporter truth。
- developer report 收集链已切到 exporter-only truth；legacy `build_developer_report()` compat / test seam 已移除。
- 本计划**无新增 compat shell**；`07.4` replay harness 与 `08` evidence pack 只能继续 pull `07.3` exporter truth，不能平行定义第二套 telemetry schema。

## Phase 07.4 / `07.4-03` Residual Delta

- 新增 `Replay scenario coverage` residual family：当前 replay harness 已 formalize，但仍只覆盖 representative `rest.mqtt-config@v1` 与 `mqtt.properties@v1` 场景；其余 replay-worthy family 留给 `07.5` 做 expand / de-scope 裁决。
- `tests/harness/protocol/`、`tests/fixtures/protocol_replay/` 与 replay run summary 已形成 assurance-only 正式家园；后续 phase 只能 pull 它们，不得重新长出第二套 simulator truth。
- 本 phase **无新增 compat shell**；replay 只是 assurance consumer，不构成新的 protocol/runtime root。

## Phase 07.5 Residual Delta

- `Replay scenario coverage` 已完成 closeout arbitration：v1.1 只正式保留 representative `rest.mqtt-config@v1` 与 `mqtt.properties@v1` 场景，其余 boundary inventory families 被显式 de-scope，而不是继续以“未来再说”方式悬空。
- `V1_1_EVIDENCE_INDEX.md` 与 `07.5-SUMMARY.md` 只作为 pull-only governance / closeout 指针，不构成新的 production root、simulator root 或 telemetry truth。
- 本 phase **无新增 compat shell**；现有 file-level kill targets 继续以 `KILL_LIST.md` 中既定 delete gate 为准。

## Phase 08 Residual Delta

- 本 phase **无新增 residual family**：AI debug evidence pack 只 pull `07.3 / 07.4 / 07.5` 正式真源，不扩大 replay corpus，也不新建第二套 telemetry / governance truth。
- `entry_ref` / `device_ref` 的报告内稳定、跨报告不可关联策略继续继承 `07.3` exporter 裁决；这属于既有政策的消费，不新增新的隐含残留。
- 本 phase **无新增 compat shell / file-level kill target**；evidence-pack tooling 与导出产物仅作为 assurance-only artifacts 保留。

## Phase 09 Residual Delta

- `LiproProtocolFacade` 与 `LiproMqttFacade` 的 `__getattr__` / `__dir__` 隐式扩面已关闭；formal protocol contract 改为显式 methods/properties，child surface 不再反向定义 root。
- `custom_components/lipro/__init__.py`、`config_flow.py`、`core/__init__.py` 与 `core/mqtt/__init__.py` 的 legacy public-name / compat exports 已关闭；`Legacy public names` residual 已缩窄为 `core.api.LiproClient` 显式 compat shell、`LiproProtocolFacade.get_device_list` compat wrapper，以及 direct transport module / `LiproMqttFacade.raw_client` seam。
- protocol root 的 implicit child-defined surface 已关闭后，`Split-root protocol surfaces` residual 只剩 `raw_client` concrete-transport seam；该 seam 仅作为显式、可计数、可删除的 compat/test seam 存在。
- runtime public surface 已收口：`Coordinator.devices` 改为 read-only mapping，`LiproDevice.outlet_power_info` 成为 outlet power formal primitive，sensor/diagnostics/runtime 统一读取该真源。
- `extra_data["power_info"]` 已退出正式 outlet-power truth 角色，仅设备对象内部保留 legacy read fallback，以承接旧夹具/旧构造。
- 本 phase **未关闭全部 compat residual**：现存 residual 只能继续收窄，不能回流为 formal public surface。

## Phase 10 Residual Delta

- `rest.device-list@v1`、`rest.device-status@v1` 与 `rest.mesh-group-status@v1` 已完成 boundary-first 收口：API drift 应先打在 protocol contract / replay proof，而不是 runtime 或 HA adapter。
- `AuthSessionSnapshot` 已成为 formal auth/session truth；`config_flow.py` 与 `entry_auth.py` 已迁到 auth manager formal contract。`get_auth_data()` fallback 仅为 legacy mocks / older callers 保留，仍属显式 compat seam。
- `custom_components/lipro/core/__init__.py` 不再导出 `Coordinator`；runtime home 继续固定在 `custom_components/lipro/coordinator_entry.py`，`control/runtime_access.py` 成为 control-plane locator。
- remaining active delete-gated compat seams 仍集中在 `core.api.LiproClient`、`LiproProtocolFacade.get_device_list` 与 `LiproMqttFacade.raw_client`；本 phase 未新增新的无 gate compat root。


## Phase 11 Residual Delta

- `custom_components/lipro/control/service_router.py` 已成为真实 formal router implementation home；`control/service_registry.py` 现为正式 registration-table owner，`services/registrations.py` compat shell 已在 Phase 74 删除。
- 仓库内测试已迁移到 `custom_components.lipro.control.service_router`，不再把 `services/wiring.py` 当成 patch-first truth。
- `custom_components/lipro/services/wiring.py` compat shell 已删除，`Legacy service wiring carrier` residual family 已关闭。
- `custom_components/lipro/core/api/endpoints/__init__.py` 不再导出 `_ClientEndpointsMixin`；`API mixin inheritance` residual 现只覆盖 remaining helper mixin / typing anchors。


## Phase 12 Residual Delta

- `core.api.LiproClient` compat shell 已删除；`LiproRestFacade` 成为唯一正式 REST child façade。
- `LiproProtocolFacade.get_device_list` compat wrapper 已删除；device-list canonical contract 固定为 `rest.device-list@v1`。
- `LiproMqttFacade.raw_client` compat seam 已删除；concrete transport 不再通过 protocol façade 暴露。
- `DeviceCapabilities` compat alias 与 `core/device/capabilities.py` 已删除；能力真源固定为 `CapabilityRegistry` / `CapabilitySnapshot`。
- `_ClientBase` 保留为 internal endpoint typing contract，但不再被视为 active public residual 或 compat shell。

## Phase 13 Residual Delta

- `LiproDevice` 与 `DeviceState` 的动态 `__getattr__` 已删除；domain surface 正式改成显式 property / method 集合。
- `custom_components/lipro/core/device/device_delegation.py` 已物理删除；`state_accessors.py` 仅保留显式 helper 角色。
- 本 phase **无新增 residual family**：收口的是既有 domain dynamic delegation，而不是引入新的 compat 层。
- active residual 现主要集中在 `_ClientBase` / `_Client*Mixin` typing/helper spine、`LiproMqttClient` legacy naming 与 helper-level compatibility envelope；hotspot glue 已完成第一次拆分。


## Phase 14 Residual Delta

- 本 phase **无新增 residual family**：`Coordinator` 的 protocol-facing passthrough 已收口到 `CoordinatorProtocolService`，但这不是新的兼容层。
- `ScheduleApiService` 已退出正式 schedule 主链；remaining API residual 继续集中在 `_ClientBase` / helper mixin family 与 helper-level compatibility，而不是 service-loop 回环。
- `custom_components/lipro/core/api/status_fallback.py` 与 `custom_components/lipro/control/developer_router_support.py` 已成为 internal helper homes；`status_service.py` 与 `service_router.py` 保留 public orchestration / handler identity。


## Phase 15 Residual Delta

- 本 phase **无新增 residual family**：收口的是既有 support/governance/tooling truth，而不是引入新的 compat 层。
- `_ClientBase` / helper mixin family 继续仅作为 `core/api` 本地 residual；`FILE_MATRIX` 与 `PUBLIC_SURFACES` 已显式写明 locality / ownership。
- `LiproMqttClient` direct-transport residual 已完成 physical rename closeout；`core/mqtt/transport.py` + package no-export 现为唯一有效故事。
- `coverage_diff.py`、benchmark baseline/threshold lane 与 dev `pip-audit` 现已被裁决为明确工具语义 / governed quality policy，而不是 residual family。

## Phase 16 Residual Delta

- `custom_components/lipro/services/execution.py` 的 coordinator 私有 auth seam 继续保持关闭；Phase 16 只允许把它记为正式 service execution facade，而不是 active residual / kill target。
- 本 phase 完成 second-pass audit 后，remaining residual inventory 仍集中在 `_ClientBase` / helper mixin typing spine、`LiproMqttClient` legacy naming、`get_auth_data()` fallback 与 helper-level compatibility envelope；不再允许无 owner / 无 delete gate / 无 evidence 的 silent carry-forward。
- Final closeout audit (`2026-03-15`) recorded `Any=711`、`except Exception=36`、`type: ignore=12`、dead pytest markers `=0`；remaining hits均落在既有 owner / delete gate 约束内，没有新的无主高风险残留。

| Item | Disposition | Owner | Phase | Delete gate | Evidence |
|------|-------------|-------|-------|-------------|----------|
| `_ClientBase` / `_Client*Mixin` typing spine | 保留为本地 residual | `core/api` | Phase 16 closeout | 当 helper consumers 全部收敛到显式 typed helpers，且不再存在 legacy mixin import 需求时删除 | `custom_components/lipro/core/api/session_state.py`, `.planning/reviews/KILL_LIST.md`, `.planning/baseline/PUBLIC_SURFACES.md` |
| `LiproMqttClient` legacy transport name | 保留为局部 legacy naming residual | `core/mqtt` | Phase 16 closeout | 当 transport-facing tests / imports 不再需要 concrete transport legacy name 时重命名/退场 | `custom_components/lipro/core/mqtt/transport.py`, `.planning/reviews/KILL_LIST.md` |
| `get_auth_data()` fallback in `persist_entry_tokens_if_changed()` | 保留为狭义 compatibility fallback | `entry_auth` | Phase 16 closeout | 当所有调用者 / test doubles 都以 `AuthSessionSnapshot` 为唯一正式契约时删除 | `custom_components/lipro/entry_auth.py`, `tests/core/test_init.py` |
| helper-level compatibility envelope (`power_service.py`) | 保留为低风险 helper-level compatibility | `core/api` | Phase 16 closeout | 当 power payload shape 只剩单一正式 contract，且 outlet-power callers 不再需要旧 shape 容忍时删除 | `custom_components/lipro/core/api/power_service.py`, `custom_components/lipro/core/coordinator/outlet_power.py` |


## Phase 17 Residual Delta

- `_ClientBase` / `_ClientPacingMixin` / `_ClientAuthRecoveryMixin` / `_ClientTransportMixin` 与 endpoint legacy mixin family 已完成 final disposition：production truth 不再把它们当作合法 skeleton / compat spine。
- `MqttTransport` 现为唯一 canonical concrete transport naming；legacy `LiproMqttClient` naming 已退出治理真源、package export 与 production/test mainline。
- `get_auth_data()` compat projection 与 helper-level outlet-power synthetic wrapper 已物理退场；`AuthSessionSnapshot` 与 explicit `OutletPowerInfoRow | list[OutletPowerInfoRow]` 成为唯一正式 typed contract。
- v1.1 remaining active residual 现只保留明确 de-scope / out-of-scope debt：external-boundary advisory naming、boundary family coverage 与 representative replay coverage。

## Phase 18 Residual Delta

- `custom_components/lipro/core/auth/bootstrap.py` 现为正式 host-neutral auth/bootstrap helper home；`config_flow.py` 与 `entry_auth.py` 只复用它装配 protocol/auth collaborators，没有引入新的 control/protocol root。
- `custom_components/lipro/helpers/platform.py` 现为唯一 HA platform projection home；`const/categories.py`、`CapabilitySnapshot`、`CapabilityRegistry`、`LiproDevice` 与 `device_views` 已不再把 HA platform strings 当成 domain truth。
- `ConfigEntryLoginProjection` 明确降格为 HA adapter projection，而不是新的 auth/session truth；`AuthSessionSnapshot` 继续是唯一正式 contract。
- 本 phase **无新增 active residual family / compat shell / file-level kill target**；新增的是更窄的 locality 守卫与 targeted bans，用来阻断旧 projection token 回流。

## Phase 19 Residual Delta

- `custom_components/lipro/headless/boot.py` 与 `tests/harness/headless_consumer.py` 只属于 local proof seam / assurance consumer；它们消费 formal truth，但不构成新的 protocol root、runtime root 或 authority family。
- `config_flow.py` 与 `entry_auth.py` 已统一 inward 到 shared headless boot seam；HA-specific projection、exception mapping 与 token persistence 继续留在 adapter shell，没有回灌到 nucleus。
- `helpers/platform.py` 与各平台 `async_setup_entry()` 现在显式收敛到 thin headless setup shell；`control/runtime_access.py` 仍是 control-plane locator，而不是 platform bridge。
- 本 phase **无新增 active residual family / compat shell / authority no-change exception**；新增的是 second-root / backflow 守卫与 proof-only identity wording。

## Phase 20 Residual Delta

- `Protocol-boundary family coverage` 已完成 closeout：`rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 均已进入正式 boundary family / authority / fixture / guard 主链。
- governance / inventory 真源现已明确：remaining families 只能沿既有 boundary / replay authority chain 收口，不得继续描述为 helper implicit behavior 或 v1.1 de-scope folklore。
- 本 phase 关闭的是 boundary-family formalization residual；显式 replay assurance closeout 继续由 `Phase 21` 收官。

## Phase 21 Residual Delta

- `Replay scenario coverage` 已完成 closeout：remaining families 现已在 replay report、evidence pack 与 integration/meta guards 中获得显式 assurance coverage，不再保留为 active residual family。
- failure taxonomy contract 已冻结到 shared telemetry truth；remaining `except Exception` 数量被转入 repo-wide audit metric 与 future sustainment backlog，而不是继续以未仲裁 residual family 存在。
- 本 phase **无新增 compat shell / authority drift**；收口的是 failure classification 语言与关键 catch-all arbitration seam。

## Phase 22 Residual Delta

- `Observability consumer convergence` residual 已进一步收口：diagnostics / system health / developer / support / evidence consumers 现在共同暴露共享 `failure_summary` vocabulary，raw transport / API error fields 仅保留为 debug detail。
- developer report consumer 已完全回归 exporter-backed truth；`build_developer_report()` compat / test seam 已物理退场，不再保留第二入口。
- 本 phase **无新增 compat shell**；`failure_summary` contract 继续 pull exporter / service truth，后续 docs / release 只允许消费这些结果，不能再平行讲述第二套失败语义。

## Phase 23 Residual Delta

- contributor docs / templates / runbook / evidence index 现已统一消费 baseline / review / milestone truth；本 phase **无新增 active residual family**。
- `failure_summary` / `failure_entries` 提示已进入 support / troubleshooting / bug-report 路径，但这些公开入口只消费 shared contract，不新增第二套 consumer vocabulary。
- workflow narrative 维持 **no-change**：release 继续复用 `ci.yml` gate，`V1_2_EVIDENCE_INDEX.md` 只作为 pull-only evidence pointer，而不是新的 authority chain。
- `custom_components/lipro/core/coordinator/coordinator.py` 与 `custom_components/lipro/core/api/client.py` 已完成本轮第一刀减重 / 边界澄清，但更深拆分仍登记为 post-closeout follow-up，不再默认为 silent debt。

## Phase 24 Final Audit Disposition

- final repo audit (`2026-03-16`) 将 repo-wide metrics 记为：`Any=614`、`except Exception=36`、`type: ignore=12`；它们已被明确定性为 future sustainment backlog / distributed tech debt，而不是 silent defer。
- 当前已无 active residual family；remaining boundary/replay coverage、observability convergence 与 external-boundary naming residual 均已完成 closeout，不再悬空。
- `v1.2` closeout 现达到 archive-ready / handoff-ready：residual disposition、milestone audit、evidence index 与 handoff assets 已讲同一条最终故事线。


## Phase 38 Residual Delta

- `External-boundary advisory naming` 已关闭：firmware authority truth 现明确为 bundled local trust-root asset + remote advisory payload；历史文件名保留，但 active residual family 已清零。

## Phase 25.2 Residual Delta

- `coordinator.client` telemetry ghost seam 已关闭：`custom_components/lipro/control/telemetry_surface.py` 只再 pull `Coordinator.protocol` formal surface，不再把 legacy alias 合法化为 observer bridge 输入。
- touched `.planning/codebase/STRUCTURE.md` 已同步这一事实，但 derived map 身份保持不变；authority 仍以 north-star / baseline / review / active truth 为准。
- 本 phase **无新增 active residual family / compat shell / second-root story**；关闭的是 formal-surface honesty seam，而不是重做 telemetry schema。


## Phase 27 Residual Delta

- `Coordinator` 顶层 schedule / diagnostics / OTA / outlet-power pure forwarder cluster 已退场：external consumers 现在只 pull `coordinator.protocol_service`，不再把 runtime root 混成 protocol passthrough façade。
- runtime 正式代码中的 `Phase C` / `Phase H4` 历史叙事已清理；关闭的是 narration seam，而不是引入新的 abstraction layer。
- 本 phase **无新增 compat shell / second-root story / active residual family**；remaining `LiproRestFacade` hotspot 仍被诚实记录为 child-façade maintainability debt，但它不是新的 public root，也不允许反向定义 runtime truth。


## Phase 35 Residual Delta

- `client.py` 已收窄为 stable import home，`rest_facade.py` / `request_gateway.py` / `transport_executor.py` / `endpoint_surface.py` / `rest_port.py` 与 `mqtt_facade.py` 继续承接内部复杂度；它们都没有升级成新的 public root 或 compat shell。
- `LiproRestFacade` / `LiproProtocolFacade` 仍保留为 formal child/root story；remaining residual 仅是后续可继续优化的 body-size maintainability debt，不再是 public-surface honesty seam。
- 本 phase **无新增 active residual family / second-root story / export growth**；关闭的是 protocol hotspot ballast 与 endpoint-operation glue 漂浮。

## Phase 36 Residual Delta

- `Coordinator` 仍保留少量 root-owned orchestration 与 sanctioned broad-catch budget，但 polling/status/outlet/snapshot cluster 已正式下沉到 `CoordinatorPollingService`，runtime root ballast 明显下降。
- `snapshot.py`、`device_runtime.py`、`mqtt_runtime.py`、`mqtt_lifecycle.py` 与 `command_service.py` 的主链宽异常已收口到 typed arbitration / fail-closed path；remaining budget 只保留 machine-guarded sanctioned points。
- 本 phase **无新增 runtime bypass seam / second manager/root**；关闭的是 broad-catch 灰区与 coordinator polling hotspot。

## Phase 37 Residual Delta

- init/service-handler/runtime/governance phase-history 巨石测试已拆成稳定 topic suites；保留的聚合文件只承担 shared helper / topic root 身份，不再吸附所有子故事线。
- `.planning/codebase/*` 与 verification/testing guidance 已重新同步到真实拓扑；remaining residual 只是不时需要跟随新增测试文件刷新 derived maps，而不是 authority drift。
- 本 phase **无新增 active residual family**；关闭的是 test-topology drift、旧单文件锚点与高噪音 prose-coupled closeout 断言。

## Phase 39 Residual Delta

- `custom_components/lipro/core/protocol/compat.py` dead shell 已物理删除；Phase 39 不再保留任何“空 compat 壳也算合法存在”的 folklore。
- `get_device_list.envelope.json` 现被固定为唯一 authority asset；相关 replay manifests、tests、readmes 与 guards 已完成单命名收口，不再存在 compat / wrapped / envelope 并行叙事。
- `custom_components/lipro/control/` 已在 north-star、developer docs、review ledgers 与治理守卫中被统一确认为 formal control-plane home；`custom_components/lipro/services/` 只再承担 service declarations / adapters / helpers 身份。
- governance current-story placeholder 已关闭：`v1.4` 已完成 milestone archive promotion，`Phase 39 complete` 作为 historical closeout evidence 保留，本 phase **无新增 active residual family**。


## Phase 40 Residual Delta

- `custom_components/lipro/services/execution.py` 继续明确保持为 formal service execution facade；`schedule.py` 现已复用 shared executor，不再维护局部 auth/error chain，也不会回流为 active residual / kill target。
- `custom_components/lipro/core/api/endpoint_surface.py` 与 `rest_facade_endpoint_methods.py` 的 touched 语义继续收口到 endpoint operations / façade wording；历史 `forwarding` 只保留在归档语境，不再作为当前架构口径。
- 本 phase **无新增 active residual family / compat shell / second-root story**；关闭的是 governance truth layering、runtime read-model 散点与 schedule execution duplication。

## Phase 43 Residual Delta

- `custom_components/lipro/control/runtime_access.py` 现已承接 typed diagnostics/system-health projection；`diagnostics_surface.py` 不再混搭 coordinator internals 与 ad-hoc runtime mapping 读取。
- `custom_components/lipro/runtime_infra.py` 现已收回 device-registry listener / pending reload task ownership；`services/maintenance.py` 只保留 `refresh_devices` thin adapter。
- `custom_components/lipro/services/device_lookup.py` 已降为 service-facing device-id resolver；`control/service_router_support.py` 成为最终 `(device, coordinator)` bridge。本 phase **无新增 active residual family / second control root**；关闭的是 helper-owned runtime truth 与 listener ownership 混淆。

## Phase 44 Residual Delta

- legacy `Client` / `Mixin` / `forwarding` symbol 名称现已被明确隔离到 residual / archive 语境；active ADR、baseline 与 docs index 统一改讲 `protocol` / `façade` / `operations` 语言。
- contributor fast-path、maintainer appendix 与 bilingual boundary 现已在 `README.md` / `README_zh.md`、`CONTRIBUTING.md`、`docs/README.md`、`SUPPORT.md`、`SECURITY.md` 与 PR template 中显式分层；维护者 continuity 真相继续保留在深层附录，不再压回根入口。
- 本 phase **无新增 active residual family / compat shell / future kill target**；收口的是 governance 噪音、术语漂移与入口边界，而不是新增 delete campaign。

## Phase 45 Residual Delta

- `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py` 已沿 localized helper seams 继续瘦身；`rest_decoder.py` 现拥有 schedule/MQTT endpoint-scoped decode logic，但 formal decoder boundary 与 public surface 未扩张。
- diagnostics/share/message touched-zone 现已共享 typed `OperationOutcome` / reason-code 语义；旧 bool wrappers 只保留为兼容薄壳，不再代表 active truth。
- benchmark lane 现已拥有 baseline manifest 与 threshold semantics，同时继续保持 `schedule` / `workflow_dispatch` maintainer-facing 边界；本 phase **无新增 active residual family / second governance story**。


## Phase 47 Residual Delta

- 本轮 **无新增 active residual family**；关闭的是 docs/tooling discoverability 与 release-signature identity 过宽 contract，而不是开启新的架构故事线。
- `scripts/agent_worker.py` 与 `scripts/orchestrator.py` 仍保留为 explicit retired compatibility stubs，但它们现在只是 fail-fast deprecation entry，不再伪装成可继续成功执行的 active tooling；delete gate 已明确收口为“仅在维护中的文档 / 自动化仍需要这些名称作为 migration hint 时保留”。
- runtime hotspot、mega-test topicization 与 REST typed-surface debt 仍已诚实路由到 `Phase 48 -> 50`，不作为 silent defer 继续漂浮。

## Phase 52 Residual Delta

- `LiproProtocolFacade` 仍是唯一 formal protocol root；`protocol_facade_rest_methods.py`、`rest_port.py` 与 `mqtt_facade.py` 只是在统一主线下继续 inward slimming，没有新增 second-root residual。
- `RequestPolicy` / `RestRequestGateway` / `RestTransportExecutor` 的 ownership 现已被代码、guards 与 baseline truth 对齐：busy / pacing / 429 决策回到 policy home，mapping/auth-aware retry-context orchestration 留在 gateway，executor 只再承担 transport execution。
- 本 phase 新增的是对 `compute_exponential_retry_wait_time()` cross-plane leak 的显式登记：它从 silent defer 变成可审计 deferred residual；后续若继续清理，只能迁往更诚实的 shared backoff home，而不是把 `request_policy.py` 再讲成跨平面 utility root。



## Phase 58 Status Update

- 本 phase **无新增 active residual family**；它刷新的是 repo-wide verdict 与 route truth，而不是新开 residual campaign。
- refreshed audit 明确认可：active residual ledger 当前仍为空；后续 follow-up 主要是 maintainability precision，而不是历史错根回潮。
- `58-REMEDIATION-ROADMAP.md` 现承担 `Phase 59+` route seed 身份；它不是 archive artifact，也不是新的 baseline root。

## Phase 59 Status Update

- 本 phase **无新增 active residual family**；它冻结的是 localized verification topology，而不是新开 residual campaign。
- thin-shell meta roots、truth-family submodules 与 split `device_refresh` suites 现都属于正式 verification topology，不是临时 compat story。
- `59-SUMMARY.md` 与 `59-VERIFICATION.md` 已作为 Phase 59 closeout evidence promoted；`59-PRD.md`、`59-CONTEXT.md`、`59-RESEARCH.md`、`59-VALIDATION.md` 与 `59-0x-PLAN.md` 继续保持 execution-trace 身份。


## Phase 60 Residual Delta

- `scripts/check_file_matrix.py` 与 `tests/meta/test_toolchain_truth.py` 现已分别收敛成 thin roots；关闭的是 giant tooling/test truth hotspot，而不是创建新的 helper-owned authority。
- sibling modules 现承接 inventory/classifier/markdown/validation 与 python/release/docs/CI/testing/checker truth families；current-story docs 与 review/baseline truth 已同步，无新增 active residual family。

## Phase 61 Residual Delta

- `anonymous_share`、diagnostics、OTA candidate 与 `select` 现都保持单一 outward roots；`manager_submission.py`、`share_client_flows.py`、`candidate_support.py` 与 `select_internal/gear.py` 均为 inward collaborators，而不是新的 public roots / compat shells。
- 本 phase **无新增 active residual family**：收口的是既有 large-but-correct production hotspots，而不是引入新的 helper-owned authority。
- `tests/meta/test_phase61_formal_home_budget_guards.py` 与更新后的 `.planning/reviews/FILE_MATRIX.md` 已冻结新的 no-growth / support-locality posture，防止 support seam 回流成第二正式故事。


## Phase 68 Residual Delta

- 无新增 active residual family。
- 本 phase 显式关闭了 MQTT authority ambiguity、docs/metadata current-story drift 与 hotspot regrowth risk；后续若继续优化，只允许沿现有 formal homes / baseline / review ledgers 收口，不得重新长出第二故事线。


## Phase 69 Residual Delta

- 无新增 active residual family。
- `runtime_access` outward home、schedule/protocol service seam、checker/integration balance 与 honest open-source contract 已在本 phase 完成收口；后续若继续优化，只允许沿既有 formal homes / governance chain 细化，不得重开第二故事线。
- 历史 archived baseline 已进一步提升到 `v1.18`；当前无 active milestone route，且 `Phase 70` 不追加 ownerless carry-forward。

## Phase 70 Residual Delta

- 无新增 active residual family。
- runtime support helper decomposition、anonymous-share / OTA shared-helper convergence 与 archive-vs-current truth freeze 已在本 phase 完成收口；后续若继续优化，只允许沿既有 formal homes / governance chain 细化，不得重开第二故事线。
- latest archived baseline 现已提升到 `v1.19`；当前 mutable current story 已升级为 `no active milestone route / latest archived baseline = v1.20`，且本 phase 不新增 ownerless carry-forward。


## Phase 71 Residual Delta

- 无新增 active residual family。
- OTA / firmware-install、anonymous-share submit、request pacing 与 command-runtime 长流程已在本 phase 获得更窄 helper decomposition；后续若继续优化，只允许沿既有 formal homes / governance chain 细化。
- milestone truth 已完成 archive promotion；当前 mutable current story 现为 `no active milestone route / latest archived baseline = v1.20`；`v1.18` 退为 previous archived baseline。


## Phase 76 Residual Delta

- 无新增 active residual family。
- machine-readable governance-route contract、latest archived pointer 与 parser-visible bootstrap shadow 已在本 phase 完成收口；后续若继续优化，只允许沿既有 planning/baseline/review truth 细化，不得重开第二故事线。

## Phase 77 Residual Delta

- 无新增 active residual family。
- bootstrap smoke topicization、shared route-truth helper 与 docs/private-boundary freeze 已在本 phase 完成收口；后续只允许继续沿 focused guard 细化，不得把 mega-suite 或 helper folklore 写回 live route。

## Phase 78 Residual Delta

- 无新增 active residual family。
- route-handoff fast path、closeout-ready wording、promoted evidence allowlist 与 review ledgers 已在本 phase 冻结；后续 archive promotion 只消费这些既有证据，不得再回头补 current-story handoff。

## Phase 79 Residual Delta

- 无新增 active residual family。
- registry classifier split、release-contract topic suites 与 live route truth 已在本 phase 冻结；后续 milestone closeout 只消费这些既有 closeout assets，不得再回头重开治理工具链热点。

## Phase 80 Residual Delta

- 无新增 active residual family。
- governance/tooling typing closure、final meta-suite hotspot topicization 与 live route truth 已在本 phase 冻结；后续 milestone closeout 只消费这些既有 closeout assets，不得再回头重开 giant-test 或类型诚实性热点。



## Phase 81 Residual Delta

- 无新增 active residual family。
- public first-hop、canonical docs map、contributor architecture change map 与 maintainer appendix boundary 已在本 phase 收口；后续只允许继续补 focused guards，不得重开第二条 docs-entry 故事线。
- contributor-facing docs 现在可直接路由 protocol / runtime / control / external-boundary / governance 改动；后续若再精修，只能沿既有 evidence destinations 同步更新。

## Phase 82 Residual Delta

- 无新增 active residual family。
- maintainer-facing release route、version-sync triad、changelog 与 archived evidence pointer 已共享一条发布主链；后续只能补强 guard / rehearsal truth，不得回流平行 runbook 或 helper folklore。
- archive evidence 继续保持 historical-only 身份；后续若再改 release continuity，只能沿既有 maintainer appendix / governance chain 收口。

## Phase 83 Residual Delta

- 无新增 active residual family。
- issue / PR / security intake 与 contributor stewardship surfaces 现已共享 evidence-first routing、best-effort triage 与 custody restoration truth；后续只允许继续扩 guard，不得把 undocumented delegate / hidden maintainer folklore 写回 live contract。
- `docs/README.md` 继续只承担 docs map / contract reachability；`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`.github/ISSUE_TEMPLATE/*.yml`、`.github/pull_request_template.md` 与 `.github/CODEOWNERS` 现共同构成 formal intake / stewardship surface family。

## Phase 84 Residual Delta

- 无新增 active residual family。
- focused governance / open-source guards 现已冻结 active-route、docs-entry、template evidence、release / version link 与 promoted closeout truth；后续只能进入 milestone closeout，不得再回退到 `Phase 83` current story。
- `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / VERIFICATION_MATRIX / PROMOTED_PHASE_ASSETS` 现共同承认 `Phase 84 complete / next = $gsd-new-milestone`。

## Phase 87 Residual Delta

- 无新增 active residual family。
- `Phase 85` route-next 的 giant assurance carriers 已在本 phase 关闭：`test_api_diagnostics_service.py`、`test_protocol_contract_matrix.py` 与 `test_mqtt_runtime.py` 现分别退化为 thin anchor / thin shell，concern-local topical suites 与 focused guard 共同冻结新的 verification topology。
- hotspot closeout truth 已回写到 `FILE_MATRIX.md`、`VERIFICATION_MATRIX.md` 与 `tests/meta/test_phase87_assurance_hotspot_guards.py`；后续若继续精修，只允许沿既有 topical homes 收口，不得把 bulk assertions 写回 root carriers。

## v1.21 Milestone Closeout Delta

- 无新增 active residual family。
- `Phase 76 -> 80` closeout 资产已全部转入 archived-only evidence chain；后续新路线只能 pull 这些既有证据，不得回头把 closeout truth 重新写成 active current story。
- latest archived baseline 已提升到 `v1.21`；`v1.20` 退为 previous archived baseline。


## Phase 90 Residual Delta

- 无新增 active residual family。
- five hotspots（`command_runtime.py`、`rest_facade.py`、`request_policy.py`、`mqtt_runtime.py`、`anonymous_share/manager.py`）在本 phase 被明确冻结为 formal homes；它们的后续演进只允许沿 sibling/support family inward split，不得被重述为 file-level residual 或 delete target。
- `custom_components/lipro/__init__.py`、`control/runtime_access.py`、`entities/base.py` 与 `entities/firmware_update.py` 继续保持 protected thin shell / projection / typed-access posture；后续 phase 若需要继续切薄，只能 narrowing / inward split，不得把 orchestration 回流到 outward shells。
- delete gate 继续只接受显式 `owner + target phase + delete gate + evidence pointer` 的 localized residual；`Phase 90` 不创建 ownerless carry-forward。


## Phase 91 Residual Delta

- 无新增 active residual family。
- protocol live-path canonicalization 与 typed-boundary closure 已在 formal homes 内完成；这些收口不是新的 delete campaign。
- shared telemetry / trace contracts 已收敛到 `runtime_types.py` / `core/coordinator/types.py` / `trace.py`，不允许再把 typed truth 退回 anonymous dynamic dict。
- protected thin shells 继续只做 projection / typed access；Phase 91 的 typed-boundary closure 不创建 ownerless carry-forward。


## Phase 92 Residual Delta

- 无新增 active residual family；本 phase 收口的是 shared redaction contract 与 touched thin-shell topicization，而不是新的 residual legalization。
- 若未来仍发现必须清退的 sink-local sanitizer folklore，必须显式登记 `owner + target phase + delete gate + evidence pointer`，不得把它们继续藏在 helper 名义下。


## Phase 93 Residual Delta

- 无新增 active residual family；Phase 93 收口的是 assurance / quality-freeze projections、typing-budget honesty 与 milestone closeout-ready proof，而不是把任何 local drift 重新包装成长期残留。
- 若未来仍发现 testing/governance 投影与正式 route truth 再次漂移，必须登记为显式治理残留，而不是默认靠下一轮 phase 顺手修掉。
## Phase 98 Residual Delta

- 无新增 active residual family；Phase 98 已关闭该 carry-forward：`outlet_power` legacy side-car fallback 已完成物理删除并由 focused guards / phase assets 冻结，不再保留为口头 carry-forward。
- 本 phase 收口的是 carry-forward eradication + route reactivation；它现在作为 `v1.27` 中的 completed predecessor 保留，不再充当 current-route selector。

## Phase 99 Residual Delta

- 无新增 active residual family；Phase 99 收口的是 hotspot support extraction / governance freeze，而不是新的 residual legalization。
- `status_fallback.py` 与 `command_runtime.py` 继续保留 formal homes；新增的 `status_fallback_support.py` / `command_runtime_support.py` 只是 inward collaborators，不是新的 public roots。
- remaining large formal homes 若未来继续精修，只允许沿既有 formal homes / local support seams inward split，不得把 support collaborator 反向合法化为第二故事线。

## Phase 100 Residual Delta

- 无新增 active residual family；Phase 100 收口的是 `schedule_service.py` / `mqtt_runtime.py` 的 hotspot support extraction 与 predecessor freeze，而不是新的 residual legalization。
- `schedule_service.py` 与 `mqtt_runtime.py` 继续保留 formal homes；新增的 `schedule_service_support.py` / `mqtt_runtime_support.py` 只是 inward collaborators，不是新的 public roots。
- remaining large formal homes 若未来继续精修，只允许沿既有 formal homes / local support seams inward split，不得把 support collaborator 反向合法化为第二故事线。

## Phase 101 Residual Delta

- 无新增 active residual family；Phase 101 收口的是 anonymous-share manager / REST decoder hotspot decomposition、boundary truth cleanup 与 previous-archived governance freeze，而不是新的 residual legalization。
- `manager_submission.py`、`manager_support.py`、`rest_decoder_support.py` 与 `mqtt_api_service.py` 继续只承担 inward collaborator / boundary helper 身份；若未来仍需继续 slim formal homes，只允许沿既有 formal homes / local support seams inward split，不得反向合法化为第二条故事线。

## Phase 103 Residual Delta

- `Phase 103` 未引入新的 orphan residual family；root adapter / test topology / terminology debt 已转为显式已完成项。
- 它识别出的 active residual 已在 `Phase 104/105` 显式承接，不再漂浮为 conversation-only 漏项。

## Phase 104 Residual Delta

- `service_router_handlers.py` family density 与 `command_runtime.py` second pass 已完成 inward split，已不再列为 active residual。
- `v1.29` 已无 live residual；`Phase 105` 的 governance rule datafication / milestone freeze 已全部并入 archived closeout bundle。

## Phase 102 Residual Delta

- 无新增 active residual family；Phase 102 收口的是 governance portability、verification stratification、docs-first continuity wording 与 latest-archived closeout hardening，而不是新的 residual legalization。
- `v1.27` closeout bundle 继续只承担 previous archived baseline 身份；任何后续优化都必须沿既有 planning/baseline/review truth 前进，不得重新拼装第二套 current-route 故事。

## Phase 113 Residual Delta

- 无新增 active residual family；Phase 113 关闭的是 `share_client_submit.py` 与 `result.py` 的 helper ballast，并把 remaining >400-line production hotspots 改写为显式 no-growth budget truth，而不是继续口头 carry-forward。
- `status_fallback_support.py`、`rest_facade.py`、`anonymous_share/manager.py`、`rest_decoder.py`、`firmware_update.py`、`rest_decoder_support.py`、`result_policy.py`、`dispatch.py` 与 `auth/manager.py` 继续保留 formal homes / sanctioned carriers 身份；后续若仍要精修，只允许沿既有 home/support seams inward split 或 narrowing，不得长出第二 authority chain。
- repo-level follow-up 仍诚实保留：私有 `gsd-tools` 进入测试/closeout guards、promoted assets 第二真源、planning route truth 多处硬编码、`.planning/codebase` freshness 漂移、planning link audit 未覆盖、contributor onramp / release continuity 单点；这些已进入最终审计，但不在本 phase 伪装成已关闭。

## Phase 123 Residual Delta

- `service_router` non-diagnostics callback family 已正式 reconverge 到 `custom_components/lipro/control/service_router_handlers.py`；四个过薄 split shells 已删除，不再计作 current residual topology。
- `service_router_diagnostics_handlers.py` 继续保留为 developer/diagnostics collaborator home；这不是 residual，而是刻意保留的语义隔离。
- 本 phase 没有继续进入 `config_flow.py` / `runtime_types.py` / `entry_auth.py` 的更高风险 slimming；这些保持为后续 carry-forward 观察点。
