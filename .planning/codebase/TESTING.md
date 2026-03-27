# Testing Patterns

**Analysis Date:** 2026-03-27

> Snapshot: `2026-03-27`
> Freshness: 基于 `tests/**`、`pyproject.toml`、`.github/workflows/{ci,release}.yml`、`scripts/{lint,check_architecture_policy.py,check_file_matrix.py}` 与 `.planning/baseline/VERIFICATION_MATRIX.md` 的当前截面。
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
uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing
./scripts/lint --full
```

## Test File Organization

**Location:**
- Tests live in a dedicated `tests/` tree, not beside production files.
- Current topology is broad and intentional: `tests/core`, `tests/services`, `tests/flows`, `tests/platforms`, `tests/entities`, `tests/meta`, `tests/integration`, `tests/snapshots`, `tests/benchmarks`, `tests/harness`, and `tests/fixtures`.
- Repository counts from current scanning: `367` Python files under `tests`, `291` runnable `test_*.py` files, `48` meta suites, `5` integration suites, `4` snapshot suites, `4` benchmark suites, and `5` fixture family READMEs.

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
- Keep async tests as plain `async def test_*` functions; current scanning finds `367` async tests, matching the repo's async integration style.
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
- `lint` runs Ruff, formatter check, mypy, translations, and shellcheck from `.github/workflows/ci.yml`.
- `governance` runs `scripts/check_architecture_policy.py`, `scripts/check_file_matrix.py`, and focused `tests/meta` guards.
- `security` exports runtime requirements and runs blocking runtime `pip-audit`; dev-environment audit is advisory only on scheduled/manual runs.
- `test` runs the full non-benchmark suite with coverage, changed-surface coverage checks, and `scripts/refactor_tools.py`.
- `benchmark` and `compatibility_preview` are schedule/manual-only lanes.
- `release` reuses `ci.yml` first, then adds tagged security, CodeQL, smoke install, SBOM, attestation, signing, and signature verification in `.github/workflows/release.yml`.

**Pre-commit / local gates:**
- `.pre-commit-config.yaml` mirrors the same contract family with local Ruff, mypy, translations, architecture/file-matrix scripts, focused diagnostics tests, and governance guards.
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

- `pytest.raises` appears heavily across the suite; current grep count is `208` occurrences.
- Parametrization is used, but selectively (`46` occurrences), so new table-driven coverage should usually land in targeted concern files rather than giant omnibus tests.

## Recommendations

- Prefer adding new assertions to concern-local sibling suites instead of enlarging current hotspots such as `tests/conftest.py`, `tests/core/test_auth.py`, `tests/core/api/test_api_status_service.py`, `tests/platforms/test_light_entity_behavior.py`, or `tests/services/test_services_diagnostics.py`.
- When changing workflows, docs routes, release semantics, or governance truth, add or update `tests/meta/*` in the same patch; this repo treats docs and CI contracts as testable behavior.
- When changing protocol payloads or replay behavior, update the owning fixture README and the fixture-backed tests together so authority stays explicit.
- Keep benchmark edits inside `tests/benchmarks` plus `benchmark_baselines.json`; do not mix performance-only assertions into the main blocking suite unless the behavior is a correctness concern.

---

*Testing analysis: 2026-03-27*
