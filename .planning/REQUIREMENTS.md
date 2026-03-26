# Requirements: Lipro-HASS North Star Evolution

## Current Milestone (v1.21)

> `v1.21` 以 `v1.20` archived baseline、machine-readable bootstrap drift 修正与 `Phase 76 -> 78` 的 governance route guards 为 immediate seed；当前 mutable story 已前推到 `Phase 78 complete`，里程碑状态为 `closeout-ready`，默认下一步为 `$gsd-complete-milestone v1.21`；本轮重点不是重开生产热点，而是把 planning/bootstrap/current-route truth 冻结成稳定、低维护、可机器消费的正式 handoff contract。

### Governance Bootstrap Truth Hardening & Planning Route Automation

- [x] **GOV-57**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / tests/meta` 必须共享单一 deterministic current-route 与 next-milestone seed；archived-only / active-route 切换不得再依赖 accidental heading order、hidden parser assumptions 或大段 prose 复制。
- [x] **ARC-20**: 历史 milestone body 可以继续保留 audit / archive 身份，但不得再在 current-route 之前以 parser-visible 形式伪装成 active/current milestone 候选。
- [x] **DOC-04**: planning docs 必须显式区分 human-readable narrative 与 machine-readable bootstrap contract，并在不污染 public docs 的前提下诚实声明 latest archived baseline / previous archived baseline / next step。
- [x] **TST-23**: focused governance guards 必须覆盖 active-route bootstrap、latest-archive projection、historical-route demotion 与 literal-drift freeze，避免同一 current-story 在多份 suites 中手工散写。
- [x] **QLT-31**: 开启下一条正式路线必须成为可重复验证的质量门：`gsd` smoke、focused route guards、file-matrix / architecture / repo-wide gates 需共同证明 route activation 不是一次性修复。

## Traceability for v1.21 route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-57 | Phase 76, 78 | Completed |
| ARC-20 | Phase 76 | Completed |
| DOC-04 | Phase 77 | Completed |
| TST-23 | Phase 77 | Completed |
| QLT-31 | Phase 78 | Completed |

**Current Coverage:**
- v1.21 requirements: 5 total
- Current mapped: 5
- Current complete: 5
- Current pending: 0
- Current unmapped: 0 ✓

<!-- governance-route-contract:start -->
```yaml
contract_version: 1
contract_name: governance-route
active_milestone:
  version: v1.21
  name: Governance Bootstrap Truth Hardening & Planning Route Automation
  status: closeout-ready (2026-03-26)
  phase: "78"
  phase_title: Quality gate formalization, route-handoff ergonomics, and milestone-closeout readiness
  route_mode: Phase 78 complete
latest_archived:
  version: v1.20
  name: Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement
  status: archived / evidence-ready (2026-03-25)
  phase: "75"
  phase_title: Access-mode truth closure, evidence promotion formalization, and thin-adapter typing hardening
  phase_dir: 75-access-mode-truth-closure-evidence-promotion-formalization-and-thin-adapter-typing-hardening
  audit_path: .planning/v1.20-MILESTONE-AUDIT.md
  evidence_path: .planning/reviews/V1_20_EVIDENCE_INDEX.md
  evidence_label: latest archived evidence index
previous_archived:
  version: v1.19
  name: Audit-Driven Final Hotspot Decomposition & Governance Truth Projection
  evidence_path: .planning/reviews/V1_19_EVIDENCE_INDEX.md
bootstrap:
  current_route: v1.21 active route / Phase 78 complete / latest archived baseline = v1.20
  default_next_command: $gsd-complete-milestone v1.21
  latest_archived_evidence_pointer: .planning/reviews/V1_20_EVIDENCE_INDEX.md
```
<!-- governance-route-contract:end -->

## Latest Archived Milestone (v1.20)

> `v1.20` 已于 `2026-03-25` 完成 archive promotion；以下 requirements / traceability 保留 `Phase 72 -> 75` 的最终 fulfilled contract，归档快照见 `.planning/milestones/v1.20-REQUIREMENTS.md`，审计裁决见 `.planning/v1.20-MILESTONE-AUDIT.md`，证据索引见 `.planning/reviews/V1_20_EVIDENCE_INDEX.md`。

### Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement

- [x] **GOV-56**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / docs / meta guards` 共同保留 `v1.20` closeout 当时的 historical closeout route truth = `no active milestone route / latest archived baseline = v1.20`、`.planning/reviews/V1_20_EVIDENCE_INDEX.md` latest pull-only archived evidence index、`v1.19` previous archived baseline 与 `v1.18` historical archived baseline；`Phase 75` 只完成 access-mode honesty 与 archive-truth closure，不单独升格为 promoted phase bundle。
- [x] **ARC-19**: bootstrap / lifecycle / `runtime_access` / `service_router` / `schedule` formal homes 已继续收敛到单一 north-star 主链；`diagnostics.py` / `system_health.py` 这些 thin adapters 继续只委托 formal control homes，不得新增 second orchestration root、builder folklore、shadow helper carrier 或 helper-owned public surface。
- [x] **HOT-32**: `Coordinator` bootstrap / builder、`EntryLifecycleController` / `EntryLifecycleSupport` orchestration 与 `runtime_access` test-aware probing 已完成 inward decomposition + probing retirement，热点保持冻结。
- [x] **HOT-33**: service-router forwarding families、diagnostics/helper duplication、`LiproEntity` runtime strategy 与 `schedule.py` runtime surface 已完成 formalize / deduplicate，并保持 outward behavior 稳定。
- [x] **HOT-34**: auth legacy snapshot / compatibility wrapper 已继续退役，剩余 legacy alias 已显式清点、缩窄并写回 delete gate。
- [x] **TYP-21**: runtime / lifecycle / service / auth seams 与 thin adapters（含 diagnostics / system-health / options-flow）继续保持 typed contract honesty，不得用 `Any` / compatibility shell 掩盖 boundary drift。
- [x] **TST-22**: 大型 suites 与治理 guards 已继续 topicize / focused freeze；`Phase 72 -> 75` touched scope 的 route / hotspot / no-growth guards 在 archive promotion 后仍定位清晰。
- [x] **QLT-30**: touched scope 已在 `uv run ruff check .`、`uv run mypy --follow-imports=silent .`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check` 与 focused/full pytest 下持续全绿。

## Traceability for archived v1.20 route

| Requirement | Phase | Status |
|-------------|-------|--------|
| GOV-56 | Phase 72, 74, 75 | Completed |
| ARC-19 | Phase 72, 73, 75 | Completed |
| HOT-32 | Phase 72 | Completed |
| HOT-33 | Phase 73 | Completed |
| HOT-34 | Phase 74 | Completed |
| TYP-21 | Phase 72, 73, 75 | Completed |
| TST-22 | Phase 72, 73, 74, 75 | Completed |
| QLT-30 | Phase 72, 73, 74, 75 | Completed |

**Coverage:**
- v1.20 routed requirements: 8 total
- Current mapped: 8
- Current complete: 8
- Current pending: 0
- Current unmapped: 0 ✓

## Previous Archived Milestone (v1.19)

> `v1.19` 已于 `2026-03-25` 完成归档；以下 requirements / traceability 保留 `Phase 71` 的最终 fulfilled contract。当前它已退为 previous archived baseline；latest archived evidence index 现为 `.planning/reviews/V1_20_EVIDENCE_INDEX.md`。

- [x] **GOV-55**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / docs index / meta guards` 在 `v1.19` archive promotion 当时共同承认 `v1.19` 已完成 archive promotion；其 historical archive-transition route truth = `no active milestone route / latest archived baseline = v1.19`；后续在 `v1.20` archive promotion 中，`v1.19` 退为 previous archived baseline。
- [x] **ARC-18**: OTA / firmware-update / anonymous-share / request pacing / command runtime 只允许 inward decomposition，不得新增 outward root、compat shell 或 second story。
- [x] **HOT-30**: OTA / firmware-install、anonymous-share submit、request pacing 与 command-runtime touched hotspots 已显著降低单函数决策密度，并把 orchestration 切回更窄的 helper/home 边界。
- [x] **HOT-31**: `Phase 71` 留下的 focused hotspot/function budgets 与 route-truth guards 继续冻结 touched scope，防止 archived closeout 之后的 density 与 truth drift 回流。
- [x] **TYP-20**: 新拆出的 helper seams 继续使用显式 typed payload / outcome / pacing contracts，不得以 `object`、宽口 mapping 或弱化返回值取代正式协作者语义。
- [x] **TST-21**: governance current-route / archive-pointer tests 已共享单一 current-truth helper，并在 archive promotion 后共同切到 latest archived pointer / no-active-route contract。
- [x] **QLT-29**: touched scope 已在 `uv run ruff check .`、`uv run mypy --follow-imports=silent .`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、focused pytest 与必要的 repo-wide governance/test suites 下保持绿色。

## Traceability for archived v1.19 route

| Requirement | Phase | Status |
|-------------|-------|--------|
| GOV-55 | Phase 71 | Completed |
| ARC-18 | Phase 71 | Completed |
| HOT-30 | Phase 71 | Completed |
| HOT-31 | Phase 71 | Completed |
| TYP-20 | Phase 71 | Completed |
| TST-21 | Phase 71 | Completed |
| QLT-29 | Phase 71 | Completed |

