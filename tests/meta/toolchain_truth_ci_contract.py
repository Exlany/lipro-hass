"""CI, pre-push, lint, and pytest-lane contract guards."""

from __future__ import annotations

from pathlib import Path
import tomllib

from tests.helpers.repo_root import repo_root

from .conftest import _as_mapping, _as_mapping_list, _as_str, _load_yaml

_ROOT = repo_root(Path(__file__))

_PYPROJECT = _ROOT / "pyproject.toml"
_PRE_COMMIT = _ROOT / ".pre-commit-config.yaml"
_CI_WORKFLOW = _ROOT / ".github" / "workflows" / "ci.yml"
_CONTRIBUTING = _ROOT / "CONTRIBUTING.md"
_LINT_SCRIPT = _ROOT / "scripts" / "lint"

_UPLOAD_ARTIFACT = "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
_GOVERNANCE_GUARD_TESTS = (
    "tests/meta/test_dependency_guards.py",
    "tests/meta/test_public_surface_guards.py",
    "tests/meta/test_governance*.py",
    "tests/meta/test_toolchain_truth.py",
    "tests/meta/test_version_sync.py",
)
_DIAGNOSTICS_PRE_PUSH_TESTS = (
    "tests/core/test_diagnostics_config_entry.py::TestAsyncGetConfigEntryDiagnostics::test_collects_and_redacts_diagnostics",
    "tests/core/test_diagnostics_config_entry.py::TestAsyncGetConfigEntryDiagnostics::test_handles_no_devices",
    "tests/core/test_diagnostics_config_entry.py::TestAsyncGetConfigEntryDiagnostics::test_diagnostics_snapshot",
)
_CHANGED_SURFACE_COMMAND = (
    'git diff --name-only --diff-filter=AMRT "$(git merge-base origin/main HEAD)...HEAD" > .coverage-changed-files'
)
_COVERAGE_GATES_COMMAND = (
    "uv run python scripts/coverage_diff.py coverage.json --minimum 95 --changed-files .coverage-changed-files --changed-minimum 95"
)


def _load_pyproject() -> dict[str, object]:
    return tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))



def _assert_tokens(text: str, tokens: tuple[str, ...]) -> None:
    for token in tokens:
        assert token in text



def test_pre_push_contract_runs_translation_and_governance_truth_early() -> None:
    """Local pre-push should mirror the focused truth gates CI relies on."""
    pre_commit = _load_yaml(_PRE_COMMIT)
    repos = _as_mapping_list(pre_commit["repos"])
    hooks = _as_mapping_list(repos[0]["hooks"])
    hook_by_id = {_as_str(hook["id"]): hook for hook in hooks}

    assert (
        _as_str(hook_by_id["translations-truth"]["entry"])
        == "uv run --extra dev python scripts/check_translations.py"
    )
    assert (
        _as_str(hook_by_id["markdown-links"]["entry"])
        == "uv run --extra dev python scripts/check_markdown_links.py"
    )
    assert (
        _as_str(hook_by_id["architecture-policy"]["entry"])
        == "uv run --extra dev python scripts/check_architecture_policy.py --check"
    )
    assert (
        _as_str(hook_by_id["file-matrix"]["entry"])
        == "uv run --extra dev python scripts/check_file_matrix.py --check"
    )

    diagnostics_entry = _as_str(hook_by_id["pytest-gate"]["entry"])
    assert "uv run --extra dev pytest -q -x" in diagnostics_entry
    _assert_tokens(diagnostics_entry, _DIAGNOSTICS_PRE_PUSH_TESTS)
    assert "tests/core/test_diagnostics.py::" not in diagnostics_entry

    governance_entry = _as_str(hook_by_id["pytest-governance-gate"]["entry"])
    assert "uv run --extra dev pytest -q -x" in governance_entry
    _assert_tokens(governance_entry, _GOVERNANCE_GUARD_TESTS)



def test_ci_governance_lane_records_same_focused_truths() -> None:
    """CI governance lane should publish the same checker and pytest story local flows mirror."""
    ci = _load_yaml(_CI_WORKFLOW)
    ci_jobs = _as_mapping(ci["jobs"])
    governance_job = _as_mapping(ci_jobs["governance"])
    governance_steps = _as_mapping_list(governance_job["steps"])

    architecture_step = next(
        step for step in governance_steps if step.get("name") == "Check architecture policy"
    )
    assert _as_str(architecture_step["run"]) == "uv run python scripts/check_architecture_policy.py --check"

    file_matrix_step = next(
        step
        for step in governance_steps
        if step.get("name") == "Check file matrix and active authority docs"
    )
    assert _as_str(file_matrix_step["run"]) == "uv run python scripts/check_file_matrix.py --check"

    governance_pytest_step = next(
        step
        for step in governance_steps
        if step.get("name") == "Run governance and architecture guards"
    )
    governance_pytest_run = _as_str(governance_pytest_step["run"])
    assert "uv run pytest -q -x" in governance_pytest_run
    _assert_tokens(governance_pytest_run, _GOVERNANCE_GUARD_TESTS)

    contract_step = next(
        step for step in governance_steps if step.get("name") == "Record governance lane contract"
    )
    contract_run = _as_str(contract_step["run"])
    assert "governance checker roots:" in contract_run
    assert "governance pytest suite:" in contract_run
    assert "./scripts/lint --full reuses the same focused guard list" in contract_run



