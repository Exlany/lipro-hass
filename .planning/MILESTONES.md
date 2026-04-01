# Milestones

## Latest Archived Milestone (v1.35)

**Name:** `Master Audit Closure, Public Surface Finalization & Release Traceability`
**Status:** `archived / evidence-ready (2026-04-01)`
**Current route:** `no active milestone route / latest archived baseline = v1.35`
**Phase range:** `122 -> 125`
**Progress:** `4/4 phases, 16/16 plans`
**Default next command:** `$gsd-new-milestone`
**Latest archived pointer:** `.planning/reviews/V1_35_EVIDENCE_INDEX.md`
**Archived audit:** `.planning/v1.35-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.35-ROADMAP.md`, `.planning/milestones/v1.35-REQUIREMENTS.md`

**Archived phase story:**

- `Phase 122`: master audit ledger, public first-hop boundary finalization, metadata traceability, and focused guard sealing ✅ (`122-01` ledger/route truth + `122-02` first-hop boundary cleanup + `122-03` metadata/guards complete)
- `Phase 123`: service-router family reconvergence, control-plane locality tightening, and public architecture hygiene ✅ (`123-01` route reopen/phase assets + `123-02` service-router reconvergence + `123-03` docs/governance freeze refresh complete)
- `Phase 124`: config-entry auth seed normalization, config-flow adapter thinning, and schedule contract closure ✅ (`124-01` route truth/assets + `124-02` auth-seed truth/config-flow thinning + `124-03` schedule contract + `124-04` closeout route/governance freeze + `124-05` codebase/evidence freeze complete)
- `Phase 125`: terminal residual eradication, runtime-types decomposition, adapter final thinning, and machine-readable governance extraction ✅ (`125-01` governance single-source + `125-02` runtime-types decomposition + `125-03` flow/auth thinning + `125-04` meta/tooling slimming + `125-05` docs/evidence freeze complete)

## Previous Archived Milestone (v1.34)

**Name:** `Terminal Audit Closure, Contract Hardening & Governance Truth Slimming`
**Status:** `archived / evidence-ready (2026-04-01)`
**Current route:** `no active milestone route / latest archived baseline = v1.34`
**Phase range:** `120 -> 121`
**Progress:** `2/2 phases, 6/6 plans`
**Default next command:** `$gsd-new-milestone`
**Latest archived pointer:** `.planning/reviews/V1_34_EVIDENCE_INDEX.md`
**Archived audit:** `.planning/v1.34-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.34-ROADMAP.md`, `.planning/milestones/v1.34-REQUIREMENTS.md`

**Archived phase story:**

- `Phase 120`: terminal audit closure, contract hardening, and governance truth slimming ✅
- `Phase 121`: residual contract closure, flow invariant tightening, and surface hygiene cleanup ✅

---

> Machine-readable bootstrap truth now lives in the shared `governance-route` contract block below; milestone chronology remains human-readable archive history instead of the parser-visible selector.

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
active_milestone: null
latest_archived:
  version: v1.35
  name: Master Audit Closure, Public Surface Finalization & Release Traceability
  status: archived / evidence-ready (2026-04-01)
  phase: '125'
  phase_title: terminal residual eradication, runtime-types decomposition, adapter
    final thinning, and machine-readable governance extraction
  phase_dir: 125-terminal-residual-eradication-runtime-types-decomposition-adapter-final-thinning-and-machine-readable-governance-extraction
  audit_path: .planning/v1.35-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_35_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.34
  name: Terminal Audit Closure, Contract Hardening & Governance Truth Slimming
  evidence_path: .planning/reviews/V1_34_EVIDENCE_INDEX.md
bootstrap:
  current_route: no active milestone route / latest archived baseline = v1.35
  default_next_command: $gsd-new-milestone
  latest_archived_evidence_pointer: .planning/reviews/V1_35_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->

## Latest Archived Milestone (v1.35)

**Phase range:** `122 -> 125`
**Phases completed:** `4/4 phases, 16/16 plans, 0 tasks`
**Status:** `archived / evidence-ready (2026-04-01)`
**Route truth:** `no active milestone route / latest archived baseline = v1.35`
**Latest archived baseline:** `v1.35`
**Default next command:** `$gsd-new-milestone`
**Route truth:** latest archived evidence index = `.planning/reviews/V1_35_EVIDENCE_INDEX.md`
**Current audit artifact:** `.planning/v1.35-MILESTONE-AUDIT.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.35`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.34`

**Archived phase story:**

- `Phase 122`: master audit ledger, public first-hop boundary finalization, metadata traceability, and focused guard sealing ✅ (`122-01` ledger/route truth + `122-02` first-hop boundary cleanup + `122-03` metadata/guards complete)
- `Phase 123`: service-router family reconvergence, control-plane locality tightening, and public architecture hygiene ✅ (`123-01` route reopen/phase assets + `123-02` service-router reconvergence + `123-03` docs/governance freeze refresh complete)
- `Phase 124`: config-entry auth seed normalization, config-flow adapter thinning, and schedule contract closure ✅ (`124-01` route truth/assets + `124-02` auth-seed truth/config-flow thinning + `124-03` schedule contract + `124-04` closeout route/governance freeze + `124-05` codebase/evidence freeze complete)
- `Phase 125`: terminal residual eradication, runtime-types decomposition, adapter final thinning, and machine-readable governance extraction ✅ (`125-01` governance single-source + `125-02` runtime-types decomposition + `125-03` flow/auth thinning + `125-04` meta/tooling slimming + `125-05` docs/evidence freeze complete)

**Archived accomplishments:**

- 完成 `Phase 122 -> 125` 全部计划与 closeout bundle，形成 `v1.35` latest archived baseline 的可审计证据链。
- 冻结 repo-wide audit ledger、service-router reconvergence、auth-seed/config-flow/schedule contract closure 与 machine-readable governance truth。
- 统一 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / docs / codebase maps / review ledgers` 的 archived-only selector truth，不再保留第二条 active story。