**Coverage:**
- v1.19 routed requirements: 7 total
- Current mapped: 7
- Current complete: 7
- Current pending: 0
- Current unmapped: 0 ✓

## Historical Archived Baseline (v1.18)

> `v1.18` 已于 `2026-03-24` 完成归档；以下 requirements / traceability 保留 `Phase 70` 的最终 fulfilled contract，供后续 milestone 继续 pull requirement lineage。

- [x] **GOV-54**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / validation assets / version guards` 现共同承认 `v1.18` 已完成 archive promotion，并把 archive / latest-evidence / version truth 的可变边界限制在 current docs / registry / runbook，不再让历史 phase/evidence 资产承担版本同步义务。
- [x] **ARC-17**: `runtime_access.py` 继续作为唯一 outward runtime home；`runtime_access_support.py` 已 inward split 为更窄的 typed helper clusters，OTA query/selection 与 anonymous-share submit/refresh/outcome 也已沿 formal homes 完成 helper convergence，没有长出第二 root。
- [x] **HOT-28**: `custom_components/lipro/control/runtime_access_support.py`、`custom_components/lipro/core/anonymous_share/share_client_flows.py`、`custom_components/lipro/core/api/diagnostics_api_ota.py` 与 `custom_components/lipro/entities/firmware_update.py` 已降低 decision density，并通过 shared helper / selector / response-resolution seams 缩小回归面。
- [x] **HOT-29**: 治理 mega-tests、archive assertions 与 release-doc guards 已进一步 topicization；重复断言已抽成 shared helpers / concern-oriented contracts，避免 single giant test 承担多个 concern。
- [x] **OSS-10**: `docs/README.md`、`SUPPORT.md`、`SECURITY.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`pyproject.toml`、`manifest.json` 与 governance registry 继续讲同一条 honest open-source contract，明确 public first-hop、live-docs reality、archive freeze boundary 与 maintainer continuity limitation。
- [x] **TST-20**: 新增或重构的治理 / hotspot guards 已提升 failure localization、domain naming 与 test ownership clarity，不再把 phase 编年史壳层当作长期测试拓扑的唯一 discoverability 入口。
- [x] **QLT-28**: touched scope 已在 `uv run ruff check .`、`uv run mypy --follow-imports=silent .`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、focused pytest 与必要的 repo-wide governance/test suites 下保持绿色。

## Traceability for archived v1.18 route

| Requirement | Phase | Status |
|-------------|-------|--------|
| GOV-54 | Phase 70 | Completed |
| ARC-17 | Phase 70 | Completed |
| HOT-28 | Phase 70 | Completed |
| HOT-29 | Phase 70 | Completed |
| OSS-10 | Phase 70 | Completed |
| TST-20 | Phase 70 | Completed |
| QLT-28 | Phase 70 | Completed |
## Archived Milestone (v1.17)

> `v1.17` 已于 `2026-03-24` 完成归档；以下 requirements / traceability 保留 `Phase 69` 的最终 fulfilled contract，归档快照见 `.planning/milestones/v1.17-REQUIREMENTS.md`，审计裁决见 `.planning/v1.17-MILESTONE-AUDIT.md`，证据索引见 `.planning/reviews/V1_17_EVIDENCE_INDEX.md`。

### Residual Formalization & Hotspot Closure

- [x] **GOV-53**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / phase context / verification assets` 现在共同区分 `v1.16` 的 archived baseline 身份与 `v1.17` 的 archived closeout 身份，没有重写 `Phase 68` current story。
- [x] **ARC-16**: `runtime_access.py` / `runtime_access_support.py`、`runtime_infra.py`、`services/schedule.py` 与 related protocol-service collaborators 已继续向显式 read-model / runtime-intent seam 收口；反射式 probing、protocol-shaped service choreography 与 broad wrapper chain 未被重新合法化。
- [x] **HOT-26**: wrapper/shim/lazy-import residual（含 MQTT/support/API stable-import and helper mirrors）已继续削减；保留下来的 localized seam 均维持正式 owner / delete-gate / no-growth contract。
- [x] **HOT-27**: 高复杂度 support-only families（如 `runtime_access_support.py`、`runtime_infra.py`、diagnostics helper mirrors）已获得更清晰的 no-growth budget 与 discoverability contract，没有继续长成隐性 subsystem。

### Open-Source & Quality Balance

- [x] **OSS-09**: release-aware docs URL、machine-readable Home Assistant support truth、maintainer continuity wording 与 live-docs caveat 已在 `pyproject.toml`、`manifest.json`、`docs/README.md`、`SECURITY.md`、templates 与 governance docs 中讲同一条 honest open-source contract。
- [x] **TST-19**: 质量体系已补足 `scripts/check_*.py` 的行为测试/coverage 视野、focused integration coverage 与 meta-shell 可导航性，后续 residual closure 不再主要依赖 budget/meta tests。
- [x] **QLT-27**: `v1.17` touched scope 已在 `uv run ruff check .`、`uv run mypy --follow-imports=silent .`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run python scripts/check_translations.py` 与 final focused pytest bundle 下保持绿色，并留下可解释的平衡化门禁证据。

## Traceability for archived v1.17 route

| Requirement | Phase | Status |
|-------------|-------|--------|
| GOV-53 | Phase 69 | Completed |
| ARC-16 | Phase 69 | Completed |
| HOT-26 | Phase 69 | Completed |
| HOT-27 | Phase 69 | Completed |
| OSS-09 | Phase 69 | Completed |
| TST-19 | Phase 69 | Completed |
| QLT-27 | Phase 69 | Completed |

**Coverage:**
- v1.17 routed requirements: 7 total
- Current mapped: 7
- Current complete: 7
- Current pending: 0
- Current unmapped: 0 ✓

## Archived Milestone (v1.16)

> `v1.16` 已于 `2026-03-24` 完成归档；以下 requirements / traceability 保留 `Phase 68` 的最终 fulfilled contract，归档快照见 `.planning/milestones/v1.16-REQUIREMENTS.md`，审计裁决见 `.planning/v1.16-MILESTONE-AUDIT.md`，证据索引见 `.planning/reviews/V1_16_EVIDENCE_INDEX.md`。

### Governance & Public-Contract Alignment

- [x] **GOV-52**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / README* / docs index / manifest / issue templates / release runbook` 必须共同承认 `v1.16` active route、`v1.15` latest archived baseline、同一 public first-hop 与同一 version/release-example truth；stale docs-entry / stale tag example / beta-vs-stable signal drift 不得继续并存。

### Architecture & Hotspot Finalization

- [x] **ARC-15**: `core/telemetry/models.py`、`core/mqtt/message_processor.py`、`core/anonymous_share/share_client_flows.py`、`core/api/diagnostics_api_ota.py`、`runtime_infra.py` 与相关 collaborator families 必须继续沿既有 formal seams inward decomposition；不能新增 public root、compat shell、helper-owned second story 或 dynamic probing folklore。
- [x] **HOT-24**: remaining long-flow / high-decision-density hotspots 必须抽回更窄的 helper / outcome / builder contracts，并清理仍会制造误导的 localized residual（如 import cycle、bool-only compat wrapper、stale alias、duplicate troubleshooting story）。
- [x] **HOT-25**: control/platform/public adapter surfaces 必须继续保持 thin projection posture：平台壳、diagnostics/export paths 与 docs navigation 只能消费显式投影或 canonical docs home，不得重新理解 domain/runtime internals 或复制 canonical troubleshooting/release guidance。

### Open-Source Maturity & Verification

- [x] **OSS-08**: README / README_zh / docs navigation / changelog / release examples / manifest metadata 必须对外讲同一条 honest open-source story；允许明确记录单维护者限制，但不得用 undocumented delegate、隐式 support promise 或 stale examples 粉饰。
- [x] **TST-18**: 本轮必须为 hotspot decomposition 与 docs contract drift 增加 focused regression/guard coverage，并通过 `$gsd-review` 把 cross-AI plan feedback 正式回灌到执行计划中；review 不得停留为一次性口头意见。
- [x] **QLT-26**: touched scope 必须在 `uv run ruff check .`、`uv run mypy --follow-imports=silent .`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、focused pytest 与必要的 repo-wide pytest 下继续绿色，证明本轮不是 aesthetic cleanup。


## Traceability for archived v1.16 route


| Requirement | Phase | Status |
|-------------|-------|--------|
| GOV-52 | Phase 68 | Completed |
| ARC-15 | Phase 68 | Completed |
| HOT-24 | Phase 68 | Completed |
| HOT-25 | Phase 68 | Completed |
| OSS-08 | Phase 68 | Completed |
| TST-18 | Phase 68 | Completed |
| QLT-26 | Phase 68 | Completed |

**Coverage:**
- v1.16 routed requirements: 7 total
- Current mapped: 7
- Current complete: 7
- Current pending: 0
- Current unmapped: 0 ✓

## Archived Milestone (v1.15)

> `v1.15` 已于 `2026-03-24` 完成归档；以下 requirements / traceability 保留 `Phase 67` 的最终 fulfilled contract，归档快照见 `.planning/milestones/v1.15-REQUIREMENTS.md`，审计裁决见 `.planning/v1.15-MILESTONE-AUDIT.md`，证据索引见 `.planning/reviews/V1_15_EVIDENCE_INDEX.md`。

- [x] **GOV-51**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / phase context / verification artifacts` 必须共同承认 `v1.15` active route 与 `v1.14` latest archived baseline；current-story 不能继续停留在“仅需 `$gsd-new-milestone`”的归档叙事。
- [x] **TYP-19**: telemetry failure-summary、sink payload、runtime/control telemetry bridge、exporter views 与 related tests 必须共享显式 JSON-safe typed truth；`FailureSummary` / `TelemetryJsonValue` / view payload 不得再由 broad `dict[str, object]` 或弱化 `str | None` 反向定义。
- [x] **ARC-14**: `LiproRestFacade`、endpoint/auth ports、anonymous-share submit manager / scoped manager contracts 与 schedule/service resolution seams 必须回到显式 Protocol / typed return contracts，不得继续让 `object`、`SimpleNamespace` 或宽口 mapping 充当 formal collaborator。
- [x] **HOT-23**: service-handler tests、telemetry exporter tests、toolchain/meta helpers 与相关 hotspots 必须通过共享 typed builders / narrowing helpers / loader adapters 缩小 failure radius，而不是继续堆叠局部 cast 或重复 fixture folklore。
- [x] **TST-17**: YAML / workflow / release / blueprint meta tests 与 telemetry/service handler focused suites 必须对 typed loader、union narrowing、fixture protocols 与 method patching 形成诚实回归；不允许靠 ignore 或 untyped import 回避验证。
- [x] **QLT-25**: 本轮 residual closure 必须在 `uv run mypy`、`uv run ruff check .`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、focused pytest 与 `uv run pytest -q` 下同时通过。

