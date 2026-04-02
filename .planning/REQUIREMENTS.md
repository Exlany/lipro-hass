# Requirements: Lipro-HASS v1.43

<!-- governance-route-contract:start -->
```yaml
contract_name: governance-route
projection_targets:
- .planning/PROJECT.md
- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- .planning/STATE.md
- .planning/MILESTONES.md
active_milestone:
  version: v1.43
  name: Hotspot Second-Pass Slimming & Governance Load Shedding
  status: active / phase 140 complete; phase 141 planning-ready (2026-04-02)
  phase: '140'
  phase_title: release/governance source compression and codebase freshness
  phase_dir: 140-release-governance-source-compression-and-codebase-freshness
  route_mode: v1.43 active milestone route / Phase 140 complete / Phase 141 planning-ready / latest archived baseline = v1.42
latest_archived:
  version: v1.42
  name: Hotspot Burn-Down, Observability Truth & Governance Cost Compression
  status: archived / evidence-ready (2026-04-02)
  phase: '138'
  phase_title: runtime contract decoupling, support-guard hardening, and docs archive alignment
  phase_dir: 138-runtime-contract-decoupling-support-guard-and-docs-alignment
  audit_path: .planning/v1.42-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_42_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.41
  name: Terminal Residual Audit, Remediation Charter & Maintainability Hardening
  evidence_path: .planning/reviews/V1_41_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.43 active milestone route / Phase 140 complete / Phase 141 planning-ready / latest archived baseline = v1.42
  default_next_command: $gsd-plan-phase 141
  latest_archived_evidence_pointer: .planning/reviews/V1_42_EVIDENCE_INDEX.md
contract_version: 1
```
<!-- governance-route-contract:end -->

## Current Milestone (v1.43)

**Milestone Goal:** 基于 `v1.42` latest archived baseline，已完成 REST/protocol second-pass slimming、forwarding honesty 与 release/governance freshness formalization，并把下一轮 control/runtime/device hotspot narrowing 诚实前推到 `Phase 141` planning-ready。
**Milestone status:** `active / phase 140 complete; phase 141 planning-ready (2026-04-02)`
**Current route mode:** `v1.43 active milestone route / Phase 140 complete / Phase 141 planning-ready / latest archived baseline = v1.42`
**Starting baseline:** `.planning/v1.42-MILESTONE-AUDIT.md, .planning/reviews/V1_42_EVIDENCE_INDEX.md, .planning/milestones/v1.42-ROADMAP.md, .planning/milestones/v1.42-REQUIREMENTS.md`
**Requirements basket:** `ARC-48, HOT-70, HOT-71, GOV-94, DOC-22, TST-59, AUD-09, GOV-95, DOC-23, TST-60`
**Latest archived baseline:** `v1.42`
**Archive pointer:** `.planning/reviews/V1_42_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.42-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-plan-phase 141`
**Current phase handoff:** `Phase 140 deliverables 已完成并写入 route truth；当前 requirements basket 已全部收口，Phase 141 仅以 planning-ready context/research 接入，等待后续正式 planning。`

### Protocol / Architecture
- [x] **ARC-48**: `custom_components/lipro/core/protocol/rest_port.py` 必须继续瘦身到 typed contracts + port family + bind helper；bound adapter mechanics 下沉到 sibling helper，但不得新增第二 protocol root。 
- [x] **HOT-70**: `custom_components/lipro/core/api/rest_facade.py` 必须把 transport/auth/mapping private mechanics inward split 到 local helper module，同时保持 `LiproRestFacade` canonical REST child-façade 身份不变。 
- [x] **HOT-71**: schedule `group_id` 在 `protocol facade -> rest ports -> rest facade -> endpoint surface -> schedule endpoint` 调用链中必须保持显式透传，mesh / standard schedule 行为不得 silently diverge。 

