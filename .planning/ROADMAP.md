# Roadmap

## Milestones

- 🚧 **v1.44 Governance Load Shedding & Sanctioned Hotspot Narrowing** - `Phase 142 -> 145` active on 2026-04-04; current route = `v1.44 active milestone route / Phase 143 planned / execution-ready / latest archived baseline = v1.43`; latest archived evidence index = `.planning/reviews/V1_43_EVIDENCE_INDEX.md`
- ✅ **v1.43 Hotspot Second-Pass Slimming & Governance Load Shedding** - `Phase 139 -> 141` archived on 2026-04-04; historical closeout route truth = `no active milestone route / latest archived baseline = v1.43`; evidence index = `.planning/reviews/V1_43_EVIDENCE_INDEX.md`
- ✅ **v1.42 Hotspot Burn-Down, Observability Truth & Governance Cost Compression** - `Phase 137 -> 138` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.42`; evidence index = `.planning/reviews/V1_42_EVIDENCE_INDEX.md`
- ✅ **v1.41 Terminal Residual Audit, Remediation Charter & Maintainability Hardening** - `Phase 136 -> 136` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.41`; evidence index = `.planning/reviews/V1_41_EVIDENCE_INDEX.md`
- ✅ **v1.40 Request Policy Ownership, Entity De-Reflection & Fan Truth Hardening** - `Phase 134 -> 135` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.40`; evidence index = `.planning/reviews/V1_40_EVIDENCE_INDEX.md`
- ✅ **v1.39 Governance Recovery, Runtime Consistency & Public Contract Correction** - `Phase 133 -> 133` archived on 2026-04-02; historical closeout route truth = `no active milestone route / latest archived baseline = v1.39`; evidence index = `.planning/reviews/V1_39_EVIDENCE_INDEX.md`

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
## Overview

`v1.44` 直接继承 `v1.43` 的 archived audit / evidence chain，但不把 zero-active archived posture 误读成“无需继续演进”：当前路线显式重开 governance load shedding、toolchain freshness hardening 与 sanctioned hotspot narrowing，继续把仓库压回单一 north-star 主链。

**Coverage:** `5/21` `v1.44` requirements complete in `Phase 142 -> 145`; current active plan bundle = `3 completed predecessor / 3 planned current phase`.
**Default next command:** `$gsd-execute-phase 143`

## Current Milestone

## v1.44: Governance Load Shedding & Sanctioned Hotspot Narrowing

**Milestone status:** `active / phase 143 planned; execution-ready (2026-04-04)`
**Default next command:** `$gsd-execute-phase 143`
**Current route story:** `v1.44 active milestone route / Phase 143 planned / execution-ready / latest archived baseline = v1.43`
**Latest archived pointer:** `.planning/reviews/V1_43_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.43-MILESTONE-AUDIT.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
**Current phase handoff:** Phase 142 已作为已完成 predecessor 固化；Phase 143 现已具备 143-01 ~ 143-03 计划束，current route 进入 execution-ready，后续按既定 wave 执行再推进 Phase 144 -> 145。
**Plans**: `3 completed predecessor + 3 planned current phase` — run `$gsd-execute-phase 143`

## Phases

- [x] **Phase 142: governance load shedding and derived truth audit** - 已收口 selector family、promoted assets、`.planning/codebase` derived views、latest archived pointer 与 maintainer-facing first-hop 的职责边界，并为 `Phase 143` 的 execution-ready 计划束清出单一路径。 (complete 2026-04-04)
- [ ] **Phase 143: toolchain freshness hardening and route-projection automation** - 已生成 `143-01` root-proof guard hardening、`143-02` freshness/link/derived-map automation、`143-03` route projection/docs continuity guard sync 三个计划束；下一步执行并收口 machine-checkable contract。 (execution-ready 2026-04-04)
- [ ] **Phase 144: runtime-types, request-policy, and dispatch hotspot narrowing** - 对 `runtime_types.py`、request-policy family 与 command-result / dispatch hot path 继续 inward split 与 typed narrowing。 (queued 2026-04-04)
- [ ] **Phase 145: auth, firmware, and share boundary hardening** - 对 auth/session recovery、firmware update / OTA manifest 与 share/report 边界继续收窄，并完成 milestone closeout sync。 (queued 2026-04-04)

