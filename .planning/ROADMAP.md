# Roadmap

## Milestones

- 🚧 **v1.37 Repo-Wide Terminal Audit, Hotspot Decomposition & Governance Continuity Decisions** - `Phase 129 -> 131` active on 2026-04-01; current route truth = `v1.37 active milestone route / starting from latest archived baseline = v1.36`; phase handoff = `active / phase 129 complete; phase 130 planning-ready (2026-04-01)`; next step = `$gsd-plan-phase 130`
- ✅ **v1.36 Terminal Residual Convergence, Runtime Access De-Reflection & Open-Source Readiness Hardening** - `Phase 126 -> 128` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.36`; evidence index = `.planning/reviews/V1_36_EVIDENCE_INDEX.md`
- ✅ **v1.35 Master Audit Closure, Public Surface Finalization & Release Traceability** - `Phase 122 -> 125` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.35`; evidence index = `.planning/reviews/V1_35_EVIDENCE_INDEX.md`
- ✅ **v1.34 Terminal Audit Closure, Contract Hardening & Governance Truth Slimming** - `Phase 120 -> 121` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.34`; evidence index = `.planning/reviews/V1_34_EVIDENCE_INDEX.md`
- ✅ **v1.33 MQTT Boundary Decoupling, Runtime Contract Unification & Release Governance Hardening** - `Phase 119` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.33`; evidence index = `.planning/reviews/V1_33_EVIDENCE_INDEX.md`
- ✅ **v1.32 Residual Hotspot Eradication, Validation Completion & Continuity Hardening** - `Phase 115 -> 118` archived on 2026-04-01; historical closeout route truth = `no active milestone route / latest archived baseline = v1.32`; evidence index = `.planning/reviews/V1_32_EVIDENCE_INDEX.md`
- ✅ **v1.31 Boundary Sealing, Governance Truth & Quality Hardening** - `Phase 111 -> 114` archived on 2026-03-31; historical closeout route truth = `no active milestone route / latest archived baseline = v1.31`; evidence index = `.planning/reviews/V1_31_EVIDENCE_INDEX.md`
- ✅ **v1.30 Protocol Hotspot Convergence, Transport De-friendization & Snapshot Surface Slimming** - `Phase 107 -> 110` archived on 2026-03-30; milestone audit: `.planning/v1.30-MILESTONE-AUDIT.md`; evidence index: `.planning/reviews/V1_30_EVIDENCE_INDEX.md`; snapshots archived at `.planning/milestones/v1.30-ROADMAP.md` / `.planning/milestones/v1.30-REQUIREMENTS.md`; historical closeout route truth = `no active milestone route / latest archived baseline = v1.30`

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
projection_targets:
- .planning/PROJECT.md
- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- .planning/STATE.md
- .planning/MILESTONES.md
active_milestone:
  version: v1.37
  name: Repo-Wide Terminal Audit, Hotspot Decomposition & Governance Continuity Decisions
  status: active / phase 129 complete; phase 130 planning-ready (2026-04-01)
  phase: '129'
  phase_title: rest fallback explicit-surface convergence and api hotspot slimming
  phase_dir: 129-rest-fallback-explicit-surface-convergence-and-api-hotspot-slimming
latest_archived:
  version: v1.36
  name: Terminal Residual Convergence, Runtime Access De-Reflection & Open-Source
    Readiness Hardening
  status: archived / evidence-ready (2026-04-01)
  phase: '128'
  phase_title: open-source readiness, benchmark-coverage gates, and maintainer continuity
    hardening
  phase_dir: 128-open-source-readiness-benchmark-coverage-gates-and-maintainer-continuity-hardening
  audit_path: .planning/v1.36-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_36_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.35
  name: Master Audit Closure, Public Surface Finalization & Release Traceability
  evidence_path: .planning/reviews/V1_35_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.37 active milestone route / starting from latest archived baseline
    = v1.36
  default_next_command: $gsd-plan-phase 130
  latest_archived_evidence_pointer: .planning/reviews/V1_36_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->
## Overview

`v1.37` 以 archived baseline `v1.36` 为起点，先用 `Phase 129` 收口 `rest_facade.py` / `status_fallback_support.py` 的显式组合与 fallback hotspot，再用 `Phase 130` 继续 inward split `command_runtime.py` / `firmware_update.py` 的 multi-topic formal homes，最后由 `Phase 131` 固化 repo-wide terminal audit 报告、governance continuity decision boundary 与 final validation evidence。

**Coverage:** `12/12` `v1.37` requirements mapped exactly once.
**Default next command:** `$gsd-plan-phase 130`

## Current Milestone

## v1.37: Repo-Wide Terminal Audit, Hotspot Decomposition & Governance Continuity Decisions

