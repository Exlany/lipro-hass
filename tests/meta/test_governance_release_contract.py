"""Release/workflow governance contract anchor suite."""

from __future__ import annotations

import ast

from .conftest import (
    _AGENTS,
    _CI_WORKFLOW,
    _CONTRIBUTING,
    _PRE_COMMIT,
    _RELEASE_WORKFLOW,
    _ROOT,
    _RUNBOOK,
    _SUPPORT,
    _as_bool,
    _as_mapping,
    _as_mapping_list,
    _as_str,
    _as_str_list,
    _load_yaml,
)
from .governance_current_truth import (
    LATEST_ARCHIVED_AUDIT_PATH,
    LATEST_ARCHIVED_EVIDENCE_PATH,
)

_CODEQL_WORKFLOW = _ROOT / ".github" / "workflows" / "codeql.yml"
_GOVERNANCE_REGISTRY = _ROOT / ".planning" / "baseline" / "GOVERNANCE_REGISTRY.json"

def _step_names(steps: list[dict[str, object]]) -> set[str]:
    return {_as_str(step["name"]) for step in steps}


def _step_named(steps: list[dict[str, object]], name: str) -> dict[str, object]:
    return next(step for step in steps if step.get("name") == name)


def _step_run(steps: list[dict[str, object]], name: str) -> str:
    return _as_str(_step_named(steps, name)["run"])


def _assert_run_contains(run: str, *tokens: str) -> None:
    for token in tokens:
        assert token in run