def test_ci_lint_lane_runs_docs_route_checker() -> None:
    ci = _load_yaml(_CI_WORKFLOW)
    ci_jobs = _as_mapping(ci["jobs"])
    lint_job = _as_mapping(ci_jobs["lint"])
    lint_steps = _as_mapping_list(lint_job["steps"])

    markdown_step = next(
        step for step in lint_steps if step.get("name") == "Check markdown docs links"
    )
    assert _as_str(markdown_step["run"]) == "uv run python scripts/check_markdown_links.py"


def test_ci_test_and_benchmark_lanes_keep_one_snapshot_story() -> None:
    """CI should avoid duplicate snapshot cost and keep benchmark evidence governed."""
    ci = _load_yaml(_CI_WORKFLOW)

    ci_jobs = _as_mapping(ci["jobs"])
    test_job = _as_mapping(ci_jobs["test"])
    test_steps = _as_mapping_list(test_job["steps"])
    test_step_names = {_as_str(step["name"]) for step in test_steps}
    assert "Run snapshot tests" not in test_step_names
    assert "Resolve changed coverage surface" in test_step_names
    contract_step = next(
        step for step in test_steps if step.get("name") == "Record test lane contract"
    )
    contract_run = _as_str(contract_step["run"])
    assert "snapshot coverage: included in the main tests/ lane" in contract_run
    assert (
        "coverage gates: total floor is blocking; changed measured files must meet the changed-surface floor; explicit baseline diff remains opt-in"
        in contract_run
    )

    coverage_step = next(
        step
        for step in test_steps
        if step.get("name") == "Check total + changed-surface coverage gates"
    )
    coverage_run = _as_str(coverage_step["run"])
    assert "uv run python scripts/coverage_diff.py coverage.json" in coverage_run
    assert "--changed-files .coverage-changed-files" in coverage_run
    assert "--changed-minimum 95" in coverage_run
    coverage_diff_script = (_ROOT / "scripts" / "coverage_diff.py").read_text(
        encoding="utf-8"
    )
    assert (
        "Changed-surface coverage: skipped (no changed file list provided)"
        in coverage_diff_script
    )
    assert (
        "Changed-surface coverage: skipped (no measured files in change set)"
        in coverage_diff_script
    )

    benchmark_job = _as_mapping(ci_jobs["benchmark"])
    benchmark_steps = _as_mapping_list(benchmark_job["steps"])
    benchmark_run = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Run benchmark suite"
    )
    assert benchmark_run.get("continue-on-error") in (None, False)
    assert _as_str(benchmark_run["id"]) == "benchmark_run"
    assert "--benchmark-json=.benchmarks/benchmark.json" in _as_str(benchmark_run["run"])

    upload_step = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Upload benchmark artifact"
    )
    assert _as_str(upload_step["uses"]) == _UPLOAD_ARTIFACT
    upload_with = _as_mapping(upload_step["with"])
    assert _as_str(upload_with["path"]) == ".benchmarks/benchmark.json"

    compare_step = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Compare benchmark results against baseline manifest"
    )
    compare_run = _as_str(compare_step["run"])
    assert "scripts/check_benchmark_baseline.py" in compare_run
    assert "tests/benchmarks/benchmark_baselines.json" in compare_run

    summary_step = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Record benchmark governed posture"
    )
    summary_run = _as_str(summary_step["run"])
    assert "threshold warning" in summary_run
    assert "no-regression gate" in summary_run
    assert "steps.benchmark_run.outcome" in summary_run
    assert "steps.benchmark_contract.outcome" in summary_run

    benchmark_script = (_ROOT / "scripts" / "check_benchmark_baseline.py").read_text(
        encoding="utf-8"
    )
    assert "Benchmark contract: warnings only" in benchmark_script
    assert "blocking regression" in benchmark_script



def test_scripts_lint_full_mode_matches_ci_coverage_contract() -> None:
    lint_text = _LINT_SCRIPT.read_text(encoding="utf-8")

    assert "governance_guard_tests=(" in lint_text
    assert 'uv run pytest -q -x "${governance_guard_tests[@]}"' in lint_text
    _assert_tokens(lint_text, _GOVERNANCE_GUARD_TESTS)
    assert "total + changed-surface coverage" in lint_text
    assert "resolve_changed_coverage_surface" in lint_text
    assert '--changed-files "$tmp_changed_coverage_surface"' in lint_text
    assert "--changed-minimum 95" in lint_text



def test_contributing_docs_keep_command_manifest_in_sync() -> None:
    docs_text = _CONTRIBUTING.read_text(encoding="utf-8")

    assert "**pre-push**:" in docs_text
    assert "uv run python scripts/check_markdown_links.py" in docs_text
    assert "uv run --extra dev python scripts/check_markdown_links.py" in docs_text
    assert "uv run --extra dev python scripts/check_file_matrix.py --check" in docs_text
    assert "uv run --extra dev pytest -q -x tests/core/test_diagnostics_config_entry.py::TestAsyncGetConfigEntryDiagnostics::test_collects_and_redacts_diagnostics" in docs_text
    assert "uv run --extra dev pytest -q -x tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py" in docs_text
    assert _CHANGED_SURFACE_COMMAND in docs_text
    assert _COVERAGE_GATES_COMMAND in docs_text
    assert "tests/core/test_diagnostics.py::TestAsyncGetConfigEntryDiagnostics" not in docs_text



def test_pytest_marker_contract_has_no_dead_declarations() -> None:
    """Only live pytest markers should remain declared in pyproject."""
    pyproject = _load_pyproject()
    tool = pyproject["tool"]
    assert isinstance(tool, dict)
    pytest_table = tool["pytest"]
    assert isinstance(pytest_table, dict)
    pytest_options = pytest_table["ini_options"]
    assert isinstance(pytest_options, dict)
    assert "markers" not in pytest_options