**Milestone status:** `active / phase 129 complete; phase 130 planning-ready (2026-04-01)`
**Default next command:** `$gsd-plan-phase 130`
**Current route story:** `v1.37 active milestone route / starting from latest archived baseline = v1.36`
**Latest archived pointer:** `.planning/reviews/V1_36_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.36-MILESTONE-AUDIT.md`
**Starting baseline snapshots:** `.planning/milestones/v1.36-ROADMAP.md`, `.planning/milestones/v1.36-REQUIREMENTS.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Phases

- [x] **Phase 129: rest fallback explicit-surface convergence and api hotspot slimming** - 已完成 `rest_facade.py` / `status_fallback_support.py` 的显式组合化瘦身、focused regression 冻结与 active-route sync。 (complete 2026-04-01)
- [ ] **Phase 130: runtime command and firmware-update hotspot decomposition** - 继续 inward split `command_runtime.py` / `entities/firmware_update.py`，把 runtime/entity hotspot 压回更窄 policy/helper seams。
- [ ] **Phase 131: repo-wide terminal audit closeout and governance continuity decisions** - 产出终极审阅报告、统一 current docs/governance truth，并把 external continuity/private-fallback debt 诚实 codify 为 decision boundary。

## Phase Details

### Phase 129: rest fallback explicit-surface convergence and api hotspot slimming
**Goal:** 把 REST fallback query 支撑与 REST façade 的显式 surface 继续压回更清晰的 formal seams：减少 generic delegation / helper 魔法，保持 `LiproRestFacade` 的组合边界更可读，同时让 binary-split fallback setup/behavior 更易验证。
**Depends on:** latest archived baseline `v1.36`
**Requirements**: ARC-40, HOT-59, TST-50, QLT-52
**Success Criteria** (what must be TRUE):
  1. `custom_components/lipro/core/api/rest_facade.py` 的 façade surface 更显式，减少 generic property/method factory 对正式 surface 的遮蔽，审阅者可以直接看到 collaborator wiring 与 outward wrapper 对应关系。
  2. `custom_components/lipro/core/api/status_fallback_support.py` 的 primary-query path、fallback setup、context / accumulator 职责更清晰，且不会长出第二条 API/query story。
  3. `tests/core/api/test_protocol_contract_facade_runtime.py`、`tests/core/api/test_api_status_service_fallback.py` 与相关 focused regressions 会在 façade surface 回到 helper magic、或 fallback 语义回退时直接失败。
  4. v1.37 active route docs / phase assets 能诚实记录 touched hotspot、验证范围与 remaining debt，不与 archived v1.36 selector truth 冲突。
**Plans:** 2/2 complete — `129-01` rest façade explicit surface、`129-02` fallback seam tightening
**Execution summaries**: `129-01-SUMMARY.md`, `129-02-SUMMARY.md`
**Verification**: `129-VERIFICATION.md`
**Validation**: `129-VALIDATION.md`

### Phase 130: runtime command and firmware-update hotspot decomposition
**Goal:** 沿既有 single-mainline runtime/entity architecture 继续 inward split `command_runtime.py` 与 `firmware_update.py` 的 multi-topic logic，把 policy、translation、result-shaping 与 fallback gating 压到更窄 formal helpers。
**Depends on:** Phase 129
**Requirements**: ARC-41, HOT-60, TST-51
**Success Criteria** (what must be TRUE):
  1. `custom_components/lipro/core/coordinator/runtime/command_runtime.py` 的命令执行、失败摘要、trace/metrics 与确认协作边界更清晰，不再把多主题逻辑堆在同一 formal home 中。
  2. `custom_components/lipro/entities/firmware_update.py` 的 OTA/version/fallback 逻辑继续 inward decomposition，entity 保持 thin projection 而非隐性 second logic hub。
  3. Focused/full suites 会在 runtime/entity outward behavior 或 typed contract 漂移时直接失败。
**Plans:** 0 plans

### Phase 131: repo-wide terminal audit closeout and governance continuity decisions
**Goal:** 以 v1.37 的 code/debt truth 为基础，产出 repo-wide terminal audit closeout：把全仓发现、热点排序、governance continuity 决策边界、开源不足与 validation evidence 统一为一条诚实 current story。
**Depends on:** Phase 130
**Requirements**: AUD-06, GOV-87, DOC-16, OSS-18, QLT-53
**Success Criteria** (what must be TRUE):
  1. 终极审阅报告覆盖 Python/docs/config/governance 主要切面，并把问题、优先级、修复状态与 remaining debt 明确落表。
  2. `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、关键 docs 与 final report 对 active route / latest archived baseline / external decision boundary 讲同一条 current story。
  3. repo-internal 可修项与 repo-external 现实 debt 明确分流：前者有代码/文档/测试证据，后者明确保留为 honest unresolved governance boundary。
  4. validation evidence 会冻结本轮 touched hotspots、repo-wide audit truth 与 docs/governance selector 一致性。
**Plans:** 0 plans

## Latest Archived Milestone

## v1.36: Terminal Residual Convergence, Runtime Access De-Reflection & Open-Source Readiness Hardening

