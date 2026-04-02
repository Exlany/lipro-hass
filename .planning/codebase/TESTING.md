# Testing Patterns

**Analysis Date:** 2026-04-02

> Snapshot: `2026-04-02`
> Freshness: 基于 `tests/**`、`pyproject.toml`、`.github/workflows/{ci,release}.yml`、`scripts/{lint,check_architecture_policy.py,check_file_matrix.py,check_markdown_links.py}` 与 `.planning/baseline/VERIFICATION_MATRIX.md` 的当前截面。
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、审阅与后续实现对齐。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md}`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本文件不得反向充当当前治理真源。

## Test Framework

**Runner:**
- `pytest` with config in `pyproject.toml`.
- Async support comes from `pytest-asyncio`; Home Assistant integration fixtures come from `pytest-homeassistant-custom-component`.
- Snapshot coverage uses `syrupy`; performance lanes use `pytest-benchmark`; coverage gates use `pytest-cov` plus `scripts/coverage_diff.py`.

**Assertion Library:**
- Plain `pytest` assertions, `pytest.raises`, `AsyncMock`/`MagicMock` checks from `unittest.mock`, and `syrupy` snapshots in `tests/snapshots/test_api_snapshots.py`.

**Run Commands:**
```bash
uv run pytest -q
uv run python scripts/check_markdown_links.py
uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing
./scripts/lint --full
```

## Phase 140 Execution Freeze

- `tests/meta/test_governance_release_docs.py`、`tests/meta/test_governance_release_continuity.py`、`tests/meta/test_governance_release_contract.py`、`tests/meta/test_phase140_governance_source_freshness_guards.py` 与 `tests/meta/governance_followup_route_current_milestones.py` 共同冻结 stale verification lane refresh、public changelog scope、runbook access-mode wording、route selector projection 与 planning-ready handoff。
- `uv run pytest -q tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_governance_release_contract.py tests/meta/test_phase140_governance_source_freshness_guards.py tests/meta/governance_followup_route_current_milestones.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/toolchain_truth_testing_governance.py tests/meta/test_version_sync.py` 与 `uv run python scripts/check_file_matrix.py --check` 共同定义 Phase 140 的 governance/docs exit proof。
- nested worktree 下 `gsd-tools` root detection 不作为 testing inventory 的 live truth authority；以 selector family、registry、baseline docs、focused guards 与 `140-*` phase assets 的一致投影为准。

## Phase 139 Execution Freeze

- `tests/core/protocol/test_facade.py`、`tests/core/api/test_api_transport_and_schedule_schedules.py`、`tests/core/api/test_protocol_contract_facade_runtime.py` 与 `tests/meta/test_phase139_mega_facade_second_pass_guards.py` 共同冻结 REST/protocol second-pass slimming、schedule `group_id` forwarding honesty、formal-home locality 与 governance route projection。
- `uv run ruff check custom_components/lipro/core/api/rest_facade.py custom_components/lipro/core/api/rest_facade_internal_methods.py custom_components/lipro/core/api/rest_facade_endpoint_methods.py custom_components/lipro/core/api/endpoint_surface.py custom_components/lipro/core/protocol/rest_port.py custom_components/lipro/core/protocol/rest_port_bindings.py tests/core/protocol/test_facade.py tests/core/api/test_api_transport_and_schedule_schedules.py tests/core/api/test_protocol_contract_facade_runtime.py tests/meta/test_phase139_mega_facade_second_pass_guards.py`、`uv run pytest -q tests/core/protocol/test_facade.py tests/core/api/test_api_transport_and_schedule_schedules.py tests/core/api/test_protocol_contract_facade_runtime.py tests/meta/test_phase69_support_budget_guards.py tests/meta/test_phase91_typed_boundary_guards.py tests/meta/test_phase139_mega_facade_second_pass_guards.py`、`uv run python scripts/check_file_matrix.py --check` 与 `uv run python scripts/check_architecture_policy.py --check` 共同构成 Phase 139 exit proof。

## Phase 131 Execution Freeze

- `Phase 131` 的 final proof chain 由三层组成：repo-wide docs/governance/toolchain truth guards、selector-route/promoted-assets guards，以及 `ruff` / `check_file_matrix` / markdown-link validation。
- current closeout proof 必须共同承认：`v1.37` 仍是 active milestone route，latest archived baseline 仍是 `v1.36`，但 execution state 已进入 `Phase 131 complete / closeout-ready`，下一步只剩 `$gsd-complete-milestone v1.37`。
- 本轮 focused proof 还额外冻结了两类 honesty 修正：docs-first public routing 不再自相矛盾，Python/toolchain truth 与 registry install semantics 不再分叉。

## Test File Organization

**Location:**
- Tests live in a dedicated `tests/` tree, not beside production files.
- Current topology is broad and intentional: `tests/core`, `tests/services`, `tests/flows`, `tests/platforms`, `tests/entities`, `tests/meta`, `tests/integration`, `tests/snapshots`, `tests/benchmarks`, `tests/harness`, and `tests/fixtures`.
- Repository counts from current scanning: `421` Python files under `tests`, `337` runnable `test_*.py` files, `78` meta suites, `5` integration suites, `4` snapshot suites, `4` benchmark suites, and `5` fixture family READMEs.

**Naming:**
- Use `test_*.py` everywhere.
- Keep thin roots stable and push detailed concerns into sibling files, e.g. `tests/meta/test_dependency_guards.py` re-exports `tests/meta/dependency_guards_*.py`, and `tests/core/api/test_protocol_contract_matrix.py` remains a thin anchor while fixtures and adjacent suites carry the real protocol contract detail.

**Structure:**
```text
tests/
├── conftest.py
├── core/
├── services/
├── flows/
├── platforms/
├── entities/
├── meta/
├── integration/
├── snapshots/
├── benchmarks/
├── fixtures/
└── harness/
```

## Phase 130 Execution Freeze

- `tests/core/coordinator/runtime/test_command_runtime_support_helpers.py`、`tests/core/coordinator/runtime/test_command_runtime_orchestration.py`、`tests/core/coordinator/runtime/test_command_runtime_outcome_support.py` 与 `tests/core/coordinator/runtime/test_runtime_telemetry_methods.py` 共同冻结 `command_runtime.py` 的 request-trace、dispatch normalization、verify/finalize 与 telemetry slimmed seams。
- `tests/platforms/test_update_install_flow.py`、`tests/platforms/test_update_background_tasks.py`、`tests/platforms/test_update_task_callback.py`、`tests/platforms/test_update_entity_refresh.py` 与 `tests/platforms/test_firmware_update_entity_edges.py` 共同冻结 `firmware_update.py` 的 install/task/query/projection inward split。
- `tests/core/ota/test_ota_candidate.py`、`tests/core/ota/test_ota_rows_cache.py`、`tests/core/ota/test_ota_row_selector.py` 与 `tests/core/ota/test_firmware_manifest.py` 继续守住 OTA candidate / cache / selector / local-manifest authority，不让 entity-side refactor 反向改写真源。
- `tests/meta/test_phase95_hotspot_decomposition_guards.py`、`tests/meta/test_phase99_runtime_hotspot_support_guards.py`、`tests/meta/test_phase111_runtime_boundary_guards.py`、`tests/meta/test_phase113_hotspot_assurance_guards.py` 与 `tests/meta/test_phase71_hotspot_route_guards.py` 共同冻结 predecessor visibility、runtime/entity boundary、hotspot budget 与 route continuity；`uv run ruff check .`、`uv run python scripts/check_file_matrix.py --check` 与 isolated `gsd-tools` fast-path 共同构成 Phase 130 exit proof。

## Phase 129 Execution Freeze

- `tests/core/api/test_protocol_contract_facade_runtime.py`、`tests/core/api/test_api_command_surface_misc.py`、`tests/core/api/test_api_transport_and_schedule_transport_boundary.py` 与 targeted `tests/core/api/test_api.py::*LiproRestFacade*` 共同冻结 `rest_facade.py` 的 explicit-surface / wrapper-ownership truth。
- `tests/core/api/test_api_status_service_wrappers.py`、`tests/core/api/test_api_status_service_fallback.py`、`tests/core/api/test_api_status_service_regressions.py` 共同冻结 fallback public route、primary-query path、depth metrics、await-count 与 summary logging 语义。
- `tests/meta/test_phase99_runtime_hotspot_support_guards.py`、`tests/meta/test_phase107_rest_status_hotspot_guards.py`、`tests/meta/test_phase113_hotspot_assurance_guards.py`、`tests/meta/test_governance_bootstrap_smoke.py`、`tests/meta/test_governance_route_handoff_smoke.py` 与 `tests/meta/test_governance_release_contract.py` 共同冻结 hotspot no-regrowth 与 route-truth projection；`uv run ruff check .`、`uv run python scripts/check_file_matrix.py --check` 与 isolated `gsd-tools` fast-path 共同构成 Phase 129 exit proof。

## Phase 128 Execution Freeze

- `tests/meta/test_governance_release_continuity.py`、`tests/meta/toolchain_truth_docs_fast_path.py`、`tests/meta/test_version_sync.py`、`tests/meta/toolchain_truth_ci_contract.py`、`tests/meta/test_governance_release_contract.py`、`tests/meta/toolchain_truth_testing_governance.py` 与 `tests/meta/test_governance_route_handoff_smoke.py` 共同冻结 readiness honesty、route selector、CI lane contract 与 closeout-ready governance truth。
- `uv run pytest -q tests/benchmarks/test_command_benchmark.py tests/benchmarks/test_mqtt_benchmark.py tests/benchmarks/test_device_refresh_benchmark.py --benchmark-only --benchmark-json=.benchmarks/benchmark-smoke.json` 与 `uv run python scripts/check_benchmark_baseline.py .benchmarks/benchmark-smoke.json --manifest tests/benchmarks/benchmark_baselines.json --benchmark-set smoke` 冻结 PR smoke benchmark contract；`pyproject.toml` 的 `--strict-markers` 则防止 marker silently drift。
- `uv run ruff check .`、`uv run python scripts/check_file_matrix.py --check` 与 `uv run pytest -q` 共同构成本轮 phase exit proof；route docs 与 gsd-tools state 也需同步识别 `v1.36 / Phase 128 complete; closeout-ready`。

## Phase 125 Execution Freeze

- Focused proof 现在覆盖三条 Phase 125 主链：governance route contract (`tests/meta/governance_followup_route_current_milestones.py`, `tests/meta/test_governance_route_handoff_smoke.py`, `tests/meta/test_governance_release_contract.py`)、runtime contract cleanup (`tests/meta/test_runtime_contract_truth.py`, `tests/meta/public_surface_architecture_policy.py`, `tests/services/test_service_resilience.py`) 与 flow/auth thinning (`tests/flows/test_config_flow_user.py`, `tests/flows/test_config_flow_reauth.py`, `tests/flows/test_config_flow_reconfigure.py`, `tests/core/test_token_persistence.py`)。
- `scripts/check_file_matrix.py --check`、focused governance/docs suites 与 registry-driven route contract 现在一起守护 current-route truth，不再依赖五份手写 selector prose。
- `Phase 125` closeout proof 必须同时通过 `uv run ruff check .`、`uv run python scripts/check_file_matrix.py --check` 与 `uv run pytest -q`；在这些命令全绿前不得宣称 `v1.35` 可以里程碑归档。

## Historical Phase Notes

- Phase 55: 当前仓库共有 `335` 个 `test_*.py` 文件，topicized thin shells 继续覆盖 command-surface、transport-runtime 与 light/fan/select/switch suites。
- Phase 59: `tests/core/test_device_refresh_{parsing,filter,snapshot,runtime}.py` 继续作为 localized device-refresh verification note；topicized meta note carriers 与 verification anchors 保持分离。
- Phase 88: `tests/meta/test_phase88_governance_quality_freeze_guards.py` 继续作为 focused guard home for phase-88 governance/evidence freeze。
- Phase 90: `tests/meta/test_phase90_hotspot_map_guards.py` 继续作为 focused guard home for five formal homes / four protected thin shells / delete-gate freeze truth。
- Phase 96: `tests/meta/test_phase96_sanitizer_burndown_guards.py` 继续作为 focused guard home for diagnostics/telemetry/anonymous-share sanitizer burn-down truth。
- Phase 97: `tests/meta/test_phase97_governance_assurance_freeze_guards.py` 继续作为 focused guard home for v1.26 archived closeout bundle / developer-architecture historical note truth。
- Phase 98: `tests/meta/test_phase98_route_reactivation_guards.py` 继续作为 focused guard home for predecessor route-reactivation / carry-forward closure truth。
- Phase 99: `tests/meta/test_phase99_runtime_hotspot_support_guards.py` 继续作为 focused predecessor guard home for runtime hotspot support extraction / governance freeze truth。
- Phase 100: `tests/meta/test_phase100_runtime_schedule_support_guards.py` 继续作为 focused predecessor guard home for MQTT/runtime schedule support extraction / governance freeze truth。
- Phase 101: `tests/meta/test_phase101_anonymous_share_rest_boundary_guards.py` 继续作为 focused predecessor guard home for anonymous-share manager / REST-boundary hotspot decomposition truth。
- Phase 102: `tests/meta/test_phase102_governance_portability_guards.py` 继续作为 focused latest-archived guard home for governance portability / verification stratification / open-source continuity hardening truth。

## Test Structure

**Suite Organization:**
```python
"""Thin shell for topicized dependency-guard suites."""