## Phase Details

### Phase 142: governance load shedding and derived truth audit

**Goal:** 先把 `.planning` 派生文档、selector projections、promoted assets、latest archived pointer 与 maintainer-facing docs first-hop 的职责重新压缩成单一 authority story，再为后续 toolchain 与 hotspot work 建立不漂移的 planning foundation。
**Depends on:** none
**Inputs**: `.planning/phases/142-governance-load-shedding-and-derived-truth-audit/142-CONTEXT.md`
**Requirements**: `AUD-10`, `GOV-99`, `GOV-100`, `DOC-25`, `TST-62`
**Success Criteria** (what must be TRUE):
  1. `.planning/codebase/*.md` 的 freshness / authority / snapshot 身份与 current route selector family 的边界被重新明确，derived views 不再伪装成 live truth。
  2. `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、registry、verification baseline、developer/runbook docs 与 focused guards 共同承认 `v1.44 active milestone route / Phase 142 complete / Phase 143 planning-ready / latest archived baseline = v1.43`。
  3. promoted assets、archive snapshots、latest archived evidence pointer 与 default-next truth 的职责分工继续 machine-checkable。
  4. 142 phase plan 明确指出哪些 toolchain / docs / guard drift 需要自动化 proof，哪些属于 archived-only predecessor evidence。
**Plans**: `3 completed` — route has since advanced to `$gsd-execute-phase 143`

### Phase 143: toolchain freshness hardening and route-projection automation

**Goal:** 把 nested worktree / repo-root detection、freshness audit、link audit 与 route projection 从“经验性好用”升级为可验证 contract，降低后续治理维护税与 handoff 失真概率。
**Depends on:** Phase 142
**Inputs**: `.planning/phases/143-toolchain-freshness-hardening-and-route-projection-automation/{143-CONTEXT.md,143-RESEARCH.md}`
**Requirements**: `QLT-60`, `GOV-101`, `DOC-26`, `TST-63`
**Success Criteria** (what must be TRUE):
  1. 本仓库中的 toolchain/root detection 不再把 nested worktree cwd 偶然性误当 authority signal。
  2. `.planning/codebase` freshness、selector projection、docs-entry drift 与 link audit 至少有一条 machine-checkable proof chain。
  3. contributor / release continuity first-hop 继续压缩到 canonical selector family + latest archived evidence，不引入新 authority layer。
  4. focused tests 能证明上述 contract 在 worktree / CI / local checks 下不再 silently drift。
**Plans**: `3 planned` — run `$gsd-execute-phase 143`

### Phase 144: runtime-types, request-policy, and dispatch hotspot narrowing

**Goal:** 在不改变 sanctioned formal homes 的前提下，继续缩减 `runtime_types.py` breadth、request-policy family ownership ambiguity 与 command dispatch/result policy 的 mixed responsibilities。
**Depends on:** Phase 143
**Inputs**: `.planning/phases/144-runtime-types-request-policy-and-dispatch-hotspot-narrowing/144-CONTEXT.md`
**Requirements**: `ARC-52`, `ARC-53`, `HOT-74`, `HOT-75`, `DOC-27`, `TST-64`
**Success Criteria** (what must be TRUE):
  1. `runtime_types.py` 继续保持唯一 outward runtime contract home，但 capability-local / control-local projections 不再把 breadth 无限制吸回 root。
  2. request-policy family 保持一个显式 owner / import home，support helpers 只承担 inward narrowing。
  3. dispatch / result / result_policy 共享单一 typed command-result taxonomy，不再重复解释 failure / pending / confirmation semantics。
  4. docs / meta guards 能解释并冻结新的 formal homes 与 dependency boundaries。
**Plans**: `0 planned`

### Phase 145: auth, firmware, and share boundary hardening

**Goal:** 在 auth/session、firmware update / OTA manifest 与 anonymous-share/report boundaries 上继续 inward split，同时把 milestone closeout selector story 一并收口。
**Depends on:** Phase 144
**Inputs**: `.planning/phases/145-auth-firmware-and-share-boundary-hardening/145-CONTEXT.md`
**Requirements**: `ARC-54`, `HOT-76`, `HOT-77`, `GOV-102`, `DOC-28`, `TST-65`
**Success Criteria** (what must be TRUE):
  1. auth manager / auth recovery 继续 inward decomposition，但 formal auth/session home 不漂移。
  2. refresh / relogin / recovery semantics 与 firmware/share boundary semantics 分别保持 typed, machine-checkable truth。
  3. firmware update entity shell 继续是 thin projection；OTA/share helpers 不得升格为第二 root。
  4. closeout 时 selector family、docs first-hop、verification baseline 与 archived evidence chain 能回到单一 authoritative story。
**Plans**: `0 planned`

## Latest Archived Milestone

## v1.43: Hotspot Second-Pass Slimming & Governance Load Shedding

**Milestone status:** `archived / evidence-ready (2026-04-04)`
**Default next command:** `$gsd-new-milestone`
**Current route story:** `no active milestone route / latest archived baseline = v1.43`
**Latest archived pointer:** `.planning/reviews/V1_43_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.43-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.43-ROADMAP.md, .planning/milestones/v1.43-REQUIREMENTS.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
**Current phase handoff:** `Milestone closeout complete；Phase 139、Phase 140 与 Phase 141 的 requirement coverage、summary / verification / validation、milestone audit 与 evidence index 已共同冻结为 latest archived baseline truth。`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.43`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.42`