**Milestone status:** `archived / evidence-ready (2026-04-01)`
**Default next command:** `$gsd-new-milestone`
**Current route story:** `no active milestone route / latest archived baseline = v1.36`
**Latest archived pointer:** `.planning/reviews/V1_36_EVIDENCE_INDEX.md`
**Current audit artifact:** `.planning/v1.36-MILESTONE-AUDIT.md`
**Starting baseline snapshots:** `.planning/milestones/v1.35-ROADMAP.md`, `.planning/milestones/v1.35-REQUIREMENTS.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Phases

- [x] **Phase 126: service-router developer callback-home convergence and diagnostics helper residual slimming** - 已完成 diagnostics helper inward thinning：`handlers.py` 直连 mechanics home、`helpers.py` 删除未使用 duplicate helper、`developer_router_support.py` 复用统一 iterator builder，并同步 v1.36 route / plan / verification truth。 (complete 2026-04-01)
- [x] **Phase 127: runtime-access de-reflection, typed runtime entry contracts, and hotspot continuation** - 已完成 `runtime_access` typed telemetry seam 收口、support-view de-reflection 与 focused/full verification 证据冻结，control/runtime seam 不再依赖 stringly dict fallback 或 `type(...).__getattribute__` 反射。 (complete 2026-04-01)
- [x] **Phase 128: open-source readiness, benchmark-coverage gates, and maintainer continuity hardening** - 已把 private-access / single-maintainer continuity / security fallback 限制诚实 codify，并把 coverage baseline diff、benchmark smoke、strict markers 与 final evidence freeze 固化为 archived evidence chain。 (complete 2026-04-01)

## Previous Archived Milestone

## v1.35: Master Audit Closure, Public Surface Finalization & Release Traceability

**Milestone status:** `archived / evidence-ready (2026-04-01)`
**Default next command:** `$gsd-new-milestone`
**Current route story:** `no active milestone route / latest archived baseline = v1.35`
**Latest archived pointer:** `.planning/reviews/V1_35_EVIDENCE_INDEX.md`
**Current audit artifact:** `.planning/v1.35-MILESTONE-AUDIT.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.35`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.34`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Phases

- [x] **Phase 122: master audit ledger, public first-hop boundary finalization, metadata traceability, and focused guard sealing** - 已完成 repo-wide audit ledger 落表、public first-hop / maintainer appendix 边界收口、tagged-release metadata traceability 与 focused guards 加固，并提升为 archived evidence chain。 (complete 2026-04-01)
- [x] **Phase 123: service-router family reconvergence, control-plane locality tightening, and public architecture hygiene** - 已完成 `service_router` non-diagnostics callback family reconvergence、public architecture/changelog drift cleanup、governance/file-matrix/focused guards 同步冻结，并提升为 archived evidence chain。 (complete 2026-04-01)
- [x] **Phase 124: config-entry auth seed normalization, config-flow adapter thinning, and schedule contract closure** - 已完成 auth-seed truth closure、config-flow thin-adapter 收敛、schedule direct-call contract single-source 化与 closeout freeze，并提升为 archived evidence chain。 (complete 2026-04-01)
- [x] **Phase 125: terminal residual eradication, runtime-types decomposition, adapter final thinning, and machine-readable governance extraction** - 已完成 runtime/service contract dedupe、flow/auth private-helper thinning、registry-backed governance truth 与 docs/evidence freeze，并提升为 archived evidence chain。 (complete 2026-04-01)

## Phase Details

### Phase 122: master audit ledger, public first-hop boundary finalization, metadata traceability, and focused guard sealing
**Goal**: 把全仓 Python/docs/config/governance 的终审残留压成单一 active route：repo-wide audit ledger 成为唯一落表真源，公开 first-hop 更清晰、maintainer appendix 不再抢 first-hop 叙事，metadata URL 能追溯到 tagged release，而 focused guards 会冻结这些 truth。
**Depends on**: latest archived baseline `v1.34`
**Requirements**: AUD-05, DOC-12, OSS-16, GOV-81, TST-44
**Success Criteria** (what must be TRUE):
  1. 审阅者可以在单一 audit ledger 中看到全仓 Python/docs/config/governance 剩余项、归类、处置状态与对应落点，而不必再拼接多份 phase folklore。
  2. 公开文档的 first-hop 入口在首屏即清晰可见；maintainer appendix 只作为附录深链存在，不再与 contributor / user first-hop 并列竞争。
  3. 对外 metadata URL 与 release-facing 文档可追溯到 semver/tagged release truth，不再出现无法说明 provenance 的 generic 或 milestone-labeled 指针。
  4. Focused guards / meta tests 会在 audit ledger 缺项、first-hop 边界回流、appendix 抢占 first-hop 或 metadata traceability 漂移时直接失败。
**Plans**: 3/3 complete — `122-01` audit ledger & route truth、`122-02` public first-hop / appendix boundary cleanup、`122-03` metadata traceability & focused guards
**Execution summaries**: `122-01-SUMMARY.md`, `122-02-SUMMARY.md`, `122-03-SUMMARY.md`
**Verification**: `122-VERIFICATION.md`

