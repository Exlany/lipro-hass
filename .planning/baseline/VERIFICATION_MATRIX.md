# Verification Matrix

**Purpose:** 建立 requirement → artifact → test → doc → phase acceptance / handoff 的统一验证闭环。
**Status:** Formal baseline asset (`BASE-03` phase acceptance truth source)
**Updated:** 2026-03-18 (Phase 32 truth-convergence closeout aligned)

## Formal Role

- 本文件是 `Phase 1.5` 及其下游 phases 的正式 acceptance truth；phase docs / summaries 只能引用、实例化或扩展，不得平行定义 exit contract。
- 任一 phase 只有同时交付 requirement evidence、artifact updates、verification proof 与 governance disposition，才可宣称完成。
- 若新增、降级或删除正式 public surface，改变 dependency truth，扩展 authority family，或新增 architecture policy rule family / CI gate，必须先回写对应 baseline doc，再更新实现、测试与 summary。
- `.planning/baseline/ARCHITECTURE_POLICY.md` 是 verification gate 的正式 policy companion；phase exit contract 与 runnable proof 只能引用或实例化它，不能绕开它自立规则。
- 若 `.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md` 无变化，phase summary 也必须明确写出“为何无变化”。
- `.planning/codebase/*.md` 若被保留，必须通过 `README.md`、统一 derived collaboration map disclaimer、snapshot/freshness/authority 头部与治理守卫声明其从属身份，不能越权成为第二条 authority chain。

## Requirement-to-Acceptance Mapping

| Requirement Group | Formal Truth / Primary Artifacts | Verification Evidence | Accepting Phases | Required Handoff |
|-------------------|----------------------------------|-----------------------|------------------|------------------|
| `BASE-*` | baseline asset pack (`TARGET_TOPOLOGY` / `DEPENDENCY_MATRIX` / `PUBLIC_SURFACES` / `VERIFICATION_MATRIX` / `AUTHORITY_MATRIX`) | document review + seed guards + phase summaries | 1.5 | baseline asset pack 成为 Phase 2+ 的 citeable input，而非 prose-only 假设 |
| `PROT-*` | protocol facades、auth/policy/normalizers、fixtures、snapshots | contract tests + snapshot suite + integration checks | 1 / 2 / 2.5 | runtime/control 只消费正式协议 surface，不再回到 mega client / mixin truth |
| `CTRL-*` | control surfaces、flows、diagnostics / system health / services docs | flow tests + lifecycle checks + diagnostics/service coverage + redaction proof | 3 | control plane 以正式 public surface 对接 runtime，而非 backdoor |
| `DOM-*` | capability registry / snapshot、projection contracts、domain docs | domain tests + entity/platform tests + snapshots | 4 | 平台/实体只消费 capability truth，不再并行生长第二套规则 |
| `RUN-*` | coordinator/runtime services、runtime invariants docs | invariant suite + integration checks + orchestration review | 5 / 14 | `Coordinator` 继续作为唯一正式 runtime root |
| `HOT-*` | hotspot decomposition artifacts、focused helper homes、hotspot closeout summaries | focused regressions + targeted full-suite proof + governance sync | 12 / 13 / 14 / 16 | 热点拆解只能让 orchestration 更薄，不得引入第二条业务故事线 |
| `GOV-*` | `FILE_MATRIX`、`AUTHORITY_MATRIX`、`PUBLIC_SURFACES`、`VERIFICATION_MATRIX`、`RESIDUAL_LEDGER`、`KILL_LIST`、phase closeout summaries | governance review + matrix sync proof + closeout summaries + audit summaries | 7 / 7.5 / 15 / 16 / 17 | 新资产必须同时具备 owner、authority、verification、residual/delete gate |
| `AID-*` | evidence-pack schema、collector/exporter、redaction policy、evidence index pointers | focused evidence-pack regressions + schema/export validation + governance pointer review | 8 | AI 调试证据只能 pull 正式真源，不能反向定义新 authority chain |
| `RSC-*` / `RES-*` | protocol/runtime residual retirement artifacts、meta guards、review ledgers | public-surface guards + dependency guards + governance closeout proof | 9 / 16 / 17 | compatibility 只能显式、可验证、可删除 |
| `TYP-*` / `ERR-*` | typed contracts、narrowed helpers、exception arbitration docs | mypy + focused regressions + repo audit counts | 12 / 16 / 17 | 类型/异常语义必须可仲裁，不得靠 silent wrapper 维持旧契约 |
| `MQT-*` | MQTT transport locality rules、`MqttTransportFacade` contract、focused meta guards | dependency guards + protocol/mqtt regressions + no-export bans | 17 | concrete transport 只能是 local collaborator，不得回流成 public surface |