## Traceability for archived v1.15 route

| Requirement | Phase | Status |
|-------------|-------|--------|
| GOV-51 | Phase 67 | Completed |
| TYP-19 | Phase 67 | Completed |
| ARC-14 | Phase 67 | Completed |
| HOT-23 | Phase 67 | Completed |
| TST-17 | Phase 67 | Completed |
| QLT-25 | Phase 67 | Completed |

**Coverage:**
- v1.15 routed requirements: 6 total
- Current mapped: 6
- Current complete: 6
- Current pending: 0
- Current unmapped: 0 ✓

## Archived Milestone (v1.14)

> `v1.14` 已于 `2026-03-23` 完成归档；以下 requirements / traceability 保留 `Phase 63 -> 66` 的最终 fulfilled contract，归档快照见 `.planning/milestones/v1.14-REQUIREMENTS.md`，审计裁决见 `.planning/v1.14-MILESTONE-AUDIT.md`，证据索引见 `.planning/reviews/V1_14_EVIDENCE_INDEX.md`。

### Governance Truth & Pointer Closure

- [x] **GOV-46**: `PROJECT / STATE / ROADMAP / REQUIREMENTS / MILESTONES / docs index / release runbook` 必须共同承认 `v1.13` 是当前最新 archive-ready closeout pointer，且 active milestone 已切到 `v1.14`。
- [x] **GOV-47**: milestone/archive/version guards 必须阻止 `latest closeout pointer`、`MILESTONES` 缺项与 stale next-route 回流；不得再把 `v1.6` 或 `v1.11` 误写成 current pointer。

### Hotspot & Typed Runtime Closure

- [x] **HOT-16**: `RuntimeAccess` 与 `custom_components/lipro/__init__.py` 必须继续沿现有 formal seams 变薄：runtime 读取改走 typed read-model / explicit port，HA root adapter 只保留 thin entry wiring。
- [x] **HOT-17**: `scripts/check_file_matrix_registry.py`、topicized API/meta hidden roots 与相关 tooling truth families 必须继续 inward decomposition，消除 second truth / hidden helper root。

### Verification & Typed Follow-Through

- [x] **TST-13**: API suites 与 governance/meta suites 的 topicized files 不得继续通过 `test_api.py` / `test_governance_guards.py` 充当隐式主根；共享 fixtures/helpers 必须显式 home 化，failure localization 继续下降。
- [x] **TYP-16**: command failure / anonymous-share follow-through 必须继续收紧到 typed summary / typed request-response contract；coordinator 与 share flows 不得继续依赖 stringly / `Any` 漏口决定主逻辑。
- [x] **QLT-21**: touched docs / baselines / review ledgers / focused guards / validation commands 必须同步更新并形成 no-growth evidence，证明 `v1.14` 不是 conversation-only cleanup。

### Telemetry / Schedule / Diagnostics Formal-Contract Follow-Through