## Previous Archived Milestone (v1.34)
**Phase range:** `120 -> 121`
**Phases completed:** `2/2 phases, 6/6 plans, 0 tasks`
**Status:** `archived / evidence-ready (2026-04-01)`
**Route truth:** `no active milestone route / latest archived baseline = v1.34`
**Latest archived baseline:** `v1.34`
**Default next command:** `$gsd-new-milestone`
**Route truth:** latest archived evidence index = `.planning/reviews/V1_34_EVIDENCE_INDEX.md`
**Current audit artifact:** `.planning/v1.34-MILESTONE-AUDIT.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.34`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.33`

**Archived phase story:**

- `Phase 120`: terminal audit closure, contract hardening, and governance truth slimming ✅ (`120-01` runtime/service contract tightening + `120-02` flow/send-command semantics hardening + `120-03` tooling/docs/governance truth slimming complete)
- `Phase 121`: residual contract closure, flow invariant tightening, and surface hygiene cleanup ✅ (`121-01` runtime-access seam closure + `121-02` auth-session projection/validator hardening + `121-03` changed-surface guard de-phaseization complete)

**Archived accomplishments:**

- `runtime_types.py` / `services/contracts.py` / `services/command.py` 现以单一 typed truth 收口 service-facing runtime contract。
- control runtime read-model / diagnostics projection / developer routing 已退出 raw-coordinator leakage，formal control home 更诚实。
- config-flow taxonomy、auth-session projection fail-closed 与 existing-entry invariant dedupe 已形成稳定 outward contract。
- `FILE_MATRIX` / `TESTING.md` / current planning docs 与 live guard chain 已统一升级为 archived-only selector truth。

## Previous Archived Milestone (v1.33)
**Phase range:** `119 -> 119`
**Phases completed:** `1/1 phases, 3/3 plans, 0 tasks`
**Status:** `archived / evidence-ready (2026-04-01)`
**Route truth:** `no active milestone route / latest archived baseline = v1.33`
**Latest archived baseline:** `v1.33`
**Route truth:** latest archived evidence index = `.planning/reviews/V1_33_EVIDENCE_INDEX.md`
**Current audit artifact:** `.planning/v1.33-MILESTONE-AUDIT.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.33`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.32`

**Archived phase story:**

- `Phase 119`: MQTT boundary, runtime contract, and release governance hardening ✅ (`119-01` MQTT boundary authority + `119-02` runtime contract unification + `119-03` semver release/governance hardening complete)

**Archived accomplishments:**

- `protocol.boundary -> mqtt` 单向 authority、runtime/service contract 真源统一、release namespace hardening、governance/changelog freshness 已在同一 phase 内完成收口。
- `Coordinator` public home 继续固定为 `custom_components/lipro/coordinator_entry.py`；本轮只收敛 typing / contract truth，没有改写 public home。
- repo-external continuity 限制继续保持 honest blocker state，没有被伪造为仓内已闭环。

## v1.31 Boundary Sealing, Governance Truth & Quality Hardening (Shipped: 2026-03-31; Closeout: 2026-03-31)

**Phase range:** `111 -> 114`
**Phases completed:** 4 phases, 13 plans, 0 tasks
**Status:** `archived / evidence-ready (2026-03-31)`
**Route truth:** `no active milestone route / latest archived baseline = v1.31`
**Latest archived baseline:** `v1.31`
**Default next command:** `$gsd-new-milestone`

**Archived phase story:**

- `Phase 111`: entity-runtime boundary sealing and dependency-guard hardening ✅
- `Phase 112`: formal-home discoverability and governance-anchor normalization ✅
- `Phase 113`: hotspot burn-down and changed-surface assurance hardening ✅
- `Phase 114`: open-source reachability honesty and security-surface normalization ✅

**Key accomplishments:**

- 完成 `Phase 111 -> 114` 全部计划与 closeout bundle，形成 `v1.31` latest archived baseline 的可审计证据链。
- 封印 entity/control → runtime concrete bypass，并用 governance / dependency guards 固化 formal runtime access 主链。
- 统一 sanctioned root homes、governance anchors、hotspot no-growth proof 与 open-source honesty truth。

## v1.30 Protocol Hotspot Convergence, Transport De-friendization & Snapshot Surface Slimming (Shipped: 2026-03-30; Closeout: 2026-03-30)

**Phases completed:** 4 phases, 15 plans, 0 tasks

**Status:** archived / evidence-ready
**Route truth:** latest archived evidence index = `.planning/reviews/V1_30_EVIDENCE_INDEX.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.30`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.29`
**Default next command:** `$gsd-new-milestone`

**Key accomplishments:**

- 完成 `Phase 107 -> 110` 全部计划与 closeout bundle，形成可审计证据链。
- `snapshot.py` inward split 到 `snapshot_support.py`，保持 `SnapshotBuilder` 唯一 outward home。
- 统一 planning/baseline/review/docs/tests truth，冻结 `v1.30` archived closeout story。

## v1.29 Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization (Shipped: 2026-03-30; Closeout: 2026-03-30)

**Phase range:** `103 -> 105`
**Phases completed:** 3 phases, 9 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archived evidence index = `.planning/reviews/V1_29_EVIDENCE_INDEX.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.29`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.28`
**Default next command:** `$gsd-new-milestone`

**Archived phase story:**