### Governance / Docs / Tests
- [x] **GOV-94**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、registry、verification baseline、developer/runbook docs 与 focused route guards 必须共同承认当前 active route truth；当前投影已切到 `v1.43 active milestone route / Phase 140 complete / Phase 141 planning-ready / latest archived baseline = v1.42`。 
- [x] **DOC-22**: `docs/developer_architecture.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 必须把 second-pass split 结果、latest archived pointer、Phase 140 formalization 与 `Phase 141` planning-ready handoff 讲清楚，而不制造新 authority chain。 
- [x] **TST-59**: focused unit tests、meta guards、route/diff verification 与 lint/check 命令必须证明本轮 second-pass slimming 没有破坏 outward contract。 
- [x] **AUD-09**: `.planning/baseline/VERIFICATION_MATRIX.md`、archived remediation docs 与 related ledgers 已清掉 stale release/governance verification paths，并把 runnable proof 更新到当前 guard family。 
- [x] **GOV-95**: release/governance selector family、baseline docs、residual ledgers 与 archived remediation docs 已压缩重复叙事，减少 stale route / stale path duplication。 
- [x] **DOC-23**: `CHANGELOG.md`、`SUPPORT.md`、`README*.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 已对 public-facing summary、private-access / future public mirror 与 release asset reachability 使用一致语义。 
- [x] **TST-60**: `tests/meta` 已补齐 changelog public-summary、runbook conditional wording 与 governance freshness 的守卫，避免上述 drift 再次无声回流。 

## Coverage Snapshot

- v1.43 requirements: 10 total
- Current mapped: 10
- Current complete: 10
- Current pending: 0

## Requirement Trace Table

| Requirement | Phase | Status |
|-------------|-------|--------|
| ARC-48 | Phase 139 | Complete |
| HOT-70 | Phase 139 | Complete |
| HOT-71 | Phase 139 | Complete |
| GOV-94 | Phase 139 | Complete |
| DOC-22 | Phase 139 | Complete |
| TST-59 | Phase 139 | Complete |
| AUD-09 | Phase 140 | Complete |
| GOV-95 | Phase 140 | Complete |
| DOC-23 | Phase 140 | Complete |
| TST-60 | Phase 140 | Complete |

## Previous Archived Milestone (v1.41)

**Milestone Goal:** 基于 `v1.40` latest archived baseline，完成 repo-wide terminal residual audit、remediation charter 与首批 focused hygiene fixes，把终极审阅结论冻结为 pull-only predecessor baseline。
**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Current route mode:** `no active milestone route / latest archived baseline = v1.41`
**Starting baseline:** `.planning/v1.40-MILESTONE-AUDIT.md, .planning/reviews/V1_40_EVIDENCE_INDEX.md, .planning/milestones/v1.40-ROADMAP.md, .planning/milestones/v1.40-REQUIREMENTS.md`
**Requirements basket:** `AUD-08, GOV-91, DOC-19, ARC-45, QLT-58, TST-56`
**Latest archived baseline:** `v1.41`
**Archive pointer:** `.planning/reviews/V1_41_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.41-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 136 的 requirement coverage、summary / verification / validation / audit / evidence index 已冻结为 previous archived baseline truth。`

## Previous Archived Milestone (v1.40)

**Milestone Goal:** 基于 `v1.39` latest archived baseline，先完成 RequestPolicy pacing ownership、entity projection de-reflection 与 fan preset truth 收口，再把 `runtime_access.py`、`auth_service.py` 与 `dispatch.py` 的剩余 sanctioned hotspot 继续压回 typed / thin / support-split 主链。 
**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Current route mode:** `no active milestone route / latest archived baseline = v1.40`
**Starting baseline:** `.planning/v1.39-MILESTONE-AUDIT.md, .planning/reviews/V1_39_EVIDENCE_INDEX.md, .planning/milestones/v1.39-ROADMAP.md, .planning/milestones/v1.39-REQUIREMENTS.md`
**Requirements basket:** `GOV-90, ARC-43, HOT-62, HOT-63, QLT-56, TST-54, ARC-44, HOT-64, HOT-65, HOT-66, QLT-57, TST-55`
**Latest archived baseline:** `v1.40`
**Archive pointer:** `.planning/reviews/V1_40_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.40-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 134 -> 135 的 requirement coverage、summary / verification / validation / audit / evidence index 已冻结为 latest archived baseline truth。`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.40`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.39`