## Phase Exit Contract

- 每个 phase 至少需要：计划资产、`SUMMARY.md`、`VALIDATION.md`、`VERIFICATION.md`、相关 baseline/review docs 回写与最小充分 runnable proof。
- 若 phase 关闭 residual/delete gate，必须同时更新 `RESIDUAL_LEDGER.md` 与 `KILL_LIST.md`。
- 若 phase 改写 public surface / authority truth / dependency truth，必须同时更新 `PUBLIC_SURFACES.md`、`AUTHORITY_MATRIX.md`、`ARCHITECTURE_POLICY.md`、`VERIFICATION_MATRIX.md`。

## Phase 02 Exit Contract

- **Required artifacts:** REST facade / auth / transport rewrite artifacts、Phase 02 summaries、baseline/review closeout。
- **Required runnable proof:** focused API contract tests + targeted regression proof。
- **Unblock effect:** mega client / mixin truth 被正式 demote，为 unified protocol root 铺路。

## Phase 02.5 Exit Contract

- **Required artifacts:** unified protocol root closeout、MQTT child façade truth、public-surface demotion proof。
- **Required runnable proof:** protocol + MQTT focused regressions。
- **Unblock effect:** `LiproProtocolFacade` 成为唯一正式协议根。

## Phase 01.5 Exit Contract

- **Required artifacts:** baseline asset pack、seed guards、phase handoff docs。
- **Required runnable proof:** baseline/meta smoke proof。
- **Unblock effect:** 后续 phase 可以基于同一 baseline 真源推进。

## Phase 09 Exit Contract

- **Required artifacts:** explicit protocol public surface、runtime read-only view、outlet power primitive closeout。
- **Required runnable proof:** public-surface guards + runtime/device focused regressions。
- **Unblock effect:** residual surface closure 成为后续 cleanup 的正式输入。

## Phase 10 Exit Contract

- **Required artifacts:** boundary/auth contract closure、host-neutral auth/session truth、governance sync。
- **Required runnable proof:** boundary/auth/control focused regressions。
- **Unblock effect:** `AuthSessionSnapshot` 成为唯一正式 auth/session truth。

## Phase 12 Exit Contract

- **Required artifacts:** type convergence、compat narrowing、governance hygiene closeout。
- **Required runnable proof:** `uv run mypy` + focused API/runtime regressions。
- **Unblock effect:** `LiproClient` / raw compatibility public seams 退出正式故事线。

## Phase 13 Exit Contract

- **Required artifacts:** explicit domain surface、runtime/status hotspot boundary decomposition、governance guard hardening。
- **Required runnable proof:** domain/runtime focused regressions + governance guards。
- **Unblock effect:** 设备域正式表面与治理守卫结构化成型。

## Phase 14 Exit Contract