### Phase 123: service-router family reconvergence, control-plane locality tightening, and public architecture hygiene
**Goal**: 把 `service_router` family 的过薄 non-diagnostics split 正式回收为单一 control-local callback home，同时刷新 developer/public architecture 叙事、governance/file-matrix 投影与 focused guards，消除 control-plane topology 的代码/文档/守卫漂移。
**Depends on**: Phase 122
**Requirements**: ARC-34, HOT-54, DOC-13, GOV-82, TST-45
**Success Criteria** (what must be TRUE):
  1. `custom_components/lipro/control/service_router_handlers.py` 重新成为 command / schedule / share / maintenance callback family 的单一 control-local home，而 `service_router_diagnostics_handlers.py` 继续作为 developer/diagnostics 独立 collaborator。
  2. 四个过薄的 split shells（command / schedule / share / maintenance）已删除，且 file-matrix、tests、docs 不再把它们当作 current topology。
  3. `docs/developer_architecture.md`、`CHANGELOG.md`、`.planning/codebase/ARCHITECTURE.md` 与 `docs/architecture_archive.md` 对当前/历史 topology 的叙事一致，不再保留过期 archived-only route 或 stale split-family 现状。
  4. Focused guards / file-matrix / planning route truth 会在 reconvergence 回退、stale path 回流或 current-topology 文案漂移时直接失败。
**Plans**: 3/3 complete — `123-01` route reopen & phase assets、`123-02` service-router reconvergence、`123-03` docs/governance freeze refresh
**Execution summaries**: `123-01-SUMMARY.md`, `123-02-SUMMARY.md`, `123-03-SUMMARY.md`
**Verification**: `123-VERIFICATION.md`

### Phase 124: config-entry auth seed normalization, config-flow adapter thinning, and schedule contract closure
**Goal**: 把 `service_router` reconvergence 之后仍残留在 control-plane 的 auth/flow/schedule contract 漏口一次性收口：persisted auth seed 语义只保留单一 formal helper、`config_flow.py` 根层继续压回 thin adapter、`schedule` direct-call path 与 registry schema 共享同一 contracts truth。
**Depends on**: Phase 123
**Requirements**: ARC-35, HOT-55, ARC-36, GOV-83, TST-46
**Success Criteria** (what must be TRUE):
  1. `entry_auth.py` 成为 persisted auth seed（password-hash / remember flag / biz_id）的唯一解释/回写真源，cleared state 不会再被旧 entry 数据复活。
  2. `config_flow.py` 的 user / reauth / reconfigure orchestration 已 inward 到 `flow/` formal home，根层只保留 HA adapter glue 与 unique-id/update wiring。
  3. `services/contracts.py` 为 schedule direct-call 提供 normalization/result typing；`services/schedule.py` 不再依赖 handler-local ad-hoc dict。
  4. Focused tests、file-matrix、route docs、baseline/testing/codebase docs 会在 auth-seed drift、config-flow 回胖、schedule contract 回退或 route truth 停在 `Phase 123` 时直接失败。
**Plans**: 5/5 complete — `124-01` route truth & phase assets、`124-02` auth-seed truth / config-flow thinning、`124-03` schedule contract、`124-04` closeout route/governance freeze、`124-05` codebase/evidence freeze
**Execution summaries**: `124-01-SUMMARY.md`, `124-02-SUMMARY.md`, `124-03-SUMMARY.md`, `124-04-SUMMARY.md`, `124-05-SUMMARY.md`, `124-SUMMARY.md`
**Verification**: `124-VERIFICATION.md`

### Phase 125: terminal residual eradication, runtime-types decomposition, adapter final thinning, and machine-readable governance extraction
**Goal**: 在 v1.35 closeout 前继续清零 remaining residual：拆解 `runtime_types.py` 的 cross-plane contract hub、继续压薄 `config_flow.py` / `entry_auth.py` adapter seam，并把 current-route/governance selector truth 提取为单一 machine-readable contract，再由 tests/tooling/docs 共同消费。
**Depends on**: Phase 124
**Requirements**: ARC-37, HOT-56, GOV-84, TST-47, QLT-49, DOC-14
**Success Criteria** (what must be TRUE):
  1. `runtime_types.py` 不再承担跨 runtime / protocol / service-facing families 的 mega contract hub 角色；formal contract families inward 到更窄 homes，outward import truth 仍可发现且不漂移。
  2. `config_flow.py` / `entry_auth.py` 进一步回到 thin adapter / bootstrap home，纯 pass-through orchestration、result shaping 与 transient auth helper 下沉到 `flow/` 或更窄 helper。
  3. `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 共用同一 machine-readable governance current-route contract，而不再手写五份近似 selector。
  4. `tests/meta` 与相关 checker 优先读取 machine-readable contract / focused manifest，减少 giant prose-heavy wording guards；route 语义不变时不再因文案微调大面积炸测。
  5. `FILE_MATRIX`、codebase docs、maintainer docs 与 focused no-regrowth guards 共同冻结新的 residual topology，v1.35 只有在这些 guard 与 Phase 125 verification 通过后才允许 closeout。
**Plans**: 5/5 complete — summaries + verification written

## Archived Highlights

- repo-wide audit ledger、public first-hop boundary、tagged-release metadata traceability 与 focused guards 已冻结为 `v1.35` archived baseline 的治理主线。
- `service_router` family reconvergence、auth-seed / config-flow thin-adapter 与 schedule contract single-source truth 已不再依赖 closeout-ready live wording 才能成立。
- `runtime_types.py` downstream shadow contracts 已删除；`PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 现通过 registry-owned contract 共享 archived selector truth。
- latest archived evidence index、milestone audit、archived snapshots 与 promoted phase bundles 现形成 pull-only closeout chain；下一步只能经 `$gsd-new-milestone` 建立新路线。

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 122. master audit ledger, public first-hop boundary finalization, metadata traceability, and focused guard sealing | 3/3 | Complete | 2026-04-01 |
| 123. service-router family reconvergence, control-plane locality tightening, and public architecture hygiene | 3/3 | Complete | 2026-04-01 |
| 124. config-entry auth seed normalization, config-flow adapter thinning, and schedule contract closure | 5/5 | Complete | 2026-04-01 |
| 125. terminal residual eradication, runtime-types decomposition, adapter final thinning, and machine-readable governance extraction | 5/5 | Complete | 2026-04-01 |

