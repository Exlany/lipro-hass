# Verification Matrix

**Purpose:** 建立 requirement → artifact → test → doc → phase acceptance / handoff 的统一验证闭环。
**Status:** Formal baseline asset (`BASE-03` phase acceptance truth source)
**Updated:** 2026-03-15

## Formal Role

- 本文件是 `Phase 1.5` 及其下游 phases 的正式 acceptance truth；phase docs / summaries 只能引用、实例化或扩展，不得平行定义 exit contract。
- 任一 phase 只有同时交付 requirement evidence、artifact updates、verification proof 与 governance disposition，才可宣称完成。
- 若新增、降级或删除正式 public surface，改变 dependency truth，扩展 authority family，或新增 architecture policy rule family / CI gate，必须先回写对应 baseline doc，再更新实现、测试与 summary。
- 若 `.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md` 无变化，phase summary 也必须明确写出“为何无变化”。
- `.planning/codebase/*.md` 若被保留，必须通过 `README.md`、统一 derived collaboration map disclaimer 与治理守卫声明其从属身份，不能越权成为第二条 authority chain。

## Requirement-to-Acceptance Mapping

| Requirement Group | Formal Truth / Primary Artifacts | Verification Evidence | Accepting Phases | Required Handoff |
|-------------------|----------------------------------|-----------------------|------------------|------------------|
| `BASE-*` | baseline asset pack (`TARGET_TOPOLOGY` / `DEPENDENCY_MATRIX` / `PUBLIC_SURFACES` / `VERIFICATION_MATRIX` / `AUTHORITY_MATRIX`) | document review + seed guards + phase summaries | 1.5 | baseline asset pack 成为 Phase 2+ 的 citeable input，而非 prose-only 假设 |
| `PROT-*` | protocol facades、auth/policy/normalizers、fixtures、snapshots | contract tests + snapshot suite + integration checks | 1 / 2 / 2.5 | runtime/control 只消费正式协议 surface，不再回到 mega client / mixin truth |
| `CTRL-*` | control surfaces、flows、diagnostics / system health / services docs | flow tests + lifecycle checks + diagnostics/service coverage + redaction proof | 3 | control plane 以正式 public surface 对接 runtime，而非 backdoor |
| `DOM-*` | capability registry / snapshot、projection contracts、domain docs | domain tests + entity/platform tests + snapshots | 4 | 平台/实体只消费 capability truth，不再并行生长第二套规则 |
| `RUN-*` | coordinator/runtime services、runtime invariants docs | invariant suite + integration checks + orchestration review | 5 / 14 | `Coordinator` 继续作为唯一正式 runtime root，protocol-facing runtime ops 只能沿 formal service surface 收口 |
| `HOT-*` | hotspot decomposition artifacts、focused helper homes、hotspot closeout summaries | focused regressions + targeted full-suite proof + governance sync | 12 / 13 / 14 | 热点拆解只能让 orchestration 更薄，不得引入第二条业务故事线 |
| `ASSR-*` | seed guards、meta guards、telemetry hooks、CI gates、verification docs | meta tests + observability evidence + CI proof | 1.5 / 6 | 结构未退化成为默认验收门，而非收尾补丁 |
| `INTG-*` | external boundary docs、fixtures、generated expectations、authority updates | targeted contract tests + fixture audits + drift checks | 2.6 | 外部边界 contract 成为后续 phase 的可引用真源 |
| `BND-*` | protocol boundary inventory、decoder family、schema registry、decode result、authority updates | boundary inventory review + protocol contract tests + governance guards | 7.1 | telemetry / replay / enforcement 继承单一 boundary truth，不再各自生长 decode authority |
| `ENF-*` | `ARCHITECTURE_POLICY.md`、shared policy helpers、architecture script、focused meta guards、governance CI gate | architecture-policy checks + meta guards + CI fail-fast proof | 7.2 | `07.3 / 07.4` 继承单一 enforcement taxonomy，而不是再造第二套规则真源 |
| `OBS-*` | `core/telemetry` exporter family、`control/telemetry_surface.py`、`07.3-VALIDATION.md`、telemetry summaries | exporter unit tests + targeted control regressions + diagnostics/system-health/service convergence + black-box exporter mainline proof | 7.3 | `07.4 / 08` 必须 pull 同一 telemetry truth，不得平行定义第二套 exporter schema |
| `SIM-*` | `tests/harness/protocol/`、`tests/fixtures/protocol_replay/`、`07.4-VALIDATION.md`、replay summaries / run summary | replay contract tests + integration harness + exporter-backed telemetry assertions + replay asset meta guards | 7.4 | `07.5 / 08` 必须 pull 同一 replay summary / authority pointer truth，不得反向定义第二套 simulator schema |
| `GOV-*` | `FILE_MATRIX`、`AUTHORITY_MATRIX`、`PUBLIC_SURFACES`、`VERIFICATION_MATRIX`、`RESIDUAL_LEDGER`、`KILL_LIST`、`V1_1_EVIDENCE_INDEX.md`、phase closeout summaries | governance review + matrix sync proof + closeout summaries + audit summaries | 7 / 7.5 | v1.1 新资产必须同时具备 owner、authority、verification、residual/delete gate，与 Phase 8 可 pull 的稳定证据入口 |
| `AID-*` | `tests/harness/evidence_pack/`、`scripts/export_ai_debug_evidence_pack.py`、`08-VALIDATION.md`、`08-01/02-SUMMARY.md`、`08-VERIFICATION.md`、更新后的 governance matrices / reviews | evidence-pack integration tests + authority/meta guards + governance sync proof | 8 | AI debug evidence pack 必须保持 assurance-only / pull-only；每个 section 都要能回溯 formal source，且统一继承 `07.3/07.4/07.5` 真相链 |
| `RSC-*` | `custom_components/lipro/core/protocol/facade.py`、`custom_components/lipro/core/coordinator/{coordinator,outlet_power}.py`、`custom_components/lipro/core/device/device.py`、`tests/meta/test_public_surface_guards.py`、`09-01/02/03-SUMMARY.md`、`09-VERIFICATION.md`、更新后的 baseline/review docs | targeted protocol/runtime regressions + meta guards + full-suite proof | 9 | residual surface closure 必须同时关闭隐式 protocol root、runtime live mutable mapping 泄露与 outlet power side-write，并把剩余 compat seam 变成显式 delete-gated 残留 |