## Phases

- [x] **Phase 139: REST/protocol mega-facade second-pass slimming and boundary hardening** - 已完成 `139-01` protocol rest-port binding split、`139-02` REST facade internal split + schedule group_id repair、`139-03` tests/docs/governance sync，并产出 summaries/verification/validation。 (complete 2026-04-02)
- [x] **Phase 140: release/governance source compression and codebase freshness** - 已 formalize stale verification path refresh、CHANGELOG public-summary scope、runbook access-mode wording、phase assets 与 governance ledgers/guards sync，并产出 summaries/verification/validation。 (complete 2026-04-02)
- [x] **Phase 141: control/runtime hotspot narrowing and device aggregate hardening** - 已完成 `141-01` router seam narrowing、`141-02` entry-root explicit factory wiring、`141-03` runtime contract inward decomposition、`141-04` device aggregate/runtime side-car hardening、`141-05` governance closeout sync，并产出 summaries/verification/validation。 (complete 2026-04-02)

## Phase Details

### Phase 139: REST/protocol mega-facade second-pass slimming and boundary hardening

**Goal:** 在不改变 `LiproRestFacade` 与 `rest_port.py` formal-home 身份的前提下，继续把 mega-facade / bound-port mechanics 往内层 support 模块迁移，并修复 schedule group_id forwarding honesty。
**Depends on:** none
**Requirements**: `ARC-48`, `HOT-70`, `HOT-71`, `GOV-94`, `DOC-22`, `TST-59`
**Success Criteria** (what must be TRUE):
  1. `custom_components/lipro/core/protocol/rest_port.py` 只保留 typed port contracts、port family 与 bind helper；bound adapters 下沉到 `rest_port_bindings.py`，但不得长出第二 protocol root。
  2. `custom_components/lipro/core/api/rest_facade.py` 只保留 canonical REST child-façade composition / outward binding；transport/auth/mapping private mechanics 下沉到 `rest_facade_internal_methods.py`，不得回退到 mixin / dynamic delegation folklore。
  3. schedule `group_id` 在 `protocol facade -> rest ports -> rest facade -> endpoint surface -> schedule endpoint` 链路中保持显式透传，不再 silently drop。
  4. `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`、registry、verification baseline、developer/runbook docs 与 focused guards 必须共同承认 `v1.43` active route。
  5. focused `pytest`、`ruff`、`check_file_matrix` 与 `check_architecture_policy` 必须通过。
**Plans**: 3 planned / 3 completed — summaries captured; successor handoff 已收束到 `Phase 140 complete`。

### Phase 140: release/governance source compression and codebase freshness

