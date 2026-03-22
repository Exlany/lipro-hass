"""CI, pre-push, lint, and pytest-lane contract guards."""

from __future__ import annotations

from pathlib import Path
import tomllib

import yaml

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))

_PYPROJECT = _ROOT / "pyproject.toml"

_PRE_COMMIT = _ROOT / ".pre-commit-config.yaml"

_CI_WORKFLOW = _ROOT / ".github" / "workflows" / "ci.yml"

_UPLOAD_ARTIFACT = "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"

_LINT_SCRIPT = _ROOT / "scripts" / "lint"



def _load_pyproject():
    return tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))



def _load_yaml(path: Path):
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    if True in loaded and "on" not in loaded:
        loaded["on"] = loaded.pop(True)
    return loaded



def test_pre_push_contract_runs_translation_and_governance_truth_early() -> None:
    """Local pre-push should surface the same translation/governance drift CI blocks on."""
    pre_commit = _load_yaml(_PRE_COMMIT)
    hooks = pre_commit["repos"][0]["hooks"]
    hook_by_id = {hook["id"]: hook for hook in hooks}

    assert (
        hook_by_id["translations-truth"]["entry"]
        == "uv run --extra dev python scripts/check_translations.py"
    )
    assert (
        hook_by_id["architecture-policy"]["entry"]
        == "uv run --extra dev python scripts/check_architecture_policy.py --check"
    )
    assert (
        hook_by_id["file-matrix"]["entry"]
        == "uv run --extra dev python scripts/check_file_matrix.py --check"
    )
    assert (
        "tests/meta/test_governance*.py"
        in hook_by_id["pytest-governance-gate"]["entry"]
    )
    assert (
        "tests/meta/test_toolchain_truth.py"
        in hook_by_id["pytest-governance-gate"]["entry"]
    )



def test_ci_test_and_benchmark_lanes_keep_one_snapshot_story() -> None:
    """CI should avoid duplicate snapshot cost and keep benchmark evidence governed."""
    ci = _load_yaml(_CI_WORKFLOW)

    test_steps = ci["jobs"]["test"]["steps"]
    test_step_names = {step["name"] for step in test_steps}
    assert "Run snapshot tests" not in test_step_names
    assert "Resolve changed coverage surface" in test_step_names
    contract_step = next(
        step for step in test_steps if step.get("name") == "Record test lane contract"
    )
    assert "snapshot coverage: included in the main tests/ lane" in contract_step["run"]
    assert (
        "coverage gates: total floor is blocking; changed measured files must meet the changed-surface floor; explicit baseline diff remains opt-in"
        in contract_step["run"]
    )

    coverage_step = next(
        step
        for step in test_steps
        if step.get("name") == "Check total + changed-surface coverage gates"
    )
    assert (
        "uv run python scripts/coverage_diff.py coverage.json" in coverage_step["run"]
    )
    assert "--changed-files .coverage-changed-files" in coverage_step["run"]
    assert "--changed-minimum 95" in coverage_step["run"]
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

    benchmark_steps = ci["jobs"]["benchmark"]["steps"]
    benchmark_run = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Run benchmark suite"
    )
    assert benchmark_run.get("continue-on-error") in (None, False)
    assert benchmark_run["id"] == "benchmark_run"
    assert "--benchmark-json=.benchmarks/benchmark.json" in benchmark_run["run"]

    upload_step = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Upload benchmark artifact"
    )
    assert upload_step["uses"] == _UPLOAD_ARTIFACT
    assert upload_step["with"]["path"] == ".benchmarks/benchmark.json"

    compare_step = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Compare benchmark results against baseline manifest"
    )
    assert "scripts/check_benchmark_baseline.py" in compare_step["run"]
    assert "tests/benchmarks/benchmark_baselines.json" in compare_step["run"]

    summary_step = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Record benchmark governed posture"
    )
    assert "threshold warning" in summary_step["run"]
    assert "no-regression gate" in summary_step["run"]
    assert "steps.benchmark_run.outcome" in summary_step["run"]
    assert "steps.benchmark_contract.outcome" in summary_step["run"]

    benchmark_script = (_ROOT / "scripts" / "check_benchmark_baseline.py").read_text(
        encoding="utf-8"
    )
    assert "Benchmark contract: warnings only" in benchmark_script
    assert "blocking regression" in benchmark_script



def test_scripts_lint_full_mode_matches_ci_coverage_contract() -> None:
    lint_text = _LINT_SCRIPT.read_text(encoding="utf-8")

    assert "total + changed-surface coverage" in lint_text
    assert "resolve_changed_coverage_surface" in lint_text
    assert '--changed-files "$tmp_changed_coverage_surface"' in lint_text
    assert "--changed-minimum 95" in lint_text



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