- [x] **ARC-11**: telemetry / diagnostics / schedule formal homes 必须继续 obey 单一主链：telemetry truth 不得被 `Any`-centric exporter plumbing 重新定义，schedule service 不得借 raw protocol/device sidecar 形成第二 contract，diagnostics API outward home 只能做 thin composition。
- [x] **HOT-18**: `custom_components/lipro/core/api/diagnostics_api_service.py` 必须继续 inward split 成更小的 OTA / history / misc collaborators，同时保留现有 outward import home 与行为契约。
- [x] **HOT-19**: telemetry family（`models.py` / `ports.py` / `exporter.py` / `sinks.py`）与 schedule service hotspots 必须沿 formal seams 继续切薄，不得长期合法化为 `Any`/mega-home。
- [x] **TYP-17**: telemetry / diagnostics / schedule touched-zone 的 `Any`、mixed tuple contract 与 dynamic attribute probing 必须继续收紧到 explicit typed aliases / protocols / JSON-safe payload contracts。
- [x] **TST-14**: diagnostics API、schedule service 与 telemetry exporter/sinks 的 hotspot refactor 必须伴随 focused regression suites，保持 failure localization 与局部可执行性。
- [x] **GOV-48**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / FILE_MATRIX` 必须冻结 telemetry/schedule/diagnostics 的新 topology truth，阻止 stale hotspot narrative 与旧 ownership wording 回流。
- [x] **QLT-22**: 本轮 hotspot slimming 必须在 `ruff`、architecture policy、file matrix 与 targeted/full pytest 下同时通过，证明不是外观式重排。

### Runtime Projection / Device Extras / Anonymous-Share Residual Closure

- [x] **ARC-12**: control/runtime/device/share touched homes 必须继续 obey 单一正式主链：runtime-access、device extras 与 anonymous-share 只能收口到更诚实的 read-model / outcome contract，不能再长出 mock-driven compat story、raw sidecar second truth 或 helper-owned second root。
- [x] **HOT-20**: `custom_components/lipro/control/runtime_access_support.py` 与相关 control-plane runtime readers 必须退出 MagicMock-aware reflection / materialized-member probing，改由显式 entry/coordinator projection 与 honest adapter contract 讲一条 runtime truth。
- [x] **HOT-21**: `custom_components/lipro/core/anonymous_share/{manager.py,manager_submission.py,share_client_flows.py}` 必须继续 inward decomposition，降低跨文件私有状态耦合与 orchestration hotspot 半径，同时保持 aggregate/scoped submit semantics 与 outward service behavior 稳定。
- [x] **TYP-18**: touched runtime/device/share zones 的 residual raw `extra_data` reads、implicit alias sidecars、broad casts 与 dynamic probing 必须继续收敛到 explicit typed projections / local contracts。
- [x] **TST-15**: runtime-access、diagnostics/device extras 与 anonymous-share touched hotspots 必须伴随 focused regression suites 或夹具收口，证明去反射化 / 去 sidecar 化不会破坏既有行为。
- [x] **GOV-49**: `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / FILE_MATRIX` 必须共同冻结 runtime-access、device-extras 与 anonymous-share 的新 topology truth，阻止 stale hotspot 与 closeout-ready 叙事回流。
- [x] **QLT-23**: 本轮 residual closure 必须在 `ruff`、architecture policy、file matrix、focused pytest 与 full pytest 下同时通过，证明不是测试夹具特判或表面重排。

### Release Fidelity, Adapter-Root Cleanup & Focused Protocol Coverage

- [x] **GOV-50**: tagged release 与 `workflow_dispatch` rehearsal 必须校验并构建同一 release ref；baseline / reviews / docs 的 active-route 与 freshness metadata 必须保持单一 current-story。
- [x] **OSS-07**: 对外 release/install 文档必须使用 freshness-safe 的 release example truth，不得再由 stale hard-coded tag 充当公开安装指南。
- [x] **ARC-13**: HA 根适配器与 platform roots 必须优先使用显式 formal imports / contracts；duplicated runtime-loaded stubs 与 adapter-owned second truth 不得继续留在 `__init__.py`、`sensor.py`、`select.py`。
- [x] **HOT-22**: release/governance 与 adapter-root touched hotspots 必须继续 slimming，而不是保留 hidden-root / dynamic-import folklore 作为长期合法实现。
- [x] **TST-16**: `RestTransportExecutor`、`CoordinatorProtocolService`、`LiproProtocolFacade` 与 `LiproMqttFacade` 必须拥有 focused regression suites；mega matrix 不得再独占这些 seam 的主要验证责任。
- [x] **QLT-24**: 本轮 hardening 必须在 `ruff`、architecture policy、file matrix、focused governance/protocol suites 与 full pytest 下同时通过。

## Traceability for archived v1.14 route

| Requirement | Phase | Status |
|-------------|-------|--------|
| GOV-46 | Phase 63 | Completed |
| GOV-47 | Phase 63 | Completed |
| HOT-16 | Phase 63 | Completed |
| HOT-17 | Phase 63 | Completed |
| TST-13 | Phase 63 | Completed |
| TYP-16 | Phase 63 | Completed |
| QLT-21 | Phase 63 | Completed |
| ARC-11 | Phase 64 | Completed |
| HOT-18 | Phase 64 | Completed |
| HOT-19 | Phase 64 | Completed |
| TYP-17 | Phase 64 | Completed |
| TST-14 | Phase 64 | Completed |
| GOV-48 | Phase 64 | Completed |
| QLT-22 | Phase 64 | Completed |
| ARC-12 | Phase 65 | Completed |
| HOT-20 | Phase 65 | Completed |
| HOT-21 | Phase 65 | Completed |
| TYP-18 | Phase 65 | Completed |
| TST-15 | Phase 65 | Completed |
| GOV-49 | Phase 65 | Completed |
| QLT-23 | Phase 65 | Completed |
| GOV-50 | Phase 66 | Completed |
| OSS-07 | Phase 66 | Completed |
| ARC-13 | Phase 66 | Completed |
| HOT-22 | Phase 66 | Completed |
| TST-16 | Phase 66 | Completed |
| QLT-24 | Phase 66 | Completed |

**Coverage:**
- v1.14 routed requirements: 27 total
- Current mapped: 27
- Current complete: 27
- Current pending: 0
- Current unmapped: 0 ✓

## Future Requirements

- **OBS-05**: 如需要外部监控对接，再评估 Prometheus / OpenTelemetry sink
- **BND-04**: 如 manual validators 成本继续升高，再裁决局部 `pydantic v2` backend
- **ENF-03**: 如 AST/meta guards 复杂度继续上升，再评估 `import-linter/grimp`
- **SIM-06**: 如需要更强双向仿真，再补 broker/cloud behavioral simulator
- **AID-03**: 如 evidence pack 编码/校验成本成为瓶颈，再单独裁决 encoding backend，而不是提前绑定 `msgspec` / `pydantic v2`


## Out of Scope

| Feature | Reason |
|---------|--------|
| 全域 schema 框架替换 | 违背“边界局部增强”原则 |
| 第二套 protocol/runtime 实现 | 会破坏单一正式主链 |
| 外部监控平台接入 | 当前重点是 exporter formalization，不是 observability productization |
| 与北极星口径无关的大规模换栈 | 收益不直接指向当前里程碑目标 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BND-01 | Phase 7.1 | Complete |
| BND-02 | Phase 7.1 | Complete |
| BND-03 | Phase 7.1 | Complete |
| ENF-01 | Phase 7.2 | Complete |
| ENF-02 | Phase 7.2 | Complete |
| OBS-01 | Phase 7.3 | Complete |
| OBS-02 | Phase 7.3 | Complete |
| SIM-01 | Phase 7.4 | Complete |
| SIM-02 | Phase 7.4 | Complete |
| GOV-06 | Phase 7.5 | Complete |
| GOV-07 | Phase 7.5 | Complete |
| AID-01 | Phase 8 | Complete |
| AID-02 | Phase 8 | Complete |
| RSC-01 | Phase 9 | Complete |
| RSC-02 | Phase 9 | Complete |
| RSC-03 | Phase 9 | Complete |
| RSC-04 | Phase 9 | Complete |
| ISO-01 | Phase 10 | Complete |
| ISO-02 | Phase 10 | Complete |
| ISO-03 | Phase 10 | Complete |
| ISO-04 | Phase 10 | Complete |
| CTRL-01 | Phase 11 | Complete |
| CTRL-02 | Phase 11 | Complete |
| CTRL-03 | Phase 11 | Complete |
| SURF-01 | Phase 11 | Complete |
| CTRL-04 | Phase 11 | Complete |
| RUN-01 | Phase 11 | Complete |
| ENT-01 | Phase 11 | Complete |
| ENT-02 | Phase 11 | Complete |
| GOV-08 | Phase 11 | Complete |

| TYP-01 | Phase 12 | Complete |
| TYP-02 | Phase 12 | Complete |
| CMP-01 | Phase 12 | Complete |
| CMP-02 | Phase 12 | Complete |
| HOT-01 | Phase 12 | Complete |
| GOV-09 | Phase 12 | Complete |
| GOV-10 | Phase 12 | Complete |
| DOM-01 | Phase 13 | Complete |
| DOM-02 | Phase 13 | Complete |
| RUN-02 | Phase 13 | Complete |
| RUN-03 | Phase 13 | Complete |
| GOV-11 | Phase 13 | Complete |
| RUN-04 | Phase 14 | Complete |
| HOT-02 | Phase 14 | Complete |
| CTRL-05 | Phase 14 | Complete |
| RUN-05 | Phase 14 | Complete |
| GOV-12 | Phase 14 | Complete |

| SPT-01 | Phase 15 | Complete |
| GOV-13 | Phase 15 | Complete |
| DOC-01 | Phase 15 | Complete |
| HOT-03 | Phase 15 | Complete |
| QLT-01 | Phase 15 | Complete |
| TYP-03 | Phase 15 | Complete |
| RES-01 | Phase 15 | Complete |
| GOV-14 | Phase 16 | Complete |
| RES-03 | Phase 17 | Complete |
| TYP-05 | Phase 17 | Complete |
| MQT-01 | Phase 17 | Complete |
| GOV-15 | Phase 17 | Complete |
| QLT-02 | Phase 16 | Complete |
| HOT-04 | Phase 16 | Complete |
| TYP-04 | Phase 16 | Complete |
| ERR-01 | Phase 16 | Complete |
| RES-02 | Phase 16 | Complete |
| CTRL-06 | Phase 16 | Complete |
| DOM-03 | Phase 16 | Complete |
| OTA-01 | Phase 16 | Complete |
| TST-01 | Phase 16 | Complete |
| DOC-02 | Phase 16 | Complete |

**Coverage:**
- active milestone requirements: 72 total
- mapped to phases: 72
- unmapped: 0 ✓

*Last updated: 2026-03-24 after completing Phase 68 closeout and seeding the planned v1.17 residual follow-through route*


## Archived Milestone (v1.2)

> `v1.2` 已完成全部执行与 closeout；以下 requirement / traceability 反映 `Phase 18-24` 全部完成，且 `Phase 24` 已在 2026-03-17 reopen revalidation 后继续保持 archive-ready / handoff-ready。归档快照已写入 `.planning/milestones/v1.2-REQUIREMENTS.md`。

### Core Reuse / Host-Neutral Nucleus

- [x] **CORE-01**: boundary/auth/device 的共享 nucleus 可在不依赖 HA entry/runtime adapter 类型的前提下独立组合。
- [x] **CORE-02**: 同一套 nucleus 必须能被 headless / CLI-style consumer 复用，完成认证、设备发现与 replay/evidence proof。
- [x] **CORE-03**: HA adapter 只能保留 adapter 身份，不得继续把 host-specific wiring 泄露回共享 nucleus。

### Replay / Boundary Completion

- [x] **SIM-03**: `rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 已成为 registry-backed boundary families。
- [x] **SIM-04**: replay harness 与 evidence pack 已覆盖新增 formalized families，并复用同一正式 public path。
- [x] **SIM-05**: 当前 authority/inventory 中对 remaining replay families 的 de-scope / partial 标记，已随 coverage 落地被移除或缩窄为真实剩余项。

### Error / Observability Hardening

- [x] **ERR-02**: protocol/runtime/control 关键 broad-catch 已被收窄或改成 documented arbitration，catch-all 不再作为默认策略。
- [x] **OBS-03**: diagnostics / system health / evidence export 已对 auth/network/protocol/runtime failure 使用统一分类语言。

### Governance

- [x] **GOV-16**: v1.2 的 host-neutral / replay-complete / observability-hardening 真相已同步到 roadmap / state / baseline / reviews / docs / meta guards。
- [x] **GOV-17**: contributor-facing docs、issue/PR templates、support/security/install/version surfaces 与 release evidence 已对齐最终 v1.2 架构与治理门禁。
- [x] **GOV-18**: milestone closeout 已留下 final repo audit、residual arbitration、archive-ready verification assets 与 v1.3 handoff，且在 2026-03-17 reopened gates 后重新验证，无 silent defer。

## Traceability for v1.2

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| CORE-01 | Phase 18 | Complete |
| CORE-02 | Phase 19 | Complete |
| CORE-03 | Phase 18 | Complete |
| SIM-03 | Phase 20 | Complete |
| SIM-04 | Phase 21 | Complete |
| SIM-05 | Phase 20 | Complete |
| ERR-02 | Phase 21 | Complete |
| OBS-03 | Phase 22 | Complete |
| GOV-16 | Phase 23 | Complete |
| GOV-17 | Phase 23 | Complete |
| GOV-18 | Phase 24 | Complete |

**Current Coverage:**
- v1.2 requirements: 11 total
- Current mapped: 11
- Current complete: 11 ✓
- Current unmapped: 0 ✓

## Next Milestone Seed (v1.3)

> `Phase 25` 已被提升为 v1.3 的总计划母相：它先冻结 `25.1 / 25.2 / 26 / 27` 首轮路由，再由 `28 / 29 / 30 / 31` 完成第二梯队 closeout；`Phase 32 / 33` 已于 `2026-03-18` 完成 final truth-convergence + hardening closeout。当前 `.planning/v1.3-MILESTONE-AUDIT.md` 已刷新为 `tech_debt / closeout-eligible`；若继续追求 10 分质量，下一步优先 `$gsd-plan-milestone-gaps`，否则可 `$gsd-complete-milestone v1.3`。

