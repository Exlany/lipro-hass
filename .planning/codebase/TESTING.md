# Testing Patterns

**Analysis Date:** 2026-03-28

> Snapshot: `2026-03-28`
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

## Test File Organization

**Location:**
- Tests live in a dedicated `tests/` tree, not beside production files.
- Current topology is broad and intentional: `tests/core`, `tests/services`, `tests/flows`, `tests/platforms`, `tests/entities`, `tests/meta`, `tests/integration`, `tests/snapshots`, `tests/benchmarks`, `tests/harness`, and `tests/fixtures`.
- Repository counts from current scanning: `394` Python files under `tests`, `314` runnable `test_*.py` files, `59` meta suites, `5` integration suites, `4` snapshot suites, `4` benchmark suites, and `5` fixture family READMEs.

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

## Historical Phase Notes

- Phase 55: 当前仓库共有 `311` 个 `test_*.py` 文件，topicized thin shells 继续覆盖 command-surface、transport-runtime 与 light/fan/select/switch suites。
- Phase 59: `tests/core/test_device_refresh_{parsing,filter,snapshot,runtime}.py` 继续作为 localized device-refresh verification note；topicized meta note carriers 与 verification anchors 保持分离。
- Phase 88: `tests/meta/test_phase88_governance_quality_freeze_guards.py` 继续作为 focused guard home for phase-88 governance/evidence freeze。
- Phase 90: `tests/meta/test_phase90_hotspot_map_guards.py` 继续作为 focused guard home for five formal homes / four protected thin shells / delete-gate freeze truth。
- Phase 96: `tests/meta/test_phase96_sanitizer_burndown_guards.py` 继续作为 focused guard home for diagnostics/telemetry/anonymous-share sanitizer burn-down truth。
- Phase 97: `tests/meta/test_phase97_governance_assurance_freeze_guards.py` 继续作为 focused guard home for v1.26 archived closeout bundle / developer-architecture historical note truth。
- Phase 98: `tests/meta/test_phase98_route_reactivation_guards.py` 继续作为 focused guard home for predecessor route-reactivation / carry-forward closure truth。
- Phase 99: `tests/meta/test_phase99_runtime_hotspot_support_guards.py` 继续作为 focused predecessor guard home for runtime hotspot support extraction / governance freeze truth。
- Phase 100: `tests/meta/test_phase100_runtime_schedule_support_guards.py` 继续作为 focused predecessor guard home for MQTT/runtime schedule support extraction / governance freeze truth。
- Phase 101: `tests/meta/test_phase101_anonymous_share_rest_boundary_guards.py` 继续作为 focused current-route guard home for anonymous-share manager / REST-boundary hotspot decomposition truth。

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
- Keep async tests as plain `async def test_*` functions; current scanning finds `841` async tests, matching the repo's async integration style.
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
- `scripts/lint` is the closest local umbrella entrypoint; default mode skips pytest/governance, while `--full` mirrors the heavy CI path.

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

- `pytest.raises` appears heavily across the suite; current grep count is `211` occurrences.
- Parametrization is used, but selectively (`46` occurrences), so new table-driven coverage should usually land in targeted concern files rather than giant omnibus tests.

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
- `tests/meta/test_governance_bootstrap_smoke.py`、`tests/meta/test_governance_route_handoff_smoke.py` 与 `tests/meta/governance_followup_route_current_milestones.py` 共同保证 `Phase 97` archived truth 仍可被 pull，而不会被 `v1.27` current route 反向污染。
- Phase 97 historical-closeout verification requires focused governance guards、`tests/meta`、`scripts/check_file_matrix.py --check`、`ruff` 与 `mypy` 一起通过，之后 `v1.26` latest archived baseline 才算稳定可拉取。

## Phase 98 Testing Freeze

- `tests/meta/test_phase98_route_reactivation_guards.py` 继续冻结 current-route reactivation、developer-architecture current note、matrix/testing counts 与 `Phase 98` bundle / next-step truth；`$gsd-next` 的自然落点必须稳定收口到 `$gsd-new-milestone`。
- `tests/meta/test_governance_route_handoff_smoke.py`、`tests/meta/governance_followup_route_current_milestones.py`、`tests/meta/test_phase97_governance_assurance_freeze_guards.py` 与 `tests/meta/test_phase90_hotspot_map_guards.py` 共同保证 current-route prose、machine contract、historical archived truth 与 hotspot freeze notes 不再分叉。
- Phase 98 verification requires focused governance guards、`tests/meta`、`scripts/check_file_matrix.py --check`、`ruff` 与 `mypy` 一起通过，之后 current route 才允许进入 milestone archive/closeout。
