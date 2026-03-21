"""Toolchain truth and local DX contract guards."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tomllib
from typing import Any

import yaml

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_PYPROJECT = _ROOT / "pyproject.toml"
_PRE_COMMIT = _ROOT / ".pre-commit-config.yaml"
_DEVCONTAINER = _ROOT / ".devcontainer.json"
_CI_WORKFLOW = _ROOT / ".github" / "workflows" / "ci.yml"
_RELEASE_WORKFLOW = _ROOT / ".github" / "workflows" / "release.yml"
_CODEQL_WORKFLOW = _ROOT / ".github" / "workflows" / "codeql.yml"
_DEVELOP_SCRIPT = _ROOT / "scripts" / "develop"
_LINT_SCRIPT = _ROOT / "scripts" / "lint"
_SETUP_PYTHON = "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405"
_UPLOAD_ARTIFACT = "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
_README = _ROOT / "README.md"
_README_ZH = _ROOT / "README_zh.md"
_SUPPORT = _ROOT / "SUPPORT.md"
_SECURITY = _ROOT / "SECURITY.md"
_TROUBLESHOOTING = _ROOT / "docs" / "TROUBLESHOOTING.md"
_RUNBOOK = _ROOT / "docs" / "MAINTAINER_RELEASE_RUNBOOK.md"
_DOCS_README = _ROOT / "docs" / "README.md"
_GOVERNANCE_REGISTRY = _ROOT / ".planning" / "baseline" / "GOVERNANCE_REGISTRY.json"
_CODEBASE_DIR = _ROOT / ".planning" / "codebase"
_ADR_README = _ROOT / "docs" / "adr" / "README.md"
_ADR_0004 = _ROOT / "docs" / "adr" / "0004-explicit-lightweight-boundaries.md"
_PUBLIC_SURFACES = _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
_DEPENDENCY_MATRIX = _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
_RESIDUAL_LEDGER = _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"

_TESTING_MAP = _ROOT / ".planning" / "codebase" / "TESTING.md"
_TESTING_COUNTS_RE = re.compile(
    r"当前仓库共有 `(?P<total>\d+)` 个 `test_\*\.py` 文件；其中 `(?P<meta>\d+)` 个 meta guard、`(?P<integration>\d+)` 个 integration、`(?P<benchmark>\d+)` 个 benchmark、`(?P<snapshot>\d+)` 个 snapshot 文件；另有 `(?P<fixture_readmes>\d+)` 个 fixture family readme"
)


def _load_pyproject() -> dict[str, Any]:
    return tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    if True in loaded and "on" not in loaded:
        loaded["on"] = loaded.pop(True)
    return loaded


def _load_devcontainer() -> dict[str, Any]:
    loaded = json.loads(_DEVCONTAINER.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _load_governance_registry() -> dict[str, Any]:
    loaded = json.loads(_GOVERNANCE_REGISTRY.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _count_testing_inventory() -> dict[str, int]:
    tests_root = _ROOT / "tests"
    test_files = sorted(tests_root.rglob("test_*.py"))
    fixture_readmes = sorted((tests_root / "fixtures").glob("*/README.md"))
    return {
        "total": len(test_files),
        "meta": sum(
            1 for path in test_files if path.is_relative_to(tests_root / "meta")
        ),
        "integration": sum(
            1 for path in test_files if path.is_relative_to(tests_root / "integration")
        ),
        "benchmark": sum(
            1 for path in test_files if path.is_relative_to(tests_root / "benchmarks")
        ),
        "snapshot": sum(
            1 for path in test_files if path.is_relative_to(tests_root / "snapshots")
        ),
        "fixture_readmes": len(fixture_readmes),
    }


def test_python_toolchain_truth_is_aligned_to_314() -> None:
    """pyproject, pre-commit, devcontainer, and CI should tell one Python story."""
    pyproject = _load_pyproject()
    project = pyproject["project"]
    assert isinstance(project, dict)
    mypy = pyproject["tool"]["mypy"]
    assert isinstance(mypy, dict)
    ruff = pyproject["tool"]["ruff"]
    assert isinstance(ruff, dict)
    pre_commit = _load_yaml(_PRE_COMMIT)
    devcontainer = _load_devcontainer()
    ci = _load_yaml(_CI_WORKFLOW)
    release = _load_yaml(_RELEASE_WORKFLOW)

    assert project["requires-python"] == ">=3.14.2"
    assert mypy["python_version"] == "3.14"
    assert ruff["target-version"] == "py314"
    assert pre_commit["default_language_version"]["python"] == "python3.14"
    assert devcontainer["image"].endswith("python:3.14")

    setup_python_versions: list[str] = []
    for workflow in (ci, release):
        jobs = workflow["jobs"]
        assert isinstance(jobs, dict)
        for job in jobs.values():
            assert isinstance(job, dict)
            steps = job.get("steps", [])
            assert isinstance(steps, list)
            for step in steps:
                if not isinstance(step, dict) or step.get("uses") != _SETUP_PYTHON:
                    continue
                with_block = step.get("with")
                assert isinstance(with_block, dict)
                python_version = with_block.get("python-version")
                assert python_version == "3.14"
                setup_python_versions.append(python_version)

    assert setup_python_versions


def test_release_workflow_keeps_identity_evidence_tools_in_sync() -> None:
    release = _load_yaml(_RELEASE_WORKFLOW)
    codeql = _load_yaml(_CODEQL_WORKFLOW)

    build_job = release["jobs"]["build"]
    steps = build_job["steps"]
    step_names = {step["name"] for step in steps}

    assert "Generate artifact attestation" in step_names
    assert "Verify generated artifact attestations" in step_names
    assert "Write release identity manifest" in step_names
    assert "Install cosign" in step_names
    assert "Sign release assets" in step_names
    assert "Verify release signatures" in step_names

    codeql_on = codeql["on"]
    assert isinstance(codeql_on, dict)
    assert "workflow_dispatch" in codeql_on
    assert "push" in codeql_on
    assert "v*" in codeql_on["push"]["tags"]
    assert codeql["permissions"]["security-events"] == "write"
    analyze_job = codeql["jobs"]["analyze"]
    analyze_step_names = {step["name"] for step in analyze_job["steps"]}
    assert "Initialize CodeQL" in analyze_step_names
    assert "Perform CodeQL Analysis" in analyze_step_names


def test_release_identity_manifest_keeps_current_trust_stack_explicit() -> None:
    release = _load_yaml(_RELEASE_WORKFLOW)
    build_job = release["jobs"]["build"]
    steps = build_job["steps"]
    assert isinstance(steps, list)

    manifest_step = next(
        step
        for step in steps
        if isinstance(step, dict)
        and step.get("name") == "Write release identity manifest"
    )
    run_block = manifest_step["run"]
    assert isinstance(run_block, str)

    for token in (
        "identity_evidence=SHA256SUMS",
        "identity_evidence=SBOM",
        "identity_evidence=GitHub artifact attestation",
        "identity_evidence=cosign keyless signature bundle",
        "provenance=GitHub artifact attestation",
        "identity_verification=gh attestation verify",
        "signing=cosign keyless sign-blob",
        "signing_verification=cosign verify-blob --bundle",
        "code_scanning=GitHub CodeQL hard gate",
        "code_scanning_verification=tagged ref analysis required + zero open alerts",
    ):
        assert token in run_block


def test_bilingual_readmes_capture_release_asset_identity_truth() -> None:
    readme_text = _README.read_text(encoding="utf-8")
    readme_zh_text = _README_ZH.read_text(encoding="utf-8")

    for text in (readme_text, readme_zh_text):
        for token in (
            "SHA256SUMS",
            "SBOM",
            "attestation",
            "provenance",
            "cosign",
            "CodeQL",
        ):
            assert token in text

    assert "Contributor Fast Path" in readme_text
    assert "docs/README.md" in readme_text
    assert "贡献快速路径" in readme_zh_text
    assert "docs/README.md" in readme_zh_text
    assert "single-maintainer model" not in readme_text
    assert "单维护者模型" not in readme_zh_text


def test_active_docs_keep_facade_era_terminology_quarantining_legacy_terms() -> None:
    active_docs = {
        _ADR_README: (
            "Entity / Service / Runtime / Client",
            "API Client 去 mixin 化",
        ),
        _ADR_0004: (
            "Entity -> Service -> Runtime -> Client",
            "`API Client`",
            "mixin 聚合",
        ),
        _PUBLIC_SURFACES: (
            "mixin-based mega client",
            "legacy `client` seam",
            "pure forwarders",
            "pure forwarder cluster",
        ),
        _DEPENDENCY_MATRIX: (
            "MQTT client",
            "`client`、`entry.runtime_data`",
            "pure forwarders",
        ),
    }

    for path, forbidden_tokens in active_docs.items():
        text = path.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in text, f"{path.as_posix()} still contains {token!r}"

    residual_text = _RESIDUAL_LEDGER.read_text(encoding="utf-8")
    assert "legacy `Client` / `Mixin` / compat symbol 名称" in residual_text
    assert "archive / delete-gate / symbol-identity" in residual_text


def test_docs_index_makes_public_fast_path_and_bilingual_boundary_explicit() -> None:
    docs_text = _DOCS_README.read_text(encoding="utf-8")

    for token in (
        "Public Fast Path",
        "Bilingual Boundary",
        "Maintainer Appendix",
        "README.md",
        "README_zh.md",
        "CONTRIBUTING.md",
        "SUPPORT.md",
        "SECURITY.md",
        "docs/MAINTAINER_RELEASE_RUNBOOK.md",
    ):
        assert token in docs_text


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


def test_testing_map_counts_and_script_boundary_notes_match_repo_facts() -> None:
    """Derived testing map should track current counts and explicit script/test boundary notes."""
    testing_text = _TESTING_MAP.read_text(encoding="utf-8")
    match = _TESTING_COUNTS_RE.search(testing_text)
    assert match is not None

    documented = {key: int(value) for key, value in match.groupdict().items()}
    assert documented == _count_testing_inventory()
    assert "scripts/check_architecture_policy.py" in testing_text
    assert "scripts/export_ai_debug_evidence_pack.py" in testing_text
    assert "tests/core/test_init_service_handlers*.py" in testing_text
    assert "tests/core/test_init_runtime_bootstrap.py" in testing_text
    assert "tests/meta/test_governance_phase_history_runtime.py" in testing_text
    assert "tests/meta/test_governance_phase_history_topology.py" in testing_text
    assert "tests/meta/test_governance_closeout_guards.py" in testing_text
    assert "tests/meta/test_governance_promoted_phase_assets.py" in testing_text
    assert "tests/meta/test_governance_followup_route.py" in testing_text
    assert "tests/meta/test_governance_milestone_archives.py" in testing_text
    assert "helper-only / pull-only" in testing_text
    assert "tests/meta/test_toolchain_truth.py" in testing_text


def test_codebase_maps_publish_snapshot_freshness_and_authority_boundaries() -> None:
    for path in sorted(_CODEBASE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")

        assert "Snapshot:" in text, path.as_posix()
        assert "Freshness:" in text, path.as_posix()
        assert "Derived collaboration map" in text, path.as_posix()

        if path.name == "README.md":
            assert "Authority order:" in text, path.as_posix()
            assert "Conflict rule:" in text, path.as_posix()
            assert "不得自称当前治理真源" in text, path.as_posix()
            continue

        assert "Authority:" in text, path.as_posix()
        assert "不得反向充当当前治理真源" in text, path.as_posix()


def test_deep_docs_keep_single_maintainer_continuity_truth() -> None:
    """Support/security/troubleshooting/runbook should tell one honest continuity story."""
    support_text = _SUPPORT.read_text(encoding="utf-8")
    security_text = _SECURITY.read_text(encoding="utf-8")
    troubleshooting_text = _TROUBLESHOOTING.read_text(encoding="utf-8")
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")

    assert "single-maintainer" in support_text
    assert "single-maintainer" in security_text
    assert "single-maintainer" in runbook_text
    assert "单维护者" in troubleshooting_text
    assert "no documented delegate exists today" in support_text
    assert "Documented delegate: none currently" in security_text
    assert "No documented delegate currently exists" in runbook_text
    assert "没有已记录的 delegate" in troubleshooting_text
    assert "freeze new tagged releases" in security_text
    assert "freeze new tagged releases" in support_text
    assert "new release promises" in support_text
    assert "freeze new tagged releases" in runbook_text
    assert "new release promises" in runbook_text
    assert "freeze new tagged releases" in troubleshooting_text
    assert "new release promises" in troubleshooting_text
    assert "no documented delegate" in support_text
    assert "Documented delegate" in security_text
    assert "No documented delegate" in runbook_text
    assert "custody restoration" in support_text
    assert "Custody restoration" in security_text
    assert "Custody restoration" in runbook_text
    assert "SECURITY.md" in troubleshooting_text
    assert "SUPPORT.md" in troubleshooting_text
    assert "docs/MAINTAINER_RELEASE_RUNBOOK.md" in troubleshooting_text


def test_governance_registry_keeps_continuity_truth_machine_readable() -> None:
    registry = _load_governance_registry()
    support_text = _SUPPORT.read_text(encoding="utf-8")
    security_text = _SECURITY.read_text(encoding="utf-8")
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")

    assert registry["continuity"]["maintainer_model"] == "single-maintainer"
    assert registry["continuity"]["documented_delegate"] is False
    assert registry["docs"]["index_route"] == "docs/README.md"
    assert registry["tooling"]["retired_stub_exit_code"] == 2
    for token in registry["continuity"]["sync_sources"]:
        assert token in {
            "SUPPORT.md",
            "SECURITY.md",
            "docs/MAINTAINER_RELEASE_RUNBOOK.md",
            ".github/CODEOWNERS",
            ".planning/baseline/GOVERNANCE_REGISTRY.json",
        }
    for text in (support_text, security_text, runbook_text):
        assert registry["continuity"]["maintainer_model"] in text
        assert registry["continuity"]["freeze_phrase"] in text


def test_docs_index_and_retired_tooling_contract_are_machine_readable() -> None:
    registry = _load_governance_registry()
    docs_text = (_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    contributing_text = (_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    issue_config = _load_yaml(_ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml")
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    worker_text = (_ROOT / "scripts" / "agent_worker.py").read_text(encoding="utf-8")
    orchestrator_text = (_ROOT / "scripts" / "orchestrator.py").read_text(encoding="utf-8")

    docs_link = next(
        link for link in issue_config["contact_links"] if "Documentation" in link["name"]
    )

    assert registry["support"]["documentation_route"] == "docs/README.md"
    assert registry["docs"]["index_route"] == "docs/README.md"
    assert registry["support"]["feature_route"].startswith("GitHub Discussions")
    assert pyproject["project"]["urls"]["Documentation"].endswith("/docs/README.md")
    assert docs_link["url"].endswith("/docs/README.md")
    for token in registry["tooling"]["active_entrypoints"]:
        assert token in docs_text
    for token in registry["tooling"]["compatibility_stubs"]:
        assert token in docs_text
    assert "docs/README.md" in contributing_text
    assert "return 2" in worker_text
    assert "return 2" in orchestrator_text
    assert "Use docs/README.md and CONTRIBUTING.md" in worker_text
    assert "Use docs/README.md and CONTRIBUTING.md" in orchestrator_text


def test_verification_matrix_and_checker_guard_active_path_truth() -> None:
    verification_text = (_ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md").read_text(
        encoding="utf-8"
    )
    checker_text = (_ROOT / "scripts" / "check_file_matrix.py").read_text(encoding="utf-8")

    assert "tests/core/anonymous_share/test_manager_submission.py" in verification_text
    assert "tests/core/test_coordinator_entry.py" in verification_text
    assert "tests/core/test_diagnostics*.py" in verification_text
    assert "tests/core/test_anonymous_share.py" not in verification_text
    assert "tests/test_coordinator_public.py" not in verification_text
    assert "tests/test_coordinator_runtime.py" not in verification_text
    assert "VERIFICATION_MATRIX_PATH" in checker_text
    assert "validate_verification_matrix_paths" in checker_text


def test_develop_script_smoke_mode_preserves_other_integrations(
    tmp_path: Path,
) -> None:
    """The local development entrypoint should only refresh Lipro's integration."""
    fake_repo = tmp_path / "repo"
    scripts_dir = fake_repo / "scripts"
    source_lipro = fake_repo / "custom_components" / "lipro"
    keep_component = fake_repo / "config" / "custom_components" / "keep_me"
    fake_bin = tmp_path / "bin"
    fake_uv = fake_bin / "uv"
    copied_script = scripts_dir / "develop"

    scripts_dir.mkdir(parents=True)
    source_lipro.mkdir(parents=True)
    keep_component.mkdir(parents=True)
    fake_bin.mkdir(parents=True)
    (fake_repo / ".venv").mkdir()

    copied_script.write_text(
        _DEVELOP_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8"
    )
    copied_script.chmod(copied_script.stat().st_mode | stat.S_IXUSR)
    (source_lipro / "manifest.json").write_text(
        '{"domain": "lipro"}',
        encoding="utf-8",
    )
    (keep_component / "sentinel.txt").write_text("keep", encoding="utf-8")
    fake_uv.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    fake_uv.chmod(fake_uv.stat().st_mode | stat.S_IXUSR)

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    env["LIPRO_DEVELOP_SMOKE_ONLY"] = "1"

    bash_executable = shutil.which("bash")
    assert bash_executable is not None

    result = subprocess.run(  # noqa: S603
        [bash_executable, str(copied_script)],
        cwd=fake_repo,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert (
        fake_repo / "config" / "custom_components" / "keep_me" / "sentinel.txt"
    ).read_text(encoding="utf-8") == "keep"
    assert (
        fake_repo / "config" / "custom_components" / "lipro" / "manifest.json"
    ).exists()
    assert "Preserved other custom integrations" in result.stdout
    assert "Smoke-only mode" in result.stdout
    assert "rm -rf config/custom_components" not in _DEVELOP_SCRIPT.read_text(
        encoding="utf-8"
    )
