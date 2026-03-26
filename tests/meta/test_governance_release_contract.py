"""Release/workflow governance contract anchor suite."""

from __future__ import annotations

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

_CODEQL_WORKFLOW = _ROOT / ".github" / "workflows" / "codeql.yml"
_GOVERNANCE_REGISTRY = _ROOT / ".planning" / "baseline" / "GOVERNANCE_REGISTRY.json"

def test_ci_and_release_workflows_share_governance_and_version_gates() -> None:
    ci_workflow = _load_yaml(_CI_WORKFLOW)
    release_workflow = _load_yaml(_RELEASE_WORKFLOW)
    codeql_workflow = _load_yaml(_CODEQL_WORKFLOW)

    ci_on = _as_mapping(ci_workflow["on"])
    ci_jobs = _as_mapping(ci_workflow["jobs"])
    release_jobs = _as_mapping(release_workflow["jobs"])
    release_permissions = _as_mapping(release_workflow["permissions"])

    assert "workflow_call" in ci_on

    governance_job = _as_mapping(ci_jobs["governance"])
    governance_steps = _as_mapping_list(governance_job["steps"])
    governance_runs = "\n".join(_as_str(step.get("run", "")) for step in governance_steps)
    assert "tests/meta/test_governance*.py" in governance_runs
    assert "tests/meta/test_toolchain_truth.py" in governance_runs
    assert "tests/meta/test_version_sync.py" in governance_runs

    security_job = _as_mapping(ci_jobs["security"])
    security_steps = _as_mapping_list(security_job["steps"])
    security_step_names = {_as_str(step["name"]) for step in security_steps}
    assert "Export runtime requirements" in security_step_names
    assert "Run pip-audit (runtime)" in security_step_names

    test_job = _as_mapping(ci_jobs["test"])
    test_steps = _as_mapping_list(test_job["steps"])
    test_step_names = {_as_str(step["name"]) for step in test_steps}
    assert "Run snapshot tests" not in test_step_names
    assert "Record test lane contract" in test_step_names
    assert "Resolve changed coverage surface" in test_step_names
    assert "Check total + changed-surface coverage gates" in test_step_names

    benchmark_job = _as_mapping(ci_jobs["benchmark"])
    benchmark_steps = _as_mapping_list(benchmark_job["steps"])
    benchmark_step_names = {_as_str(step["name"]) for step in benchmark_steps}
    assert "Run benchmark suite" in benchmark_step_names
    assert "Upload benchmark artifact" in benchmark_step_names
    assert "Compare benchmark results against baseline manifest" in benchmark_step_names
    assert "Record benchmark governed posture" in benchmark_step_names
    benchmark_run = next(step for step in benchmark_steps if step.get("name") == "Run benchmark suite")
    assert benchmark_run.get("continue-on-error") in (None, False)
    assert _as_str(benchmark_run["id"]) == "benchmark_run"
    upload_step = next(step for step in benchmark_steps if step.get("name") == "Upload benchmark artifact")
    assert _as_str(upload_step["uses"]) == "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
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
    benchmark_summary = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Record benchmark governed posture"
    )
    assert "no-regression gate" in _as_str(benchmark_summary["run"])

    validate_job = _as_mapping(release_jobs["validate"])
    assert _as_str(validate_job["uses"]) == "./.github/workflows/ci.yml"
    validate_with = _as_mapping(validate_job["with"])
    assert _as_str(validate_with["ref"]) == "refs/tags/${{ env.RELEASE_TAG }}"
    assert _as_str(validate_job["secrets"]) == "inherit"

    workflow_call = _as_mapping(ci_on["workflow_call"])
    workflow_inputs = _as_mapping(workflow_call["inputs"])
    workflow_ref = _as_mapping(workflow_inputs["ref"])
    assert _as_bool(workflow_ref["required"]) is False
    assert _as_str(workflow_ref["default"]) == ""

    security_gate = _as_mapping(release_jobs["security_gate"])
    assert _as_str(security_gate["needs"]) == "validate"
    security_gate_steps = _as_mapping_list(security_gate["steps"])
    security_gate_step_names = {_as_str(step["name"]) for step in security_gate_steps}
    assert "Checkout tagged release ref" in security_gate_step_names
    assert "Set up Python" in security_gate_step_names
    assert "Run pip-audit (runtime, tagged release)" in security_gate_step_names

    security_setup = next(
        step for step in security_gate_steps if step.get("name") == "Set up Python"
    )
    security_setup_with = _as_mapping(security_setup["with"])
    assert _as_str(security_setup["uses"]) == "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405"
    assert _as_str(security_setup_with["python-version"]) == "3.14"

    code_scanning_gate = _as_mapping(release_jobs["code_scanning_gate"])
    assert _as_str(code_scanning_gate["needs"]) == "validate"
    code_scanning_gate_steps = _as_mapping_list(code_scanning_gate["steps"])
    code_scanning_gate_step_names = {_as_str(step["name"]) for step in code_scanning_gate_steps}
    assert "Checkout tagged release ref" in code_scanning_gate_step_names
    assert "Wait for tagged CodeQL analysis" in code_scanning_gate_step_names
    assert "Fail on open CodeQL alerts for tagged ref" in code_scanning_gate_step_names

    assert _as_str(release_permissions["contents"]) == "write"
    assert _as_str(release_permissions["attestations"]) == "write"
    assert _as_str(release_permissions["id-token"]) == "write"
    assert _as_str(release_permissions["security-events"]) == "read"

    build_job = _as_mapping(release_jobs["build"])
    assert set(_as_str_list(build_job["needs"])) == {"validate", "security_gate", "code_scanning_gate"}
    build_steps = _as_mapping_list(build_job["steps"])
    step_names = {_as_str(step["name"]) for step in build_steps}
    assert "Checkout tagged release ref" in step_names
    assert "Verify tag matches project version" in step_names
    assert "Build zip, installer, and checksums" in step_names
    assert "Smoke-test release artifact install" in step_names
    assert "Export SBOM" in step_names
    assert "Generate artifact attestation" in step_names
    assert "Verify generated artifact attestations" in step_names
    assert "Install cosign" in step_names
    assert "Sign release assets" in step_names
    assert "Verify release signatures" in step_names
    assert "Write release identity manifest" in step_names

    checkout_step = next(
        step for step in build_steps if step.get("name") == "Checkout tagged release ref"
    )
    checkout_with = _as_mapping(checkout_step["with"])
    assert _as_str(checkout_with["ref"]) == "refs/tags/${{ env.RELEASE_TAG }}"
    version_guard = next(
        _as_str(step["run"])
        for step in build_steps
        if step.get("name") == "Verify tag matches project version"
    )
    assert "pyproject.toml" in version_guard
    assert "RELEASE_TAG" in version_guard

    signature_verify = next(
        _as_str(step["run"])
        for step in build_steps
        if step.get("name") == "Verify release signatures"
    )
    assert 'identity_regex="^https://github.com/${GITHUB_REPOSITORY}/.github/workflows/release.yml@refs/tags/${RELEASE_TAG}$"' in signature_verify
    assert "heads/.+" not in signature_verify

    install_smoke = next(
        _as_str(step["run"])
        for step in build_steps
        if step.get("name") == "Smoke-test release artifact install"
    )
    for token in ("--archive-file", "--checksum-file", "configuration.yaml", ".storage", "custom_components/lipro/manifest.json"):
        assert token in install_smoke

    publish_release = next(
        step for step in build_steps if step.get("name") == "Publish release assets"
    )
    published_with = _as_mapping(publish_release["with"])
    published_files = _as_str(published_with["files"])
    assert "dist/install.sh" in published_files
    assert "SHA256SUMS" in published_files
    assert ".spdx.json" in published_files
    assert ".release-identity.txt" in published_files
    assert ".sigstore.json" in published_files

    codeql = _load_yaml(_CODEQL_WORKFLOW)
    codeql_permissions = _as_mapping(codeql["permissions"])
    assert _as_str(codeql_permissions["security-events"]) == "write"
    codeql_jobs = _as_mapping(codeql["jobs"])
    codeql_analyze = _as_mapping(codeql_jobs["analyze"])
    analyze_steps = {_as_str(step["name"]) for step in _as_mapping_list(codeql_analyze["steps"])}
    assert "Initialize CodeQL" in analyze_steps
    assert "Perform CodeQL Analysis" in analyze_steps

    codeql_on = _as_mapping(codeql_workflow["on"])
    assert "workflow_dispatch" in codeql_on
    assert "push" in codeql_on
    codeql_push = _as_mapping(codeql_on["push"])
    assert "v*" in _as_str_list(codeql_push["tags"])
    codeql_workflow_permissions = _as_mapping(codeql_workflow["permissions"])
    assert _as_str(codeql_workflow_permissions["security-events"]) == "write"
    codeql_workflow_jobs = _as_mapping(codeql_workflow["jobs"])
    codeql_workflow_analyze = _as_mapping(codeql_workflow_jobs["analyze"])
    codeql_steps = {_as_str(step["name"]) for step in _as_mapping_list(codeql_workflow_analyze["steps"])}
    assert "Initialize CodeQL" in codeql_steps
    assert "Perform CodeQL Analysis" in codeql_steps

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