| `ISO-*` | `custom_components/lipro/core/protocol/boundary/rest_decoder.py`、`custom_components/lipro/core/protocol/contracts.py`、`custom_components/lipro/core/auth/manager.py`、`custom_components/lipro/{config_flow.py,entry_auth.py}`、`10-01/02/03/04-SUMMARY.md`、`10-VERIFICATION.md`、更新后的 baseline/review docs | protocol contract matrix + REST/MQTT replay + auth/flow regressions + public-surface/dependency/governance guards | 10 | API drift 必须优先失败在 protocol boundary；HA adapters 只能消费 formal auth/session contract；未来 CLI / other host 只能建立在 boundary-first nucleus 之上 |

## Locked Upstream Inputs

| Upstream Phase | Required Inputs Before Acceptance | Why It Matters |
|----------------|-----------------------------------|----------------|
| Phase 1 | `.planning/phases/01-protocol-contract-baseline/01-01-SUMMARY.md`、`.planning/phases/01-protocol-contract-baseline/01-02-SUMMARY.md`、`.planning/phases/01-protocol-contract-baseline/01-IMMUTABLE-CONSTRAINTS.md`、`tests/fixtures/api_contracts/**`、`tests/snapshots/test_api_snapshots.py` | `Phase 1.5` 与 `Phase 2+` 必须继承协议边界 truth，而不是重判 contract baseline |

## Phase Exit Contract

