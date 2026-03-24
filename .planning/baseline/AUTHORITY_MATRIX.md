# Authority Matrix

**Purpose:** 定义文档、fixtures、generated、implementation 的权威来源与同步方向，避免多口径漂移。
**Status:** Formal baseline asset (`BASE-01` authority truth source)
**Updated:** 2026-03-24 (Phase 70 closeout aligned)

## Formal Role

- 本文件是 docs / fixtures / generated / implementation 同步方向的正式 baseline 真源。
- `Phase 2.6` 起，external boundary family 不能再只靠 implementation 口头约定；必须声明 authority source、fixture family 与 drift guard。
- `Phase 7.2` 起，architecture enforcement 也必须遵守同一 authority order：north-star / baseline 先裁决，再由 helper / script / tests / CI 执行。
- 后续 phase 只能扩展 authority families 或补充验证证据，不能绕开本文件另造平行真相。

## Authority Sources

| Artifact Family | Authority Source | Sync Direction | Notes |
|-----------------|------------------|----------------|-------|
| 终态架构原则 | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` | north-star -> planning/docs/code review | 终态判断真源 |
| 基准资产 | `.planning/baseline/*.md` | baseline -> phase design / review / verification | downstream phase docs 只能解释或扩展，不能反向改写 |
| architecture enforcement policy | `.planning/baseline/ARCHITECTURE_POLICY.md` | baseline -> helpers / scripts / meta guards / CI | `Phase 7.2` 起的执行型 policy truth，不得被 tests/scripts 倒逼改写 |
| 项目目标与阶段路线 | `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` | planning -> phase execution | GSD 执行真源 |
| promoted phase evidence allowlist | `.planning/reviews/PROMOTED_PHASE_ASSETS.md` | roadmap/verification/reviews -> manifest -> governance closeout / phase-history guards | `.planning/phases/**` 默认是 execution-trace；未被 allowlist 列出的 summary/verification/validation 不得自动升级为 current truth |
| machine-readable governance truth | `.planning/baseline/GOVERNANCE_REGISTRY.json` | registry -> public docs / contributor templates / governance tests | 只承载 active governance facts；archive snapshots 与 milestone evidence 不能反向升级成 current truth |
| archive milestone snapshots / evidence | `.planning/MILESTONES.md`, `.planning/milestones/*.md`, `.planning/v1.12-MILESTONE-AUDIT.md`, `.planning/v1.13-MILESTONE-AUDIT.md`, `.planning/v1.14-MILESTONE-AUDIT.md`, `.planning/v1.15-MILESTONE-AUDIT.md`, `.planning/v1.16-MILESTONE-AUDIT.md`, `.planning/v1.17-MILESTONE-AUDIT.md`, `.planning/v1.18-MILESTONE-AUDIT.md`, `.planning/v1.6-MILESTONE-AUDIT.md`, `.planning/v1.5-MILESTONE-AUDIT.md`, `.planning/reviews/V1_12_EVIDENCE_INDEX.md`, `.planning/reviews/V1_13_EVIDENCE_INDEX.md`, `.planning/reviews/V1_14_EVIDENCE_INDEX.md`, `.planning/reviews/V1_15_EVIDENCE_INDEX.md`, `.planning/reviews/V1_16_EVIDENCE_INDEX.md`, `.planning/reviews/V1_17_EVIDENCE_INDEX.md`, `.planning/reviews/V1_18_EVIDENCE_INDEX.md`, `.planning/reviews/V1_6_EVIDENCE_INDEX.md`, `.planning/reviews/V1_5_EVIDENCE_INDEX.md` | archive evidence -> audit / handoff / historical review | 历史追溯与 continuity 证据；不是 active governance truth；latest pull-only closeout pointer 当前是 `V1_18_EVIDENCE_INDEX.md`，当前无 active milestone route，下一步治理动作是 `$gsd-new-milestone` |
| 当前工程落地说明 | `docs/developer_architecture.md` | codebase/planning -> developer docs | 当前态解释真源，不凌驾于 baseline 之上 |
| 本地 codebase maps | `.planning/codebase/README.md`, `.planning/codebase/*.md` | governance truth -> derived collaboration maps -> contributor navigation | 只允许派生解释，不得升级为 baseline/review/roadmap/state 的平行 authority chain |
| 文件治理状态 | `.planning/reviews/FILE_MATRIX.md` | execution -> governance review | file-level governance truth |
| 残留状态 | `.planning/reviews/RESIDUAL_LEDGER.md` | execution -> cleanup / audit | compat/residual 真源 |
| 删除裁决 | `.planning/reviews/KILL_LIST.md` | execution -> cleanup / audit | kill decision 真源 |
| 协议样例 / fixtures | `tests/fixtures/api_contracts/` | baseline/contracts -> fixtures -> contract tests | 必须脱敏，禁止真实敏感数据 |
| protocol boundary decoder families | `.planning/phases/07.1-protocol-boundary-schema-decoder/07.1-01-BOUNDARY-INVENTORY.md`, `custom_components/lipro/core/protocol/boundary/`, `tests/fixtures/protocol_boundary/`, `tests/fixtures/api_contracts/` | boundary inventory -> schema registry -> decoder families -> replay-ready fixtures -> protocol tests / telemetry / replay assets | REST/MQTT decode authority 必须登记到单一 boundary family home |
| runtime telemetry exporter family | `custom_components/lipro/core/telemetry/`, `custom_components/lipro/control/telemetry_surface.py`, `.planning/phases/07.3-runtime-telemetry-exporter/07.3-VALIDATION.md`, `07.3-01/02-SUMMARY.md` | runtime/protocol signals -> exporter contracts/views -> diagnostics/system-health/developer/replay/evidence consumers | exporter 只拥有 observer-only telemetry truth |
| replay manifest + run summary families | `tests/fixtures/protocol_replay/`, `tests/fixtures/api_contracts/`, `tests/fixtures/protocol_boundary/`, `tests/harness/protocol/`, `tests/integration/test_protocol_replay_harness.py`, `07.4-01/02/03-SUMMARY.md` | authority fixtures -> replay manifests -> deterministic driver -> replay assertions / run summary | replay manifests 只能索引 authority payload |
| v1.1 closeout evidence index | `.planning/baseline/AUTHORITY_MATRIX.md`, `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/RESIDUAL_LEDGER.md`, `.planning/reviews/KILL_LIST.md`, `.planning/phases/07.3-runtime-telemetry-exporter/`, `.planning/phases/07.4-protocol-replay-simulator-harness/` | governance truth + phase evidence -> `V1_1_EVIDENCE_INDEX.md` -> Phase 8 pull-only packaging inputs | evidence index 只是稳定指针，不得反向定义新真相 |
| AI debug evidence pack family | `custom_components/lipro/core/telemetry/`, `tests/harness/protocol/`, `.planning/phases/07.1-protocol-boundary-schema-decoder/07.1-01-BOUNDARY-INVENTORY.md`, `.planning/reviews/V1_1_EVIDENCE_INDEX.md`, `.planning/baseline/AUTHORITY_MATRIX.md`, `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/RESIDUAL_LEDGER.md` | formal telemetry/replay/boundary/governance truths -> `tests/harness/evidence_pack/` collector/redaction/schema -> `scripts/export_ai_debug_evidence_pack.py` -> `ai_debug_evidence_pack.json` / `ai_debug_evidence_pack.index.md` | assurance/tooling only；只允许 pull 正式真源 |
| runtime device registry read surface | `custom_components/lipro/core/coordinator/runtime/state/reader.py`, `custom_components/lipro/core/coordinator/coordinator.py`, `custom_components/lipro/core/coordinator/services/{state_service,device_refresh_service}.py`, `.planning/phases/09-residual-surface-closure/09-02-SUMMARY.md` | runtime state containers -> read-only mapping view -> coordinator/service/platform consumers/tests | `Phase 9` 起，`devices` formal public surface 必须通过 read-only view 暴露 |
| control/runtime service boundary contract | `custom_components/lipro/control/{runtime_access.py,service_router_support.py}`, `custom_components/lipro/runtime_infra.py`, `custom_components/lipro/services/{device_lookup.py,maintenance.py}`, `.planning/phases/43-control-services-boundary-decoupling-and-typed-runtime-access/43-01/02/03-SUMMARY.md` | service call / diagnostics inputs -> service-facing target resolution + typed runtime projection -> control/runtime listener & lookup homes -> focused control/service/meta guards | `services/` helpers 只能 shape service-facing inputs；typed runtime projection、最终 `(device, coordinator)` lookup 与 device-registry listener ownership 不得回流到 helper layer |
| outlet power primitive | `custom_components/lipro/core/device/device.py`, `custom_components/lipro/core/coordinator/outlet_power.py`, `custom_components/lipro/sensor.py`, `custom_components/lipro/control/diagnostics_surface.py`, `.planning/phases/17-final-residual-retirement-typed-contract-tightening-and-milestone-closeout/17-02-SUMMARY.md` | protocol/runtime payload -> `LiproDevice.outlet_power_info` -> entity / diagnostics / runtime consumers | formal truth 只承认 single-row primitive 与 explicit list contract；synthetic wrapper 已退场 |
| auth/session snapshot contract | `custom_components/lipro/core/auth/manager.py::AuthSessionSnapshot`, `custom_components/lipro/core/auth/manager.py::LiproAuthManager`, `custom_components/lipro/config_flow.py`, `custom_components/lipro/entry_auth.py`, `.planning/phases/17-final-residual-retirement-typed-contract-tightening-and-milestone-closeout/17-02-SUMMARY.md` | protocol/auth login + refresh -> `AuthSessionSnapshot` -> HA adapters / token persistence / future hosts | raw login/result dict 不再是 authority truth；`get_auth_data()` compat projection 已退场 |
| generated artifacts | fixture families + canonical normalization rules | baseline/contracts -> fixture/snapshot truth -> generated expectation -> implementation review | 具体 family 由 `Phase 2.6` 明确登记 |
| share/support payload families | `tests/fixtures/external_boundaries/share_worker/`, `tests/fixtures/external_boundaries/support_payload/` | authority docs -> fixture families -> payload builders/services -> owning tests | `generated_at` / `timestamp` 等动态字段必须先 canonicalize |
| firmware trust-root/advisory families | `custom_components/lipro/firmware_support_manifest.json`, `tests/fixtures/external_boundaries/firmware/` | local trust root -> advisory remote -> adapters/tests | remote advisory 不能单独放宽 `certified` |
| diagnostics external endpoints | `tests/fixtures/api_contracts/` for `get_city/query_user_cloud`; `tests/fixtures/external_boundaries/diagnostics_capabilities/` for other endpoint families | protocol truth -> external-boundary fixtures -> diagnostics services/tests | `get_city/query_user_cloud` 不得复制第二套真源 |
| benchmark baseline contract | `tests/benchmarks/benchmark_baselines.json`, `scripts/check_benchmark_baseline.py`, `.github/workflows/ci.yml`, `CONTRIBUTING.md` | baseline/review docs -> benchmark baseline manifest -> benchmark artifact (`.benchmarks/benchmark.json`) -> compare script / CI / contributor guidance | warning threshold 只做 maintainer signal；failure threshold 才构成 schedule/manual benchmark lane 的 no-regression gate，且不进入 PR blocking lane |
| 测试期望 | `tests/**` | requirements/baseline -> implementation | 测试需跟随正式结构迁移 |
| 实现代码 | `custom_components/lipro/**` | north-star + planning -> code | 不是架构真源，只是实现载体 |

## Conflict Resolution

若出现口径冲突，优先级如下：

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/baseline/*.md`
3. `.planning/PROJECT.md` / `.planning/ROADMAP.md` / `.planning/STATE.md`
4. phase execution summaries / validation docs
5. tests / fixtures / implementation comments

## Synchronization Rule

按 artifact family 的正式同步方向执行：

- **docs**：`north-star -> baseline -> phase docs / developer docs`，实现与测试只能触发回写需求，不能静默改写文档真相。
- **fixtures**：`baseline/contracts -> fixture family -> owning tests`，fixture 漂移必须伴随 baseline、summary 或 validation 解释。
- **generated**：`fixture families + canonical normalization rules -> generated expectation -> implementation review`，禁止由实现临时输出反向定义真相。
- **implementation**：`north-star + baseline + tests -> code`，实现是载体，不是 authority source。
- **enforcement**：`baseline -> policy doc -> helpers/scripts/tests/CI`，脚本、测试与工作流只能执行规则，不能成为规则真源。

出现以下任一情况时，必须同步检查 authority matrix：

- 新增或删除正式 public surface
- phase 引入新的 fixture / generated artifact / shadow doc
- 旧 compat shell 被降级或删除
- 文档与实现出现双口径风险
- external-boundary truth 从“实现 folklore”升级为“formal contract”
- protocol-boundary decoder family 新增/升级/删除 family、version 或 authority source
- architecture policy 新增 rule family、例外、extension hook 或 CI gate

## Phase 20 Continuity Note

- `Phase 20` 只允许扩充既有 `protocol boundary decoder families` 与 `replay manifest + run summary families` authority chain，不得改变 authority precedence。
- `rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 若落地，authority 仍必须收口到 boundary inventory、`custom_components/lipro/core/protocol/boundary/`、`tests/fixtures/api_contracts/`、`tests/fixtures/protocol_boundary/` 与 `tests/fixtures/protocol_replay/`，不得把 `schedule_codec.py`、`topics.py`、`message_processor.py`、`payload.py` 提升为第二 authority chain。
- `ROADMAP.md`、`REQUIREMENTS.md` 与 `STATE.md` 的 phase-complete 回写继续以 final gate 为前提；本文件只提前锁定 authority continuity，不提前宣告 Phase 20 已完成。

---
*Used by: external boundary formalization, architecture policy enforcement, docs hygiene, and audit arbitration*


## v1.2 Closeout Evidence Note

- `.planning/reviews/V1_2_EVIDENCE_INDEX.md` 是 `v1.2` closeout 的 pull-only evidence pointer；它只能索引 `Phase 18-24` verification/summaries、baseline/review ledgers 与 milestone audit，不得反向成为 authority source。
- `.planning/v1.2-MILESTONE-AUDIT.md` 记录的是 audit verdict / scorecard / evidence references，而不是实现 authority；若与 north-star、baseline 或 review ledgers 冲突，必须先修正上游真源。
- `.planning/v1.3-HANDOFF.md` 只记录下一轮 seed、defer 与 no-return zones；它不能覆盖 `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` / `.planning/STATE.md` 的当前 closeout truth。


## Phase 60 Tooling Truth Note

- `scripts/check_file_matrix.py` 与 `tests/meta/test_toolchain_truth.py` 现均为 thin runnable roots；它们只保留 single-entry contract，不再独占 inventory/classifier/validator 或 toolchain/release/docs/testing truth 主体。
- post-Phase-60 tooling topology 的正式 authority 继续锁定在 `.planning/reviews/FILE_MATRIX.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/codebase/TESTING.md` 与 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`。
- `scripts/check_file_matrix_{inventory,registry,markdown,validation}.py` 与 `tests/meta/toolchain_truth_*.py` 只承载 implementation / verification concerns，不得反向升级为第二套 governance prose。


## Phase 68 Authority Note

- `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py` 继续是 MQTT topic/payload decode 的唯一 canonical authority；`custom_components/lipro/core/mqtt/topics.py` 与 `custom_components/lipro/core/mqtt/message_processor.py` 只能通过 boundary-backed adapter / staged consumer 读取该 authority，不得各自长出 second truth。
- `custom_components/lipro/core/telemetry/models.py` 继续是 outward telemetry contract home；`outcomes.py` / `json_payloads.py` 只是 inward helper modules，必须经 `models.py` re-export 或 inward compose，而不能自立 authority chain。
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 是 `Phase 68` summary/verification/validation 资产的唯一 allowlist；`68-VERIFICATION.md` 只索引 executed proof，不得反向改写 current governance truth。

## Phase 70 Authority Note

- 当前可变 version / route truth 只允许停留在 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/GOVERNANCE_REGISTRY.json`、`docs/README.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md`；historical phase/evidence assets 继续只承担 frozen archive pointer 身份。
- `custom_components/lipro/control/runtime_access_support_{members,telemetry,views,devices}.py`、`custom_components/lipro/core/anonymous_share/share_client_{ports,refresh,submit}.py` 与 `custom_components/lipro/core/ota/query_support.py` 只是 implementation helpers；它们帮助 formal homes inward split，但不能反向升级为 public / governance / authority source。
