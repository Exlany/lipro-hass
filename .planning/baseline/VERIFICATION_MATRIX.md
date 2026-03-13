# Verification Matrix

**Purpose:** 建立 requirement → artifact → test → doc → phase acceptance / handoff 的统一验证闭环。
**Status:** Formal baseline asset (`BASE-03` phase acceptance truth source)
**Updated:** 2026-03-13

## Formal Role

- 本文件是 `Phase 1.5` 及其下游 phases 的正式 acceptance truth；phase docs / summaries 只能引用、实例化或扩展，不得平行定义 exit contract。
- 任一 phase 只有同时交付 requirement evidence、artifact updates、verification proof 与 governance disposition，才可宣称完成。
- 若新增、降级或删除正式 public surface，改变 dependency truth，扩展 authority family，或新增 architecture policy rule family / CI gate，必须先回写对应 baseline doc，再更新实现、测试与 summary。
- 若 `.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md` 无变化，phase summary 也必须明确写出“为何无变化”。

## Requirement-to-Acceptance Mapping

| Requirement Group | Formal Truth / Primary Artifacts | Verification Evidence | Accepting Phases | Required Handoff |
|-------------------|----------------------------------|-----------------------|------------------|------------------|
| `BASE-*` | baseline asset pack (`TARGET_TOPOLOGY` / `DEPENDENCY_MATRIX` / `PUBLIC_SURFACES` / `VERIFICATION_MATRIX` / `AUTHORITY_MATRIX`) | document review + seed guards + phase summaries | 1.5 | baseline asset pack 成为 Phase 2+ 的 citeable input，而非 prose-only 假设 |
| `PROT-*` | protocol facades、auth/policy/normalizers、fixtures、snapshots | contract tests + snapshot suite + integration checks | 1 / 2 / 2.5 | runtime/control 只消费正式协议 surface，不再回到 mega client / mixin truth |
| `CTRL-*` | control surfaces、flows、diagnostics / system health / services docs | flow tests + lifecycle checks + diagnostics/service coverage + redaction proof | 3 | control plane 以正式 public surface 对接 runtime，而非 backdoor |
| `DOM-*` | capability registry / snapshot、projection contracts、domain docs | domain tests + entity/platform tests + snapshots | 4 | 平台/实体只消费 capability truth，不再并行生长第二套规则 |
| `RUN-*` | coordinator/runtime services、runtime invariants docs | invariant suite + integration checks + orchestration review | 5 | `Coordinator` 继续作为唯一正式 runtime root |
| `ASSR-*` | seed guards、meta guards、telemetry hooks、CI gates、verification docs | meta tests + observability evidence + CI proof | 1.5 / 6 | 结构未退化成为默认验收门，而非收尾补丁 |
| `INTG-*` | external boundary docs、fixtures、generated expectations、authority updates | targeted contract tests + fixture audits + drift checks | 2.6 | 外部边界 contract 成为后续 phase 的可引用真源 |
| `BND-*` | protocol boundary inventory、decoder family、schema registry、decode result、authority updates | boundary inventory review + protocol contract tests + governance guards | 7.1 | telemetry / replay / enforcement 继承单一 boundary truth，不再各自生长 decode authority |
| `ENF-*` | `ARCHITECTURE_POLICY.md`、shared policy helpers、architecture script、focused meta guards、governance CI gate | architecture-policy checks + meta guards + CI fail-fast proof | 7.2 | `07.3 / 07.4` 继承单一 enforcement taxonomy，而不是再造第二套规则真源 |
| `OBS-*` | `core/telemetry` exporter family、`control/telemetry_surface.py`、`07.3-VALIDATION.md`、telemetry summaries | exporter unit tests + targeted control regressions + diagnostics/system-health/service convergence + black-box exporter mainline proof | 7.3 | `07.4 / 08` 必须 pull 同一 telemetry truth，不得平行定义第二套 exporter schema |
| `SIM-*` | `tests/harness/protocol/`、`tests/fixtures/protocol_replay/`、`07.4-VALIDATION.md`、replay summaries / run summary | replay contract tests + integration harness + exporter-backed telemetry assertions + replay asset meta guards | 7.4 | `07.5 / 08` 必须 pull 同一 replay summary / authority pointer truth，不得反向定义第二套 simulator schema |
| `GOV-*` | `FILE_MATRIX`、`RESIDUAL_LEDGER`、`KILL_LIST`、final report | governance review + cleanup proof + audit summaries | 7 | 仓库最终收口具备完整治理证据链 |

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

## Governance Update Triggers

| Document | Update When | No-Update Still Requires |
|----------|-------------|--------------------------|
| `.planning/baseline/VERIFICATION_MATRIX.md` | phase acceptance proof、handoff contract、verification expectations 发生变化 | summary 指明本文件仍是当前 acceptance truth |
| `.planning/reviews/FILE_MATRIX.md` | 文件归属、phase owner、cluster scope 或 target fate 发生变化 | summary 明确“无 file-governance delta” |
| `.planning/reviews/RESIDUAL_LEDGER.md` | 新 residual family、exit condition 变化、或 residual 横跨额外 phase | summary 明确“无 residual delta” |
| `.planning/reviews/KILL_LIST.md` | 新删除候选、删除门槛变化、或某删除项被正式关闭 | summary 明确“无 deletion delta” |

---
*Used by: phase exit review, downstream handoff, and final audit arbitration*