**Goal:** 压缩 release/governance docs duplication，刷新 archived remediation / verification commands 的过期路径，并把 public release notes、support contract 与 maintainer runbook 的 access-mode 语义重新对齐。
**Depends on:** Phase 139
**Requirements**: `AUD-09`, `GOV-95`, `DOC-23`, `TST-60`
**Success Criteria** (what must be TRUE):
  1. `.planning/baseline/VERIFICATION_MATRIX.md`、archived remediation charter 与 related ledgers 不再引用已删除/迁移的测试路径。
  2. `CHANGELOG.md` 重新回到 public-facing release summary 身份，不再直接承载 `.planning` / selector / phase-internal 术语。
  3. `docs/MAINTAINER_RELEASE_RUNBOOK.md` 与 `SUPPORT.md` / `README*.md` 对 private-access / future public mirror / release asset reachability 的条件语义保持一致。
  4. `tests/meta` 补齐相应守卫，避免上述 drift 再次无声回流。
**Plans**: 3 planned / 3 completed — `140-01` stale-proof / baseline refresh、`140-02` public-summary / access-mode contract formalization、`140-03` route/governance/guard sync 已形成 phase asset bundle。

### Phase 141: control/runtime hotspot narrowing and device aggregate hardening

**Goal:** 在不破坏既有 formal homes 的前提下，继续收窄 `service_router` layering / underscore leakage、`runtime_types.py` breadth、`core/device/device.py` aggregate 宽面与 `entry_root_support.py` lazy-import maintenance tax。
**Depends on:** Phase 140
**Inputs**: `.planning/phases/141-control-runtime-hotspot-narrowing-and-device-aggregate-hardening/{141-CONTEXT.md,141-RESEARCH.md}`
**Requirements**: `ARC-49`, `ARC-50`, `ARC-51`, `HOT-72`, `HOT-73`, `GOV-96`, `DOC-24`, `TST-61`
**Plans**: 5 planned / 5 completed — `141-01` router seam narrowing、`141-02` entry-root explicit factory wiring、`141-03` runtime contract inward decomposition、`141-04` device aggregate/runtime side-car hardening、`141-05` governance closeout and route sync。
**Status**: complete / closeout-ready — `141-*` summaries、aggregate closeout bundle 与 governance route truth 已同步收口。
**Default next**: `$gsd-complete-milestone v1.43`
## Previous Archived Milestone

## v1.42: Hotspot Burn-Down, Observability Truth & Governance Cost Compression

**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Default next command:** `$gsd-new-milestone`
**Current route story:** `no active milestone route / latest archived baseline = v1.42`
**Latest archived pointer:** `.planning/reviews/V1_42_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.42-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.42-ROADMAP.md, .planning/milestones/v1.42-REQUIREMENTS.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
**Current phase handoff:** `Milestone closeout complete；Phase 137 与 Phase 138 的 requirement coverage、summary / verification / validation、milestone audit 与 evidence index 已共同冻结为 latest archived baseline truth。`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.42`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.41`

## Phases

- [x] **Phase 137: hotspot burn-down, command/observability convergence, and governance derivation compression** - 已完成 `137-01` governance/docs/test contract hardening、`137-02` protocol/rest/auth hotspot decomposition、`137-03` device/command/observability hardening，并产出 closeout-ready summaries/verification。 (complete 2026-04-02)
- [x] **Phase 138: runtime contract decoupling, support-guard hardening, and docs archive alignment** - 已完成 `138-01` governance/docs/route follow-up、`138-02` runtime/service contract decoupling、`138-03` support naming guard + verification sync、`138-04` connect-status outcome propagation，并产出 closeout-ready summaries/verification。 (complete 2026-04-02)

## Phase Details

### Phase 137: hotspot burn-down, command/observability convergence, and governance derivation compression

**Goal:** 把 v1.41 审阅章程中的 WS-01 ~ WS-06 收敛到一个 machine-checkable 的 active phase：先压低 governance derivation tax 与 semantic-guard blind spot，再处理 mega-facade / auth hotspot，最后同步压缩 device relay wall、typed command semantics 与 connect-status observability。
**Depends on:** none
**Requirements**: `ARC-46`, `HOT-67`, `HOT-68`, `HOT-69`, `GOV-92`, `DOC-20`, `TST-57`
**Success Criteria** (what must be TRUE):
  1. runbook/developer docs/current-route guards 对 latest archived pointer 与 current selector 的断言必须只有单一 canonical 角色，不允许“新旧 pointer 同页共存也算通过”。
  2. `core/api/rest_facade.py` 与 `core/protocol/facade.py` 必须继续削减 manual delegation wall / child-façade rebinding seam，同时保持单一 formal root、stable import home 与 outward contract 不回退。
  3. `core/auth/manager.py` 必须把 credential seed、token lifecycle、adaptive expiry、refresh dedupe 与 re-login fallback 拆回更清晰的 collaborator / helper 边界。
  4. `core/device/device.py` 必须收紧 relay wall 的正式边界，`core/command/dispatch.py` 与 `core/api/status_service.py` 必须保持 typed command / observability honesty。
  5. `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、registry、verification baseline、developer/runbook note 与 current-route guards 必须共同承认 `v1.42 active milestone route / starting from latest archived baseline = v1.41`。
  6. focused `pytest`、`ruff`、`check_file_matrix` 与 `check_architecture_policy` 必须通过。