- **Required artifacts:** `custom_components/lipro/core/coordinator/coordinator.py`、`custom_components/lipro/core/coordinator/services/protocol_service.py`、`custom_components/lipro/core/api/{client.py,client_base.py,endpoints/payloads.py,endpoints/schedule.py,schedule_service.py,status_service.py,status_fallback.py}`、`custom_components/lipro/control/{service_router.py,developer_router_support.py}`、`14-01~14-04-SUMMARY.md`、`14-VALIDATION.md`、`14-VERIFICATION.md` 与更新后的 baseline/review/governance docs。
- **Required governance proof:** `PUBLIC_SURFACES.md`、`ARCHITECTURE_POLICY.md`、`VERIFICATION_MATRIX.md`、`FILE_MATRIX.md`、`RESIDUAL_LEDGER.md`、`KILL_LIST.md`、`docs/developer_architecture.md` 与 `.planning/codebase/STRUCTURE.md` 必须同步反映 `CoordinatorProtocolService`、schedule residual closeout、`status_fallback.py` / `developer_router_support.py` helper homes、以及 residual-guard hardening truth。
- **Required runnable proof:** `uv run ruff check .`、`uv run mypy`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py` 与 `uv run pytest -q` 通过。
- **Unblock effect:** `Coordinator.client` / `ScheduleApiService` 等旧 API spine 语义退出正式故事线；remaining cleanup 转入更小粒度的 residual closeout。

## Phase 15 Exit Contract

- **Required artifacts:** `custom_components/lipro/core/anonymous_share/report_builder.py`、`custom_components/lipro/services/diagnostics/{helpers.py,types.py}`、`custom_components/lipro/control/{runtime_access.py,developer_router_support.py,service_router.py}`、README / README_zh / SUPPORT / SECURITY / CONTRIBUTING / bug template、`15-01~15-05-SUMMARY.md`、`15-VALIDATION.md`、`15-VERIFICATION.md` 与更新后的 baseline/review/governance docs。
- **Required governance proof:** `PROJECT.md`、`ROADMAP.md`、`STATE.md`、`REQUIREMENTS.md`、`PUBLIC_SURFACES.md`、`VERIFICATION_MATRIX.md`、`FILE_MATRIX.md`、`RESIDUAL_LEDGER.md`、`KILL_LIST.md` 必须同时反映 upload-only developer feedback truth、source-path guards、version/support truth、tooling arbitration 与 residual locality wording。
- **Required runnable proof:** `uv run ruff check .`、`uv run mypy`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/core/test_report_builder.py tests/core/test_anonymous_share.py tests/core/test_control_plane.py tests/services/test_services_diagnostics.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py` 与 `uv run python scripts/coverage_diff.py coverage.json --minimum 95` 通过。
- **Unblock effect:** `v1.1` 已具备 milestone audit / closeout 输入；remaining residual 只允许继续本地化与 delete-gated 收口。

## Phase 16 Governance / Toolchain Entry Contract

- **Required governance proof:** `.planning/codebase/README.md` 必须存在；`.planning/codebase/*.md` 必须带 derived collaboration map disclaimer；`.gitignore` 必须允许 track `.planning/codebase/*.md`。
- **Required drift proof:** `AGENTS.md`、`FILE_MATRIX.md` 与 `.planning/codebase/STRUCTURE.md` / `ARCHITECTURE.md` 不得再把 `custom_components/lipro/services/execution.py` 写成 active `runtime-auth seam`。
- **Required executable proof:** `scripts/check_architecture_policy.py --check`、`scripts/check_file_matrix.py --check` 与 `tests/meta/test_governance_guards.py` 必须对上述真相 fail-fast。

## Phase 16 Closeout Contract

- **Required artifacts:** `docs/TROUBLESHOOTING.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`README.md`、`README_zh.md`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`.github/pull_request_template.md`、`.github/ISSUE_TEMPLATE/bug.yml`、`.github/workflows/release.yml`、`16-03~16-06-SUMMARY.md` 与更新后的 Phase 16 governance ledgers。
- **Required closeout proof:** `RESIDUAL_LEDGER.md` / `KILL_LIST.md` 必须写出 `item / disposition / owner / phase / delete gate / evidence`；任何 high-risk carry-forward 若保留，必须显式登记，不允许 silent defer。
- **Required runnable proof:** `uv run ruff check .`、`uv run mypy`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py`、`uv run pytest -q tests/platforms tests/flows/test_config_flow.py` 与 targeted Phase 16 code suites 通过。
- **Unblock effect:** `Phase 16` 可标记为 `6/6 complete`；Phase 17 进入最终 residual retirement / milestone closeout。

## Phase 17 Closeout Contract

- **Required artifacts:** `.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`、`.planning/PROJECT.md`、`.planning/v1.1-MILESTONE-AUDIT.md`、`.planning/baseline/{PUBLIC_SURFACES,ARCHITECTURE_POLICY,AUTHORITY_MATRIX,VERIFICATION_MATRIX}.md`、`.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER,KILL_LIST}.md`、`docs/developer_architecture.md`、`AGENTS.md`、`17-01~17-04-SUMMARY.md`、`17-VALIDATION.md`、`17-VERIFICATION.md`。
- **Required governance proof:** `_ClientTransportMixin`、endpoint legacy mixin family、`LiproMqttClient` legacy naming、`get_auth_data()` compat projection 与 synthetic outlet-power wrapper 都必须在 governance truth 中得到正确 disposition：已删除、已退场、或只剩 local helper locality，不得继续登记为 active residual。
- **Required runnable proof:** `uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py`、`uv run ruff check .`、`uv run mypy`、`uv run pytest -q`。
- **Unblock effect:** `Phase 17` 可标记为 `4/4 complete`，`v1.1` closeout 与 final repo audit 完成，里程碑进入 archive-ready 状态。