def _import_modules(path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
            continue
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            dotted = f"{'.' * node.level}{module}" if node.level else module
            if dotted:
                modules.add(dotted)
    return modules


def test_ci_governance_job_runs_meta_version_and_toolchain_guards() -> None:
    ci_workflow = _load_yaml(_CI_WORKFLOW)
    ci_on = _as_mapping(ci_workflow["on"])
    ci_jobs = _as_mapping(ci_workflow["jobs"])
    assert "workflow_call" in ci_on

    governance_job = _as_mapping(ci_jobs["governance"])
    governance_steps = _as_mapping_list(governance_job["steps"])
    governance_runs = "\n".join(_as_str(step.get("run", "")) for step in governance_steps)
    _assert_run_contains(
        governance_runs,
        "tests/meta/test_governance*.py",
        "tests/meta/test_toolchain_truth.py",
        "tests/meta/test_version_sync.py",
    )

    workflow_call = _as_mapping(ci_on["workflow_call"])
    workflow_inputs = _as_mapping(workflow_call["inputs"])
    workflow_ref = _as_mapping(workflow_inputs["ref"])
    assert _as_bool(workflow_ref["required"]) is False
    assert _as_str(workflow_ref["default"]) == ""


def test_ci_security_and_test_jobs_keep_expected_gate_steps() -> None:
    ci_workflow = _load_yaml(_CI_WORKFLOW)
    ci_jobs = _as_mapping(ci_workflow["jobs"])

    security_job = _as_mapping(ci_jobs["security"])
    security_step_names = _step_names(_as_mapping_list(security_job["steps"]))
    assert "Export runtime requirements" in security_step_names
    assert "Run pip-audit (runtime)" in security_step_names

    test_job = _as_mapping(ci_jobs["test"])
    test_step_names = _step_names(_as_mapping_list(test_job["steps"]))
    assert "Run snapshot tests" not in test_step_names
    assert "Record test lane contract" in test_step_names
    assert "Resolve changed coverage surface" in test_step_names
    assert "Check total + changed-surface coverage gates" in test_step_names


def test_ci_benchmark_lane_enforces_baseline_and_artifact_contract() -> None:
    ci_workflow = _load_yaml(_CI_WORKFLOW)
    ci_jobs = _as_mapping(ci_workflow["jobs"])
    benchmark_job = _as_mapping(ci_jobs["benchmark"])
    benchmark_steps = _as_mapping_list(benchmark_job["steps"])
    benchmark_step_names = _step_names(benchmark_steps)

    assert "Run benchmark suite" in benchmark_step_names
    assert "Upload benchmark artifact" in benchmark_step_names
    assert "Compare benchmark results against baseline manifest" in benchmark_step_names
    assert "Record benchmark governed posture" in benchmark_step_names

    benchmark_run = _step_named(benchmark_steps, "Run benchmark suite")
    assert benchmark_run.get("continue-on-error") in (None, False)
    assert _as_str(benchmark_run["id"]) == "benchmark_run"

    upload_step = _step_named(benchmark_steps, "Upload benchmark artifact")
    assert _as_str(upload_step["uses"]) == "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
    upload_with = _as_mapping(upload_step["with"])
    assert _as_str(upload_with["path"]) == ".benchmarks/benchmark.json"

    compare_run = _step_run(benchmark_steps, "Compare benchmark results against baseline manifest")
    _assert_run_contains(compare_run, "scripts/check_benchmark_baseline.py", "tests/benchmarks/benchmark_baselines.json")
    benchmark_summary = _step_run(benchmark_steps, "Record benchmark governed posture")
    assert "no-regression gate" in benchmark_summary


def test_release_validate_and_security_gates_reuse_tagged_ref_contract() -> None:
    release_workflow = _load_yaml(_RELEASE_WORKFLOW)
    release_jobs = _as_mapping(release_workflow["jobs"])
    release_permissions = _as_mapping(release_workflow["permissions"])

    validate_job = _as_mapping(release_jobs["validate"])
    assert _as_str(validate_job["uses"]) == "./.github/workflows/ci.yml"
    validate_with = _as_mapping(validate_job["with"])
    assert _as_str(validate_with["ref"]) == "refs/tags/${{ env.RELEASE_TAG }}"
    assert _as_str(validate_job["secrets"]) == "inherit"

    security_gate = _as_mapping(release_jobs["security_gate"])
    assert _as_str(security_gate["needs"]) == "validate"
    security_gate_steps = _as_mapping_list(security_gate["steps"])
    security_gate_step_names = _step_names(security_gate_steps)
    assert "Checkout tagged release ref" in security_gate_step_names
    assert "Set up Python" in security_gate_step_names
    assert "Run pip-audit (runtime, tagged release)" in security_gate_step_names

    security_setup = _step_named(security_gate_steps, "Set up Python")
    security_setup_with = _as_mapping(security_setup["with"])
    assert _as_str(security_setup["uses"]) == "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405"
    assert _as_str(security_setup_with["python-version"]) == "3.14"

    code_scanning_gate = _as_mapping(release_jobs["code_scanning_gate"])
    assert _as_str(code_scanning_gate["needs"]) == "validate"
    code_scanning_gate_step_names = _step_names(_as_mapping_list(code_scanning_gate["steps"]))
    assert "Checkout tagged release ref" in code_scanning_gate_step_names
    assert "Wait for tagged CodeQL analysis" in code_scanning_gate_step_names
    assert "Fail on open CodeQL alerts for tagged ref" in code_scanning_gate_step_names

    assert _as_str(release_permissions["contents"]) == "write"
    assert _as_str(release_permissions["attestations"]) == "write"
    assert _as_str(release_permissions["id-token"]) == "write"
    assert _as_str(release_permissions["security-events"]) == "read"


def test_release_build_job_enforces_version_install_and_signing_contract() -> None:
    release_workflow = _load_yaml(_RELEASE_WORKFLOW)
    release_jobs = _as_mapping(release_workflow["jobs"])
    build_job = _as_mapping(release_jobs["build"])
    assert set(_as_str_list(build_job["needs"])) == {"validate", "security_gate", "code_scanning_gate"}

    build_steps = _as_mapping_list(build_job["steps"])
    step_names = _step_names(build_steps)
    for expected in (
        "Checkout tagged release ref",
        "Verify tag matches project version",
        "Build zip, installer, and checksums",
        "Smoke-test release artifact install",
        "Export SBOM",
        "Generate artifact attestation",
        "Verify generated artifact attestations",
        "Install cosign",
        "Sign release assets",
        "Verify release signatures",
        "Write release identity manifest",
    ):
        assert expected in step_names

    checkout_with = _as_mapping(_step_named(build_steps, "Checkout tagged release ref")["with"])
    assert _as_str(checkout_with["ref"]) == "refs/tags/${{ env.RELEASE_TAG }}"

    version_guard = _step_run(build_steps, "Verify tag matches project version")
    _assert_run_contains(version_guard, "pyproject.toml", "RELEASE_TAG")

    signature_verify = _step_run(build_steps, "Verify release signatures")
    assert 'identity_regex="^https://github.com/${GITHUB_REPOSITORY}/.github/workflows/release.yml@refs/tags/${RELEASE_TAG}$"' in signature_verify
    assert "heads/.+" not in signature_verify

    install_smoke = _step_run(build_steps, "Smoke-test release artifact install")
    _assert_run_contains(
        install_smoke,
        "--archive-file",
        "--checksum-file",
        "configuration.yaml",
        ".storage",
        "custom_components/lipro/manifest.json",
    )

    published_with = _as_mapping(_step_named(build_steps, "Publish release assets")["with"])
    published_files = _as_str(published_with["files"])
    _assert_run_contains(
        published_files,
        "dist/install.sh",
        "SHA256SUMS",
        ".spdx.json",
        ".release-identity.txt",
        ".sigstore.json",
    )


def test_codeql_tag_workflow_matches_release_scanning_contract() -> None:
    codeql_workflow = _load_yaml(_CODEQL_WORKFLOW)
    codeql_permissions = _as_mapping(codeql_workflow["permissions"])
    assert _as_str(codeql_permissions["security-events"]) == "write"

    codeql_jobs = _as_mapping(codeql_workflow["jobs"])
    codeql_analyze = _as_mapping(codeql_jobs["analyze"])
    codeql_steps = _step_names(_as_mapping_list(codeql_analyze["steps"]))
    assert "Initialize CodeQL" in codeql_steps
    assert "Perform CodeQL Analysis" in codeql_steps

    codeql_on = _as_mapping(codeql_workflow["on"])
    assert "workflow_dispatch" in codeql_on
    assert "push" in codeql_on
    codeql_push = _as_mapping(codeql_on["push"])
    assert "v*" in _as_str_list(codeql_push["tags"])


def test_architecture_policy_checker_consumes_script_owned_helpers() -> None:
    checker_path = _ROOT / "scripts" / "check_architecture_policy.py"
    checker_text = checker_path.read_text(encoding="utf-8")
    checker_imports = _import_modules(checker_path)

    assert "sys.path.insert" not in checker_text
    assert "tests.helpers.architecture_policy" not in checker_imports
    assert "tests.helpers.ast_guard_utils" not in checker_imports
    assert (_ROOT / "scripts" / "lib" / "architecture_policy.py").exists()
    assert (_ROOT / "scripts" / "lib" / "ast_guard_utils.py").exists()

    architecture_helper_text = (_ROOT / "tests" / "helpers" / "architecture_policy.py").read_text(
        encoding="utf-8"
    )
    ast_helper_text = (_ROOT / "tests" / "helpers" / "ast_guard_utils.py").read_text(
        encoding="utf-8"
    )
    assert "from scripts.lib.architecture_policy import" in architecture_helper_text
    assert "from scripts.lib.ast_guard_utils import" in ast_helper_text
    assert "@dataclass" not in architecture_helper_text
    assert "def policy_root" not in architecture_helper_text
    assert "def iter_import_modules" not in ast_helper_text


def test_governance_closeout_suite_is_wired_into_daily_gate_commands() -> None:
    agents_text = _AGENTS.read_text(encoding="utf-8")
    contributing_text = _CONTRIBUTING.read_text(encoding="utf-8")
    pre_commit_text = _PRE_COMMIT.read_text(encoding="utf-8")
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")
    ci_text = _CI_WORKFLOW.read_text(encoding="utf-8")

    for text in (
        agents_text,
        contributing_text,
        pre_commit_text,
        runbook_text,
        ci_text,
    ):
        assert "tests/meta/test_governance*.py" in text

    for text in (
        contributing_text,
        pre_commit_text,
        runbook_text,
        ci_text,
    ):
        assert "tests/meta/test_toolchain_truth.py" in text

def test_phase_23_audit_checklist_covers_addendum_and_explicit_defers() -> None:
    checklist_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "23-governance-convergence-contributor-docs-and-release-evidence-closure"
        / "23-AUDIT-CHECKLIST.md"
    ).read_text(encoding="utf-8")

    for token in (
        "`23-04`",
        "`23-05`",
        "`23-06`",
        "`23-07`",
        "`23-08`",
        ".planning/codebase/TESTING.md",
        "script ↔ tests coupling",
        "wording-guard brittleness",
        "giant tests / private-internal coupling",
        "release supply-chain hardening",
        "firmware manifest metadata",
        "No item may be silently dropped.",
        "`ARCHIVE_TAG=latest`",
        "provenance",
        "SBOM",
        "signing",
        "code scanning",
    ):
        assert token in checklist_text