**Plans**: 3 planned / 3 completed — summaries captured; archived baseline frozen; next = `$gsd-new-milestone`

### Phase 138: runtime contract decoupling, support-guard hardening, and docs archive alignment

**Goal:** 在 `Phase 137` 已完成 sanctioned hotspot burn-down 的前提下，继续收口 closeout review 暴露的 remaining structural debt：runtime/service shared contract reverse import、connect-status outcome flattening、support bridge naming tension 与 live docs/archive appendix 叙事分工。
**Depends on:** Phase 137
**Requirements**: `OBS-01`, `ARC-47`, `QLT-59`, `GOV-93`, `DOC-21`, `TST-58`
**Success Criteria** (what must be TRUE):
  1. `custom_components/lipro/runtime_types.py` 不再从 `services/contracts.py` 导入 shared service-facing types；新的 root-level typed contract home 必须 machine-checkable。
  2. `core/api/status_service.py` 与 `endpoint_surface -> rest_port -> protocol facade` 调用链必须保留显式 `ConnectStatusQueryResult`，不再把不同 outcome 压平成 `{}`。
  3. `control/service_router_support.py` 的角色必须被 docs/tests 明确限制为 inward formal bridge home，而不是第二 public control root。
  4. `docs/README.md`、`docs/developer_architecture.md`、runbook 与 baseline docs 必须共同承认 live docs / pull-only archive appendix 的角色分工。
  5. `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`、registry 与 verification baseline 必须共同承认 `Phase 138` 是当前 terminal closeout-ready phase。
  6. focused `pytest`、`ruff`、`check_file_matrix` 与 `check_architecture_policy` 必须通过。
**Plans**: 4 planned / 4 completed — summaries captured; archived baseline frozen; next = `$gsd-new-milestone`
## Previous Archived Milestone

## v1.41: Terminal Residual Audit, Remediation Charter & Maintainability Hardening

**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Default next command:** `$gsd-new-milestone`
**Current route story:** `no active milestone route / latest archived baseline = v1.41`
**Latest archived pointer:** `.planning/reviews/V1_41_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.41-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.41-ROADMAP.md, .planning/milestones/v1.41-REQUIREMENTS.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
**Current phase handoff:** `Milestone closeout complete；Phase 136 的 requirement coverage、summary / verification / validation / audit / evidence index 已冻结为 previous archived baseline truth。`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.41`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.40`

## Phases

- [x] **Phase 136: repo-wide terminal residual audit, hygiene fixes, and remediation charter** - 已完成 `136-01` terminal audit report + remediation charter、`136-02` vendor-crypto/log-safety hygiene fixes、`136-03` governance/docs/guards sync。 (complete 2026-04-02)

## Phase Details

### Phase 136: repo-wide terminal residual audit, hygiene fixes, and remediation charter

**Requirements**: `AUD-08`, `GOV-91`, `DOC-19`, `ARC-45`, `QLT-58`, `TST-56`
**Success Criteria** (what must be TRUE):
  1. 全仓 Python/docs/config/governance 审查必须形成单一 `V1_41_TERMINAL_AUDIT_REPORT.md` verdict home，而不是散落在 summary 片段中。
  2. `V1_41_REMEDIATION_CHARTER.md` 必须把热点按 severity、formal home、delete gate 与后续计划分流，明确哪些已修复、哪些仍需后续 phase。
  3. 首批生产修复必须至少覆盖一类策略漂移：本轮选定 vendor-crypto helper 统一与 log-safety placeholder 一致性。
  4. `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、registry、verification baseline、developer/runbook note 与 current-route guards 必须共同承认 `v1.41 active milestone route / starting from latest archived baseline = v1.40`。
  5. phase assets、focused tests 与 `uv run ruff check` 必须证明本轮 deliverable 不是文档空转，而是可回放的 closeout-ready current route。