- `Phase 103`: root adapter thinning, test topology second pass, and terminology contract normalization ✅
- `Phase 104`: service-router family split and command-runtime second-pass decomposition ✅
- `Phase 105`: governance rule datafication and milestone freeze ✅

**Key accomplishments:**

- 把 `custom_components/lipro/__init__.py` 的 lazy-load / entry-auth / service-registry adapter 支撑抽回 `custom_components/lipro/control/entry_root_support.py`，保持 HA 根入口只承担 thin adapter 装配。
- 把 `tests/conftest.py` 的 topicized collection hooks 与 `_CoordinatorDouble` 下沉到 `tests/topicized_collection.py` / `tests/coordinator_double.py`，fixture giant-root 不再继续承担 mixed governance truth。
- 把 `support / surface / wiring / handlers / facade` 的术语裁决写入 ADR，并把 `service_router_handlers.py` / `command_runtime.py` 的 second-pass inward split 收口为 focused predecessor bundles。
- 把 `tests/meta/governance_followup_route_specs.py` 与 `scripts/check_file_matrix_registry_*` 统一成 data-driven rule sources，减少规划台账 / classifier truth 的重复文字维护。
- 把 `.planning/v1.29-MILESTONE-AUDIT.md`、`.planning/reviews/V1_29_EVIDENCE_INDEX.md`、archive snapshots 与 promoted closeout bundle 共同冻结为 latest pull-only evidence chain，让下一条正式路线只能经 `$gsd-new-milestone` 启动。

**Closeout assets:**

- `.planning/v1.29-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_29_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.29-ROADMAP.md`
- `.planning/milestones/v1.29-REQUIREMENTS.md`
- `.planning/phases/103-root-adapter-thinning-test-topology-second-pass-and-terminology-contract-normalization/{103-01-SUMMARY.md,103-02-SUMMARY.md,103-03-SUMMARY.md,103-VERIFICATION.md,103-VALIDATION.md}`
- `.planning/phases/104-service-router-family-split-and-command-runtime-second-pass-decomposition/{104-01-SUMMARY.md,104-02-SUMMARY.md,104-03-SUMMARY.md,104-VERIFICATION.md,104-VALIDATION.md}`
- `.planning/phases/105-governance-rule-datafication-and-milestone-freeze/{105-01-SUMMARY.md,105-02-SUMMARY.md,105-03-SUMMARY.md,105-SUMMARY.md,105-VERIFICATION.md,105-VALIDATION.md}`

## v1.28 Governance Portability, Verification Stratification & Open-Source Continuity Hardening (Shipped: 2026-03-28; Closeout: 2026-03-28)

**Phase range:** `102 -> 102`
**Phases completed:** 3 phases, 9 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archived evidence index = `.planning/reviews/V1_28_EVIDENCE_INDEX.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.28`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.27`
**Default next command:** `$gsd-new-milestone`

**Archived phase story:**

- `Phase 102`: Governance portability, verification stratification, and open-source continuity hardening ✅

**Key accomplishments:**

- 把 governance/meta smoke 对本机 `node` / `gsd-tools.cjs` 的脆弱耦合收口成 capability-aware fast-path proof，避免 portable review/CI 因环境缺口而误报 route drift。
- 把 `.planning/baseline/VERIFICATION_MATRIX.md` 当前 archived-only truth、Phase 102 closeout proof 与 historical phase closeout reference 明确分层，不再让最新真相与旧 closeout note 混排。
- 把 `.planning/v1.28-MILESTONE-AUDIT.md`、`.planning/reviews/V1_28_EVIDENCE_INDEX.md`、archive snapshots 与 promoted closeout bundle 建成最新 pull-only evidence chain，让下一条正式路线只能经 `$gsd-new-milestone` 启动。

**Closeout assets:**

- `.planning/v1.28-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_28_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.28-ROADMAP.md`
- `.planning/milestones/v1.28-REQUIREMENTS.md`
- `.planning/phases/102-governance-portability-verification-stratification-and-open-source-continuity-hardening/{102-01-SUMMARY.md,102-02-SUMMARY.md,102-03-SUMMARY.md,102-VERIFICATION.md,102-VALIDATION.md}`

## v1.27 Final Carry-Forward Eradication & Route Reactivation (Shipped: 2026-03-28; Closeout: 2026-03-28)

**Phase range:** `98 -> 101`
**Phases completed:** 4 phases, 12 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archived evidence index = `.planning/reviews/V1_27_EVIDENCE_INDEX.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.27`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.26`
**Default next command:** `$gsd-new-milestone`（historical closeout command）

**Archived phase story:**

- `Phase 98`: carry-forward eradication, route reactivation, and closeout proof ✅
- `Phase 99`: runtime hotspot support extraction and terminal audit freeze ✅
- `Phase 100`: MQTT runtime and schedule service support extraction freeze ✅
- `Phase 101`: Anonymous-share manager and REST decoder hotspot decomposition freeze ✅

**Key accomplishments:**

- 把 `Phase 98` 的 carry-forward eradication 与 route reactivation bundle 正式冻结为 archived predecessor evidence，不再残留 live route drift。
- 把 `Phase 99 / 100` 的 runtime / MQTT / schedule support seams inward split 到 local collaborators，并保持 formal homes / predecessor chain 一致。
- 把 `Phase 101` 的 anonymous-share manager / REST decoder hotspot decomposition、MQTT-config decode reuse 与 governance freeze 一次性收口为 previous archived baseline。
- 把 `.planning/v1.27-MILESTONE-AUDIT.md`、`.planning/reviews/V1_27_EVIDENCE_INDEX.md` 与 archive snapshots 建成 pull-only closeout bundle，供 `v1.28` 继续 pull。

