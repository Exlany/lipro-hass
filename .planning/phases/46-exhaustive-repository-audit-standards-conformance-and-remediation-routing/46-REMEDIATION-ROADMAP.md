# Phase 46 Remediation Roadmap

## Roadmap Posture

- 本路线不是重新打开“大一统重构”，而是把 Phase 46 审阅结果转成更窄、更可验证、更不易回流第二故事线的正式 phase seeds。
- 排序原则：先解 continuity / governance high-risk contract，再处理 formal-root density、mega-test topology、typed-surface debt；所有路线都必须带 verify anchors。
- 优先级符号：`P0` = 仓库级高优先级 contract 缺口；`P1` = 高杠杆 maintainability / testability / typeability 改进；`P2` = 重要但可后置的降噪与 polish。

## P0 Immediate Risk Reduction

### Phase 47: Continuity contract, governance entrypoint compression, and tooling discoverability

**Why first**
- 当前最真实的 P0 不是代码结构阻断，而是 single-maintainer / no-delegate continuity risk。
- 同一个 phase 内可以顺手解决 docs discoverability、scripts active/deprecated 噪音、Documentation URL 偏差、installer stable/preview 语义提示等高杠杆治理问题。

**Primary outcomes**
- formalize release custody / delegate / successor / maintainer-unavailable contract
- sync `SUPPORT.md` / `SECURITY.md` / `docs/MAINTAINER_RELEASE_RUNBOOK.md` / `.github/CODEOWNERS` / templates / governance registry
- expose `docs/README.md` more directly as the documentation index
- classify `scripts/**` into active vs deprecated / compatibility stubs
- refine installer stable-vs-preview wording or opt-in semantics without weakening verified release path

**Core files**
- `SUPPORT.md`
- `SECURITY.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `docs/README.md`
- `.github/CODEOWNERS`
- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/pull_request_template.md`
- `pyproject.toml`
- `scripts/agent_worker.py`
- `scripts/orchestrator.py`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`

**Verify anchors**
- `uv run pytest tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_closeout_guards.py tests/meta/test_version_sync.py -q`

## P1 High-Leverage Structural Fixes

### Phase 48: Runtime-access and formal-root hotspot decomposition without public-surface drift

**Why next**
- `RuntimeAccess`、`Coordinator`、`__init__.py`、`EntryLifecycleController` 是当前最该限流的正确热点。
- 这一 phase 的目标不是换架构，而是防止“正确 home 继续变成新根”。

**Primary outcomes**
- slim `control/runtime_access.py` by topicizing projections and telemetry/system-health helpers
- continue inward decomposition of `Coordinator`, `__init__.py`, and `EntryLifecycleController`
- keep runtime public surface stable while reducing decision density
- preserve lazy wiring and control/runtime boundary guards

**Core files**
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/__init__.py`
- `custom_components/lipro/control/entry_lifecycle_controller.py`
- `custom_components/lipro/control/diagnostics_surface.py`
- `custom_components/lipro/control/system_health_surface.py`
- `tests/core/test_coordinator.py`
- `tests/core/test_init*.py`
- `tests/core/test_diagnostics.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_public_surface_guards.py`

**Verify anchors**
- `uv run pytest tests/core/test_control_plane.py tests/core/test_coordinator.py tests/core/test_init.py tests/core/test_init_service_handlers.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py -q`

### Phase 49: Mega-test topicization and failure-localization hardening

**Why next**
- 仓库测试体系已经成熟，接下来最值钱的是 failure-localization，而不是盲目加更多 guard。
- 先拆治理 megaguards 与 runtime-root megas，再处理平台 megas，收益最大。

**Primary outcomes**
- split governance megaguards by concern (`closeout-assets`, `phase-promotions`, `milestone-archives`, `public-exports`, etc.)
- topicize `tests/core/test_coordinator.py` and `tests/core/test_diagnostics.py`
- decompose `tests/platforms/test_update.py` into manifest / certification / install / cache sub-surfaces
- re-home stray top-level tests into natural domain directories
- improve assertion ids / parameterization so failures name the actual `(phase, doc, token)` or runtime facet

**Core files**
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/core/test_coordinator.py`
- `tests/core/test_diagnostics.py`
- `tests/platforms/test_update.py`
- `tests/core/api/test_api_command_surface.py`
- `tests/core/mqtt/test_transport_runtime.py`
- `tests/test_coordinator_public.py`
- `tests/test_coordinator_runtime.py`
- `tests/test_refactor_tools.py`

**Verify anchors**
- `uv run pytest tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/core/test_coordinator.py tests/core/test_diagnostics.py tests/platforms/test_update.py tests/core/api/test_api_command_surface.py tests/core/mqtt/test_transport_runtime.py -q`

### Phase 50: REST typed-surface reduction and command/result ownership convergence

**Why next**
- 当前最大的结构化类型债集中在 REST child façade family；同时 `core/command` 的 write-side helper 身份与 protocol/api policy 之间还有 ownership 漂移。
- 这一 phase 可以同时解决 typeability 与 conceptual ownership 两类问题。

**Primary outcomes**
- reduce `Any` in `endpoint_surface.py`, `rest_facade.py`, `request_gateway.py`, and related request/endpoint method helpers
- make sanctioned vs backlog `Any` classifications narrower and more explicit
- converge duplicated command-result policy logic into one shared home
- close diagnostics/helper auth-error duplication back toward `services/execution.py`
- keep public REST surface unchanged while increasing typed helper honesty

**Core files**
- `custom_components/lipro/core/api/endpoint_surface.py`
- `custom_components/lipro/core/api/rest_facade.py`
- `custom_components/lipro/core/api/request_gateway.py`
- `custom_components/lipro/core/api/rest_facade_request_methods.py`
- `custom_components/lipro/core/api/rest_facade_endpoint_methods.py`
- `custom_components/lipro/core/command/dispatch.py`
- `custom_components/lipro/core/command/result.py`
- `custom_components/lipro/core/command/result_policy.py`
- `custom_components/lipro/services/diagnostics/helpers.py`
- `tests/core/api/test_api_command_surface.py`
- `tests/core/api/test_api_status_service.py`
- `tests/core/test_command_result.py`
- `tests/meta/test_phase31_runtime_budget_guards.py`
- `tests/meta/test_phase45_hotspot_budget_guards.py`

**Verify anchors**
- `uv run pytest tests/core/api/test_api_command_surface.py tests/core/api/test_api_status_service.py tests/core/test_command_result.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py -q`

## P2 Governance and Documentation Hygiene

### Deferred but valuable follow-through

- maintainer appendix English summary / delegate-onboarding aids
- further README weight reduction and public-vs-maintainer navigation tightening
- narrower repo-wide `Any` metrics that exclude guard/test literal noise
- localized compat-shim honesty improvements in ledgers / baseline docs when needed

## Dependency Order

1. `Phase 47` first — continuity contract and docs/governance discoverability are repo-wide risk reducers.
2. `Phase 48` second — formal-root hotspot decomposition should happen before further typed-surface refinement.
3. `Phase 49` third — test topicization benefits from stabilized root boundaries.
4. `Phase 50` fourth — REST typed-surface reduction and command/result convergence land best after hotspot seams are clearer.

## Non-Goals

- 不恢复第二套 root、compat shell、legacy public names 或 package-level folklore。
- 不在 remediation roadmap 中直接承诺大规模 API redesign。
- 不把 `Phase 46` 自己的 planning workspace 误升为长期治理真源；长期 evidence promotion 只允许最终 audit package。