## Phase 18 Host-Neutral Nucleus Contract

- **Required artifacts:** `.planning/baseline/{PUBLIC_SURFACES,DEPENDENCY_MATRIX,ARCHITECTURE_POLICY,VERIFICATION_MATRIX}.md`、`.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER,KILL_LIST}.md`、`scripts/check_architecture_policy.py`、`tests/meta/test_dependency_guards.py`、`tests/meta/test_public_surface_guards.py`、`custom_components/lipro/core/auth/bootstrap.py` 与对齐后的 auth/device/platform focused suites。
- **Required governance proof:** `core/auth` / `core/capability` / `core/device` nucleus homes 不得重新吸入 `homeassistant` 或 `helpers/platform.py`；`helpers/platform.py` 必须保持 adapter-only HA platform projection 身份；`ConfigEntryLoginProjection` 只能作为 HA config-entry projection，不得替代 `AuthSessionSnapshot` formal truth。
- **Required runnable proof:** `uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`、`uv run pytest -q tests/flows/test_config_flow.py tests/core/test_init.py tests/core/test_token_persistence.py tests/core/test_categories.py tests/core/device/test_capabilities.py tests/core/capability/test_registry.py tests/core/test_device.py tests/core/device/test_device.py tests/platforms/test_entity_behavior.py tests/entities/test_descriptors.py tests/snapshots/test_device_snapshots.py`、`uv run ruff check .` 与 `uv run mypy` 通过。
- **Unblock effect:** `Phase 18` 的 host-neutral nucleus extraction / adapter projection demotion 获得 baseline、guard 与 focused regression 三重闭环，而不引入第二 root 或 silent residual。

## Phase 19 Headless Consumer Proof Contract

- **Required artifacts:** `.planning/baseline/{PUBLIC_SURFACES,DEPENDENCY_MATRIX,ARCHITECTURE_POLICY,VERIFICATION_MATRIX}.md`、`.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER,KILL_LIST}.md`、`custom_components/lipro/headless/{__init__.py,boot.py}`、`tests/harness/headless_consumer.py`、`tests/integration/test_headless_consumer_proof.py`、`19-01~19-04-SUMMARY.md`、`19-VALIDATION.md`、`19-VERIFICATION.md`。
- **Required governance proof:** headless boot / proof 必须保持 non-public / non-authority / non-second-root 身份；`ConfigEntryLoginProjection` 继续只属于 HA adapter；platform setup shells 不得重新依赖 `control/runtime_access.py`。
- **Required bridge proof:** headless consumer proof 只能复用 `LiproProtocolFacade`、`CapabilityRegistry`、`LiproDevice`、replay manifests 与 evidence-pack formal source paths；proof outputs 不得反向成为 authority source。
- **Required runnable proof:** `uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/core/test_headless_boot.py tests/flows/test_config_flow.py tests/core/test_init.py tests/core/test_token_persistence.py`、`uv run pytest -q tests/integration/test_headless_consumer_proof.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py`、`uv run pytest -q tests/core/test_helpers.py tests/core/test_control_plane.py -k runtime_access tests/platforms/test_entity_behavior.py`、`uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`、`uv run ruff check .` 与 `uv run mypy` 通过。
- **Unblock effect:** `CORE-02` 获得 single-chain proof；Phase 20 可以继续 boundary family completion，而不会把 headless proof 误读成第二 root。

## Phase 20 Remaining Boundary Family Completion Contract