**Closeout assets:**

- `.planning/v1.27-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_27_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.27-ROADMAP.md`
- `.planning/milestones/v1.27-REQUIREMENTS.md`
- `.planning/phases/98-carry-forward-eradication-route-reactivation-and-closeout-proof/{98-01-SUMMARY.md,98-02-SUMMARY.md,98-03-SUMMARY.md,98-VERIFICATION.md,98-VALIDATION.md}`
- `.planning/phases/99-runtime-hotspot-support-extraction-and-terminal-audit-freeze/{99-01-SUMMARY.md,99-02-SUMMARY.md,99-03-SUMMARY.md,99-VERIFICATION.md,99-VALIDATION.md}`
- `.planning/phases/100-mqtt-runtime-and-schedule-service-support-extraction-freeze/{100-01-SUMMARY.md,100-02-SUMMARY.md,100-03-SUMMARY.md,100-VERIFICATION.md,100-VALIDATION.md}`
- `.planning/phases/101-anonymous-share-manager-and-rest-decoder-hotspot-decomposition-freeze/{101-01-SUMMARY.md,101-02-SUMMARY.md,101-03-SUMMARY.md,101-VERIFICATION.md,101-VALIDATION.md}`

## v1.26 Terminal Architecture Audit Follow-through, Typed Mapping Retirement & Hotspot Decomposition (Shipped: 2026-03-28; Closeout: 2026-03-28)

**Phase range:** `94 -> 97`
**Phases completed:** 4 phases, 12 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archived evidence index = `.planning/reviews/V1_26_EVIDENCE_INDEX.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.26`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.26`

**Key accomplishments:**

- 把 broad typed seam、schedule/runtime hotspot、shared sanitizer burn-down 与 governance freeze 收口为 `v1.26` archived baseline，而不再依赖口头路由记忆。
- 把 `.planning/v1.26-MILESTONE-AUDIT.md`、`.planning/reviews/V1_26_EVIDENCE_INDEX.md` 与 archive snapshots 冻结为 pull-only closeout bundle。

## v1.25 Hotspot Inward Decomposition, Typed Boundary Hardening & Redaction Convergence (Shipped: 2026-03-28; Closeout: 2026-03-28)

**Phase range:** `90 -> 93`
**Phases completed:** 4 phases, 12 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archived evidence index = `.planning/reviews/V1_25_EVIDENCE_INDEX.md`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.25`

**Key accomplishments:**

- 把 five hotspot formal homes、typed boundary hardening、redaction convergence 与 assurance freeze 收口为 `v1.25` archived baseline，而不再依赖口头路由记忆。
- 把 `.planning/v1.25-MILESTONE-AUDIT.md`、`.planning/reviews/V1_25_EVIDENCE_INDEX.md` 与 archive snapshots 冻结为 pull-only closeout bundle。

## v1.24 Runtime Boundary Tightening, Tooling Kernel Decoupling & Open-Source Entry Convergence (Shipped: 2026-03-27; Closeout: 2026-03-27)