**Plans**: 3/3 complete — `136-01` audit+charter、`136-02` hygiene fixes、`136-03` governance route sync
**Execution summaries**: `136-01-SUMMARY.md`, `136-02-SUMMARY.md`, `136-03-SUMMARY.md`, `136-SUMMARY.md`
**Verification**: `136-VERIFICATION.md`
**Validation**: `136-VALIDATION.md`

## Previous Archived Milestone


## v1.38: Governance Story Compression, Archive Segregation & Public Entry Simplification

**Milestone status:** `archived / evidence-ready (2026-04-02)`
**Default next command:** `$gsd-new-milestone`
**Current route story:** `no active milestone route / latest archived baseline = v1.38`
**Latest archived pointer:** `.planning/reviews/V1_38_EVIDENCE_INDEX.md`
**Latest archived audit artifact:** `.planning/v1.38-MILESTONE-AUDIT.md`
**Archived snapshots:** `.planning/milestones/v1.38-ROADMAP.md`, `.planning/milestones/v1.38-REQUIREMENTS.md`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Phases

- [x] **Phase 132: current-story compression and archive-boundary cleanup** - 已完成 current planning docs / developer-runbook route compression、route-marker helper dedupe、recent promoted-asset coverage 回流与 handoff smoke 瘦身。 (complete 2026-04-02)

## Phase Details

### Phase 132: current-story compression and archive-boundary cleanup
**Goal:** 把 live selector、latest archived pointer、historical archive story 与 governance smoke/test helper 的职责重新分层：current docs 只讲当前路线与必要 handoff，archive/history 回到 pull-only 边界，meta guards 通过 canonical registry + shared helper 断言，而不再扩散相同 prose/asset family。
**Depends on:** Phase 131
**Requirements**: AUD-07, GOV-88, DOC-17, OSS-19, QLT-54, TST-52
**Success Criteria** (what must be TRUE):
  1. `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 必须把 active-route compression 与 closeout 一并收敛到单一 registry-backed selector：live docs 只保留 archived-only current route、latest archived pointer 与 default next command。
  2. `docs/developer_architecture.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 首屏不再混用 archived-only frozen wording；current route / latest archived pointer 与 registry 投影一致。
  3. `tests/meta/governance_contract_helpers.py` 提供统一 route-marker helper，phase guards 不再各自重复 `CURRENT_ROUTE` / `CURRENT_MILESTONE_DEFAULT_NEXT` presence loops。
  4. `tests/meta/test_governance_route_handoff_smoke.py` 只保留 docs+GSD fast-path smoke；recent promoted asset family 回到 promoted-phase guards，不再在 smoke suite 里重复维护。
  5. `tests/meta/governance_current_truth.py` 不再内联 historical/forbidden-literal clutter；legacy markers 退回专属 helper home，canonical route 继续只读 registry-backed contract。
**Plans**: 3/3 complete — `132-01` active-route docs compression、`132-02` current-truth/helper dedupe、`132-03` promoted-asset / handoff smoke topic cleanup
**Execution summaries**: `132-01-SUMMARY.md`, `132-02-SUMMARY.md`, `132-03-SUMMARY.md`, `132-SUMMARY.md`
**Verification**: `132-VERIFICATION.md`
**Validation**: `132-VALIDATION.md`

## Historical Archived Milestone

## v1.36: Terminal Residual Convergence, Runtime Access De-Reflection & Open-Source Readiness Hardening