- **Required artifacts:** `.planning/baseline/{AUTHORITY_MATRIX,VERIFICATION_MATRIX}.md`、`.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER,KILL_LIST}.md`、`tests/fixtures/protocol_boundary/README.md`、`tests/fixtures/protocol_replay/README.md`、`tests/meta/test_protocol_replay_assets.py`、`tests/integration/test_protocol_replay_harness.py`、`20-VALIDATION.md`；`20-VERIFICATION.md` 与 `.planning/{ROADMAP,REQUIREMENTS,STATE}.md` 只允许在 final gate 后回写。
- **Required governance proof:** `rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 必须被描述为 formal boundary/replay family，而不是 service helper、transport util、`topics.py`、`message_processor.py` 或 `payload.py` 的隐式局部约定。
- **Required runnable proof:** `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/mqtt/test_mqtt.py tests/core/mqtt/test_topic_builder.py tests/core/mqtt/test_mqtt_payload.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_client_refactored.py tests/core/mqtt/test_protocol_replay_mqtt.py`、`uv run pytest -q tests/integration/test_protocol_replay_harness.py tests/meta/test_protocol_replay_assets.py tests/meta/test_evidence_pack_authority.py`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`、`uv run ruff check .` 与 `uv run mypy` 通过。
- **Unblock effect:** `SIM-03` / `SIM-05` 获得 boundary-first、replay-visible、governance-aligned 闭环；Phase 21 可以专注 exception / observability hardening，而不是继续携带 remaining-family 漂移。


## Phase 21 Replay / Exception Taxonomy Contract

- **Required artifacts:** `custom_components/lipro/core/telemetry/{models,sinks}.py`、`custom_components/lipro/core/protocol/{facade,telemetry}.py`、`custom_components/lipro/core/coordinator/{coordinator,mqtt_lifecycle.py}`、`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`、`custom_components/lipro/core/coordinator/services/telemetry_service.py`、`custom_components/lipro/control/entry_lifecycle_controller.py`、`custom_components/lipro/services/diagnostics/helpers.py`、`tests/harness/protocol/{replay_models,replay_driver,replay_assertions,replay_report}.py`、`tests/harness/evidence_pack/collector.py`、`21-01~21-03-SUMMARY.md`、`21-VERIFICATION.md`。
- **Required governance proof:** remaining boundary families 必须在 replay / evidence surfaces 中显式可见；shared `failure_summary` / `error_category` / `error_type` contract 只能由 telemetry truth 输出，不能由 replay report 或 diagnostics helper 私自再定义。
- **Required runnable proof:** `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_protocol_replay_assets.py tests/meta/test_evidence_pack_authority.py tests/core/telemetry/test_models.py tests/core/telemetry/test_sinks.py tests/core/telemetry/test_exporter.py tests/core/coordinator/runtime/test_runtime_telemetry_methods.py tests/core/coordinator/services/test_telemetry_service.py tests/integration/test_telemetry_exporter_integration.py`、`uv run pytest -q tests/core/test_init.py tests/core/test_init_edge_cases.py tests/core/test_coordinator.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/services/test_telemetry_service.py tests/services/test_service_resilience.py tests/integration/test_mqtt_coordinator_integration.py`、`uv run ruff check .` 与 `uv run mypy` 通过。
- **Unblock effect:** `SIM-04` / `ERR-02` 获得 replay-complete、failure-taxonomy-stable、typed-arbitration-aware 的 assurance 闭环；Phase 22 只需消费共享 failure language，而不再补 replay blind spot。

## Phase 22 Observability Consumer Convergence Contract