**Phase range:** `89 -> 89`
**Phases completed:** 1 phase, 4 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archived evidence index = `.planning/reviews/V1_24_EVIDENCE_INDEX.md`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.24`

**Key accomplishments:**

- 把 entity-facing runtime surface 收窄成命名 verbs，移除了 service/lock awareness 对实体层的渗透。
- 把 runtime bootstrap 与 support-service wiring 收口成单一 bootstrap artifact story，避免 `Coordinator` 与 `RuntimeOrchestrator` 并行装配。
- 把 architecture/file-matrix governance tooling 的 helper ownership 收回 `scripts/lib/*` / sibling modules，不再依赖 `tests.helpers` 或 ad-hoc `sys.path` 注入。
- 把 README / docs / issue templates / manifest / metadata 的 docs-first open-source entry 故事收敛成一条公开协作路径。
- 把 `.planning/v1.24-MILESTONE-AUDIT.md`、`.planning/reviews/V1_24_EVIDENCE_INDEX.md` 与 archive snapshots 建成 pull-only closeout bundle，让下一条正式路线只能经 `$gsd-new-milestone` 启动。

**Closeout assets:**

- `.planning/v1.24-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_24_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.24-ROADMAP.md`
- `.planning/milestones/v1.24-REQUIREMENTS.md`
- `.planning/phases/89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence/{89-01-SUMMARY.md,89-02-SUMMARY.md,89-03-SUMMARY.md,89-04-SUMMARY.md,89-VERIFICATION.md,89-VALIDATION.md}`

---

## v1.23 Repository-Wide Terminal Code Audit, Residual Eradication & Closeout Truth Freeze (Shipped: 2026-03-27; Closeout: 2026-03-27)

**Phase range:** `85 -> 88`
**Phases completed:** 4 phases, 14 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archived evidence index = `.planning/reviews/V1_23_EVIDENCE_INDEX.md`
**Historical closeout marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.23`

**Key accomplishments:**

- 把 `custom_components/lipro`、tests、docs、planning/baseline/review assets 与 workflow/config entry points 拉进同一份 terminal audit verdict，消除“靠记忆判断还有没有尾巴”的隐性治理模式。
- 把 production residual / boundary drift 收口回 formal homes，并明确把 giant assurance carriers 退回 concern-local suites + focused guards 的组合，不再让少数 mega files 扛全仓真相。
- 把 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、baselines、review ledgers、runbook 与 focused governance tests 同步到 archived-only route truth：`no active milestone route / latest archived baseline = v1.23`。
- 把 `v1.23-MILESTONE-AUDIT.md`、`V1_23_EVIDENCE_INDEX.md` 与 archive snapshots 建成 pull-only closeout bundle，使下一条路线只能从显式的 `$gsd-new-milestone` 启动。
- archived snapshots created / handoff-ready。

**Closeout assets:**

- `.planning/v1.23-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_23_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.23-ROADMAP.md`
- `.planning/milestones/v1.23-REQUIREMENTS.md`
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/{85-01-SUMMARY.md,85-02-SUMMARY.md,85-03-SUMMARY.md}`
- `.planning/phases/86-production-residual-eradication-and-boundary-re-tightening/{86-01-SUMMARY.md,86-02-SUMMARY.md,86-03-SUMMARY.md,86-04-SUMMARY.md,86-VALIDATION.md}`
- `.planning/phases/87-assurance-hotspot-decomposition-and-no-regrowth-guards/{87-01-SUMMARY.md,87-02-SUMMARY.md,87-03-SUMMARY.md,87-04-SUMMARY.md}`
- `.planning/phases/88-governance-sync-quality-proof-and-milestone-freeze/{88-01-SUMMARY.md,88-02-SUMMARY.md,88-03-SUMMARY.md,88-SUMMARY.md,88-VERIFICATION.md,88-VALIDATION.md}`

---

## v1.22 Maintainer Entry Contracts, Release Operations Closure & Contributor Routing (Shipped: 2026-03-27; Closeout: 2026-03-27)

**Phase range:** `81 -> 84`
**Phases completed:** 4 phases, 12 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archived evidence index = `.planning/reviews/V1_22_EVIDENCE_INDEX.md`

**Key accomplishments:**

- 把 contributor-facing README / docs / support / security / contribution 路径收口为统一 public first hop，并新增 `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md` 作为 change-routing / evidence-destination surface。
- 把 maintainer-facing release runbook、changelog、version-sync triad、release workflow anchors 与 archived evidence pull-chain 收口成单一 maintainer route，不再残留平行 runbook / helper folklore。
- 把 issue / PR / security intake 与 maintainer stewardship contract 升级为 evidence-first / continuity-aware community-health surface，减少无边界、无复现、无验证命令的维护噪音。
- 用 focused governance/open-source guards 冻结 `Phase 84 complete` closeout truth，并在 archived-only governance truth 生效后作为 previous archived baseline 保留；historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.22`。

**Closeout assets:**

- `.planning/v1.22-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_22_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.22-ROADMAP.md`
- `.planning/milestones/v1.22-REQUIREMENTS.md`
- `.planning/phases/81-contributor-onramp-route-convergence-and-public-entry-contract/{81-01-SUMMARY.md,81-02-SUMMARY.md,81-03-SUMMARY.md,81-SUMMARY.md,81-VERIFICATION.md,81-VALIDATION.md}`
- `.planning/phases/82-release-operations-closure-and-evidence-chain-formalization/{82-01-SUMMARY.md,82-02-SUMMARY.md,82-03-SUMMARY.md,82-SUMMARY.md,82-VERIFICATION.md,82-VALIDATION.md}`
- `.planning/phases/83-intake-templates-and-maintainer-stewardship-contract/{83-01-SUMMARY.md,83-02-SUMMARY.md,83-03-SUMMARY.md,83-SUMMARY.md,83-VERIFICATION.md,83-VALIDATION.md}`
- `.planning/phases/84-governance-open-source-guard-coverage-and-milestone-truth-freeze/{84-01-SUMMARY.md,84-02-SUMMARY.md,84-03-SUMMARY.md,84-SUMMARY.md,84-VERIFICATION.md,84-VALIDATION.md}`

---

## v1.21 Governance Bootstrap Truth Hardening & Planning Route Automation (Shipped: 2026-03-26; Closeout: 2026-03-26)

**Phase range:** `76 -> 80`
**Phases completed:** 5 phases, 15 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archived evidence index = `.planning/reviews/V1_21_EVIDENCE_INDEX.md`

**Key accomplishments:**

- 把 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 的 bootstrap selector 收口为 machine-readable `governance-route` contract，并在 archive promotion 后稳定切到 `no active milestone route / latest archived baseline = v1.21`，同时保留 historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.21`
- 完成 focused bootstrap smoke、route-handoff quality gate 与 promoted-evidence / review-ledger 冻结，让 `$gsd-next` 只能把下一步前推到 `$gsd-new-milestone`
- 拆薄 `check_file_matrix_registry` hotspot、topicize release-contract mega-suite，并保持 governance/tooling outward contract 与 file-matrix honesty 稳定
- 收口 governance/tooling typing regressions、补齐 `77-VALIDATION` 与 final meta-suite hotspot topicization，把 `Phase 76 -> 80` 一次性冻结为 archived-only evidence bundle

**Closeout assets:**

- `.planning/v1.21-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_21_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.21-ROADMAP.md`
- `.planning/milestones/v1.21-REQUIREMENTS.md`
- `.planning/phases/76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation/{76-01-SUMMARY.md,76-02-SUMMARY.md,76-03-SUMMARY.md,76-VERIFICATION.md,76-VALIDATION.md}`
- `.planning/phases/77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction/{77-01-SUMMARY.md,77-02-SUMMARY.md,77-03-SUMMARY.md,77-VERIFICATION.md,77-VALIDATION.md}`
- `.planning/phases/78-quality-gate-formalization-route-handoff-ergonomics-and-milestone-closeout-readiness/{78-01-SUMMARY.md,78-02-SUMMARY.md,78-03-SUMMARY.md,78-SUMMARY.md,78-VERIFICATION.md,78-VALIDATION.md}`
- `.planning/phases/79-governance-tooling-hotspot-decomposition-and-release-contract-topicization/{79-01-SUMMARY.md,79-02-SUMMARY.md,79-03-SUMMARY.md,79-SUMMARY.md,79-VERIFICATION.md,79-VALIDATION.md}`
- `.planning/phases/80-governance-typing-closure-and-final-meta-suite-hotspot-topicization/{80-01-SUMMARY.md,80-02-SUMMARY.md,80-03-SUMMARY.md,80-SUMMARY.md,80-VERIFICATION.md,80-VALIDATION.md}`

---

## v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement (Shipped: 2026-03-25; Closeout: 2026-03-25)

**Phase range:** `72 -> 75`
**Phases completed:** 4 phases, 16 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archived evidence index = `.planning/reviews/V1_20_EVIDENCE_INDEX.md`

**Key accomplishments:**

- 收口 `Coordinator` bootstrap / lifecycle orchestration / `runtime_access` probing，把 startup 与 lifecycle hotspot 压回既有 formal homes
- 完成 service-router forwarding family、diagnostics/helper duplication、entity runtime strategy 与 schedule runtime surface 的 formalize / deduplicate
- 继续退役 auth legacy snapshot / compatibility wrapper，完成 suite topicization、governance cleanup 与 archive-readiness arbitration
- 统一 private-access honest story、promoted closeout evidence allowlist 与 thin-adapter typing，并保留 historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.20`

**Closeout assets:**

- `.planning/v1.20-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_20_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.20-ROADMAP.md`
- `.planning/milestones/v1.20-REQUIREMENTS.md`
- `.planning/phases/72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement/{72-01-SUMMARY.md,72-02-SUMMARY.md,72-03-SUMMARY.md,72-04-SUMMARY.md,72-VERIFICATION.md,72-VALIDATION.md}`
- `.planning/phases/73-service-family-deduplication-diagnostics-helper-convergence-and-runtime-surface-formalization/{73-01-SUMMARY.md,73-02-SUMMARY.md,73-03-SUMMARY.md,73-04-SUMMARY.md,73-VERIFICATION.md,73-VALIDATION.md}`
- `.planning/phases/74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout/{74-01-SUMMARY.md,74-02-SUMMARY.md,74-03-SUMMARY.md,74-04-SUMMARY.md,74-VERIFICATION.md,74-VALIDATION.md}`

---

## v1.0 North Star Rebuild (Shipped: 2026-03-13)

**Phase range:** `1 -> 7`（含 `1.5 / 2.5 / 2.6`）
**Phases completed:** 10 phases, 32 plans, 0 tasks
**Status:** shipped / archived

**Key accomplishments:**

- 重建北极星单一正式主链
- 收口 protocol / runtime / control / assurance / governance 五平面骨架
- 建立 v1.0 归档资产与 milestone 级基线

---

## v1.1 Protocol Fidelity & Operability (Closeout: 2026-03-15)

**Phase range:** `7.1 -> 17`
**Phases completed:** 15 phases, 58 plans, 0 tasks
**Status:** archived / evidence-ready

**Key accomplishments:**

- formalized boundary decoder families、architecture policy enforcement、runtime telemetry exporter 与 replay/evidence 主链
- 完成 final residual retirement、typed contract tightening、governance closeout 与 `v1.1-MILESTONE-AUDIT.md`
- 固化 `V1_1_EVIDENCE_INDEX.md` 作为 pull-only closeout pointer

**Closeout assets:**

- `.planning/v1.1-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_1_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.1-ROADMAP.md`
- `.planning/milestones/v1.1-REQUIREMENTS.md`

---

## v1.2 Host-Neutral Core & Replay Completion (Closeout revalidated: 2026-03-17)

**Phase range:** `18 -> 24`
**Phases completed:** 7 phases, 24 plans, 0 tasks
**Status:** archived snapshots created / handoff-ready；archive-ready verdict revalidated 2026-03-17

**Key accomplishments:**

- 完成 host-neutral boundary/auth/device nucleus 抽取，并以 headless consumer proof 证明 single-chain reuse
- 完成 remaining boundary family formalization、replay/evidence explicit coverage、shared failure taxonomy 与 observability consumer convergence
- 完成 governance/docs/release evidence closeout、`v1.2` milestone audit、final repo audit 与 `v1.3` handoff bundle
- `Phase 24` reopen (`24-04` / `24-05`) 已修复 closeout gate regressions，并用 fresh evidence 重新验证 archive-ready / handoff-ready verdict

**Closeout assets:**

- `.planning/reviews/V1_2_EVIDENCE_INDEX.md`
- `.planning/v1.2-MILESTONE-AUDIT.md`
- `.planning/v1.3-HANDOFF.md`
- `.planning/milestones/v1.2-ROADMAP.md`
- `.planning/milestones/v1.2-REQUIREMENTS.md`

---

## v1.4 Sustainment, Trust Gates & Final Hotspot Burn-down (Shipped: 2026-03-19)

**Phase range:** `34 -> 39`
**Phases completed:** 6 phases, 19 plans, 0 tasks
**Status:** archived / evidence-ready

**Key accomplishments:**

- formalized continuity / custody / freeze contract，并补齐 tagged `CodeQL` hard gate、keyless `cosign` signing 与 provenance verification
- 完成 protocol/runtime hotspot 最后一轮瘦身，把 exception / typed budget 与 child-façade seams 收回正式主链
- 完成 mega-test 第三波 topicization、derived-truth convergence 与 final external-boundary residual retirement
- 完成 governance current-story convergence、control-home clarification、dead-shell retirement 与 full hard-gate closeout promotion

**Closeout assets:**

- `.planning/v1.4-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_4_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.4-ROADMAP.md`
- `.planning/milestones/v1.4-REQUIREMENTS.md`
- `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-SUMMARY.md`
- `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-VERIFICATION.md`

---

## v1.5 Governance Truth Consolidation & Control-Surface Finalization (Shipped: 2026-03-19)

**Phase range:** `40`
**Phases completed:** 1 phase, 7 plans, 0 tasks
**Status:** archived / evidence-ready

**Key accomplishments:**

- unified active truth, archive identity, promoted phase assets, and continuity order into one current-story contract
- introduced `.planning/baseline/GOVERNANCE_REGISTRY.json` as machine-readable governance truth and synchronized release/support/install routing
- converged control/services runtime reads through `runtime_access` and removed parallel traversal / lookup stories
- unified schedule service auth/error execution through the formal shared executor and closed touched naming residue

**Closeout assets:**

- `.planning/v1.5-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_5_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.5-ROADMAP.md`
- `.planning/milestones/v1.5-REQUIREMENTS.md`
- `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-SUMMARY.md`
- `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-VERIFICATION.md`
- `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-VALIDATION.md`

---

## v1.6 Delivery Trust Hardening, Runtime Boundary Decoupling & Maintainability Closure (Closeout: 2026-03-20)

**Phase range:** `42 -> 45`
**Phases completed:** 4 phases, 16 plans, 0 tasks
**Status:** archived / evidence-ready

**Key accomplishments:**

- formalized maintainer continuity, release artifact install smoke, dual coverage gates, and compatibility preview truth
- decoupled `control/` ↔ `services/`, typed `RuntimeAccess`, and moved runtime infra back to their formal homes
- pruned phase-trace authority noise, converged façade-era terminology, and clarified contributor fast-path / bilingual boundary
- decomposed hotspot files, introduced typed failure semantics, and upgraded benchmark evidence into anti-regression truth

**Closeout assets:**

- `.planning/v1.6-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_6_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.6-ROADMAP.md`
- `.planning/milestones/v1.6-REQUIREMENTS.md`
- `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-SUMMARY.md`
- `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-VERIFICATION.md`

---

## v1.12 Verification Localization & Governance Guard Topicization (Closeout: 2026-03-22)

**Phase range:** `59`
**Phases completed:** 3 phases, 9 plans, 0 tasks
**Status:** archived / evidence-ready

**Key accomplishments:**

- public-surface / governance-history / follow-up-route megaguards 退成 thin shell runnable roots，并按 truth family localized
- `device_refresh` giant suite 已拆成 parsing / filter / snapshot / runtime focused verification topology
- current-story docs、verification matrix、testing map 与 review ledgers 已冻结 localized verification / no-growth story

**Closeout assets:**

- `.planning/v1.12-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_12_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.12-ROADMAP.md`
- `.planning/milestones/v1.12-REQUIREMENTS.md`
- `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-SUMMARY.md`
- `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-VERIFICATION.md`

---

## v1.13 Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence (Closeout: 2026-03-22)

**Phase range:** `60 -> 62`
**Phases completed:** 3 phases, 11 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** prior archive-ready closeout baseline = `.planning/reviews/V1_13_EVIDENCE_INDEX.md`

**Key accomplishments:**

- 完成 tooling truth / file-governance hotspot inward decomposition，并冻结 `FILE_MATRIX / VERIFICATION_MATRIX / TESTING` 的 current story
- 继续切薄 `anonymous_share` / diagnostics / OTA / `select` 等 large-but-correct formal homes，并补齐 focused maintainability evidence
- 收口 support-seam naming、public docs fast path 与 discoverability / anti-regression governance truth

**Closeout assets:**

- `.planning/v1.13-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_13_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.13-ROADMAP.md`
- `.planning/milestones/v1.13-REQUIREMENTS.md`
- `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-SUMMARY.md`
- `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-SUMMARY.md`
- `.planning/phases/62-naming-clarity-support-seam-governance-and-public-discoverability/62-SUMMARY.md`

---

## v1.14 Governance Truth Realignment, Typed Runtime Access & Final Hidden-Root Closure (Closeout: 2026-03-23)

**Phase range:** `63 -> 66`
**Phases completed:** 4 phases, 15 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** prior archive-ready closeout baseline = `.planning/reviews/V1_14_EVIDENCE_INDEX.md`

**Key accomplishments:**

- 完成 governance latest-pointer / release-target fidelity 对齐，并把 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / docs / runbook` 收束到同一 archive story
- 把 `RuntimeAccess`、telemetry / schedule / diagnostics、runtime alias / device extras 与 anonymous-share submit contract 全部收口到更诚实的 typed formal seams
- 清理 HA root adapter folklore，并为 `transport_executor` / `protocol_service` / `protocol facade` 铺设 focused seam regressions，结束 mega-matrix 独占验证

**Closeout assets:**

- `.planning/v1.14-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_14_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.14-ROADMAP.md`
- `.planning/milestones/v1.14-REQUIREMENTS.md`
- `.planning/phases/63-governance-truth-realignment-typed-runtime-access-and-hidden-root-closure/63-SUMMARY.md`
- `.planning/phases/64-telemetry-typing-schedule-contracts-and-diagnostics-hotspot-slimming/64-SUMMARY.md`
- `.planning/phases/65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure/65-SUMMARY.md`
- `.planning/phases/66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening/66-SUMMARY.md`

---

## v1.15 Typed Contract Convergence, Tooling Kernel Hardening & Mypy Closure (Closeout: 2026-03-24)

**Phase range:** `67`
**Phases completed:** 1 phase, 6 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** prior archive-ready closeout baseline = `.planning/reviews/V1_15_EVIDENCE_INDEX.md`

**Key accomplishments:**

- 把 telemetry / REST / anonymous-share / control telemetry surface / service-handler fixtures 全部收口到更诚实的 typed formal seams，并让 `uv run mypy` 回到正式绿色
- 统一 toolchain/governance payload narrowing、typed test doubles、runtime/control wiring callable truth，结束 broad `object` / stale route 双真相
- 以 `PROJECT / ROADMAP / REQUIREMENTS / STATE / docs/README` 为核心冻结 `v1.15` closeout truth，并在同一轮通过 repo-wide quality gates

**Closeout assets:**

- `.planning/v1.15-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_15_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.15-ROADMAP.md`
- `.planning/milestones/v1.15-REQUIREMENTS.md`
- `.planning/phases/67-typed-contract-convergence-toolchain-hardening-and-mypy-closure/67-SUMMARY.md`
- `.planning/phases/67-typed-contract-convergence-toolchain-hardening-and-mypy-closure/67-VERIFICATION.md`

---

## v1.16 Master Audit Follow-Through, Hotspot Finalization & Docs Contract Hardening (Closeout: 2026-03-24)

**Phase range:** `68`
**Phases completed:** 1 phase, 6 plans, 0 tasks
**Status:** archived / evidence-ready with carry-forward
**Route truth (at v1.16 closeout):** latest archive-ready closeout pointer = `.planning/reviews/V1_16_EVIDENCE_INDEX.md`

**Key accomplishments:**

- 完成 refreshed repo-wide audit follow-through，继续 inward split telemetry / MQTT / anonymous-share / OTA / runtime hotspots，并冻结 regrowth budget 与 no-growth story
- 统一 `README*`、`docs/README.md`、`manifest.json`、`pyproject.toml`、GitHub templates 与 governance guards 的 docs first-hop / version / release contract
- 在同一轮通过 focused proof、`ruff`、`mypy`、architecture policy、file-matrix 与 full pytest，并把 non-blocking residual 正式 carry-forward 到 `v1.17 / Phase 69`

**Closeout assets:**

- `.planning/v1.16-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_16_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.16-ROADMAP.md`
- `.planning/milestones/v1.16-REQUIREMENTS.md`
- `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-SUMMARY.md`
- `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-VERIFICATION.md`
- `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-VALIDATION.md`

---

## v1.17 Residual Formalization, Quality-Balance Hardening & Open-Source Contract Closure (Closeout: 2026-03-24)

**Phase range:** `69`
**Phases completed:** 1 phase, 5 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth (at v1.17 closeout):** latest archive-ready closeout pointer = `.planning/reviews/V1_17_EVIDENCE_INDEX.md`

**Key accomplishments:**

- formalize `runtime_access` read-model seams、继续 thin `runtime_access_support.py` / `runtime_infra.py`，并保持 single outward runtime home 不漂移
- 把 schedule/service path 压回 typed device-context contract，去掉 protocol-shaped choreography 与多余 wrapper / shim / lazy-import 故事
- 统一 checker、focused integration、open-source docs / metadata / continuity truth，并把里程碑切换到 latest archived baseline / no active milestone route

**Closeout assets:**

- `.planning/v1.17-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_17_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.17-ROADMAP.md`
- `.planning/milestones/v1.17-REQUIREMENTS.md`
- `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-SUMMARY.md`
- `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-VERIFICATION.md`
- `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-VALIDATION.md`

---

## v1.18 Support-Seam Slimming, OTA Resolver Consolidation & Governance Test Topicization (Closeout: 2026-03-24)

**Phase range:** `70`
**Phases completed:** 1 phase, 5 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archive-ready closeout pointer = `.planning/reviews/V1_18_EVIDENCE_INDEX.md`

**Key accomplishments:**

- 将 `runtime_access_support.py` inward split 为更窄的 support-only helper cluster，并继续保持 `runtime_access.py` 唯一 outward runtime home
- 收口 anonymous-share submit/refresh/outcome 与 OTA query/selection shared helper truth，避免 helper-owned second story 与 entity-local choreography 回流
- 冻结 archive-vs-current version truth、topicize governance mega-tests，并在同一轮通过 focused gates、`ruff`、`mypy`、architecture policy 与 file-matrix

**Closeout assets:**

- `.planning/v1.18-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_18_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.18-ROADMAP.md`
- `.planning/milestones/v1.18-REQUIREMENTS.md`
- `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-SUMMARY.md`
- `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-VERIFICATION.md`
- `.planning/phases/70-support-seam-slimming-ota-resolver-consolidation-and-governance-test-topicization/70-VALIDATION.md`

---

---

## v1.19 Audit-Driven Final Hotspot Decomposition & Governance Truth Projection (Closeout: 2026-03-25)

**Phase range:** `71`
**Phases completed:** 1 phase, 5 plans, 0 tasks
**Status:** archived / evidence-ready
**Route truth:** latest archive-ready closeout pointer = `.planning/reviews/V1_19_EVIDENCE_INDEX.md`

**Key accomplishments:**

- 继续 inward split OTA diagnostics / firmware-install orchestration，保持 entity outward surface 与 helper-owned second story 不回流
- 收口 anonymous-share submit、request pacing 与 command-runtime 长流程，把热点切回更窄 typed helper seams
- 统一 planning / docs / tests 的 route truth，完成 `v1.19 -> v1.20` 的 archive-transition 交接并退为历史归档基线

**Closeout assets:**

- `.planning/v1.19-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_19_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.19-ROADMAP.md`
- `.planning/milestones/v1.19-REQUIREMENTS.md`
- `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-SUMMARY.md`
- `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VERIFICATION.md`
- `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-VALIDATION.md`

---