## Previous Archived Milestone (v1.34)
## v1.34: Terminal Audit Closure, Contract Hardening & Governance Truth Slimming

**Milestone status:** `archived / evidence-ready (2026-04-01)`
**Default next command:** `$gsd-new-milestone`
**Current route story:** `no active milestone route / latest archived baseline = v1.34`
**Latest archived pointer:** `.planning/reviews/V1_34_EVIDENCE_INDEX.md`
**Current audit artifact:** `.planning/v1.34-MILESTONE-AUDIT.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.34`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.33`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Phases

- [x] **Phase 120: terminal audit closure, contract hardening, and governance truth slimming** - 已完成 runtime/service contract tightening、flow error taxonomy hardening、toolchain/docs/governance truth slimming，并把 live route 收敛为 archived milestone proof。 (complete 2026-04-01)
- [x] **Phase 121: residual contract closure, flow invariant tightening, and surface hygiene cleanup** - 已完成 runtime-access raw-coordinator seam closure、auth-session projection fail-closed、existing-entry validator dedupe、changed-surface route de-phaseization，并提升到 archived evidence chain。 (complete 2026-04-01)

## Archived Highlights

- `runtime_types.py` / `services/contracts.py` / `services/command.py` 的 typed contract truth 已冻结为 v1.34 archived baseline 的正式 runtime/service mainline。
- `runtime_access` read-model、diagnostics projection 与 developer helper routing 已退出 raw-coordinator leakage，control-plane 只保留 explicit fact-only surface。
- config-flow taxonomy、auth projection fail-closed 与 existing-entry invariant dedupe 已形成稳定 flow contract，不再保留 silent default 与 duplicated validation 路径。
- `scripts/lint` changed-surface assurance、`FILE_MATRIX`、`TESTING.md`、`ROADMAP / REQUIREMENTS / STATE / PROJECT` 共同承认 `v1.34` archived-only selector truth。

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 120. terminal audit closure, contract hardening, and governance truth slimming | 3/3 | Complete | 2026-04-01 |
| 121. residual contract closure, flow invariant tightening, and surface hygiene cleanup | 3/3 | Complete | 2026-04-01 |

## Previous Archived Milestone (v1.33)
## v1.33: MQTT Boundary Decoupling, Runtime Contract Unification & Release Governance Hardening

**Milestone status:** `archived / evidence-ready (2026-04-01)`
**Default next command:** `$gsd-new-milestone`
**Current route story:** `no active milestone route / latest archived baseline = v1.33`
**Latest archived pointer:** `.planning/reviews/V1_33_EVIDENCE_INDEX.md`
**Current audit artifact:** `.planning/v1.33-MILESTONE-AUDIT.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.33`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.32`
**Historical next command before next milestone kickoff:** `$gsd-new-milestone`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Phases

- [x] **Phase 119: MQTT boundary, runtime contract, and release governance hardening** - 已一次性收口 MQTT boundary cycle、runtime contract duplication、release tag namespace collision 与 governance/changelog freshness。 (complete 2026-04-01)

## Phase Details