- **Required artifacts:** `custom_components/lipro/control/{diagnostics_surface.py,system_health_surface.py}`、`custom_components/lipro/core/telemetry/sinks.py`、`custom_components/lipro/services/diagnostics/{helpers.py,handlers.py}`、`custom_components/lipro/core/anonymous_share/report_builder.py`、`tests/core/{test_diagnostics.py,test_system_health.py,test_control_plane.py,test_report_builder.py}`、`tests/core/telemetry/test_sinks.py`、`tests/services/{test_services_diagnostics.py,test_services_share.py,test_execution.py}`、`tests/integration/{test_telemetry_exporter_integration.py,test_ai_debug_evidence_pack.py}` 与 `.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER}.md`。
- **Required governance proof:** diagnostics / system health / developer / support / evidence consumers 必须复用共享 `failure_summary` vocabulary；raw `mqtt_last_error_type`、`last_transport_error` 与 service `last_error.message` 只能作为 debug detail 保留，不得重新成为 consumer canonical truth。
- **Required runnable proof:** `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_control_plane.py tests/core/telemetry/test_sinks.py tests/integration/test_telemetry_exporter_integration.py`、`uv run pytest -q tests/services/test_services_diagnostics.py tests/services/test_services_share.py tests/services/test_execution.py tests/core/test_report_builder.py tests/integration/test_ai_debug_evidence_pack.py`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`、`uv run ruff check .` 与 `uv run mypy` 通过。
- **Unblock effect:** `OBS-03` 获得 control/service/evidence 三层 consumer convergence proof；Phase 23 可以只处理 governance/docs/release closure，而不必再次解释 observability consumer 语义。


## Phase 23 Governance / Contributor / Release Evidence Contract

- **Required artifacts:** `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/{PUBLIC_SURFACES,VERIFICATION_MATRIX}.md`、`.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER,KILL_LIST,V1_2_EVIDENCE_INDEX.md}`、`README.md`、`README_zh.md`、`CONTRIBUTING.md`、`SUPPORT.md`、`docs/TROUBLESHOOTING.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.github/pull_request_template.md`、`.github/ISSUE_TEMPLATE/{bug.yml,config.yml}`、`23-01~23-03-SUMMARY.md`、`23-VERIFICATION.md`。
- **Required governance proof:** baseline / reviews / lifecycle docs 必须先于 public entry points 对齐；`V1_2_EVIDENCE_INDEX.md` 只能作为 pull-only evidence pointer，不能反向替代 authority matrix、verification matrix 或 milestone audit。
- **Required runnable proof:** `uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`、`uv run ruff check .` 通过。
- **Unblock effect:** `GOV-16` / `GOV-17` 获得 contributor-facing docs、release narrative 与 governance truth 的单一故事线；Phase 24 可以直接消费 closeout bundle 做 final audit / handoff。

## Phase 24 Final Audit / Archive-Ready / Handoff Contract

- **Required artifacts:** `.planning/reviews/{RESIDUAL_LEDGER,KILL_LIST}.md`、`.planning/v1.2-MILESTONE-AUDIT.md`、`.planning/MILESTONES.md`、`.planning/reviews/V1_2_EVIDENCE_INDEX.md`、`.planning/v1.3-HANDOFF.md`、`.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`、`24-01~24-03-SUMMARY.md`、`24-VERIFICATION.md`。
- **Required governance proof:** final repo audit 必须给所有 remaining items 明确 close / retain / defer disposition；`archive-ready` 与 `handoff-ready` 只能建立在 evidence index、milestone audit 与 handoff doc 同步一致之上，不得只在单一文件口头宣告。
- **Required runnable proof:** `uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`、`uv run ruff check .`、`uv run mypy` 通过。
- **Unblock effect:** `GOV-18` 获得 archive-ready / handoff-ready closeout bundle；下一轮维护者可直接从 `v1.3-HANDOFF.md` 起步，而不再依赖 phase 对话残影。


## Phase 25.2 Telemetry Formal-Surface Closure Contract

- **Required artifacts:** `custom_components/lipro/{runtime_types.py,control/telemetry_surface.py}`、`tests/{integration/test_telemetry_exporter_integration.py,core/test_system_health.py}`、`.planning/codebase/STRUCTURE.md`、`.planning/baseline/{PUBLIC_SURFACES,VERIFICATION_MATRIX}.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`25.2-01~25.2-03-SUMMARY.md`、`25.2-VERIFICATION.md`。
- **Required governance proof:** control-plane telemetry consumer 只能通过 `Coordinator.protocol` / `telemetry_service` pull formal telemetry truth；legacy `coordinator.client` ghost seam 已关闭；touched `.planning/codebase/*` 继续只是 derived collaboration maps，而不是 authority source。
- **Required runnable proof:** `uv run pytest -q tests/integration/test_telemetry_exporter_integration.py tests/core/test_system_health.py`、`uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py`、`uv run ruff check custom_components/lipro/runtime_types.py custom_components/lipro/control/telemetry_surface.py tests/integration/test_telemetry_exporter_integration.py tests/core/test_system_health.py` 通过。
- **Unblock effect:** `OBS-04` / `GOV-20` 获得 formal-surface honesty 与 planning-truth sync 闭环；Phase 26 可以专注 release trust chain / productization，而不再携带 telemetry ghost seam。


## Phase 27 Hotspot Slimming / Protocol-Service Convergence Contract