| Phase | Must Cite Inputs | Must Produce | Must Prove | Governance / Handoff Contract |
|-------|------------------|--------------|------------|-------------------------------|
| 1 | protocol fixtures、contract matrix、canonical snapshots、immutable constraints | `01-01/02-SUMMARY.md`、locked baseline fixtures / snapshots | contract matrix + canonical snapshot suite pass | `Phase 1.5` 只能消费已锁定协议真源，不得重新解释协议 contract |
| 1.5 | Phase 1 closeout inputs + 五份 baseline docs + `01.5-ARCHITECTURE.md` + `01.5-VALIDATION.md` | `01.5-01/02/03-SUMMARY.md`、seed guards、formal baseline asset wording | baseline doc alignment review + `uv run pytest tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py -q` | `VERIFICATION_MATRIX.md` 成为正式 acceptance truth；Phase 2 / 2.5 / 2.6 / 3 必须引用 baseline asset pack 与 `01.5` summaries |
| 2 | baseline asset pack、`01.5-02-SUMMARY.md` seed-guard proof、Phase 1 protocol truth、`02-ARCHITECTURE.md` | `LiproRestFacade` slice artifacts、`02-01~02-04-SUMMARY.md`、更新后的 `FILE_MATRIX` / `RESIDUAL_LEDGER` / `KILL_LIST`，必要时回写 `PUBLIC_SURFACES.md` | 至少保持 `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/snapshots/test_api_snapshots.py -q` 通过，并补足 REST slice targeted regressions；若 public surface 变化还需 guard proof | `FILE_MATRIX` 必须覆盖 `custom_components/lipro/core/api/**/*.py`、`tests/core/api/**/*.py` 与 direct consumer tests；`RESIDUAL_LEDGER` / `KILL_LIST` 必须点名 compat wrappers、mixin inheritance、legacy public names 的 owner 与删除门槛 |
| 2.5 | baseline asset pack + Phase 2 protocol outputs | unified protocol root / MQTT integration artifacts、必要的 residual cleanup | `uv run pytest tests/core/api tests/core/mqtt tests/snapshots/test_api_snapshots.py -q` + `uv run pytest tests/integration/test_mqtt_coordinator_integration.py tests/flows/test_config_flow.py tests/core/test_init.py tests/core/test_token_persistence.py tests/meta/test_public_surface_guards.py -q` | control/runtime 之后只能引用统一协议 surface，不再并行引用旧根 |
| 2.6 | `AUTHORITY_MATRIX.md`、baseline asset pack、Phase 2 / 2.5 protocol outputs | external boundary docs、fixtures、generated expectations、authority updates | targeted boundary contract tests + fixture audits + drift detection | 后续 phases 只能扩展已登记 authority / external-boundary truth，不得自建平行文档 |
| 3 | baseline asset pack + Phase 2 / 2.5 formal protocol surfaces | control-plane docs、formal control surfaces、support tests | config-flow / reauth / diagnostics / services tests + redaction proof | control plane 访问 runtime 必须通过正式 public surface，并把 support surface 留给 Phase 4 / 5 引用 |
| 4 | baseline asset pack + Phase 3 control surface contract | `custom_components/lipro/core/capability/**/*.py`、capability registry / snapshot artifacts、domain slice docs、必要的 file-matrix updates | domain/entity/platform verification + snapshots | 平台/实体只能消费 capability projection；任何影子规则必须登记 residual 或 kill |
| 5 | baseline asset pack + Phase 2-4 formal surfaces | runtime invariants docs、runtime orchestration artifacts、必要的 residual cleanup | runtime invariant suite + integration proof | `Coordinator` 仍为唯一 runtime root；旁路刷新/写状态/重复订阅必须被证明受控 |
| 6 | 本文件、seed guards、prior formal surfaces、Phase 5 runtime proof | assurance taxonomy、hardened guards、CI gates、coverage / quality proof | meta guards + CI proof + test-structure alignment review | “结构未退化” 成为默认质量门；后续变更必须先经过 assurance contract |
| 7 | all prior summaries + governance docs + baseline asset pack | final `FILE_MATRIX`、`RESIDUAL_LEDGER`、`KILL_LIST`、closeout report | full governance review + cleanup / deletion proof | 形成仓库级最终 acceptance record |
| 7.1 | baseline asset pack、Phase 2 / 2.5 protocol outputs、`tests/fixtures/api_contracts/**`、`tests/fixtures/protocol_boundary/**`、`.planning/phases/07.1-protocol-boundary-schema-decoder/07.1-ARCHITECTURE.md` | boundary inventory、`core/protocol/boundary/` family、`07.1-01~03-SUMMARY.md`、authority/file-matrix/residual updates | targeted protocol contract tests + governance guards + replay/telemetry handoff review | decode authority 必须在 `LiproProtocolFacade` 之下形成单一 boundary family home，且首批 family 要留下 replay-ready fixture evidence |
| 7.2 | baseline asset pack、`.planning/baseline/ARCHITECTURE_POLICY.md`、`07.2-ARCHITECTURE.md`、`07.2-VALIDATION.md`、Phase 7.1 boundary outputs | architecture policy baseline、shared policy helpers、`scripts/check_architecture_policy.py`、`07.2-01/02-SUMMARY.md`、CI governance ordering updates | `uv run python scripts/check_architecture_policy.py --check` + `uv run python scripts/check_file_matrix.py --check` + `uv run pytest -q -x tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py` | plane/root/surface/authority 规则必须形成单一 enforcement chain，且为 `07.3` observer-only surface 与 `07.4` assurance-only boundary consumer 预留 extension hooks |
| 7.3 | baseline asset pack、`07.3-ARCHITECTURE.md`、`07.3-VALIDATION.md`、protocol/runtime telemetry seeds | `core/telemetry/` family、`control/telemetry_surface.py`、`07.3-01/02-SUMMARY.md`、governance delta updates | `uv run ruff check custom_components/lipro/core/telemetry custom_components/lipro/control/telemetry_surface.py custom_components/lipro/services/diagnostics/helpers.py tests/core/telemetry tests/services/test_services_diagnostics.py tests/integration/test_telemetry_exporter_integration.py` + `uv run pytest -q -x tests/core/coordinator/services/test_telemetry_service.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/services/test_services_diagnostics.py tests/integration/test_telemetry_exporter_integration.py` | `RuntimeTelemetryExporter` 必须保持 observer-only、pull-first，且 diagnostics / system health / replay / evidence pack 后续都只能 pull 同一 telemetry truth |
| 7.4 | baseline asset pack、`07.4-ARCHITECTURE.md`、`07.4-VALIDATION.md`、`07.3` exporter truth、protocol-boundary authority fixtures | `tests/harness/protocol/`、`tests/fixtures/protocol_replay/`、`07.4-01/02/03-SUMMARY.md`、replay report/meta guards、governance delta updates | `uv run ruff check tests/harness/protocol tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/meta/test_protocol_replay_assets.py` + `uv run pytest -q -x tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/meta/test_protocol_replay_assets.py tests/meta/test_external_boundary_authority.py tests/meta/test_external_boundary_fixtures.py` | replay harness 必须保持 assurance-only、deterministic、authority-indexed，且 telemetry assertions 只能 pull `07.3` exporter truth |
| 7.5 | baseline asset pack、`07.3/07.4` summaries + validation evidence、`07.4-UAT.md` residual handoff、`.planning/phases/07.5-integration-governance-verification-closeout/07.5-ARCHITECTURE.md` | `07.5-01/02-SUMMARY.md`、`07.5-SUMMARY.md`、`V1_1_EVIDENCE_INDEX.md`、governance matrix deltas、updated `ROADMAP / REQUIREMENTS / STATE` | `uv run python scripts/check_architecture_policy.py --check` + `uv run python scripts/check_file_matrix.py --check` + `uv run pytest -q -x tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_protocol_replay_assets.py` | `07.5` 只能做治理仲裁与 closeout evidence；`08` 只能 pull evidence index + 正式真源，不得重新扫描仓库拼装第二套事实 |
| 8 | `07.3` exporter truth、`07.4` replay harness/report truth、`07.5` evidence index / governance matrices、`08-ARCHITECTURE.md`、`08-VALIDATION.md` | `tests/harness/evidence_pack/`、`scripts/export_ai_debug_evidence_pack.py`、`tests/integration/test_ai_debug_evidence_pack.py`、`tests/meta/test_evidence_pack_authority.py`、`08-01/02-SUMMARY.md`、`08-VERIFICATION.md`、governance delta updates | `uv run ruff check scripts/export_ai_debug_evidence_pack.py tests/harness/evidence_pack tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py` + `uv run pytest -q -x tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py` | AI debug evidence pack 必须保持 assurance-only / pull-only；不得新建 runtime root；只允许导出统一脱敏、可追溯、可给 AI 调试/分析的 evidence outputs |
| 9 | `docs/archive/COMPREHENSIVE_AUDIT_2026-03-13.md`、`09-ARCHITECTURE.md`、`09-VALIDATION.md`、baseline/review truth docs | `09-01/02/03-SUMMARY.md`、`09-UAT.md`、`09-VERIFICATION.md`、governance delta updates、updated `ROADMAP / REQUIREMENTS / STATE` | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_public_surface_guards.py tests/core/test_outlet_power.py tests/test_coordinator_public.py tests/platforms/test_sensor.py tests/core/test_diagnostics.py tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py` + `uv run python scripts/check_architecture_policy.py --check` + `uv run python scripts/check_file_matrix.py --check` + `uv run pytest -q` | residual surface closure 必须把 compat seams 收窄为显式、可计数、可删除的最小集合；不得回流 implicit root delegation、live mutable runtime public surface 或 `extra_data` power side-write |

## Phase 02 Exit Contract

- **Required artifacts:** `LiproRestFacade` formal slice outputs、`.planning/phases/02-api-client-de-mixin/02-ARCHITECTURE.md`、`.planning/phases/02-api-client-de-mixin/02-VALIDATION.md`、`02-01/02/03/04-SUMMARY.md`、更新后的 `FILE_MATRIX` / `RESIDUAL_LEDGER` / `KILL_LIST`，以及在 public surface 语义变化时同步更新的 `PUBLIC_SURFACES.md`。
- **Required governance proof:** `FILE_MATRIX` 必须给出 `core/api`、`tests/core/api`、direct consumer tests 的 file-level target fate；`RESIDUAL_LEDGER` / `KILL_LIST` 必须对 compat wrappers、mixin inheritance、legacy public names 写明 current example、owner、delete gate。
- **Required runnable proof:** 至少保持 `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/snapshots/test_api_snapshots.py -q` 与 `uv run pytest tests/flows/test_config_flow.py tests/test_coordinator_runtime.py tests/platforms/test_update_task_callback.py -q` 通过；随后再以 targeted REST slice regressions 与 public-surface guards 证明 demixin 没有破坏 Phase 1 canonical truth。
- **Unblock effect:** `Phase 2.5` 可把 `LiproRestFacade` 视为唯一 REST root，并把 `LiproClient` 明确降级为 transitional compat shell，而不是继续作为正式 public direction。

## Phase 02.5 Exit Contract

- **Required artifacts:** `custom_components/lipro/core/protocol/**/*.py`、`custom_components/lipro/core/coordinator/mqtt_lifecycle.py`、`custom_components/lipro/core/coordinator/{coordinator,orchestrator,factory}.py`、`custom_components/lipro/config_flow.py`、`custom_components/lipro/__init__.py`、`02.5-02/03-SUMMARY.md`，以及回写后的 `PUBLIC_SURFACES.md` / `DEPENDENCY_MATRIX.md` / `VERIFICATION_MATRIX.md` / `FILE_MATRIX.md` / `RESIDUAL_LEDGER.md` / `KILL_LIST.md`。
- **Required runnable proof:** `uv run pytest tests/core/api tests/core/mqtt tests/snapshots/test_api_snapshots.py -q` 与 `uv run pytest tests/integration/test_mqtt_coordinator_integration.py tests/flows/test_config_flow.py tests/core/test_init.py tests/core/test_token_persistence.py tests/meta/test_public_surface_guards.py -q` 通过，证明 unified root、MQTT child façade、control/runtime consumer migration 与 canonical contracts 同时成立。
- **Unblock effect:** `Phase 2.6` 与 `Phase 3` 只能继承 `LiproProtocolFacade` 这条单一协议主链；`LiproClient` / `LiproMqttClient` 仅剩显式 compat 语义，不再定义 public direction。

## Phase 01.5 Exit Contract

- **Required artifacts:** `.planning/baseline/TARGET_TOPOLOGY.md`、`.planning/baseline/DEPENDENCY_MATRIX.md`、`.planning/baseline/PUBLIC_SURFACES.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/baseline/AUTHORITY_MATRIX.md`、`tests/meta/test_dependency_guards.py`、`tests/meta/test_public_surface_guards.py`、`01.5-01/02/03-SUMMARY.md`。
- **Required proof:** Phase 1 upstream closeout artifacts 已存在；baseline docs wording 无双口径；seed guards 可作为最小 runnable proof；summary 记录 governance docs 的变更或无变更原因。
- **Unblock effect:** `Phase 2`、`2.5`、`2.6`、`3` 从此必须把 baseline asset pack 视为正式 handoff contract，而不是只引用 phase prose。

## Phase 09 Exit Contract

- **Required artifacts:** `custom_components/lipro/core/protocol/{facade,__init__,compat}.py`、`custom_components/lipro/{__init__,config_flow.py}`、`custom_components/lipro/core/{__init__,api/__init__,mqtt/__init__}.py`、`custom_components/lipro/core/coordinator/{coordinator.py,outlet_power.py}`、`custom_components/lipro/core/device/device.py`、`custom_components/lipro/{sensor.py}`、`custom_components/lipro/control/diagnostics_surface.py`、`09-01/02/03-SUMMARY.md`、`09-UAT.md`、`09-VERIFICATION.md`，以及更新后的 baseline / review truth docs。
- **Required governance proof:** `PUBLIC_SURFACES.md`、`AUTHORITY_MATRIX.md`、`VERIFICATION_MATRIX.md`、`FILE_MATRIX.md`、`RESIDUAL_LEDGER.md` 与 `KILL_LIST.md` 必须同步反映 explicit protocol root、remaining compat seams、read-only coordinator device surface 与 formal outlet-power primitive。
- **Required runnable proof:** 至少保持 `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_public_surface_guards.py tests/core/test_outlet_power.py tests/test_coordinator_public.py tests/platforms/test_sensor.py tests/core/test_diagnostics.py tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check` 与 `uv run pytest -q` 通过。
- **Unblock effect:** `Phase 12` 完成后，typed runtime / REST / diagnostics 合同与显式 compat seams 已同步收口；后续阶段可以直接基于单一正式主链规划新里程碑，而不是继续为 legacy public names 支付治理成本。

## Phase 10 Exit Contract

- **Required artifacts:** `custom_components/lipro/core/protocol/{boundary/rest_decoder.py,contracts.py,facade.py}`、`custom_components/lipro/core/auth/{__init__.py,manager.py}`、`custom_components/lipro/{config_flow.py,entry_auth.py}`、`custom_components/lipro/control/{runtime_access.py,telemetry_surface.py}`、`custom_components/lipro/core/__init__.py`、`10-01/02/03/04-SUMMARY.md`、`10-UAT.md`、`10-VERIFICATION.md`，以及更新后的 baseline / review truth docs。
- **Required governance proof:** `PUBLIC_SURFACES.md`、`DEPENDENCY_MATRIX.md`、`AUTHORITY_MATRIX.md`、`VERIFICATION_MATRIX.md`、`FILE_MATRIX.md`、`RESIDUAL_LEDGER.md` 与 `KILL_LIST.md` 必须同步反映 `rest.device-list` / `rest.device-status` / `rest.mesh-group-status` authority、`AuthSessionSnapshot` formal home、`core/__init__.py` 不再导出 `Coordinator`、以及 remaining compat seams。
- **Required runnable proof:** 至少保持 `uv run ruff check custom_components/lipro tests`、`uv run pytest -q -x tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/core/test_auth.py tests/core/test_init.py tests/flows/test_config_flow.py tests/meta/test_modularization_surfaces.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance_guards.py tests/meta/test_protocol_replay_assets.py tests/test_coordinator_public.py tests/core/test_diagnostics.py tests/core/test_system_health.py`、`uv run python scripts/check_architecture_policy.py --check` 与 `uv run python scripts/check_file_matrix.py --check` 通过。
- **Unblock effect:** 后续若真的要做 CLI / other host，只需复用已锁定的 boundary/auth/device nucleus，而不用再次把 `Coordinator` 或 HA adapter 从仓库里物理抽成 second root。

## Governance Update Triggers

| Document | Update When | No-Update Still Requires |
|----------|-------------|--------------------------|
| `.planning/baseline/VERIFICATION_MATRIX.md` | phase acceptance proof、handoff contract、verification expectations 发生变化 | summary 指明本文件仍是当前 acceptance truth |
| `.planning/reviews/FILE_MATRIX.md` | 文件归属、phase owner、cluster scope 或 target fate 发生变化 | summary 明确“无 file-governance delta” |
| `.planning/reviews/RESIDUAL_LEDGER.md` | 新 residual family、exit condition 变化、或 residual 横跨额外 phase | summary 明确“无 residual delta” |
| `.planning/reviews/KILL_LIST.md` | 新删除候选、删除门槛变化、或某删除项被正式关闭 | summary 明确“无 deletion delta” |
| `.planning/baseline/ARCHITECTURE_POLICY.md` | rule ids、governed paths、forbidden/required signals、enforcement scope 发生变化 | summary 明确“无 architecture-policy delta” |

---
*Used by: phase exit review, downstream handoff, and final audit arbitration*


## Phase 12 Exit Contract

- **Required artifacts:** `custom_components/lipro/runtime_types.py`、`custom_components/lipro/core/{api/client.py,protocol/facade.py}`、`custom_components/lipro/core/coordinator/{coordinator.py,runtime/device/snapshot.py}`、`custom_components/lipro/control/diagnostics_surface.py`、`custom_components/lipro/services/diagnostics/helpers.py`、`custom_components/lipro/core/api/__init__.py`、`custom_components/lipro/core/device/__init__.py`、`12-01~12-05-SUMMARY.md`、`12-VALIDATION.md`、`12-VERIFICATION.md` 与更新后的 baseline/review/governance docs。
- **Required governance proof:** `PUBLIC_SURFACES.md`、`VERIFICATION_MATRIX.md`、`FILE_MATRIX.md`、`RESIDUAL_LEDGER.md`、`KILL_LIST.md`、`CONTRIBUTING.md`、`.github/pull_request_template.md`、`.github/workflows/ci.yml` 必须同时反映 seam retirement、shellcheck gate、community governance files 与 single-maintainer support contract。
- **Required runnable proof:** 至少保持 `uv run mypy`、`uv run pytest -q tests/core/api/test_api.py tests/core/test_anonymous_share.py tests/core/test_boundary_conditions.py tests/core/device/test_capabilities.py`、`uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check` 通过。
- **Unblock effect:** `v1.1` 可以进入 milestone closeout；后续规划不再需要把 legacy REST constructor、device-list compat wrapper、MQTT raw transport seam 或 capability alias 当作 active residual。


## Phase 13 Exit Contract

- **Required artifacts:** `custom_components/lipro/core/device/{device.py,state.py,state_accessors.py}`、`custom_components/lipro/core/coordinator/{orchestrator.py,mqtt_lifecycle.py}`、`custom_components/lipro/core/api/status_service.py`、README/support/governance assets、`13-01~13-03-SUMMARY.md`、`13-VALIDATION.md`、`13-VERIFICATION.md` 与更新后的 baseline/review/governance docs。
- **Required governance proof:** `PUBLIC_SURFACES.md`、`VERIFICATION_MATRIX.md`、`FILE_MATRIX.md`、`RESIDUAL_LEDGER.md`、`KILL_LIST.md`、README / README_zh / CONTRIBUTING / SUPPORT / CODEOWNERS / quality-scale / devcontainer 必须同步反映显式 device/state surface、hotspot helper boundaries 与公开治理入口结构化守卫。
- **Required runnable proof:** 至少保持 `uv run pytest -q tests/core/device/test_device.py tests/core/device/test_state.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_device_refresh.py tests/core/api/test_api_status_service.py tests/core/api/test_api_status_service_regressions.py`、`uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py`、`uv run ruff check .`、`uv run mypy` 与 `uv run pytest -q` 通过。
- **Unblock effect:** 设备域正式表面、runtime/status 热点 helper 边界与 contributor-facing governance truth 可以作为 Phase 14 的稳定输入，而不是继续依赖动态委托或文案约定。

## Phase 14 Exit Contract

- **Required artifacts:** `custom_components/lipro/core/coordinator/coordinator.py`、`custom_components/lipro/core/coordinator/services/protocol_service.py`、`custom_components/lipro/core/api/{client.py,client_base.py,endpoints/payloads.py,endpoints/schedule.py,schedule_service.py,status_service.py,status_fallback.py}`、`custom_components/lipro/control/{service_router.py,developer_router_support.py}`、`14-01~14-04-SUMMARY.md`、`14-VALIDATION.md`、`14-VERIFICATION.md` 与更新后的 baseline/review/governance docs。
- **Required governance proof:** `PUBLIC_SURFACES.md`、`ARCHITECTURE_POLICY.md`、`VERIFICATION_MATRIX.md`、`FILE_MATRIX.md`、`RESIDUAL_LEDGER.md`、`KILL_LIST.md`、`docs/developer_architecture.md` 与 `.planning/codebase/STRUCTURE.md` 必须同步反映 `CoordinatorProtocolService`、schedule residual closeout、`status_fallback.py` / `developer_router_support.py` helper homes、以及 residual-guard hardening truth。
- **Required runnable proof:** 至少保持 `uv run ruff check .`、`uv run mypy`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py` 与 `uv run pytest -q` 通过。
- **Unblock effect:** `Coordinator.client` / `ScheduleApiService` 等旧 API spine 语义退出正式故事线，remaining residual 只剩 `_ClientBase` / helper mixin family、`LiproMqttClient` legacy naming 与 helper-level compatibility；`v1.1` 可进入 milestone audit / closeout。