### Governance / Route Ownership

- [x] **GOV-19**: 终极复审中的全部 P0 / P1 / P2 问题必须被显式路由到 `25.1 / 25.2 / 26 / 27` 或被裁决为外部协议约束 / 非当前 debt；禁止 silent defer。
- [x] **GOV-20**: telemetry seam closure 触及的 authority docs、residual ledgers、handoff truth 与 touched `.planning/codebase/*` derived maps 必须同步，明确 formal surface 迁移且 derived maps 继续只是协作图谱。
- [x] **GOV-21**: release/install trust chain、support matrix、双语策略、维护者冗余与 contributor-facing productization surfaces 必须达到更成熟的开源治理标准。

### Runtime / Observability Correctness

- [x] **RUN-06**: 全量设备快照刷新必须满足原子性；分页失败、拓扑 enrich 失败或 parse failure 不得静默发布 partial truth 覆盖既有运行态。
- [x] **ERR-03**: refresh failure 必须具备可判定 arbitration；`拒绝提交 / 保留 last-known-good / 结构化 degraded` 三者必须显式、可测且语义稳定。
- [x] **OBS-04**: telemetry / diagnostics / system health consumer 只能通过正式 protocol telemetry surface 或显式 port 拉取协议信号，不得继续依赖 `Coordinator.client`、隐式属性或 ghost seam。

### Productization / Maintainability Follow-Through

