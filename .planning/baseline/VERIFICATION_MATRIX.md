# Verification Matrix

**Purpose:** 建立 requirement → artifact → test → doc → phase acceptance / handoff 的统一验证闭环。
**Status:** Formal baseline asset (`BASE-03` phase acceptance truth source)
**Updated:** 2026-03-16 (Phase 18 nucleus locality aligned)

## Formal Role

- 本文件是 `Phase 1.5` 及其下游 phases 的正式 acceptance truth；phase docs / summaries 只能引用、实例化或扩展，不得平行定义 exit contract。
- 任一 phase 只有同时交付 requirement evidence、artifact updates、verification proof 与 governance disposition，才可宣称完成。
- 若新增、降级或删除正式 public surface，改变 dependency truth，扩展 authority family，或新增 architecture policy rule family / CI gate，必须先回写对应 baseline doc，再更新实现、测试与 summary。
- `.planning/baseline/ARCHITECTURE_POLICY.md` 是 verification gate 的正式 policy companion；phase exit contract 与 runnable proof 只能引用或实例化它，不能绕开它自立规则。
- 若 `.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md` 无变化，phase summary 也必须明确写出“为何无变化”。
- `.planning/codebase/*.md` 若被保留，必须通过 `README.md`、统一 derived collaboration map disclaimer 与治理守卫声明其从属身份，不能越权成为第二条 authority chain。

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
- **Required runnable proof:** `uv run ruff check .`、`uv run mypy`、`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q tests/core/test_developer_report.py tests/core/test_report_builder.py tests/core/test_anonymous_share.py tests/core/test_control_plane.py tests/services/test_services_diagnostics.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py` 与 `uv run python scripts/coverage_diff.py coverage.json --minimum 95` 通过。
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