### Phase 119: MQTT boundary, runtime contract, and release governance hardening
**Goal**: MQTT decode authority 必须恢复 `protocol.boundary -> mqtt` 单向依赖；runtime/service handlers 必须回到 `runtime_types.py` 单一 contract truth；release workflow / governance route helper / `CHANGELOG.md` 必须只讲 semver public release + current active route 的一条故事。
**Depends on**: latest archived baseline `v1.32`
**Requirements**: ARC-30, ARC-31, GOV-76, GOV-77, TST-41
**Success Criteria** (what must be TRUE):
  1. `mqtt_decoder.py` 不再反向 import `mqtt.payload` / `mqtt.topics`；`payload.py`、`topics.py` 与 `message_processor.py` 直接复用 boundary decode/support，且 focused guards 会阻断 lazy-import regression。
  2. `runtime_types.py` 覆盖 `auth_service` / `command_service` 的 service-facing contract；`services/execution.py`、`services/command.py` 与 `control/entry_lifecycle_support.py` 不再保留平行 Protocol 或 concrete coordinator typing。
  3. `release.yml` 与 `codeql.yml` 只在 semver tag 上触发；governance route helper 不再硬编码当前 contract；`CHANGELOG.md` 与 runbook/docs 只暴露当前 public release / archived evidence 的正式 story。
  4. Focused tests / guards / docs 证明上述 contract，同一轮通过最小充分验证集。
**Status**: Complete (`2026-04-01`)
**Plans**: 3/3 complete
**Plan assets**: `119-01-PLAN.md`, `119-02-PLAN.md`, `119-03-PLAN.md`
**Summary assets**: `119-01-SUMMARY.md`, `119-02-SUMMARY.md`, `119-03-SUMMARY.md`, `119-SUMMARY.md`
**Verification**: `119-VERIFICATION.md`
**Closeout proof**: `119-01` 已交付 MQTT boundary 单向 authority 与 focused guard 冻结；`119-02` 已交付 runtime/service contract single-source truth；`119-03` 已交付 semver-only release namespace、canonical governance route helper 与 docs/changelog freshness 收口。

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 119. MQTT boundary, runtime contract, and release governance hardening | 3/3 | Complete | 2026-04-01 |


## Previous Archived Milestone (v1.32)

## v1.32: Residual Hotspot Eradication, Validation Completion & Continuity Hardening

> `v1.32` 沿 `v1.31` latest archived baseline 的唯一 north-star 主线，把 `Phase 115 -> 118` 的 hotspot / validation / continuity 修复收口为 archived-only baseline，而不再承担当前 active route selector。

**Milestone Goal:** 已把 `v1.31` 已诚实登记的 remaining hotspots、validation backfill 与 continuity hardening 收口为同一条 archived baseline：在 `Phase 115 -> 117` 已完成 contract freeze / continuity repair 的基础上，`Phase 118` 进一步完成了 route truth sync、remaining hotspot decomposition 与 phase-local validation closure。
**Milestone status:** `archived / evidence-ready (2026-04-01)`
**Starting baseline:** `.planning/v1.31-MILESTONE-AUDIT.md`, `.planning/reviews/V1_31_EVIDENCE_INDEX.md`, `.planning/milestones/v1.31-ROADMAP.md`, `.planning/milestones/v1.31-REQUIREMENTS.md`
**Requirements basket:** `HOT-48`, `HOT-49`, `HOT-50`, `HOT-51`, `TST-39`, `TST-40`, `GOV-73`, `GOV-75`
**Latest archived baseline:** `v1.32`
**Latest archived pointer:** `.planning/reviews/V1_32_EVIDENCE_INDEX.md`
**Current route mode at closeout:** `no active milestone route / latest archived baseline = v1.32`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.32`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.31`
**Historical next command before v1.33 kickoff:** `$gsd-new-milestone`

### Phase 115: Status-fallback query-flow normalization
**Goal**: `status_fallback` family 的入口语义必须在空输入、primary batch 与 fallback-depth 维度上保持单一正式 contract，不再允许 public entry 与 binary-split support 再次分叉。
**Depends on**: latest archived baseline `v1.31`
**Requirements**: HOT-48
**Status**: Complete (`2026-03-31`)
**Plans**: 1/1 complete
**Closeout assets**: `.planning/phases/115-status-fallback-query-flow-normalization/115-01-SUMMARY.md`, `.planning/phases/115-status-fallback-query-flow-normalization/115-SUMMARY.md`, `.planning/phases/115-status-fallback-query-flow-normalization/115-VERIFICATION.md`

### Phase 116: Anonymous-share and REST façade hotspot slimming
**Goal**: `AnonymousShareManager` 与 `LiproRestFacade` 继续 inward split，但 formal outward home、stable import shell 与 child-façade composition truth 保持不变。
**Depends on**: Phase 115
**Requirements**: HOT-49
**Status**: Complete (`2026-03-31`)
**Plans**: 3/3 complete
**Closeout assets**: `.planning/phases/116-anonymous-share-and-rest-fa-ade-hotspot-slimming/116-01-SUMMARY.md`, `.planning/phases/116-anonymous-share-and-rest-fa-ade-hotspot-slimming/116-02-SUMMARY.md`, `.planning/phases/116-anonymous-share-and-rest-fa-ade-hotspot-slimming/116-03-SUMMARY.md`, `.planning/phases/116-anonymous-share-and-rest-fa-ade-hotspot-slimming/116-SUMMARY.md`, `.planning/phases/116-anonymous-share-and-rest-fa-ade-hotspot-slimming/116-VERIFICATION.md`