### Governance Ownership
- [x] **GOV-90**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 与 `GOVERNANCE_REGISTRY.json` 必须共同承认 `v1.40 active milestone route / starting from latest archived baseline = v1.39`，并把 `Phase 134 -> 135` 作为当前 active milestone 范围、`$gsd-complete-milestone v1.40` 作为默认下一步。

### RequestPolicy / Entity Architecture
- [x] **ARC-43**: `custom_components/lipro/core/api/request_policy.py` 必须把 pacing caches / busy counters / target locks 收回单一实例 owner；`request_policy_support.py` 只保留 support helpers，不再让 mutable pacing state 以 parallel dict 参数形式四处流动。
- [x] **HOT-62**: `custom_components/lipro/entities/descriptors.py`、`custom_components/lipro/light.py` 与 `custom_components/lipro/binary_sensor.py` 必须移除 dotted-path/getattr 反射，改为显式 resolver / state-reader projection。
- [x] **HOT-63**: `custom_components/lipro/fan.py` 的 unknown `fanMode` 不能再 fallback 成 `cycle`；preset / supported_features / behavior tests 必须维持 truthful 一致投影。

### Runtime Hotspot Final Hardening
- [x] **ARC-44**: `custom_components/lipro/control/runtime_access.py` 必须继续薄化为 outward import home；runtime snapshot / diagnostics projection coercion 必须委托给 support surface，而不是继续在 import home 中膨胀。
- [x] **HOT-64**: `custom_components/lipro/runtime_types.py`、`custom_components/lipro/core/coordinator/services/auth_service.py` 与 `custom_components/lipro/services/execution.py` 必须围绕单一 typed reauth reason contract 协作。
- [x] **HOT-65**: `custom_components/lipro/core/command/dispatch.py` 的 route contract 必须采用 enum-backed canonical form，不再以裸字符串作为唯一正式表达。
- [x] **HOT-66**: sender / runtime command orchestration 必须承认新的 dispatch route canonical form，避免 stringly route 在下游继续漂移。

### Quality / Verification
- [x] **QLT-56**: developer architecture、maintainer runbook、public-surface meta guards 与 phase assets 必须同步描述 Phase 134 的 owner/projection truth，避免 route/docs/guards 各讲一套。
- [x] **TST-54**: focused `pytest`/meta/ruff lane 必须覆盖 RequestPolicy ownership、entity de-reflection、fan truth 与 `v1.40` 当前治理路由。
- [x] **QLT-57**: Phase 135 完成后，`runtime_access` support split、typed reauth reason 与 enum-backed route 必须有 focused architecture guard 防回流。
- [x] **TST-55**: focused `pytest`/meta/ruff lane 必须覆盖 runtime_access/auth_service/dispatch 以及 reopened `v1.40` current-route truth。

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GOV-90 | Phase 134 | Complete |
| ARC-43 | Phase 134 | Complete |
| HOT-62 | Phase 134 | Complete |
| HOT-63 | Phase 134 | Complete |
| QLT-56 | Phase 134 | Complete |
| TST-54 | Phase 134 | Complete |
| ARC-44 | Phase 135 | Complete |
| HOT-64 | Phase 135 | Complete |
| HOT-65 | Phase 135 | Complete |
| HOT-66 | Phase 135 | Complete |
| QLT-57 | Phase 135 | Complete |
| TST-55 | Phase 135 | Complete |

## Coverage

- v1.40 requirements: 12 total
- Current mapped: 12
- Current complete: 12
- Current pending: 0

## Historical Traceability Appendix