from .dependency_guards_policy import *
from .dependency_guards_protocol_contracts import *
from .dependency_guards_review_ledgers import *
from .dependency_guards_service_runtime import *
```

**Patterns:**
- Use topicized suites to keep failure localization narrow. This pattern appears in `tests/meta/test_dependency_guards.py`, `tests/meta/test_governance_milestone_archives.py`, and multiple API/runtime roots described in the planning baselines.
- Prefer explicit fixture-driven setup over ad-hoc inline state creation. `tests/conftest.py` remains the main shared fixture home and also manages thin-shell collection rules.
- Keep async tests as plain `async def test_*` functions; current scanning finds `859` async tests, matching the repo's async integration style.
- Use file-reading assertions for governance/docs/workflow truth instead of mocking the filesystem. Example: `tests/meta/test_governance_release_contract.py` reads `.github/workflows/*.yml`, `CONTRIBUTING.md`, and governance docs directly.

## Mocking

**Framework:** `unittest.mock`.

**Patterns:**
```python
with patch("custom_components.lipro.config_flow.LiproProtocolFacade", autospec=True) as mock_client_class:
    mock_client = mock_client_class.return_value
    mock_client.login = AsyncMock(return_value={"access_token": "test_access_token"})
```

- Mock Home Assistant adapters, protocol façades, auth managers, and coordinator seams; examples live in `tests/conftest.py`, `tests/core/test_init.py`, and `tests/flows/test_options_flow.py`.
- Keep governance truth tests mostly unmocked. Files such as `tests/meta/dependency_guards_protocol_contracts.py` and `tests/meta/toolchain_truth_docs_fast_path.py` read repository files directly to catch real drift.

**What to Mock:**
- Home Assistant services and config entry interactions.
- Protocol and auth collaborators (`LiproProtocolFacade`, auth managers, MQTT façade seams).
- Coordinator side effects and network responses.

**What NOT to Mock:**
- Fixture truth in `tests/fixtures/api_contracts`, `tests/fixtures/protocol_boundary`, `tests/fixtures/protocol_replay`, and `tests/fixtures/evidence_pack`.
- Docs/workflow/governance files in `tests/meta`, because those suites intentionally validate the committed files themselves.

## Fixtures and Factories

**Test Data:**
```python
@pytest.fixture
def make_device():
    def _make(kind: str = "light", **overrides: Any) -> Any:
        from custom_components.lipro.core.device import LiproDevice
        return LiproDevice(...)
    return _make
```

- Shared factories and doubles live in `tests/conftest.py`, including `make_device`, `_CoordinatorDouble`, `mock_lipro_api_client`, and `mock_auth_manager`.
- Fixture README files explain authority and ownership instead of letting payloads become folklore: `tests/fixtures/api_contracts/README.md`, `tests/fixtures/protocol_boundary/README.md`, `tests/fixtures/protocol_replay/README.md`, and `tests/fixtures/evidence_pack/README.md`.

**Location:**
- Shared fixtures: `tests/conftest.py`
- Fixture payloads: `tests/fixtures/**`
- Reusable harness helpers: `tests/harness/**`
- Small utility helpers: `tests/helpers/**`

## Coverage

**Requirements:**
- Total coverage floor is `95%` in `.github/workflows/ci.yml`, `scripts/lint`, and `CONTRIBUTING.md`.
- Changed-surface coverage floor is also `95%` via `scripts/coverage_diff.py` and `.coverage-changed-files`.
- Snapshot coverage is folded into the main `tests/` lane; benchmark coverage is deliberately excluded from the blocking test lane.
- Typing-budget governance remains part of the testing story: `production_any`, `production_type_ignore`, `tests_any_non_meta`, `meta_guard_any_literals`, `meta_support_any`, `tests_type_ignore`, and `meta_guard_type_ignore_literals` stay documented in `.planning/baseline/VERIFICATION_MATRIX.md` and must remain explainable from this testing map.

**View Coverage:**
```bash
uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing
uv run python scripts/coverage_diff.py coverage.json --minimum 95 --changed-files .coverage-changed-files --changed-minimum 95
uv run python scripts/refactor_tools.py --coverage-json coverage.json --minimum-coverage 95
```

## Test Types

**Unit Tests:**
- Most behavior tests live in `tests/core`, `tests/services`, `tests/flows`, `tests/platforms`, and `tests/entities`.
- These suites mirror the production planes and adapters instead of mixing every concern into one directory.

**Integration Tests:**
- Integration-style tests live in `tests/integration`, including MQTT coordinator behavior, headless consumer proof, telemetry exporter, replay harness, and AI evidence pack flows.

**E2E Tests:**
- Full UI/browser E2E is not used.
- The closest equivalents are Home Assistant integration tests plus repository validation jobs such as Hassfest/HACS validation in `.github/workflows/ci.yml`.

**Governance / Meta Tests:**
- `tests/meta` is a first-class layer, not a sidecar. It validates architecture guards, docs routing, workflow contracts, version sync, promoted phase assets, and governance current-truth rules.
- Focused guards such as `tests/meta/test_phase89_tooling_decoupling_guards.py` keep script-owned helper truth local to `scripts/check_architecture_policy.py` while `tests/helpers/*` stay thin consumers.
- If you change docs, workflows, release contracts, planning truth, or architecture ledgers, add or update meta tests rather than relying only on runtime assertions.

**Performance Tests:**
- Benchmarks live in `tests/benchmarks`, use `@pytest.mark.benchmark`, and are governed by `tests/benchmarks/benchmark_baselines.json` plus `scripts/check_benchmark_baseline.py`.
- CI only runs benchmarks on `schedule` or `workflow_dispatch`; the benchmark lane is governed but not part of normal PR blocking.

## CI and Quality Gates

**CI lanes:**
- `lint` runs Ruff, formatter check, mypy, translations, Markdown docs-link checks, and shellcheck from `.github/workflows/ci.yml`.
- `governance` runs `scripts/check_architecture_policy.py`, `scripts/check_file_matrix.py`, and focused `tests/meta` guards.
- `security` exports runtime requirements and runs blocking runtime `pip-audit`; dev-environment audit is advisory only on scheduled/manual runs.
- `test` runs the full non-benchmark suite with coverage, changed-surface coverage checks, and `scripts/refactor_tools.py`.
- `benchmark` and `compatibility_preview` are schedule/manual-only lanes.
- `release` reuses `ci.yml` first, then adds tagged security, CodeQL, smoke install, SBOM, attestation, signing, and signature verification in `.github/workflows/release.yml`.

**Pre-commit / local gates:**
- `.pre-commit-config.yaml` mirrors the same contract family with local Ruff, mypy, translations, Markdown docs-link checks, architecture/file-matrix scripts, focused diagnostics tests, and governance guards.
- `scripts/lint` is the closest local umbrella entrypoint; default mode still skips the generic governance/full-pytest matrix, but it now auto-runs the Phase 113 focused assurance chain when matching hotspot / toolchain / governance-handoff surfaces are touched, while `--full` mirrors the heavy CI path.

## Common Patterns

**Async Testing:**
```python
@pytest.mark.asyncio
async def test_protocol_contract_baseline_snapshots(snapshot: SnapshotAssertion) -> None:
    ...
    assert {"mqtt_config": ..., "get_city": ..., "query_user_cloud": ...} == snapshot
```

**Error Testing:**
```python
with pytest.raises(ServiceValidationError):
    await service_call(...)
```

- `pytest.raises` appears heavily across the suite; current grep count is `215` occurrences.
- Parametrization is used, but selectively (`52` occurrences), so new table-driven coverage should usually land in targeted concern files rather than giant omnibus tests.

## Recommendations

- Prefer adding new assertions to concern-local sibling suites instead of enlarging current hotspots such as `tests/conftest.py`, `tests/core/test_auth.py`, `tests/core/api/test_api_status_service.py`, `tests/platforms/test_light_entity_behavior.py`, or `tests/services/test_services_diagnostics.py`.
- When changing workflows, docs routes, release semantics, or governance truth, add or update `tests/meta/*` in the same patch; this repo treats docs and CI contracts as testable behavior.
- When changing protocol payloads or replay behavior, update the owning fixture README and the fixture-backed tests together so authority stays explicit.
- Keep benchmark edits inside `tests/benchmarks` plus `benchmark_baselines.json`; do not mix performance-only assertions into the main blocking suite unless the behavior is a correctness concern.

---

*Testing analysis: 2026-03-27*


## Phase 91 Testing Freeze

- `tests/meta/test_phase91_typed_boundary_guards.py` now freezes protocol live canonicalization, typed boundary narrowing, and protected thin-shell no-backflow truth.
- Phase 91 verification requires both focused runtime/protocol tests and governance-route/file-matrix proofs before the next phase can start.


## Phase 92 Testing Freeze

- `tests/meta/test_phase92_redaction_convergence_guards.py` 现在冻结 shared redaction registry、value-level redaction budget 协调，以及 touched thin-shell roots 的 no-regrowth truth。
- `tests/core/api/test_api_status_service.py`、`tests/core/api/test_api_command_surface_responses.py`、`tests/platforms/test_light_entity_behavior.py` 与 `tests/services/test_services_diagnostics.py` 继续是 thin shell roots；新增 sibling suites 承载 concern-local assertions。
- Phase 92 verification requires focused redaction/unit tests、topicized root-suite regressions、`tests/meta`、`scripts/check_file_matrix.py --check`、`ruff` 与 `mypy` 一起通过，之后 current route 才能前推到 `Phase 93`。


## Phase 93 Testing Freeze

- `tests/meta/test_phase31_runtime_budget_guards.py` 继续冻结 repo-wide typing-budget honesty；Phase 93 在不放宽预算的前提下烧尽 diagnostics topicization 带来的 incidental `Any` drift。
- `FILE_MATRIX.md`、`TESTING.md`、`VERIFICATION_MATRIX.md` 与 route smoke tests 现在共同构成 assurance freeze proof；任何一个投影滞后都视为 current-route regression，而不是“文档小问题”。
- Phase 93 verification requires focused diagnostics/test-budget regressions、`tests/meta`、`scripts/check_file_matrix.py --check`、`ruff` 与 `mypy` 一起通过，之后 `$gsd-next` 的自然落点才允许前推到 milestone closeout。

## Phase 96 Testing Freeze

- `tests/meta/test_phase96_sanitizer_burndown_guards.py` 现在冻结 diagnostics / telemetry / anonymous-share sanitizer hotspot 的 no-regrowth truth，并要求 `96-VERIFICATION.md` / `96-VALIDATION.md` 与 file/dependency truth 同步前推到 `Phase 97 planning-ready`。
- `tests/core/test_diagnostics_redaction.py`、`tests/integration/test_telemetry_exporter_integration.py` 与 `tests/core/anonymous_share/test_sanitize.py` / `test_manager_submission.py` 共同构成 Phase 96 focused proof；sanitizer helper 粒度变化不得绕开这些本地 suites。
- Phase 96 verification requires focused diagnostics / telemetry / anonymous-share tests、focused meta guard、`tests/meta`、`scripts/check_file_matrix.py --check`、`ruff` 与 `mypy` 一起通过，之后 current route 才能前推到 `Phase 97`。

## Phase 97 Testing Freeze

- `tests/meta/test_phase97_governance_assurance_freeze_guards.py` 继续冻结 `v1.26` archived closeout bundle、historical closeout marker、developer-architecture phase note 与 latest archived pointer truth；它不再承担 live current-route guard 身份。
- `tests/meta/test_governance_bootstrap_smoke.py`、`tests/meta/test_governance_route_handoff_smoke.py` 与 `tests/meta/governance_followup_route_current_milestones.py` 共同保证 `Phase 97` archived truth 仍可被 pull，而不会被 `v1.28` archived-only route 反向污染。
- Phase 97 historical-closeout verification requires focused governance guards、`tests/meta`、`scripts/check_file_matrix.py --check`、`ruff` 与 `mypy` 一起通过，之后 `v1.26` latest archived baseline 才算稳定可拉取。

## Phase 98 Testing Freeze

- `tests/meta/test_phase98_route_reactivation_guards.py` 继续冻结 predecessor reactivation、developer-architecture predecessor note、matrix/testing counts 与 `Phase 98` bundle / next-step truth；`$gsd-next` 的自然落点必须稳定收口到 `$gsd-new-milestone`。
- `tests/meta/test_governance_route_handoff_smoke.py`、`tests/meta/governance_followup_route_current_milestones.py`、`tests/meta/test_phase97_governance_assurance_freeze_guards.py` 与 `tests/meta/test_phase102_governance_portability_guards.py` 共同保证 archived-only prose、machine contract、historical archived truth 与 hotspot freeze notes 不再分叉。
- Phase 98 verification requires focused governance guards、`tests/meta`、`scripts/check_file_matrix.py --check`、`ruff` 与 `mypy` 一起通过，之后 `v1.28` latest archived baseline 才保持 pull-only 稳定。

## Phase 103 Testing Freeze

- `tests/meta/test_phase103_root_thinning_guards.py` now freezes predecessor visibility for root-adapter thinning, test-topology second pass, and terminology-contract projection under the current `v1.30 active route / Phase 110 complete / latest archived baseline = v1.29`.
- Phase 103 proof must remain visible after Phase 107 completion; it is no longer the active-route selector.

## Phase 104 Testing Freeze

- `tests/meta/test_phase104_service_router_runtime_split_guards.py` now freezes predecessor visibility for the `service_router_handlers.py` family split, `command_runtime_outcome_support.py` extraction, and governance projection under the current `v1.30 active route / Phase 110 complete / latest archived baseline = v1.29`.
- Phase 104 verification remains required as a completed predecessor bundle; active-route freeze has moved to `tests/meta/test_phase107_rest_status_hotspot_guards.py`.

## Phase 123 Testing Freeze

- `tests/meta/test_phase123_service_router_reconvergence_guards.py` now freezes the current closeout truth for service-router family reconvergence, file-matrix projection, and control-plane locality tightening under the active `v1.35 / Phase 123 complete` route.
- Reconvergence does not erase predecessor history: `tests/meta/test_phase104_service_router_runtime_split_guards.py` continues to freeze historical visibility for the Phase 104 split, while Phase 123 owns the live no-regrowth contract.

## Phase 110 Testing Freeze

- `tests/meta/test_phase110_runtime_snapshot_closeout_guards.py` now freezes phase110 current-route ownership, snapshot inward-helper topology, and v1.30 closeout evidence-chain pointers.
- `tests/core/test_device_refresh_snapshot.py`, `tests/core/coordinator/runtime/test_device_runtime.py`, and `tests/core/coordinator/runtime/test_snapshot_support.py` remain the focused regression chain for snapshot/runtime behavior after helper extraction.
- Phase 110 verification requires focused runtime/meta suites, `check_file_matrix`, `check_markdown_links`, `ruff`, `mypy`, and `gsd-tools` state/progress/phase-plan-index honesty before handing off to `$gsd-complete-milestone v1.30`.

## Phase 109 Testing Freeze

- `tests/meta/test_phase109_anonymous_share_manager_inward_decomposition_guards.py` now freezes predecessor visibility for anonymous-share manager inward decomposition, route projection, and governance convergence.
- `tests/core/anonymous_share/test_manager_scope_views.py`, `tests/core/anonymous_share/test_manager_recording.py`, `tests/core/anonymous_share/test_manager_submission.py`, `tests/core/anonymous_share/test_observability.py`, and `tests/services/test_services_share.py` remain the focused regression chain for the hotspot families touched in Phase 109.
- Phase 109 verification requires focused anonymous-share/meta suites, `check_file_matrix`, `ruff`, `mypy`, and `gsd-tools` state/progress/phase-plan-index proof before handing off to `$gsd-complete-milestone v1.30`.

## Phase 108 Testing Freeze

- `tests/meta/test_phase108_mqtt_transport_de_friendization_guards.py` now freezes predecessor visibility for explicit MQTT runtime owner/state contract, transport/runtime de-friendization, and governance projection.
- `tests/core/mqtt/test_transport_refactored.py`, `tests/core/mqtt/test_transport_runtime_lifecycle.py`, `tests/core/mqtt/test_transport_runtime_connection_loop.py`, `tests/core/mqtt/test_transport_runtime_ingress.py`, `tests/core/mqtt/test_transport_runtime_subscriptions.py`, and `tests/core/mqtt/test_connection_manager.py` remain the focused regression chain for the hotspot families touched in Phase 108.
- Phase 108 verification requires focused MQTT/meta suites, `check_file_matrix`, `ruff`, `mypy`, and `gsd-tools` state/progress/phase-plan-index proof before handing off to `$gsd-complete-milestone v1.30`.

## Phase 107 Testing Freeze

- `tests/meta/test_phase107_rest_status_hotspot_guards.py` now freezes predecessor visibility for REST child-façade assembly convergence, status fallback helper decomposition, request-policy pacing-cache localization, and governance projection.
- `tests/core/api/test_api.py`, `tests/core/api/test_api_status_service_fallback.py`, and `tests/core/api/test_api_request_policy.py` remain the focused regression chain for the three hotspot families touched in Phase 107.
- Phase 107 verification requires focused API/meta suites, predecessor-visibility proof, `check_file_matrix`, `ruff`, `mypy`, and `gsd-tools` honesty before the current route continues toward `$gsd-complete-milestone v1.30`.

## Phase 105 Testing Freeze

- `tests/meta/test_phase105_governance_freeze_guards.py` now freezes the latest archived `v1.29` closeout route, governance rule datafication, promoted closeout bundle, and archived handoff visibility under current `v1.30 active route / Phase 110 complete / latest archived baseline = v1.29`.
- `tests/meta/governance_followup_route_specs.py` centralizes repeated current-milestone / closeout / continuation case data, while `tests/meta/test_governance_route_handoff_smoke.py` keeps parser-stable GSD fast-path coverage honest.
- Phase 105 verification remains required as latest-archived closeout proof before the current route is allowed to continue.

## Phase 102 Testing Freeze

- `tests/meta/test_phase102_governance_portability_guards.py` 继续冻结 archived `v1.28` predecessor bundle、promoted closeout package、docs-first continuity wording 与 residual/kill-ledger honesty。
- `tests/meta/test_governance_bootstrap_smoke.py`、`tests/meta/test_governance_route_handoff_smoke.py` 与 `tests/meta/governance_followup_route_current_milestones.py` 共同保证 capability-aware gsd fast-path、machine-readable contract 与 latest archived pointer 不再分叉。
- Phase 102 verification requires focused governance/docs/archive guards、`tests/meta`、`scripts/check_file_matrix.py --check`、`ruff` 与 `mypy` 一起通过，之后 `$gsd-next` 的自然落点才允许稳定收口到 `$gsd-new-milestone`。

## Phase 113 Testing Freeze

- `tests/meta/test_phase113_hotspot_assurance_guards.py` now freezes the Phase 113 hotspot line-budget registry and helper-import locality as historical evidence.
- `tests/meta/test_changed_surface_assurance_guards.py` now freezes the live `scripts/lint` changed-surface assurance contract without routing through a phase-labeled guard home.
- `tests/core/test_share_client_submit.py` and `tests/core/test_command_result.py` remain the focused regression chain for the two low-blast-radius hotspot decompositions completed in this phase; `tests/meta/toolchain_truth_ci_contract.py`, `tests/meta/test_governance_release_docs.py`, and `tests/meta/toolchain_truth_docs_fast_path.py` keep the default-lint tooling/docs story honest when those surfaces move.
- Phase 113 verification requires focused submit/command/meta suites, docs/toolchain fast-path guards when docs change, `scripts/check_file_matrix.py --check`, `ruff`, and governance handoff smoke before the current route advances to `Phase 114`.

## Phase 114 Testing Freeze

- `tests/meta/test_phase114_open_source_surface_honesty_guards.py` now freezes the access-mode/private-fallback truth, schema-limited metadata projection registry, debug-mode-only developer-service disclosure, privacy terminology, and default `scripts/lint` changed-surface help contract.
- `tests/meta/test_governance_release_continuity.py`, `tests/meta/test_version_sync.py`, and `tests/meta/toolchain_truth_docs_fast_path.py` remain the focused continuity/metadata proof chain for docs-first routes, package metadata, issue contact links, and machine-readable governance truth touched in Phase 114.
- Phase 114 verification requires the focused Phase 114/meta suites plus `scripts/check_file_matrix.py --check`, `ruff`, and governance handoff smoke before the current route may close to milestone completion.