- **Required artifacts:** `custom_components/lipro/{runtime_types.py,services/schedule.py,services/diagnostics/handlers.py,entities/firmware_update.py}`、`custom_components/lipro/core/coordinator/{coordinator.py,runtime_context.py,orchestrator.py}`、`tests/{conftest.py,core/test_init.py,core/test_init_service_handlers*.py,services/test_services_diagnostics.py,services/test_service_resilience.py,test_coordinator_public.py,meta/test_governance_guards.py,meta/test_governance_closeout_guards.py,meta/test_public_surface_guards.py,meta/test_toolchain_truth.py}`、`.planning/codebase/{STRUCTURE,TESTING}.md`、`.planning/baseline/{PUBLIC_SURFACES,DEPENDENCY_MATRIX,VERIFICATION_MATRIX}.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`27-01~27-04-SUMMARY.md`、`27-VERIFICATION.md`。
- **Required governance proof:** external protocol-capability consumers 只能通过 `coordinator.protocol_service` 读取 schedule / diagnostics / OTA abilities；coordinator 顶层 pure forwarders 与历史 phase narration 已退场；新增测试文件后的 inventory / minimal-suite guidance 继续和仓库事实一致。
- **Required runnable proof:** `uv run pytest -q tests/core/test_init.py tests/core/test_init_service_handlers*.py tests/services/test_services_diagnostics.py tests/services/test_service_resilience.py tests/test_coordinator_public.py tests/core/test_coordinator.py`、`uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py`、`uv run ruff check custom_components/lipro/runtime_types.py custom_components/lipro/services/schedule.py custom_components/lipro/services/diagnostics/handlers.py custom_components/lipro/entities/firmware_update.py custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/core/coordinator/runtime_context.py custom_components/lipro/core/coordinator/orchestrator.py tests/core/test_init.py tests/core/test_init_service_handlers*.py tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py` 通过。
- **Unblock effect:** `HOT-05` / `RES-04` / `TST-02` 获得 runtime contract honesty、forwarder retirement 与 test monolith split 的同源闭环；后续 maintainability work 不再需要重复争论 protocol capability surface 应该住在哪里。

## Phase 32 Truth-Convergence / Gate-Honesty / Governance Closeout Contract

- **Required artifacts:** `.github/workflows/{ci,release}.yml`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/codebase/*.md`、`README.md`、`README_zh.md`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`tests/meta/test_toolchain_truth.py`。
- **Required governance proof:** repo-wide `ruff` / `mypy` / governance / release claims 必须与 `ci.yml`、`release.yml` 实际门禁完全一致；GitHub artifact `attestation` / `provenance`、`SHA256SUMS`、`SBOM`、artifact `signing` defer、GitHub `code scanning` defer 必须作为不同事实分别记录；`.planning/codebase/*.md` 顶部必须显式声明 snapshot、freshness 与 derived-map 身份，不能自称当前 authority truth；双语 public docs 与 maintainer docs 必须制度化 single-maintainer continuity truth，且不得虚构 backup maintainer。
- **Required runnable proof:** `uv run python scripts/check_translations.py`、`uv run pytest -q tests/meta/test_toolchain_truth.py`、`uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py -k "release or runbook or support or security"` 通过。
- **Unblock effect:** `QLT-05` / `GOV-25` / `GOV-26` 获得 gate honesty、release identity posture 与 derived-map freshness 的单一真相闭环；后续 closeout 不再依赖维护者脑内常识维持口径一致。


## Phase 35 Protocol Hotspot Final Slimming Contract

