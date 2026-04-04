# Requirements

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
  version: v1.44
  name: Governance Load Shedding & Sanctioned Hotspot Narrowing
  status: active / phase 143 planned; execution-ready (2026-04-04)
  phase: '143'
  phase_title: toolchain freshness hardening and route-projection automation
  phase_dir: 143-toolchain-freshness-hardening-and-route-projection-automation
  route_mode: v1.44 active milestone route / Phase 143 planned / execution-ready / latest archived baseline = v1.43
latest_archived:
  version: v1.43
  name: Hotspot Second-Pass Slimming & Governance Load Shedding
  status: archived / evidence-ready (2026-04-04)
  phase: '141'
  phase_title: control/runtime hotspot narrowing and device aggregate hardening
  phase_dir: 141-control-runtime-hotspot-narrowing-and-device-aggregate-hardening
  audit_path: .planning/v1.43-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_43_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.42
  name: Hotspot Burn-Down, Observability Truth & Governance Cost Compression
  evidence_path: .planning/reviews/V1_42_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.44 active milestone route / Phase 143 planned / execution-ready / latest archived baseline = v1.43
  default_next_command: $gsd-execute-phase 143
  latest_archived_evidence_pointer: .planning/reviews/V1_43_EVIDENCE_INDEX.md
contract_version: 1
```
<!-- governance-route-contract:end -->
## Current Milestone (v1.44)

**Milestone Goal:** 基于 `v1.43` latest archived baseline，显式重开 governance load shedding、toolchain freshness hardening 与 sanctioned hotspot narrowing：先清掉 derived truth / route hardcode / docs-entry 漂移，再继续 inward split `runtime_types.py`、request-policy family、dispatch / command-result、auth/session 与 firmware/share boundaries。 
**Milestone status:** `active / phase 143 planned; execution-ready (2026-04-04)`
**Current route mode:** `v1.44 active milestone route / Phase 143 planned / execution-ready / latest archived baseline = v1.43`
**Starting baseline:** `.planning/v1.43-MILESTONE-AUDIT.md`, `.planning/reviews/V1_43_EVIDENCE_INDEX.md`, `.planning/milestones/v1.43-ROADMAP.md`, `.planning/milestones/v1.43-REQUIREMENTS.md`
**Requirements basket:** `AUD-10, GOV-99, GOV-100, DOC-25, TST-62, QLT-60, GOV-101, DOC-26, TST-63, ARC-52, ARC-53, HOT-74, HOT-75, DOC-27, TST-64, ARC-54, HOT-76, HOT-77, GOV-102, DOC-28, TST-65`
**Latest archived baseline:** `v1.43`
**Archive pointer:** `.planning/reviews/V1_43_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.43-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-execute-phase 143`
**Current phase handoff:** `Phase 142` 已完成治理减负 / derived-truth audit；`Phase 143` 当前已拥有 `143-01` ~ `143-03` plan bundle，下一步执行 `$gsd-execute-phase 143`，而不是回流为 archived-only continuation。

### Governance / Derived Truth
- [x] **AUD-10**: 审计 `.planning/codebase/*`、promoted assets、selector projections 与 maintainer-facing docs first-hop，清除重复 / 过期 / 影子真相，并把 derived-view 身份重新固定到 authority matrix / verification baseline 中。
- [x] **GOV-99**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、registry、verification baseline、developer/runbook docs 与 focused route guards 必须共同承认 `v1.44 active milestone route / Phase 142 complete / Phase 143 planning-ready / latest archived baseline = v1.43`。
- [x] **GOV-100**: selector family、latest archived pointer、promoted asset allowlist 与 archive snapshots 的职责边界必须继续 machine-checkable，避免 `.planning/codebase`、docs 或工具链回流成第二 authority chain。
- [x] **DOC-25**: developer architecture / runbook 的 first-hop 说明必须从 archived-only posture 切到 `v1.44` active route，同时继续保持 `v1.43` 作为 pull-only archived evidence。
- [x] **TST-62**: focused governance/toolchain/meta guards 必须冻结新 selector state、latest archived pointer 与 derived-view non-authority 边界。

### Toolchain / Freshness
- [ ] **QLT-60**: nested worktree / repo-root detection 在本仓库的工具链、freshness guard 与 link audit 中必须被显式硬化或降级为非 authority fallback，不再依赖 accidental cwd folklore。
- [ ] **GOV-101**: `.planning/codebase` freshness、promoted asset projection、link audit 与 route hardcode 漏洞必须转成 machine-checkable proof，而不是靠手工复述。
- [ ] **DOC-26**: contributor / release continuity first-hop 必须进一步压缩为 canonical selector family + latest archived evidence pointer，不得把 planning-only 叙事泄漏给 public docs。
- [ ] **TST-63**: focused toolchain/freshness/link guards 必须覆盖 worktree/root-detection、selector projection 与 docs-entry drift。

### Runtime / Command Contracts
- [ ] **ARC-52**: `custom_components/lipro/runtime_types.py` 必须继续保持 shared runtime contract 的唯一 sanctioned outward root，但 breadth 仍可继续 inward decomposition 到 capability-local or control-local homes。
- [ ] **ARC-53**: request-policy family 必须继续收敛到一个显式 owner / import home；support helper 只允许 inward narrowing，不得恢复 dual policy truth。
- [ ] **HOT-74**: `core/command/dispatch.py`、`core/command/result.py` 与 `core/command/result_policy.py` 必须围绕单一 typed command-result taxonomy 继续瘦身。
- [ ] **HOT-75**: request-policy / dispatch / command-result 交界处不得继续漂浮 stringly helper leakage、cross-family fallback folklore 或重复 failure classification。
- [ ] **DOC-27**: developer/governance docs 必须记录 runtime-types、request-policy 与 command-result formal homes 的最新 narrowing 结果，但不得再造第二解释链。
- [ ] **TST-64**: focused runtime/command/meta guards 必须冻结 narrowed command-policy contracts 与 outward semantics。

### Auth / OTA / Share Boundaries
- [ ] **ARC-54**: `core/auth/manager.py` 与 `core/api/auth_recovery.py` 必须继续 inward split / typed seam 收敛，同时保留单一 auth/session formal home。
- [ ] **HOT-76**: refresh / relogin / recovery failure semantics 必须继续统一到 one typed contract，不再在 auth manager、API recovery 与 runtime call-sites 各自解释。
- [ ] **HOT-77**: `entities/firmware_update.py`、`core/ota/manifest.py` 与 related share/report boundary 必须继续收窄 breadth；entity shell 仍是 thin projection，helpers 不得升格为 root。
- [ ] **GOV-102**: v1.44 closeout 需要把 governance load shedding、toolchain hardening 与 sanctioned hotspot narrowing 同步收束为单一 selector story，而不是遗留 planning-only shadow route。
- [ ] **DOC-28**: developer/release docs 必须解释 auth / firmware / share 正式归属与 archived evidence chain 的关系，不得引入新的 authority layer。
- [ ] **TST-65**: focused auth/ota/share/meta suites 必须冻结 narrowed auth-session and firmware/share boundary contracts。

## Coverage Snapshot

- v1.44 requirements: 21 total
- Current mapped: 21
- Current complete: 5
- Current pending: 16

## Requirement Trace Table

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUD-10 | Phase 142 | Complete |
| GOV-99 | Phase 142 | Complete |
| GOV-100 | Phase 142 | Complete |
| DOC-25 | Phase 142 | Complete |
| TST-62 | Phase 142 | Complete |
| QLT-60 | Phase 143 | Planned |
| GOV-101 | Phase 143 | Planned |
| DOC-26 | Phase 143 | Planned |
| TST-63 | Phase 143 | Planned |
| ARC-52 | Phase 144 | Planned |
| ARC-53 | Phase 144 | Planned |
| HOT-74 | Phase 144 | Planned |
| HOT-75 | Phase 144 | Planned |
| DOC-27 | Phase 144 | Planned |
| TST-64 | Phase 144 | Planned |
| ARC-54 | Phase 145 | Planned |
| HOT-76 | Phase 145 | Planned |
| HOT-77 | Phase 145 | Planned |
| GOV-102 | Phase 145 | Planned |
| DOC-28 | Phase 145 | Planned |
| TST-65 | Phase 145 | Planned |

## Latest Archived Milestone (v1.43)

**Milestone Goal:** 基于 `v1.42` latest archived baseline，完成 REST/protocol second-pass slimming、group_id forwarding honesty、release/governance freshness formalization，以及 control/runtime/device hotspot narrowing 与 governance closeout truth 的一次性收口；这些结果现已正式冻结为 archived baseline，而不是继续悬停在 closeout-ready 中间态。
**Milestone status:** `archived / evidence-ready (2026-04-04)`
**Current route mode:** `no active milestone route / latest archived baseline = v1.43`
**Starting baseline:** `.planning/v1.42-MILESTONE-AUDIT.md, .planning/reviews/V1_42_EVIDENCE_INDEX.md, .planning/milestones/v1.42-ROADMAP.md, .planning/milestones/v1.42-REQUIREMENTS.md`
**Requirements basket:** `ARC-48, HOT-70, HOT-71, GOV-94, DOC-22, TST-59, AUD-09, GOV-95, DOC-23, TST-60, ARC-49, ARC-50, ARC-51, HOT-72, HOT-73, GOV-96, DOC-24, TST-61`
**Latest archived baseline:** `v1.43`
**Archive pointer:** `.planning/reviews/V1_43_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.43-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `Milestone closeout complete；Phase 139 + 140 + 141 的 requirement coverage、summary / verification / validation、archived snapshots 与 evidence index 已冻结为 latest archived baseline truth。`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.43`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.42`

### Protocol / Architecture
- [x] **ARC-48**: `custom_components/lipro/core/protocol/rest_port.py` 必须继续瘦身到 typed contracts + port family + bind helper；bound adapter mechanics 下沉到 sibling helper，但不得新增第二 protocol root。 
- [x] **HOT-70**: `custom_components/lipro/core/api/rest_facade.py` 必须把 transport/auth/mapping private mechanics inward split 到 local helper module，同时保持 `LiproRestFacade` canonical REST child-façade 身份不变。 
- [x] **HOT-71**: schedule `group_id` 在 `protocol facade -> rest ports -> rest facade -> endpoint surface -> schedule endpoint` 调用链中必须保持显式透传，mesh / standard schedule 行为不得 silently diverge。 

### Governance / Docs / Tests
- [x] **GOV-94**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、registry、verification baseline、developer/runbook docs 与 focused route guards 必须共同承认当前 active route truth；当前投影已切到 `v1.43 active milestone route / Phase 141 complete / closeout-ready / latest archived baseline = v1.42`。 
- [x] **DOC-22**: `docs/developer_architecture.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 必须把 second-pass split 结果、latest archived pointer、Phase 140 predecessor freshness chain 与 `Phase 141` closeout-ready current route 讲清楚，而不制造新 authority chain。 
- [x] **TST-59**: focused unit tests、meta guards、route/diff verification 与 lint/check 命令必须证明本轮 second-pass slimming 没有破坏 outward contract。 
- [x] **AUD-09**: `.planning/baseline/VERIFICATION_MATRIX.md`、archived remediation docs 与 related ledgers 已清掉 stale release/governance verification paths，并把 runnable proof 更新到当前 guard family。 
- [x] **GOV-95**: release/governance selector family、baseline docs、residual ledgers 与 archived remediation docs 已压缩重复叙事，减少 stale route / stale path duplication。 
- [x] **DOC-23**: `CHANGELOG.md`、`SUPPORT.md`、`README*.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 已对 public-facing summary、private-access / future public mirror 与 release asset reachability 使用一致语义。 
- [x] **TST-60**: `tests/meta` 已补齐 changelog public-summary、runbook conditional wording 与 governance freshness 的守卫，避免上述 drift 再次无声回流。 

### Phase 141 Delivered Hotspots
- [x] **ARC-49**: `custom_components/lipro/control/service_router.py` 必须退回 public callback shell；underscore helper 与 imported collaborator patch seam 必须收回 `service_router_support.py` 这样的 sanctioned seam。 
- [x] **ARC-50**: `custom_components/lipro/control/entry_root_support.py` / `custom_components/lipro/__init__.py` 必须把 lazy factory wiring 显式化，同时保持 HA root adapter 的 call-time factory 与 patch-friendly 语义。 
- [x] **ARC-51**: `custom_components/lipro/runtime_types.py` 必须 inward decomposition 到 capability-local projections，但仍是 shared runtime contract 的唯一 sanctioned outward root。 
- [x] **HOT-72**: service-router layering / underscore leakage 必须继续收窄，focused control-plane tests 与 guards 不得再依赖 router-root accidental exports。 
- [x] **HOT-73**: `custom_components/lipro/core/device/device.py` 必须继续收窄 aggregate surface，并把 MQTT freshness / outlet-power / legacy cleanup 固定在本地 runtime side-car seam。 
- [x] **GOV-96**: Phase 141 closeout 必须把 selector family、registry、verification baseline、phase assets 与 governance guards 一次性推进到 `Phase 141 complete / closeout-ready`。 
- [x] **DOC-24**: `docs/developer_architecture.md` 必须记录 service-router、entry-root、runtime-types、device aggregate 的新 formal home，但不得形成第二 authority chain。 
- [x] **TST-61**: focused control/runtime/device/meta/governance lanes 必须冻结本 phase 的 narrowing/hardening 与 final closeout truth。 

## Coverage Snapshot

- v1.43 requirements: 18 total
- Current mapped: 18
- Current complete: 18
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
| ARC-49 | Phase 141 | Complete |
| ARC-50 | Phase 141 | Complete |
| ARC-51 | Phase 141 | Complete |
| HOT-72 | Phase 141 | Complete |
| HOT-73 | Phase 141 | Complete |
| GOV-96 | Phase 141 | Complete |
| DOC-24 | Phase 141 | Complete |
| TST-61 | Phase 141 | Complete |
## Previous Archived Milestone (v1.42)

**Milestone Goal:** 基于 `v1.41` latest archived baseline，先完成 sanctioned hotspot burn-down，再把 closeout review 暴露出的 runtime/service typed contract 反向依赖、connect-status outcome 压平、support 命名守卫与 docs/archive 叙事张力收回同一 execution route；当前它已退回 previous archived baseline。
**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Current route mode:** `no active milestone route / latest archived baseline = v1.42`
**Starting baseline:** `.planning/v1.41-MILESTONE-AUDIT.md, .planning/reviews/V1_41_EVIDENCE_INDEX.md, .planning/milestones/v1.41-ROADMAP.md, .planning/milestones/v1.41-REQUIREMENTS.md`
**Requirements basket:** `ARC-46, HOT-67, HOT-68, HOT-69, OBS-01, GOV-92, DOC-20, TST-57, ARC-47, QLT-59, GOV-93, DOC-21, TST-58`
**Latest archived baseline:** `v1.42`
**Archive pointer:** `.planning/reviews/V1_42_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.42-MILESTONE-AUDIT.md`
**Default next command:** `$gsd-new-milestone`
**Current phase handoff:** `v1.42 现已退回 previous archived baseline；其 archived snapshots、milestone audit 与 evidence index 继续作为 v1.43 closeout 的 pull-only predecessor truth。`
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