- [x] **QLT-03**: 依赖、兼容、支持窗口与升级策略必须更诚实、更可复现，并与 release / support surfaces 保持一致。
- [x] **HOT-05**: `Coordinator`、`LiproRestFacade` 与纯转发层必须继续沿正式边界切薄，不得再用“只是转发”合理化巨型根对象。
- [x] **RES-04**: 过渡命名、历史 phase 叙事、残留噪声与协议受限实现说明必须更诚实；reverse-engineered vendor `MD5` 登录哈希路径被记录为协议约束，而不是仓库弱密码学债。
- [x] **TST-02**: 巨型测试文件与贡献者高认知负担测试面必须继续拆分成稳定、可局部执行的专题套件，同时保留现有治理门禁强度。
- [x] **GOV-22**: maintainer continuity、emergency access、support window / EOL / triage ownership 必须从“诚实说明”升级为制度化、可审计的运维/治理资产，且不虚构额外维护者。
- [x] **QLT-04**: release identity posture 必须进一步硬化；signing、code-scanning gate 或等价 machine-enforced release security controls 必须形成一致 story。
- [x] **HOT-06**: `LiproRestFacade` remaining hotspot 必须继续拆成更聚焦的 child collaborators / services，不得保留巨型 child façade 作为长期合法形态。
- [x] **RES-05**: 与 `LiproRestFacade` / protocol child-collaborator decomposition 相关的命名、职责与 residual truth 必须继续收口并诚实同步。
- [x] **TST-03**: remaining mega-test suites 必须继续专题化拆分，并保持局部可执行与治理门禁强度。
- [x] **TYP-06**: 高价值 `core/api` / `core/protocol` / `control` hotspots 的 `Any` / `type: ignore` 必须继续沿正式 contract 收窄，不得长期停留在 boundary-adjacent distributed backlog。
- [x] **ERR-04**: remaining broad-catch paths in touched protocol/control hotspots 必须改成 typed arbitration、documented failure contract 或显式 deferred truth。
- [x] **TYP-07**: runtime/service/platform touched zones 的 `Any` / `type: ignore` backlog 必须建立预算、继续下降，并形成 no-growth typed hardening story。
- [x] **ERR-05**: remaining runtime/service broad-catch paths 必须收敛为 documented fail-closed / degraded semantics 或被移除；新增 catch-all regression 必须被 guard 阻断。
- [x] **GOV-23**: typed/exception budget、phase closeout assets 与 daily governance gates 必须机器化守护 `30/31` 的 no-growth contract，而不是依赖人工补漏。
- [x] **GOV-24**: `.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 与 retained handoff/audit pointers 已对 `Phase 25 -> 32` complete 讲同一条 current story，不再分叉。
- [x] **QLT-05**: repo-wide `ruff` / `mypy` / CI / contributor docs gate story 已诚实且 machine-checkable；工具范围、blocking truth 与 release posture 均已被文档和 guards 显式固定。
- [x] **GOV-25**: release identity posture、code-scanning / signing defer truth、maintainer continuity、support/security process 与 contributor-facing templates 已收敛成单一、诚实、可审计的治理故事。
- [x] **GOV-26**: `.planning/codebase/*.md` 与双语 public docs 现已带 freshness / disclaimer / authority-boundary truth，并与 baseline/review docs 同步。
- [x] **HOT-07**: touched runtime/platform/governance hotspots 已继续沿现有正式 seams 收口，helper/platform/runtime typing 不再并行生长第二 coordinator 故事。
- [x] **TST-04**: touched replay/runtime/governance suites 已继续按契约与守卫专题化收口，并保持局部可执行性与守卫强度。
- [x] **TYP-08**: 高价值 touched hotspots 的 typed debt 已进一步 burn-down，并通过 repo-wide `mypy` / Phase 31 budget guard 区分 sanctioned truth 与 backlog truth。
- [x] **ERR-06**: touched hotspots 的 broad-catch / catch-all truth 已继续收敛为 named arbitration、documented semantics 或 explicit defer truth，并由 guard 固化。
- [x] **RES-06**: fallback / legacy / phase residue 与 protocol-constrained crypto wording 已被继续清理或显式文档化，不再依赖口头约定。

## Traceability for v1.3 route map

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-19 | Phase 25 | Complete |
| RUN-06 | Phase 25.1 | Complete |
| ERR-03 | Phase 25.1 | Complete |
| OBS-04 | Phase 25.2 | Complete |
| GOV-20 | Phase 25.2 | Complete |
| GOV-21 | Phase 26 | Complete |
| QLT-03 | Phase 26 | Complete |
| HOT-05 | Phase 27 | Complete |
| RES-04 | Phase 27 | Complete |
| TST-02 | Phase 27 | Complete |
| GOV-22 | Phase 28 | Complete |
| QLT-04 | Phase 28 | Complete |
| HOT-06 | Phase 29 | Complete |
| RES-05 | Phase 29 | Complete |
| TST-03 | Phase 29 | Complete |
| TYP-06 | Phase 30 | Complete |
| ERR-04 | Phase 30 | Complete |
| TYP-07 | Phase 31 | Complete |
| ERR-05 | Phase 31 | Complete |
| GOV-23 | Phase 31 | Complete |
| GOV-24 | Phase 32 | Complete |
| QLT-05 | Phase 32 | Complete |
| GOV-25 | Phase 32 | Complete |
| GOV-26 | Phase 32 | Complete |
| HOT-07 | Phase 32 | Complete |
| TST-04 | Phase 32 | Complete |
| TYP-08 | Phase 32 | Complete |
| ERR-06 | Phase 32 | Complete |
| RES-06 | Phase 32 | Complete |

**Seed Coverage:**
- v1.3 routed requirements: 29 total
- Current mapped: 29
- Current complete: 29
- Current pending: 0
- Current unmapped: 0 ✓

## Audit-Driven Continuation Seed (Phase 33)

> `Phase 25 -> 32` 已把 correctness、telemetry seam、truth convergence 与 release honesty 推到高位；`2026-03-18` 的全仓终审仍确认存在一簇剩余 P1/P2 debt。`Phase 33` 把这些问题全部正式路由成下一轮可执行 tranche，而不是继续停留在终审备忘里。

### Architecture / Control Truth

- [x] **ARC-03**: runtime public surface 必须只有一份正式类型真源；HA 顶层 adapter 可以 import / alias，但不得继续自定义第二份 `LiproRuntimeCoordinator` 契约。
- [x] **CTRL-07**: control-plane telemetry / runtime-access / support read-model 必须改成 acyclic、port-based 边界；`RuntimeCoordinatorSnapshot` 必须变成纯 DTO，不再携带活体 runtime root。

### Hotspots / Quality Gates

- [x] **HOT-08**: giant runtime/protocol/helper hotspots 必须继续沿现有正式 seams 切薄；`LiproRestFacade`、`LiproProtocolFacade`、`Coordinator`、`SnapshotBuilder`、`CommandResult` family 不得被长期合法化为 forwarding roots。
- [x] **ERR-07**: remaining broad-catch paths 必须收敛到 named arbitration、documented degraded semantics 或 fail-closed contract；新增 catch-all regression 必须被 no-growth guards 拦截。
- [x] **QLT-06**: local / CI / release / benchmark gates 必须收敛到 machine-checkable truth；snapshot duplicate execution、local late feedback 与 performance advisory-only posture 必须被修正。
- [x] **QLT-07**: dependency / compatibility posture 必须更可复现、更显式；runtime dependency bounds、Python floor、support window 与 release posture 必须讲同一条故事。

### Governance / Productization / Testing

- [x] **GOV-27**: control public exports、empty compat shells、legacy/mixin naming residue 与 internal helper exposure 必须缩面或重分类，不能继续暗示第二条 public story。
- [x] **GOV-28**: 深层 public docs 必须朝 bilingual parity、support/security continuity 与 maintainer custody honesty 再推进一轮；`signing` / `code scanning` / release custody 仍须显式、非虚构。
- [x] **TST-05**: remaining giant test suites 必须继续 topicize 成更稳定、可局部执行的专题面，同时保持治理门禁强度与回归信号。

## Traceability for Phase 33 continuation

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| ARC-03 | Phase 33 | Complete |
| CTRL-07 | Phase 33 | Complete |
| HOT-08 | Phase 33 | Complete |
| ERR-07 | Phase 33 | Complete |
| TST-05 | Phase 33 | Complete |
| QLT-06 | Phase 33 | Complete |
| GOV-27 | Phase 33 | Complete |
| GOV-28 | Phase 33 | Complete |
| QLT-07 | Phase 33 | Complete |

**Seed Coverage:**
- Phase 33 routed requirements: 9 total
- Current mapped: 9
- Current complete: 9
- Current pending: 0
- Current unmapped: 0 ✓



## Archived Milestone (v1.13)

> `v1.13` 已于 `2026-03-22` 完成归档；以下 requirements / traceability 保留 `Phase 60 -> 62` 的最终 fulfilled contract，归档快照见 `.planning/milestones/v1.13-REQUIREMENTS.md`，审计裁决见 `.planning/v1.13-MILESTONE-AUDIT.md`，证据索引见 `.planning/reviews/V1_13_EVIDENCE_INDEX.md`。

### Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence

- [x] **HOT-14**: `scripts/check_file_matrix.py` 与相关 file-governance tooling truth 必须沿 existing truth families inward decomposition，保留稳定 CLI / import contract，不再让单个巨石脚本承担全部 inventory / classifier / validator / render story。
- [x] **TST-12**: `tests/meta/test_toolchain_truth.py` 与相关 toolchain / governance megaguards 必须 topicize 成更小、更诚实的 focused suites 或 thin runnable roots，降低 daily failure radius。
- [x] **GOV-44**: `.planning/reviews/FILE_MATRIX.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/codebase/TESTING.md` 与 current-story docs 必须在 tooling decomposition 后继续讲同一条 ownership / no-growth 故事。
- [x] **HOT-15**: `anonymous_share`、diagnostics API、OTA candidate 与 `select` 等 large-but-correct production homes 必须继续沿现有 formal seams 切薄，而不新增长期 public root / compat shell。
- [x] **QLT-20**: production hotspot slimming 必须同步带来 family-level focused regressions、no-growth budget 或 maintainability evidence，而不是只留下美观层重排。
- [x] **TYP-15**: 由 hotspot slimming 引入的 collaborator / projection seams 必须保持显式 typed contract，不能回流动态字典、宽布尔失败或 helper-owned truth。
- [x] **RES-14**: `*_support.py` / `*_surface.py` 与相关命名残留必须收口到诚实角色语义；support-only seams 不得继续暗示 public / formal root 身份。
- [x] **DOC-07**: README、docs index、contributor fast path、retired tooling discoverability 与双语入口必须在 naming cleanup 后继续讲一条低噪声 public story。
- [x] **GOV-45**: current-story docs、review ledgers 与 public-surface / dependency guards 必须冻结 post-slimming naming/discoverability topology，并阻止 stale terminology 回流。

## Traceability for archived v1.13 route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| HOT-14 | Phase 60 | Complete |
| TST-12 | Phase 60 | Complete |
| GOV-44 | Phase 60 | Complete |
| HOT-15 | Phase 61 | Complete |
| QLT-20 | Phase 61 | Complete |
| TYP-15 | Phase 61 | Complete |
| RES-14 | Phase 62 | Complete |
| DOC-07 | Phase 62 | Complete |
| GOV-45 | Phase 62 | Complete |

**Coverage:**
- v1.13 routed requirements: 9 total
- Current mapped: 9
- Current complete: 9
- Current pending: 0
- Current unmapped: 0 ✓

## Archived Milestone (v1.12)

> `v1.12` 已于 `2026-03-22` 完成归档；以下 requirement / traceability 反映 `Phase 59` 的 fulfilled contract。归档快照已写入 `.planning/milestones/v1.12-REQUIREMENTS.md`，审计裁决见 `.planning/v1.12-MILESTONE-AUDIT.md`，证据入口见 `.planning/reviews/V1_12_EVIDENCE_INDEX.md`。

### Verification Localization & Governance Guard Topicization

- [x] **TST-11**: `tests/meta/test_public_surface_guards.py`、`tests/meta/test_governance_phase_history.py`、`tests/meta/test_governance_followup_route.py` 已收敛为 thin shell + stable truth-family modules，`tests/core/test_device_refresh_{parsing,filter,snapshot,runtime}.py` 也已形成 focused suites，giant verification buckets 不再维持。
- [x] **QLT-19**: localized verification topology 已提供更小的 focused runnable suites 与更诚实的 failure-localization contract，split 过程中未丢 coverage、未丢 guard semantics，也未引入新的 helper-owned truth。
- [x] **GOV-43**: `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/codebase/TESTING.md` 与相关 review truth 已显式记录 `Phase 59` 的 localized verification route、ownership boundary 与 no-growth story。

## Traceability for archived v1.12 route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| TST-11 | Phase 59 | Complete |
| QLT-19 | Phase 59 | Complete |
| GOV-43 | Phase 59 | Complete |

**Coverage:**
- v1.12 routed requirements: 3 total
- Current mapped: 3
- Current complete: 3
- Current pending: 0
- Current unmapped: 0 ✓


## Planned Milestone (v1.11)

> `v1.11` 以 `Phase 46` audit package、`v1.8 -> v1.10` closeout evidence 与当前 refreshed audit request 为 immediate seed；当前重点不是再猜测下一块代码该改哪里，而是先把整个仓库的 current-state verdict 重新刷新并正式路由。

### Repository Audit Refresh & Next-Wave Remediation Routing

- [x] **AUD-03**: refreshed audit 必须覆盖所有仓库 Python / docs / config / governance surfaces，并对每个区域给出显式 verdict 或范围说明，不能留下 silent blind spot。
- [x] **ARC-10**: current formal roots、热点、命名、目录结构、旧新代码边界与 refactor residue 必须基于现状代码重做架构裁决，而不是继续沿用旧快照假设。
- [x] **OSS-06**: README / docs / SUPPORT / SECURITY / CONTRIBUTING / manifest / packaging / tooling surfaces 必须按当前开源项目最佳实践重新审阅，明确优点、不足与改进方向。
- [x] **GOV-42**: refreshed audit 结论必须固化到 current-story docs 与 promoted phase evidence，并明确路由成 `Phase 59+` remediation truth。

## Traceability for completed v1.11 route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| AUD-03 | Phase 58 | Complete |
| ARC-10 | Phase 58 | Complete |
| OSS-06 | Phase 58 | Complete |
| GOV-42 | Phase 58 | Complete |

**Coverage:**
- v1.11 routed requirements: 4 total
- Current mapped: 4
- Current complete: 4
- Current pending: 0
- Current unmapped: 0 ✓


## Planned Milestone (v1.10)

> `v1.10` 以 `v1.9` closeout evidence 为 immediate seed；当前重点不是重开 backoff ownership，而是把 command-result family 从 scattered literals 收口到一套 shared typed outcome / reason-code contract。

### Command-Result Typed Outcome & Reason-Code Hardening

- [x] **ERR-12**: command-result polling 与 failure arbitration 必须共享 typed outcome / reason-code vocabulary，而不是继续散落 `confirmed / failed / pending / unknown / unconfirmed` 与 raw failure-reason strings。
- [x] **TYP-14**: runtime sender traces 与 diagnostics `query_command_result` response typing 必须复用同一 command-result state contract，不能继续裸 `str` 漂移。
- [x] **GOV-41**: current-story docs、baseline/review notes、promoted assets 与 focused meta guards 必须显式记录 command-result typed contract home 与 closeout truth。

## Traceability for completed v1.10 route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| ERR-12 | Phase 57 | Complete |
| TYP-14 | Phase 57 | Complete |
| GOV-41 | Phase 57 | Complete |

**Coverage:**
- v1.10 routed requirements: 3 total
- Current mapped: 3
- Current complete: 3
- Current pending: 0
- Current unmapped: 0 ✓


## Planned Milestone (v1.9)

> `v1.9` 以 `v1.8` promoted closeout evidence 为 immediate seed；当前重点不是重开 broad audit，而是关闭唯一明确登记到 `Phase 56+` 的 active residual family：generic backoff helper leak。

### Shared Backoff Neutralization & Cross-Plane Retry Hygiene

- [x] **RES-13**: generic exponential backoff primitive 必须迁到 neutral shared helper home；`request_policy.py` 不得继续充当 command/runtime/MQTT 的 cross-plane utility export。
- [x] **ARC-09**: command-result polling、runtime command verification 与 MQTT setup backoff 只允许共享 neutral primitive；各自的 retry semantics、caps、jitter 与 budget 必须继续留在 plane-local home。
- [x] **GOV-40**: baseline/review docs、file inventory、promoted assets 与 focused meta guards 必须显式记录 neutral backoff home 与 residual closeout truth。

## Traceability for completed v1.9 route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| RES-13 | Phase 56 | Complete |
| ARC-09 | Phase 56 | Complete |
| GOV-40 | Phase 56 | Complete |

**Coverage:**
- v1.9 routed requirements: 3 total
- Current mapped: 3
- Current complete: 3
- Current pending: 0
- Current unmapped: 0 ✓


## Planned Milestone (v1.8)

> `v1.8` 以 `v1.6` archive truth 为 shipped baseline，以 `v1.7` promoted audit/closeout evidence 为 immediate route seed；当前重点是 continuity automation、formal-root sustainment 与 hotspot round 2，而不是重开 `v1.7`。

### Operational Continuity Automation, Formal-Root Sustainment & Hotspot Round 2

- [x] **GOV-38**: maintainer-unavailable / delegate / custody / freeze / restoration drill 已从 prose agreement 升级为可执行、低摩擦、可重复演练的 continuity contract。
- [x] **GOV-39**: `.planning/baseline/GOVERNANCE_REGISTRY.json` 已进一步承担下游 maintainer/public metadata projection truth，降低 docs / templates / contributor guidance 的手工同步漂移。
- [x] **QLT-18**: release chain 已支持 verify-only / non-publish rehearsal，并为 docs-only / governance-only / release-only 等 change type 提供最小充分验证矩阵。
- [x] **ARC-08**: `LiproProtocolFacade` 已继续 inward decomposition，并保持其作为唯一 protocol-plane root 的正式身份不变。
- [x] **HOT-12**: `Coordinator`、`__init__.py` 与 `EntryLifecycleController` 必须继续沿现有 seams 限流，降低 orchestration density。
- [x] **HOT-13**: `AnonymousShareManager`、diagnostics API helper family 与 request-policy companions 必须继续切薄，而不新增 public wrapper / helper-owned truth。
- [x] **TST-10**: second-wave mega-tests 必须继续按 concern topicize，让 API/MQTT/platform 大套件失败直接命中局部语义。
- [x] **TYP-13**: repo-wide typing truth 必须区分 production debt 与 test/guard literal debt，并继续压缩非 REST 区域的 `Any` 集中区。

## Traceability for completed v1.8 route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-38 | Phase 51 | Complete |
| GOV-39 | Phase 51 | Complete |
| QLT-18 | Phase 51 | Complete |
| ARC-08 | Phase 52 | Complete |
| HOT-12 | Phase 53 | Complete |
| HOT-13 | Phase 54 | Complete |
| TST-10 | Phase 55 | Complete |
| TYP-13 | Phase 55 | Complete |

**Coverage:**
- v1.8 routed requirements: 8 total
- Current mapped: 8
- Current complete: 8
- Current pending: 0
- Current unmapped: 0 ✓

## Completed Milestone (v1.7)

> `v1.7` 以 `v1.6` archive truth 为 shipped baseline；`Phase 46` 完成了 repo-wide 审阅，`Phase 47 -> 50` 则把 high-value follow-up route 全部正式落地并收束为 promoted closeout evidence。

### Full-Spectrum Repository Audit, Open-Source Maturity & Remediation Routing

- [x] **GOV-36**: 所有 Python 代码、测试、文档、配置、工作流与 `.planning` 治理真源都必须进入可追溯的 file-level 审阅范围，不能留下未被定性的盲区。
- [x] **ARC-05**: formal roots、public surfaces、dependency direction、control/runtime/protocol/service ownership 与 hotspot seams 必须按北极星架构与优秀开源案例完成系统审阅，并给出 keep / split / forbid / defer 裁决。
- [x] **DOC-05**: 开源项目入口、README/README_zh、CONTRIBUTING、SUPPORT、SECURITY、runbook、issue/PR templates 与 bilingual boundary 必须完成国际化可维护性审阅，明确 strengths、gaps 与改进优先级。
- [x] **RES-12**: 重构后的代码与老旧术语/旧残留风险必须被重新盘点，明确哪些是历史遗留、哪些是 future sustainment debt、哪些必须在后续 phase 物理清退。
- [x] **TST-08**: 巨石测试、验证拓扑、回归半径与失败定位体验必须完成 repo-wide 审阅，并输出下一轮 topicization / contract-hardening 路线。
- [x] **TYP-11**: `Any`、`type: ignore`、broad exception、typed budget 守卫覆盖范围与异常语义一致性必须完成量化盘点，并形成后续 no-growth / reduction 策略。
- [x] **QLT-16**: 必须形成机器可审计的终极审阅报告、评分矩阵、优先级排序与 `Phase 47+` remediation roadmap，使质量改进可以被持续执行与验证。

## Traceability for completed v1.7 audit route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-36 | Phase 46 | Complete |
| ARC-05 | Phase 46 | Complete |
| DOC-05 | Phase 46 | Complete |
| RES-12 | Phase 46 | Complete |
| TST-08 | Phase 46 | Complete |
| TYP-11 | Phase 46 | Complete |
| QLT-16 | Phase 46 | Complete |

**Coverage:**
- v1.7 routed requirements: 7 total
- Current mapped: 7
- Current complete: 7
- Current pending: 0
- Current unmapped: 0 ✓

## Formalized follow-up route from Phase 46

- [x] **GOV-37**: `SUPPORT.md`、`SECURITY.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.github/CODEOWNERS`、issue/PR templates 与 `.planning/baseline/GOVERNANCE_REGISTRY.json` 必须对 continuity / custody / delegate / freeze / restoration 讲同一条单维护者合同故事线。
- [x] **DOC-06**: `docs/README.md` 与 package metadata 必须把 documentation index 暴露成对外正式入口；public fast path、maintainer appendix 与双语边界不得继续视觉混层。
- [x] **RUN-08**: `RuntimeAccess` 必须继续按 projection / telemetry / system-health concern 拆薄；control consumers 不得恢复对 `entry.runtime_data` 或 coordinator internals 的散点读取。
- [x] **ARC-06**: `Coordinator`、`__init__.py` 与 `EntryLifecycleController` 必须继续 inward decomposition，降低 hotspot density，同时保持 lazy wiring 与单一正式主链。
- [x] **TST-09**: 治理 megaguards、runtime-root megatests 与 platform megatests 必须按 concern topicize，减少 giant-file failure triage 成本。
- [x] **QLT-17**: 测试与治理守卫的 failure localization 必须直接标出 phase / doc / token / runtime facet，避免“一个断言管全仓”的模糊失败面。
- [x] **TYP-12**: REST child façade family 的 `Any` / typed helper budget 必须继续收紧，并把 sanctioned-vs-backlog debt 分类压缩到更小、更诚实的边界。
- [x] **ARC-07**: command/result policy 与 diagnostics auth-error duplication 必须收敛到单一 formal home，不得让 ownership drift 继续散落在 helper / service / API family 之间。

## Traceability for formalized v1.7 follow-up route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-37 | Phase 47 | Complete |
| DOC-06 | Phase 47 | Complete |
| RUN-08 | Phase 48 | Complete |
| ARC-06 | Phase 48 | Complete |
| TST-09 | Phase 49 | Complete |
| QLT-17 | Phase 49 | Complete |
| TYP-12 | Phase 50 | Complete |
| ARC-07 | Phase 50 | Complete |

**Follow-up coverage:**
- formalized requirements: 8 total
- Current mapped: 8
- Current complete: 8
- Current pending: 0
- Current unmapped: 0 ✓

## Archived Milestone (v1.6)

> `v1.6` 已于 `2026-03-20` 完成归档；以下 requirements / traceability 保留 `Phase 42 -> 45` 的最终 fulfilled contract，归档快照见 `.planning/milestones/v1.6-REQUIREMENTS.md`，审计裁决见 `.planning/v1.6-MILESTONE-AUDIT.md`，证据入口见 `.planning/reviews/V1_6_EVIDENCE_INDEX.md`。

### Delivery Trust, Boundary Decoupling & Maintainability Closure

- [x] **GOV-34**: maintainer delegate、security fallback、`.github/CODEOWNERS`、issue/PR templates 与 maintainer runbook 必须形成单一 continuity truth，不能继续依赖单点隐性记忆。
- [x] **QLT-12**: release workflow 必须对发布产物运行 install / uninstall smoke，验证 release asset 在临时 HA 目录中的真实可用性。
- [x] **QLT-13**: 质量门禁必须同时约束 total coverage 与 changed-surface diff coverage，并保持 local/CI 命令语义一致。
- [x] **QLT-14**: 必须引入 scheduled compatibility / deprecation preview lane，提前暴露 Home Assistant 或依赖漂移。
- [x] **ARC-04**: `control/` 与 `services/` 必须收敛为单向依赖合同，禁止 helper / runtime / locator 双向缠绕回流。
- [x] **CTRL-10**: runtime infra 与 service helper 的 formal home 必须明确；`services/maintenance.py` 不得继续承载 runtime truth。
- [x] **RUN-07**: `RuntimeAccess` 必须提供 typed public read-model API；生产消费者不得依赖反射、`MagicMock` 形状或私有字段。
- [x] **GOV-35**: `.planning/phases/**` 默认仅是 execution trace；只有 promoted allowlist 资产可进入长期治理 / CI truth。
- [x] **RES-11**: `client / mixin / forwarding` 等旧术语必须退出 current docs、ADR 与注释，只允许留在历史资产或 residual ledger。
- [x] **DOC-04**: contributor fast-path、maintainer appendix 与双语边界策略必须显式化、可链接、可守卫。
- [x] **HOT-11**: 高复杂度热点文件与长函数必须沿现有正式 seams 切薄，且不得扩张 public surface。
- [x] **ERR-11**: 布尔失败返回必须升级为 typed result / reason code，并可被 diagnostics / share / message 路径消费。
- [x] **TYP-10**: runtime / diagnostics / share / message touched-zone 的 typed budget 必须继续收紧，并设 no-growth guard。
- [x] **QLT-15**: benchmark 必须从“留证据”升级为“防回退”门禁，具备基线比较与阈值告警。

## Traceability for archived v1.6 route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-34 | Phase 42 | Completed |
| QLT-12 | Phase 42 | Completed |
| QLT-13 | Phase 42 | Completed |
| QLT-14 | Phase 42 | Completed |
| ARC-04 | Phase 43 | Completed |
| CTRL-10 | Phase 43 | Completed |
| RUN-07 | Phase 43 | Completed |
| GOV-35 | Phase 44 | Completed |
| RES-11 | Phase 44 | Completed |
| DOC-04 | Phase 44 | Completed |
| HOT-11 | Phase 45 | Completed |
| ERR-11 | Phase 45 | Completed |
| TYP-10 | Phase 45 | Completed |
| QLT-15 | Phase 45 | Completed |

**Coverage:**
- v1.6 routed requirements: 14 total
- Current mapped: 14
- Current complete: 14
- Current pending: 0
- Current unmapped: 0 ✓

## Archived Milestone (v1.5)

> `v1.5` 已于 `2026-03-19` 完成归档；以下 requirements / traceability 保留 `Phase 40` 的最终 fulfilled contract，归档快照见 `.planning/milestones/v1.5-REQUIREMENTS.md`，审计裁决见 `.planning/v1.5-MILESTONE-AUDIT.md`，证据入口见 `.planning/reviews/V1_5_EVIDENCE_INDEX.md`。

### Governance Truth & Control-Surface Finalization

- [x] **GOV-33**: authority precedence、active truth、archive snapshots、promoted phase assets 与 derived collaboration maps 的身份必须在 `AGENTS.md`、baseline 三件套、`docs/README.md` 与 current-story docs 中讲同一条故事，并吸收 `V1_4_EVIDENCE_INDEX.md` / `v1.4-MILESTONE-AUDIT.md` / `Phase 38-39` closeout 证据。
- [x] **QLT-11**: continuity / release-trust / install-path / support-routing 事实必须收口到 machine-readable governance registry，并以 meta guards 强制 README、README_zh、CONTRIBUTING、SUPPORT、SECURITY、TROUBLESHOOTING、runbook、issue/PR templates 同步；同时补齐 break-glass verify-only 与 non-publish rehearsal 语义。
- [x] **CTRL-09**: control/services 对 runtime 的枚举、device read-model、snapshot/telemetry projection 与 diagnostics lookup 必须统一经 `runtime_access` formal home 暴露，不得继续在 `diagnostics_surface.py`、`device_lookup.py`、`maintenance.py` 各自复制 locator/read logic。
- [x] **ERR-10**: service-layer auth/error execution contract 必须统一到正式 shared executor；`schedule.py` 不得继续复制 coordinator auth chain、旁路 reauth 语义或独立 broad arbitration story。
- [x] **RES-10**: touched protocol/runtime/service hotspots 中的 `client` / `forwarding` / `mixin` stale terminology 必须继续收口到 `protocol` / `port` / `facade` / `operations` 语义；compat-leaning wording 只允许留在历史文档或显式 residual 账本中。

## Traceability for archived v1.5 route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-33 | Phase 40 | Complete |
| QLT-11 | Phase 40 | Complete |
| CTRL-09 | Phase 40 | Complete |
| ERR-10 | Phase 40 | Complete |
| RES-10 | Phase 40 | Complete |

**Coverage:**
- v1.5 routed requirements: 5 total
- Current mapped: 5
- Current complete: 5
- Current pending: 0
- Current unmapped: 0 ✓

## Archived Milestone (v1.4)

> `v1.4` 已于 `2026-03-19` 完成归档；以下 requirements / traceability 保留 `Phase 34 -> 39` 的最终 fulfilled contract，归档快照见 `.planning/milestones/v1.4-REQUIREMENTS.md`，审计裁决见 `.planning/v1.4-MILESTONE-AUDIT.md`，证据入口见 `.planning/reviews/V1_4_EVIDENCE_INDEX.md`。

### Continuity & Release Trust

- [x] **GOV-29**: maintainer continuity 已从“单维护者现实的诚实记录”升级为“delegate / custody transfer / freeze escalation”的正式合同；support / security / release 不再依赖隐性人治。
- [x] **QLT-08**: release identity 已补齐 machine-verifiable artifact signing，并把 hard release-trust gate 与现有 `SHA256SUMS` / `SBOM` / attestation / provenance story 统一成单一 blocking contract。

### Protocol Hotspots

- [x] **HOT-09**: `LiproRestFacade` 与 `LiproProtocolFacade` 必须继续沿现有 seams 切薄，root 层 forwarding glue 不得长期合法化为协议主链的一部分。
- [x] **RES-07**: protocol/control touched hotspots 的 compat / forwarding residue、反射/私有实现细节依赖（如 `__dict__` / `_waiters` 类模式）与命名残留必须继续删除、下沉或显式登记 delete gate；public surface 不能借重构反向扩张。

### Runtime Root & Exception Policy

- [x] **HOT-10**: `Coordinator` 运行根必须继续瘦身，并把 runtime/service 协作者 home 固化到更小、更清晰的边界。
- [x] **ERR-08**: 生产宽异常必须继续 burn-down 到可守护阈值；核心热点只能保留 named arbitration、documented degraded semantics 或 fail-closed path。
- [x] **TYP-09**: runtime/service/platform touched-zone 的 typed budget 必须继续收紧，并以 no-growth guards 固化到 daily governance gates。

### Test Topology & Derived Truth

- [x] **TST-06**: 剩余巨石测试必须继续 topicize 成稳定、可局部执行的专题面，避免单文件持续吸附多条故事线。
- [x] **GOV-30**: `.planning/codebase/*`、测试策略文档、verification / authority truth 与 public docs entry topology 必须和真实测试命令、目录结构、support/security/docs routing 及守卫语义保持一致，并有 drift guard 约束。
- [x] **QLT-09**: benchmark / test-topology / closeout evidence / governance guards 必须从“可执行”提升到“可解释、可对齐、可审计”的质量故事：形成预算或基线语义、降低 prose-coupled 高噪音断言，并避免派生真相漂移于实际门禁之外。

### Fresh-Audit Residual & Quality-Signal Hardening

- [x] **RES-08**: external-boundary firmware naming 必须退役最后一条 active residual family，统一到 bundled local trust-root asset + remote advisory payload 的诚实术语，同时保留历史资产文件名与 authority contract。
- [x] **QLT-10**: coverage floor / explicit-baseline diff / advisory benchmark artifact posture 必须在脚本、CI、贡献文档与 derived testing map 中讲同一条 machine-checkable 质量故事，dead marker semantics 不得回流。
- [x] **GOV-31**: governance closeout / phase-history guards 必须优先依赖 `ROADMAP` / `REQUIREMENTS` / recommended command anchors，而不是 sentence-level `PROJECT` / `STATE` prose 复述，同时保持审计强度。

### Governance Current-Story & Test Topology Closeout

- [x] **GOV-32**: `ROADMAP / REQUIREMENTS / STATE / PROJECT` 必须共同承认 `v1.4 / Phase 39 complete / closeout-ready` 当前故事，coverage / traceability 算术可被守卫验证。
- [x] **DOC-03**: `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 与 `docs/developer_architecture.md` 必须刷新到 current topology，并显式说明 `custom_components/lipro/control/` 是 formal control-plane home。
- [x] **CTRL-08**: control-plane formal home / thin-adapter boundary / `services/` helper identity 必须同步到治理真源、review ledgers 与守卫断言。
- [x] **RES-09**: dead protocol shell、误导性 fixture/replay authority 命名与相关 residual folklore 必须退场或历史化，不得继续暗示第二 public truth。
- [x] **TST-07**: remaining mega-tests 与治理巨石守卫必须继续 topicize / structure 化，Phase 39 closeout evidence 必须显式 promoted。

## Traceability for v1.4 route + fresh-audit continuation

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-29 | Phase 34 | Complete |
| QLT-08 | Phase 34 | Complete |
| HOT-09 | Phase 35 | Complete |
| RES-07 | Phase 35 | Complete |
| HOT-10 | Phase 36 | Complete |
| ERR-08 | Phase 36 | Complete |
| TYP-09 | Phase 36 | Complete |
| TST-06 | Phase 37 | Complete |
| GOV-30 | Phase 37 | Complete |
| QLT-09 | Phase 37 | Complete |
| RES-08 | Phase 38 | Complete |
| QLT-10 | Phase 38 | Complete |
| GOV-31 | Phase 38 | Complete |
| GOV-32 | Phase 39 | Complete |
| DOC-03 | Phase 39 | Complete |
| CTRL-08 | Phase 39 | Complete |
| RES-09 | Phase 39 | Complete |
| TST-07 | Phase 39 | Complete |

**Coverage:**
- v1.4 requirements + fresh-audit continuation: 18 total
- Current mapped: 18
- Current complete: 18
- Current pending: 0
- Current unmapped: 0 ✓