### Phase 117: Validation backfill and continuity hardening
**Goal**: `Phase 112 -> 114` 的 validation / changed-surface / continuity proof 必须补齐，让 archived baseline 与下一条 active route 之间的 selector、runbook、evidence chain 继续保持单一 truth。
**Depends on**: Phase 116
**Requirements**: TST-39, GOV-73
**Status**: Complete (`2026-03-31`)
**Plans**: 3/3 complete
**Closeout assets**: `.planning/phases/117-validation-backfill-and-continuity-hardening/117-01-SUMMARY.md`, `.planning/phases/117-validation-backfill-and-continuity-hardening/117-02-SUMMARY.md`, `.planning/phases/117-validation-backfill-and-continuity-hardening/117-03-SUMMARY.md`, `.planning/phases/117-validation-backfill-and-continuity-hardening/117-SUMMARY.md`, `.planning/phases/117-validation-backfill-and-continuity-hardening/117-VERIFICATION.md`

### Phase 118: Final hotspot decomposition and validation closure
**Goal**: 把 `v1.32` 当前仍显著可由仓内直接修复的技术债一次性收口：修正 `Phase 118` live route truth、继续切薄 remaining formal-home hotspots，并回补 `115 -> 117` 的 phase-local validation contracts，让 `$gsd-next` 再次诚实返回 milestone closeout。
**Depends on**: Phase 117
**Requirements**: HOT-50, HOT-51, TST-40, GOV-75
**Status**: Complete (`2026-04-01`)
**Plans**: 3/3 complete
**Planning Assets**: `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-CONTEXT.md`, `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-RESEARCH.md`, `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-01-PLAN.md`, `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-01-SUMMARY.md`, `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-02-PLAN.md`, `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-02-SUMMARY.md`, `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-03-PLAN.md`, `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-03-SUMMARY.md`, `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-SUMMARY.md`, `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-VERIFICATION.md`, `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-VALIDATION.md`
**Archive promotion proof**: `118-01` 已交付 `GOV-75` route truth sync；`118-02` 已交付 hotspot decomposition；`118-03` 已交付 validation closure / audit refresh；`v1.32` 现已归档为 `no active milestone route / latest archived baseline = v1.32`。
## v1.31: Boundary Sealing, Governance Truth & Quality Hardening

> `v1.31` 沿 `v1.30` latest archived baseline 的唯一 north-star 主线，把 `Phase 111 -> 114` 的 boundary / governance / quality / honesty 修复收口为 closeout bundle，并翻转为 archived-only baseline。

**Milestone Goal:** 封印 entity/control → runtime concrete bypass、统一 formal-home discoverability 与治理锚点、继续 burn-down 当前热点，并把 open-source reachability / security continuity 的外部 blocker 诚实冻结为 pull-only archived truth。
**Milestone status:** `archived / evidence-ready (2026-03-31)`
**Starting baseline:** `.planning/v1.30-MILESTONE-AUDIT.md`, `.planning/reviews/V1_30_EVIDENCE_INDEX.md`, `.planning/milestones/v1.30-ROADMAP.md`, `.planning/milestones/v1.30-REQUIREMENTS.md`
**Requirements basket:** `ARC-28`, `ARC-29`, `GOV-71`, `GOV-72`, `QLT-46`, `TST-38`, `OSS-14`, `SEC-09`
**Latest archived baseline:** `v1.31`
**Latest archived pointer:** `.planning/reviews/V1_31_EVIDENCE_INDEX.md`
**Current route mode:** `no active milestone route / latest archived baseline = v1.31`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.31`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.30`
**Default next command:** `$gsd-new-milestone`
**Current follow-up target:** start next route with `$gsd-new-milestone`.

### Phase 111: Entity-runtime boundary sealing and dependency-guard hardening
**Goal**: Entity 与 control 消费者只经 sanctioned runtime public surface 协作，任何回流到 concrete runtime internals 的依赖漂移都会被自动拒绝。
**Depends on**: latest archived baseline `v1.30`
**Requirements**: ARC-28, GOV-71, TST-38
**Status**: Complete (`2026-03-31`)
**Plans**: 3/3 complete
**Closeout assets**: `.planning/phases/111-entity-runtime-boundary-sealing-and-dependency-guard-hardening/{111-01-SUMMARY.md,111-02-SUMMARY.md,111-03-SUMMARY.md,111-SUMMARY.md,111-VERIFICATION.md,111-VALIDATION.md}`

### Phase 112: Formal-home discoverability and governance-anchor normalization
**Goal**: sanctioned root homes、formal ownership 与治理文档共同讲一条当前主线故事，不再出现目录拓扑与 governance anchor 长期分叉。
**Depends on**: Phase 111
**Requirements**: ARC-29, GOV-72
**Status**: Complete (`2026-03-31`)
**Plans**: 3/3 complete
**Closeout assets**: `.planning/phases/112-formal-home-discoverability-and-governance-anchor-normalization/{112-01-SUMMARY.md,112-02-SUMMARY.md,112-03-SUMMARY.md,112-SUMMARY.md,112-VERIFICATION.md}`