**Milestone status:** `archived / evidence-ready (2026-04-01)`
**Default next command:** `$gsd-new-milestone`
**Current route story:** `no active milestone route / latest archived baseline = v1.36`
**Latest archived pointer:** `.planning/reviews/V1_36_EVIDENCE_INDEX.md`
**Current audit artifact:** `.planning/v1.36-MILESTONE-AUDIT.md`
**Historical closeout marker:** historical closeout route truth = `no active milestone route / latest archived baseline = v1.36`
**Historical archive-transition marker:** historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.35`
**Promoted phase evidence allowlist:** `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Phases

- [x] **Phase 126: service-router developer callback-home convergence and diagnostics helper residual slimming** - 已完成 diagnostics helper inward thinning：`handlers.py` 直连 mechanics home、`helpers.py` 删除未使用 duplicate helper、`developer_router_support.py` 复用统一 iterator builder，并同步 v1.36 route / plan / verification truth。 (complete 2026-04-01)
- [x] **Phase 127: runtime-access de-reflection, typed runtime entry contracts, and hotspot continuation** - 已完成 `runtime_access` typed telemetry seam 收口、support-view de-reflection 与 focused/full verification 证据冻结，control/runtime seam 不再依赖 stringly dict fallback 或 `type(...).__getattribute__` 反射。 (complete 2026-04-01)
- [x] **Phase 128: open-source readiness, benchmark-coverage gates, and maintainer continuity hardening** - 已把 private-access / single-maintainer continuity / security fallback 限制诚实 codify，并把 coverage baseline diff、benchmark smoke、strict markers 与 final evidence freeze 固化为 archived evidence chain。 (complete 2026-04-01)

## Historical Archived Milestone

## Archive Chronology Appendix

## v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement
- archived continuity anchor preserved for release/history guards.

## v1.23 Repository-Wide Terminal Code Audit, Residual Eradication & Closeout Truth Freeze
- historical archived milestone reference retained for continuity guards.

## v1.24 Runtime Boundary Tightening, Tooling Kernel Decoupling & Open-Source Entry Convergence
- historical archived milestone reference retained for continuity guards.

## v1.25: Hotspot Inward Decomposition, Typed Boundary Hardening & Redaction Convergence
- archived roadmap anchor retained for Phase 90 hotspot freeze guards.

## v1.28 Governance Portability, Verification Stratification & Open-Source Continuity Hardening
- historical archived milestone reference retained for continuity guards.

## v1.29 Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization
- evidence pointer: `.planning/reviews/V1_29_EVIDENCE_INDEX.md`

## Historical Archive Snapshot Index

- `v1.1-ROADMAP.md`
- `v1.1-REQUIREMENTS.md`
- `v1.2-ROADMAP.md`
- `v1.2-REQUIREMENTS.md`
- `v1.4-ROADMAP.md`
- `v1.4-REQUIREMENTS.md`
- `v1.5-ROADMAP.md`
- `v1.5-REQUIREMENTS.md`
- `v1.6-ROADMAP.md`
- `v1.6-REQUIREMENTS.md`
- `v1.12-ROADMAP.md`
- `v1.12-REQUIREMENTS.md`
- `v1.13-ROADMAP.md`
- `v1.13-REQUIREMENTS.md`
- `v1.14-ROADMAP.md`
- `v1.14-REQUIREMENTS.md`
- `v1.15-ROADMAP.md`
- `v1.15-REQUIREMENTS.md`
- `v1.16-ROADMAP.md`
- `v1.16-REQUIREMENTS.md`
- `v1.17-ROADMAP.md`
- `v1.17-REQUIREMENTS.md`
- `v1.21-ROADMAP.md`
- `v1.21-REQUIREMENTS.md`
- `v1.22-ROADMAP.md`
- `v1.22-REQUIREMENTS.md`
- `v1.23-ROADMAP.md`
- `v1.23-REQUIREMENTS.md`
- `v1.24-ROADMAP.md`
- `v1.24-REQUIREMENTS.md`
- `v1.25-ROADMAP.md`
- `v1.25-REQUIREMENTS.md`
- `v1.26-ROADMAP.md`
- `v1.26-REQUIREMENTS.md`
- `v1.27-ROADMAP.md`
- `v1.27-REQUIREMENTS.md`
- `v1.28-ROADMAP.md`
- `v1.28-REQUIREMENTS.md`