为保持 archived continuity guards 与历史 requirement mapping 的单一叙事，保留以下已归档 traceability 锚点：

| Requirement | Phase | Status |
|-------------|-------|--------|
| HOT-14 | Phase 60 | Complete |
| TST-12 | Phase 60 | Complete |
| GOV-44 | Phase 60 | Complete |
| GOV-56 | Phase 72, 74, 75 | Completed |
| ARC-19 | Phase 72, 73, 75 | Completed |
| TYP-21 | Phase 72, 73, 75 | Completed |
| TST-22 | Phase 72, 73, 74, 75 | Completed |
| QLT-30 | Phase 72, 73, 74, 75 | Completed |

## Previous Archived Milestone (v1.39)

**Milestone Goal:** 基于 `v1.38` latest archived baseline，先恢复 current governance lane 的 route/source-path/projection 一致性，再为 runtime consistency 与 public contract correction 建立单一执行入口，不再把 sanctioned hotspot 混写进 docs-only closeout。
**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Current route mode:** `no active milestone route / latest archived baseline = v1.39`
**Starting baseline:** `.planning/v1.38-MILESTONE-AUDIT.md, .planning/reviews/V1_38_EVIDENCE_INDEX.md, .planning/milestones/v1.38-ROADMAP.md, .planning/milestones/v1.38-REQUIREMENTS.md`
**Requirements basket:** `GOV-89, ARC-42, HOT-61, DOC-18, QLT-55, TST-53`
**Latest archived baseline:** `v1.39`
**Archive pointer:** `.planning/reviews/V1_39_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.39-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 133 的 requirement coverage、summary / verification / validation / audit / evidence index 已冻结为 latest archived baseline truth。`

## Previous Archived Milestone (v1.38)


**Milestone Goal:** 基于 `v1.37` latest archived baseline，压缩 current selector / archive boundary / docs-first governance story，把 route-marker / promoted-asset / handoff smoke 的重复断言压回 shared helper 与单一 canonical source。
**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Current route mode:** `no active milestone route / latest archived baseline = v1.38`
**Starting baseline:** `.planning/v1.37-MILESTONE-AUDIT.md, .planning/reviews/V1_37_EVIDENCE_INDEX.md, .planning/milestones/v1.37-ROADMAP.md, .planning/milestones/v1.37-REQUIREMENTS.md`
**Requirements basket:** `AUD-07, GOV-88, DOC-17, OSS-19, QLT-54, TST-52`
**Latest archived baseline:** `v1.38`
**Archive pointer:** `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.38-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 132 的 requirement coverage、summary / verification / validation / audit / evidence index 已冻结为 archived baseline truth。`

## Historical Archived Milestone (v1.37)

**Milestone Goal:** 基于 `v1.36` latest archived baseline，先完成一次不遗漏 Python/docs/config/governance 切面的 repo-wide terminal audit，再把首批 repo-internal hotspots（REST fallback / runtime-command / firmware-update）继续 inward decomposition，最后把 open-source continuity / private fallback reality 诚实固化为治理决策边界与最终审阅报告。
**Milestone status:** `archived / evidence-ready (2026-04-01)`
**Current route mode:** `no active milestone route / latest archived baseline = v1.37`
**Starting baseline:** `.planning/v1.36-MILESTONE-AUDIT.md, .planning/reviews/V1_36_EVIDENCE_INDEX.md, .planning/milestones/v1.36-ROADMAP.md, .planning/milestones/v1.36-REQUIREMENTS.md`
**Requirements basket:** `AUD-06, ARC-40, HOT-59, TST-50, QLT-52, ARC-41, HOT-60, TST-51, GOV-87, DOC-16, OSS-18, QLT-53`
**Latest archived baseline:** `v1.37`
**Archive pointer:** `.planning/reviews/V1_37_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.37-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 129 -> 131 的 requirement coverage、summary / verification / audit / evidence index 已冻结为 archived evidence frozen。`

## Historical Archived Milestone (v1.35)