## Phase 15 Exit Contract

- **Required artifacts:** `custom_components/lipro/core/anonymous_share/report_builder.py`、`custom_components/lipro/services/diagnostics/{helpers.py,types.py}`、`custom_components/lipro/control/{runtime_access.py,developer_router_support.py,service_router.py}`、README / README_zh / SUPPORT / SECURITY / CONTRIBUTING / bug template、`15-01~15-05-SUMMARY.md`、`15-VALIDATION.md`、`15-VERIFICATION.md` 与更新后的 baseline/review/governance docs。
- **Required governance proof:** `PROJECT.md`、`ROADMAP.md`、`STATE.md`、`REQUIREMENTS.md`、`PUBLIC_SURFACES.md`、`VERIFICATION_MATRIX.md`、`FILE_MATRIX.md`、`RESIDUAL_LEDGER.md`、`KILL_LIST.md` 必须同时反映 upload-only developer feedback truth、source-path guards、version/support truth、tooling arbitration 与 residual locality wording。
- **Required runnable proof:** 至少保持 `uv run ruff check .`、`uv run mypy`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/core/test_developer_report.py tests/core/test_report_builder.py tests/core/test_anonymous_share.py tests/core/test_control_plane.py tests/services/test_services_diagnostics.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py` 与 `uv run python scripts/coverage_diff.py coverage.json --minimum 95` 通过。
- **Unblock effect:** `v1.1` 已具备 milestone audit / closeout 输入；remaining residual 只允许继续本地化与 delete-gated 收口，不得回流为正式 surface。

## Phase 16 Governance / Toolchain Entry Contract

- **Required governance proof:** `.planning/codebase/README.md` 必须存在；`.planning/codebase/*.md` 必须带 derived collaboration map disclaimer；`.gitignore` 必须允许 track `.planning/codebase/*.md`。
- **Required drift proof:** `AGENTS.md`、`FILE_MATRIX.md` 与 `.planning/codebase/STRUCTURE.md` / `ARCHITECTURE.md` 不得再把 `custom_components/lipro/services/execution.py` 写成 active `runtime-auth seam`。
- **Required executable proof:** `scripts/check_architecture_policy.py --check`、`scripts/check_file_matrix.py --check` 与 `tests/meta/test_governance_guards.py` 必须对上述真相 fail-fast。


## Phase 16 Closeout Contract

- **Required artifacts:** `docs/TROUBLESHOOTING.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`README.md`、`README_zh.md`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`.github/pull_request_template.md`、`.github/ISSUE_TEMPLATE/bug.yml`、`.github/workflows/release.yml`、`16-03~16-06-SUMMARY.md` 与更新后的 Phase 16 governance ledgers。
- **Required closeout proof:** `RESIDUAL_LEDGER.md` / `KILL_LIST.md` 必须写出 `item / disposition / owner / phase / delete gate / evidence`；任何 high-risk carry-forward 若保留，必须显式登记，不允许 silent defer。
- **Required runnable proof:** `uv run ruff check .`、`uv run mypy`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py`、`uv run pytest -q tests/platforms tests/flows/test_config_flow.py` 与 targeted Phase 16 code suites 通过。
- **Unblock effect:** `Phase 16` 可标记为 `6/6 complete`，`v1.1` 进入 milestone audit / closeout；remaining residual 仅允许以低风险、本地化、delete-gated 形态保留。