### Phase 113: Hotspot burn-down and changed-surface assurance hardening
**Goal**: 当前 top-priority implementation hotspots 继续 inward split，或被 bounded no-regrowth guards 冻结，不再依赖“永久大型文件例外”叙事存活。
**Depends on**: Phase 112
**Requirements**: QLT-46
**Status**: Complete (`2026-03-31`)
**Plans**: 4/4 complete
**Closeout assets**: `.planning/phases/113-hotspot-burn-down-and-changed-surface-assurance-hardening/{113-01-SUMMARY.md,113-02-SUMMARY.md,113-03-SUMMARY.md,113-04-SUMMARY.md,113-SUMMARY.md,113-VERIFICATION.md,113-AUDIT.md}`

### Phase 114: Open-source reachability honesty and security-surface normalization
**Goal**: public metadata 与 security reporting 只陈述真实可达 surface，并把缺失的私有回报通道或 delegate continuity 明确保留为外部 blocker。
**Depends on**: Phase 113
**Requirements**: OSS-14, SEC-09
**Status**: Complete (`2026-03-31`)
**Plans**: 3/3 complete
**Closeout assets**: `.planning/phases/114-open-source-reachability-honesty-and-security-surface-normalization/{114-01-SUMMARY.md,114-02-SUMMARY.md,114-03-SUMMARY.md,114-SUMMARY.md,114-VERIFICATION.md,114-AUDIT.md}`
**Closeout evidence index**: `.planning/reviews/V1_31_EVIDENCE_INDEX.md`
**Milestone audit**: `.planning/v1.31-MILESTONE-AUDIT.md`

## Historical Phase Visibility Appendix

> 该附录只保留历史 phase 的可搜索锚点、计划计数与 archived milestone 索引，供治理守卫与审计追踪使用；它不重新激活任何旧 route，也不覆盖当前 `v1.32` active milestone story。

## v1.25: Hotspot Inward Decomposition, Typed Boundary Hardening & Redaction Convergence
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.25`

## v1.26: Terminal Architecture Audit Follow-through, Typed Mapping Retirement & Hotspot Decomposition
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.26`

| Phase | Milestone | Plans | Status | Date |
|-------|-----------|-------|--------|------|
| 16 Post-audit Truth Alignment, Hotspot Decomposition & Residual Endgame | v1.1 | 6/6 | Complete | 2026-03-15 |
| 17 Final Residual Retirement, Typed-Contract Tightening & Milestone Closeout | v1.1 | 4/4 | Complete | 2026-03-15 |

### Phase 16: Post-audit truth alignment, hotspot decomposition, and residual endgame
**Plans:** 6/6 complete across 3 waves

### Phase 17: Final residual retirement, typed-contract tightening and milestone closeout
**Plans:** 4/4 complete

### Phase 19: Headless Consumer Proof & Adapter Demotion
**Requirements**: [CORE-02]
**Status**: Complete (`2026-03-16`)
**Plans**: 4/4 complete

### Phase 30: Protocol/control typed contract tightening
**Status**: Complete (`2026-03-17`)
**Plans**: 3/3 complete

### Phase 31: Runtime/service typed budget and exception closure
**Status**: Complete (`2026-03-17`)
**Plans**: 4/4 complete

### Phase 43: Control-services boundary decoupling and typed runtime access
**Status**: Complete (`2026-03-20`)
**Plans**: 4/4 complete

### Phase 98: Carry-forward eradication, route reactivation, and closeout proof
**Status**: Complete (`2026-03-28`)
**Plans**: 3/3 complete

### Phase 99: Runtime hotspot support extraction and terminal audit freeze
**Status**: Complete (`2026-03-28`)
**Plans**: 3/3 complete

### Phase 100: MQTT runtime and schedule service support extraction freeze
**Status**: Complete (`2026-03-28`)
**Plans**: 3/3 complete

### Phase 103: Root adapter thinning, test topology second pass, and terminology contract normalization
**Status**: Complete (`2026-03-28`)
**Plans**: 3/3 complete

### Phase 104: Service-router family split and command-runtime second-pass decomposition
**Status**: Complete (`2026-03-30`)
**Plans**: 3/3 complete

### Phase 105: Governance rule datafication and milestone freeze
**Status**: Complete (`2026-03-30`)
**Plans**: 3/3 complete

### Phase 107: REST/auth/status hotspot convergence and support-surface slimming
**Status**: Complete (`2026-03-30`)
**Plans**: 3/3 complete

### Phase 108: MQTT transport-runtime de-friendization
**Status**: Complete (`2026-03-30`)
**Plans**: 3/3 complete

### Phase 109: Anonymous-share manager inward decomposition
**Status**: Complete (`2026-03-30`)
**Plans**: 3/3 complete

### Phase 110: Runtime snapshot surface reduction and milestone closeout
**Status**: Complete (`2026-03-30`)
**Plans**: 6/6 complete