- **Required artifacts:** `custom_components/lipro/core/api/{client.py,client_request_gateway.py,client_endpoint_surface.py}`、`custom_components/lipro/core/protocol/{facade.py,rest_port.py,mqtt_facade.py}`、`tests/core/api/{test_api_command_surface.py,test_api_transport_and_schedule.py,test_auth_recovery_telemetry.py,test_protocol_contract_matrix.py}`、`.planning/baseline/{PUBLIC_SURFACES,DEPENDENCY_MATRIX,VERIFICATION_MATRIX}.md`、`.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER}.md`、`35-01~35-03-SUMMARY.md`、`35-SUMMARY.md`、`35-VERIFICATION.md`。
- **Required governance proof:** `LiproProtocolFacade` 与 `LiproRestFacade` 继续是唯一 formal protocol/root story；request pipeline、endpoint forwarding 与 MQTT child façade 复杂度已 inward 到 localized collaborators，没有新增 package export 或 second-root seam。
- **Required runnable proof:** `uv run pytest -q tests/core/api/test_api_command_surface.py tests/core/api/test_api_transport_and_schedule.py tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_protocol_contract_matrix.py tests/meta/test_public_surface_guards.py`、`uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_governance*.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py`、`uv run ruff check custom_components/lipro/core/api/client.py custom_components/lipro/core/api/client_request_gateway.py custom_components/lipro/core/api/client_endpoint_surface.py custom_components/lipro/core/protocol/facade.py custom_components/lipro/core/protocol/rest_port.py custom_components/lipro/core/protocol/mqtt_facade.py tests/core/api/test_protocol_contract_matrix.py` 通过。
- **Unblock effect:** `HOT-09` / `RES-07` 获得更薄的 protocol root/body、稳定回归与同步治理真相；后续 runtime hardening 不再背负 protocol hotspot ballast。

## Phase 36 Runtime Root / Exception Burn-Down Contract

- **Required artifacts:** `custom_components/lipro/core/coordinator/{coordinator.py,mqtt_lifecycle.py}`、`custom_components/lipro/core/coordinator/runtime/{device_runtime.py,mqtt_runtime.py}`、`custom_components/lipro/core/coordinator/runtime/device/snapshot.py`、`custom_components/lipro/core/coordinator/services/{command_service.py,polling_service.py}`、`tests/core/{test_coordinator.py}`、`tests/core/coordinator/services/{test_command_service.py,test_polling_service.py}`、`tests/core/coordinator/runtime/{test_device_runtime.py,test_mqtt_runtime.py}`、`tests/integration/test_mqtt_coordinator_integration.py`、`tests/meta/test_phase31_runtime_budget_guards.py`、`36-01~36-03-SUMMARY.md`、`36-SUMMARY.md`、`36-VERIFICATION.md`。
- **Required governance proof:** `Coordinator` 继续是唯一 runtime root；polling/status/outlet/device snapshot orchestration 已 inward 到 `CoordinatorPollingService`，runtime broad catches 已收紧为 named typed arbitration / fail-closed semantics，并同步 phase31 no-growth budget truth。
- **Required runnable proof:** `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/services/test_polling_service.py tests/core/coordinator/services/test_command_service.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_phase31_runtime_budget_guards.py`、`uv run pytest -q tests/meta/test_governance*.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py`、`uv run ruff check custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/core/coordinator/services/polling_service.py custom_components/lipro/core/coordinator/services/command_service.py custom_components/lipro/core/coordinator/runtime/device/snapshot.py custom_components/lipro/core/coordinator/runtime/device_runtime.py custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py custom_components/lipro/core/coordinator/mqtt_lifecycle.py` 通过。
- **Unblock effect:** `HOT-10` / `ERR-08` / `TYP-09` 获得更薄 runtime root、收紧后的 broad-catch budget 与 machine-checked mainline arbitration。

## Phase 37 Test Topology / Derived-Truth Convergence Contract

- **Required artifacts:** `tests/core/test_init_service_handlers*.py`、`tests/core/test_init_runtime*.py`、`tests/meta/test_governance_phase_history*.py`、`tests/meta/{test_governance_closeout_guards.py,test_toolchain_truth.py}`、`.planning/codebase/{README,ARCHITECTURE,STRUCTURE,TESTING}.md`、`CONTRIBUTING.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`37-01~37-03-SUMMARY.md`、`37-SUMMARY.md`、`37-VERIFICATION.md`。
- **Required governance proof:** init/runtime/governance mega-tests 已 topicize 成稳定专题套件；`.planning/codebase/*` freshness、testing topology、verification guidance 与实际命令/文件布局已重新对齐，并有 drift guards 约束。
- **Required runnable proof:** `uv run pytest -q tests/core/test_init*.py tests/meta/test_governance_phase_history*.py`、`uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py`、`uv run python scripts/check_file_matrix.py --check`、`uv run ruff check .` 通过。
- **Unblock effect:** `TST-06` / `GOV-30` / `QLT-09` 获得稳定的测试拓扑、较低噪音的治理守卫与可审计的 derived-truth baseline，为后续 fresh audit 提供干净起点。