def test_preview_lane_and_release_identity_keep_stable_contract_separate() -> None:
    ci_workflow = _load_yaml(_CI_WORKFLOW)
    release_workflow = _load_yaml(_RELEASE_WORKFLOW)
    support_text = _SUPPORT.read_text(encoding="utf-8")
    contributing_text = _CONTRIBUTING.read_text(encoding="utf-8")
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")

    ci_jobs = _as_mapping(ci_workflow["jobs"])
    preview_job = _as_mapping(ci_jobs["compatibility_preview"])
    assert _as_str(preview_job["if"]) == "github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'"
    preview_steps = _as_mapping_list(preview_job["steps"])
    preview_step_names = {_as_str(step["name"]) for step in preview_steps}
    assert "Upgrade Home Assistant preview dependency set" in preview_step_names
    assert "Run compatibility preview smoke" in preview_step_names
    assert "Record compatibility preview posture" in preview_step_names

    preview_summary = next(
        _as_str(step["run"])
        for step in preview_steps
        if step.get("name") == "Record compatibility preview posture"
    )
    assert "advisory only" in preview_summary
    assert "stable PR + release contract unchanged" in preview_summary
    assert "DeprecationWarning/PendingDeprecationWarning promoted to errors" in preview_summary

    release_on = _as_mapping(release_workflow["on"])
    workflow_dispatch = _as_mapping(release_on["workflow_dispatch"])
    dispatch_inputs = _as_mapping(workflow_dispatch["inputs"])
    publish_assets = _as_mapping(dispatch_inputs["publish_assets"])
    assert _as_str(publish_assets["type"]) == "boolean"
    assert _as_bool(publish_assets["default"]) is False
    assert "verify-only" in _as_str(publish_assets["description"])

    release_jobs = _as_mapping(release_workflow["jobs"])
    build_job = _as_mapping(release_jobs["build"])
    build_steps = _as_mapping_list(build_job["steps"])
    release_manifest = next(
        _as_str(step["run"])
        for step in build_steps
        if step.get("name") == "Write release identity manifest"
    )
    assert "compatibility_preview_lane=ci.yml schedule/workflow_dispatch advisory" in release_manifest
    assert "compatibility_preview_semantics=signal-only; stable release and support guarantees stay unchanged" in release_manifest
    assert "deprecation_signal=DeprecationWarning/PendingDeprecationWarning promoted to errors in preview smoke" in release_manifest

    record_mode = next(
        _as_str(step["run"])
        for step in build_steps
        if step.get("name") == "Record release mode"
    )
    publish_step = next(
        step for step in build_steps if step.get("name") == "Publish release assets"
    )
    assert "release_mode=verify-only" in record_mode
    assert "Non-publish rehearsal" in record_mode
    assert _as_str(publish_step["if"]) == "${{ github.event_name == 'push' || github.event.inputs.publish_assets == 'true' }}"

    for text_block in (support_text, contributing_text, runbook_text):
        lowered = text_block.lower()
        assert "compatibility preview" in lowered
        assert "schedule" in lowered
        assert "workflow_dispatch" in lowered
        assert "advisory" in lowered



def test_runbook_docs_appendix_and_changelog_share_single_release_story() -> None:
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")
    docs_readme_text = (_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    changelog_text = (_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    for token in (
        LATEST_ARCHIVED_EVIDENCE_PATH,
        LATEST_ARCHIVED_AUDIT_PATH,
        "CHANGELOG.md",
    ):
        assert token in runbook_text

    for token in (
        "docs/MAINTAINER_RELEASE_RUNBOOK.md",
        "latest archived evidence index",
        "archived milestone audit",
        "not part of the public first hop",
    ):
        assert token in docs_readme_text

    assert LATEST_ARCHIVED_EVIDENCE_PATH not in docs_readme_text
    assert LATEST_ARCHIVED_AUDIT_PATH not in docs_readme_text

    for token in (
        "CI reuse",
        "CodeQL",
        "SBOM",
        "cosign",
        "release identity",
        "compatibility preview",
    ):
        assert token in changelog_text
