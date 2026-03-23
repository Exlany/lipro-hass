"""Topicized governance regression coverage extracted from `tests/meta/test_governance_guards.py` (test_governance_release_contract)."""

from __future__ import annotations

import re

from .conftest import (
    _AGENTS,
    _CI_WORKFLOW,
    _CODEOWNERS,
    _CONTRIBUTING,
    _DEVCONTAINER,
    _DOCS_README,
    _ISSUE_CONFIG,
    _MANIFEST,
    _PR_TEMPLATE,
    _PRE_COMMIT,
    _QUALITY_SCALE,
    _README,
    _README_ZH,
    _RELEASE_WORKFLOW,
    _ROOT,
    _RUNBOOK,
    _SECURITY,
    _SUPPORT,
    _TROUBLESHOOTING,
    _count_numbered_markdown_items,
    _extract_checklist_labels,
    _extract_labeled_bullets,
    _extract_markdown_section,
    _load_json,
    _load_yaml,
    _parse_codeowners_handles,
)

_CODEQL_WORKFLOW = _ROOT / ".github" / "workflows" / "codeql.yml"
_GOVERNANCE_REGISTRY = _ROOT / ".planning" / "baseline" / "GOVERNANCE_REGISTRY.json"


def test_ci_and_release_workflows_share_governance_and_version_gates() -> None:
    ci_workflow = _load_yaml(_CI_WORKFLOW)
    release_workflow = _load_yaml(_RELEASE_WORKFLOW)
    codeql_workflow = _load_yaml(_CODEQL_WORKFLOW)

    assert "workflow_call" in ci_workflow["on"]

    governance_steps = ci_workflow["jobs"]["governance"]["steps"]
    governance_runs = "\n".join(step.get("run", "") for step in governance_steps)
    assert "tests/meta/test_governance*.py" in governance_runs
    assert "tests/meta/test_toolchain_truth.py" in governance_runs
    assert "tests/meta/test_version_sync.py" in governance_runs

    security_job = ci_workflow["jobs"]["security"]
    security_step_names = {step["name"] for step in security_job["steps"]}
    assert "Export runtime requirements" in security_step_names
    assert "Run pip-audit (runtime)" in security_step_names

    test_job = ci_workflow["jobs"]["test"]
    test_step_names = {step["name"] for step in test_job["steps"]}
    assert "Run snapshot tests" not in test_step_names
    assert "Record test lane contract" in test_step_names
    assert "Resolve changed coverage surface" in test_step_names
    assert "Check total + changed-surface coverage gates" in test_step_names

    benchmark_job = ci_workflow["jobs"]["benchmark"]
    benchmark_steps = benchmark_job["steps"]
    benchmark_step_names = {step["name"] for step in benchmark_steps}
    assert "Run benchmark suite" in benchmark_step_names
    assert "Upload benchmark artifact" in benchmark_step_names
    assert "Compare benchmark results against baseline manifest" in benchmark_step_names
    assert "Record benchmark governed posture" in benchmark_step_names
    benchmark_run = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Run benchmark suite"
    )
    assert benchmark_run.get("continue-on-error") in (None, False)
    assert benchmark_run["id"] == "benchmark_run"
    upload_step = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Upload benchmark artifact"
    )
    assert (
        upload_step["uses"]
        == "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
    )
    assert upload_step["with"]["path"] == ".benchmarks/benchmark.json"
    compare_step = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Compare benchmark results against baseline manifest"
    )
    assert "scripts/check_benchmark_baseline.py" in compare_step["run"]
    assert "tests/benchmarks/benchmark_baselines.json" in compare_step["run"]
    benchmark_summary = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Record benchmark governed posture"
    )
    assert "no-regression gate" in benchmark_summary["run"]

    validate_job = release_workflow["jobs"]["validate"]
    assert validate_job["uses"] == "./.github/workflows/ci.yml"
    assert validate_job["with"]["ref"] == "refs/tags/${{ env.RELEASE_TAG }}"
    assert validate_job["secrets"] == "inherit"

    workflow_call = ci_workflow["on"]["workflow_call"]
    assert workflow_call["inputs"]["ref"]["required"] is False
    assert workflow_call["inputs"]["ref"]["default"] == ""

    security_gate = release_workflow["jobs"]["security_gate"]
    assert security_gate["needs"] == "validate"
    security_gate_steps = {step["name"] for step in security_gate["steps"]}
    assert "Checkout tagged release ref" in security_gate_steps
    assert "Set up Python" in security_gate_steps
    assert "Run pip-audit (runtime, tagged release)" in security_gate_steps

    security_setup = next(
        step for step in security_gate["steps"] if step.get("name") == "Set up Python"
    )
    assert (
        security_setup["uses"]
        == "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405"
    )
    assert security_setup["with"]["python-version"] == "3.14"

    code_scanning_gate = release_workflow["jobs"]["code_scanning_gate"]
    assert code_scanning_gate["needs"] == "validate"
    code_scanning_gate_steps = {step["name"] for step in code_scanning_gate["steps"]}
    assert "Checkout tagged release ref" in code_scanning_gate_steps
    assert "Wait for tagged CodeQL analysis" in code_scanning_gate_steps
    assert "Fail on open CodeQL alerts for tagged ref" in code_scanning_gate_steps

    assert release_workflow["permissions"]["contents"] == "write"
    assert release_workflow["permissions"]["attestations"] == "write"
    assert release_workflow["permissions"]["id-token"] == "write"
    assert release_workflow["permissions"]["security-events"] == "read"

    build_job = release_workflow["jobs"]["build"]
    assert set(build_job["needs"]) == {
        "validate",
        "security_gate",
        "code_scanning_gate",
    }
    step_names = {step["name"] for step in build_job["steps"]}
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
    assert "Install cosign" in step_names
    assert "Sign release assets" in step_names
    assert "Verify release signatures" in step_names
    checkout_step = next(
        step
        for step in build_job["steps"]
        if step.get("name") == "Checkout tagged release ref"
    )
    checkout_with = checkout_step.get("with")
    assert isinstance(checkout_with, dict)
    assert checkout_with.get("ref") == "refs/tags/${{ env.RELEASE_TAG }}"
    version_guard = next(
        step["run"]
        for step in build_job["steps"]
        if step.get("name") == "Verify tag matches project version"
    )
    assert "pyproject.toml" in version_guard
    assert "RELEASE_TAG" in version_guard

    signature_verify = next(
        step["run"]
        for step in build_job["steps"]
        if step.get("name") == "Verify release signatures"
    )
    assert (
        'identity_regex="^https://github.com/${GITHUB_REPOSITORY}/.github/workflows/release.yml@refs/tags/${RELEASE_TAG}$"'
        in signature_verify
    )
    assert "heads/.+" not in signature_verify

    install_smoke = next(
        step["run"]
        for step in build_job["steps"]
        if step.get("name") == "Smoke-test release artifact install"
    )
    for token in (
        "--archive-file",
        "--checksum-file",
        "configuration.yaml",
        ".storage",
        "custom_components/lipro/manifest.json",
    ):
        assert token in install_smoke

    publish_release = next(
        step
        for step in build_job["steps"]
        if step.get("name") == "Publish release assets"
    )
    published_files = publish_release["with"]["files"]
    assert "dist/install.sh" in published_files
    assert "SHA256SUMS" in published_files
    assert ".spdx.json" in published_files
    assert ".release-identity.txt" in published_files
    assert ".sigstore.json" in published_files

    codeql = _load_yaml(_CODEQL_WORKFLOW)
    assert codeql["permissions"]["security-events"] == "write"
    analyze_steps = {step["name"] for step in codeql["jobs"]["analyze"]["steps"]}
    assert "Initialize CodeQL" in analyze_steps
    assert "Perform CodeQL Analysis" in analyze_steps
    codeql_on = codeql_workflow["on"]
    assert isinstance(codeql_on, dict)
    assert "workflow_dispatch" in codeql_on
    assert "push" in codeql_on
    assert "v*" in codeql_on["push"]["tags"]
    assert codeql_workflow["permissions"]["security-events"] == "write"
    codeql_steps = {
        step["name"] for step in codeql_workflow["jobs"]["analyze"]["steps"]
    }
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


def test_contributor_contract_matches_ci_language() -> None:
    contributing_bullets = _extract_labeled_bullets(
        _extract_markdown_section(
            _CONTRIBUTING.read_text(encoding="utf-8"),
            "CI Contract / CI 契约",
        )
    )
    pr_checklist = _extract_checklist_labels(_PR_TEMPLATE.read_text(encoding="utf-8"))

    assert {"lint", "governance", "test", "benchmark", "validate", "release"} <= set(
        contributing_bullets
    )
    assert {"lint", "governance", "test", "benchmark"} <= set(pr_checklist)
    assert "uv run python scripts/check_translations.py" in contributing_bullets["lint"]
    assert "tests/meta/test_governance*.py" in contributing_bullets["governance"]
    assert "tests/meta/test_toolchain_truth.py" in contributing_bullets["governance"]
    assert "tests/meta/test_version_sync.py" in contributing_bullets["governance"]
    assert "--ignore=tests/benchmarks" in contributing_bullets["test"]
    assert "tests/snapshots/" not in contributing_bullets["test"]
    assert "snapshot coverage" in contributing_bullets["test"]
    assert "changed measured files" in contributing_bullets["test"]
    assert "--changed-files .coverage-changed-files" in contributing_bullets["test"]
    assert "--baseline" in contributing_bullets["test"]
    assert "tests/benchmarks/" in contributing_bullets["benchmark"]
    assert ".benchmarks/benchmark.json" in contributing_bullets["benchmark"]
    assert "scripts/check_benchmark_baseline.py" in contributing_bullets["benchmark"]
    assert "benchmark_baselines.json" in contributing_bullets["benchmark"]
    assert "threshold warning" in contributing_bullets["benchmark"]
    assert "no-regression gate" in contributing_bullets["benchmark"]


def test_supported_shell_installer_path_uses_verified_release_assets() -> None:
    install_text = (_ROOT / "install.sh").read_text(encoding="utf-8")
    readme_text = _README.read_text(encoding="utf-8")
    readme_zh_text = _README_ZH.read_text(encoding="utf-8")
    troubleshooting_text = _TROUBLESHOOTING.read_text(encoding="utf-8")

    assert "--archive-file" in install_text
    assert "--checksum-file" in install_text
    assert "ARCHIVE_TAG=latest bash -" not in readme_text
    assert "ARCHIVE_TAG=latest bash -" not in readme_zh_text
    assert (
        "bash ./install.sh --archive-file ./lipro-hass-<release-tag>.zip --checksum-file ./SHA256SUMS"
        in readme_text
    )
    assert (
        "bash ./install.sh --archive-file ./lipro-hass-<release-tag>.zip --checksum-file ./SHA256SUMS"
        in readme_zh_text
    )
    assert "v1.0.0" not in readme_text
    assert "v1.0.0" not in readme_zh_text
    assert "verified GitHub Release assets" in troubleshooting_text
    assert "ARCHIVE_TAG=main" in readme_text
    assert "ARCHIVE_TAG=main" in readme_zh_text


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


def test_troubleshooting_and_runbook_navigation_is_consistent() -> None:
    assert _TROUBLESHOOTING.exists()
    assert _RUNBOOK.exists()

    troubleshooting_targets = (
        _README,
        _README_ZH,
        _CONTRIBUTING,
        _SUPPORT,
        _DOCS_README,
    )
    runbook_targets = (
        _README,
        _README_ZH,
        _CONTRIBUTING,
        _SUPPORT,
        _SECURITY,
        _DOCS_README,
        _PR_TEMPLATE,
        _ROOT / ".github" / "ISSUE_TEMPLATE" / "bug.yml",
    )

    for path in troubleshooting_targets:
        assert "docs/TROUBLESHOOTING.md" in path.read_text(encoding="utf-8")
    for path in runbook_targets:
        assert "docs/MAINTAINER_RELEASE_RUNBOOK.md" in path.read_text(encoding="utf-8")


def test_latest_closeout_pointer_and_active_route_stay_current() -> None:
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(encoding="utf-8")
    docs_text = _DOCS_README.read_text(encoding="utf-8")
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")

    assert ".planning/reviews/V1_14_EVIDENCE_INDEX.md" in docs_text
    assert "当前无 active milestone route" in docs_text
    assert "V1_14_EVIDENCE_INDEX.md" in runbook_text
    assert "V1_6_EVIDENCE_INDEX.md" not in runbook_text
    assert "$gsd-new-milestone" in project_text
    assert "$gsd-new-milestone" in state_text
    assert "## v1.14 Governance Truth Realignment, Typed Runtime Access & Final Hidden-Root Closure" in milestones_text
    assert "latest archive-ready closeout pointer = `.planning/reviews/V1_14_EVIDENCE_INDEX.md`" in milestones_text
    assert "v1.11" not in docs_text
    assert "v1.11" not in runbook_text


def test_security_disclosure_path_is_present() -> None:
    security_text = _SECURITY.read_text(encoding="utf-8")
    issue_config = _load_yaml(_ISSUE_CONFIG)
    contact_urls = {link["url"] for link in issue_config["contact_links"]}

    assert "/security/advisories/new" in security_text
    assert "public GitHub issue" in security_text
    assert "https://github.com/Exlany/lipro-hass/security/policy" in contact_urls


def test_readme_exposes_community_and_governance_entrypoints() -> None:
    for readme_path in (_README, _README_ZH):
        readme_text = readme_path.read_text(encoding="utf-8")
        for asset in (
            "CONTRIBUTING.md",
            "SUPPORT.md",
            "SECURITY.md",
            "CODE_OF_CONDUCT.md",
            "docs/README.md",
            "custom_components/lipro/quality_scale.yaml",
            ".devcontainer.json",
        ):
            assert asset in readme_text


def test_manifest_codeowners_match_repo_codeowners() -> None:
    manifest = _load_json(_MANIFEST)
    assert manifest.get("codeowners") == _parse_codeowners_handles(
        _CODEOWNERS.read_text(encoding="utf-8")
    )


def test_release_runbook_and_support_docs_expose_continuity_truth() -> None:
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")
    support_text = _SUPPORT.read_text(encoding="utf-8")
    security_text = _SECURITY.read_text(encoding="utf-8")
    codeowners_text = _CODEOWNERS.read_text(encoding="utf-8")

    for token in (
        "single-maintainer",
        "release custody",
        "freeze",
        "best effort",
        "delegate",
    ):
        assert token in runbook_text
    assert "Continuity Drill Checklist" in runbook_text
    assert "maintainer-unavailable drill" in runbook_text.lower()
    assert "triage owner" in support_text
    assert "best effort" in support_text
    assert "no documented delegate exists today" in support_text
    assert "maintainer-unavailable drill" in support_text.lower()
    assert "freeze new tagged releases" in security_text
    assert "Documented delegate: none currently" in security_text
    assert "maintainer-unavailable drill" in security_text.lower()
    assert "release custodian" in codeowners_text
    assert "maintainer-unavailable drill" in codeowners_text.lower()
    assert "restore custody only after" in codeowners_text


def test_support_and_issue_routing_are_consistent() -> None:
    support_text = _SUPPORT.read_text(encoding="utf-8")
    security_text = _SECURITY.read_text(encoding="utf-8")
    contributing_text = _CONTRIBUTING.read_text(encoding="utf-8")
    issue_config = _load_yaml(_ISSUE_CONFIG)
    contact_urls = [link["url"] for link in issue_config.get("contact_links", [])]

    assert "SUPPORT.md" in contributing_text
    assert "SECURITY.md" in contributing_text
    assert "verified release assets" in contributing_text
    assert any("discussions" in url.lower() for url in contact_urls)
    assert any("security/policy" in url.lower() for url in contact_urls)
    assert "Discussion" in support_text or "讨论" in support_text
    assert "SECURITY.md" in support_text
    assert "single-maintainer" in support_text
    assert "verified GitHub Release assets" in support_text
    assert "Best effort" in security_text or "best effort" in security_text
    assert "verified GitHub Release assets" in security_text


def test_templates_and_governance_docs_keep_continuity_contract() -> None:
    bug_text = (_ROOT / ".github" / "ISSUE_TEMPLATE" / "bug.yml").read_text(
        encoding="utf-8"
    )
    pr_text = _PR_TEMPLATE.read_text(encoding="utf-8")
    support_text = _SUPPORT.read_text(encoding="utf-8")
    security_text = _SECURITY.read_text(encoding="utf-8")
    codeowners_text = _CODEOWNERS.read_text(encoding="utf-8")

    assert "do not transfer release custody" in bug_text
    assert "undocumented delegate" in bug_text
    assert "freeze new tagged releases and new release promises" in bug_text
    assert "do not transfer release custody" in support_text
    assert "do not by themselves transfer release custody" in security_text
    assert "issue/PR template text" in security_text
    assert "docs/README.md" in pr_text
    assert "docs/MAINTAINER_RELEASE_RUNBOOK.md" in pr_text
    assert ".github/CODEOWNERS" in pr_text
    assert "maintainer-unavailable drill" in bug_text.lower()
    assert "maintainer-unavailable drill" in pr_text.lower()
    assert "undocumented delegate" in pr_text
    assert "do not transfer custody" in codeowners_text


def test_preview_lane_and_release_identity_keep_stable_contract_separate() -> None:
    ci_workflow = _load_yaml(_CI_WORKFLOW)
    release_workflow = _load_yaml(_RELEASE_WORKFLOW)
    support_text = _SUPPORT.read_text(encoding="utf-8")
    contributing_text = _CONTRIBUTING.read_text(encoding="utf-8")
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")

    preview_job = ci_workflow["jobs"]["compatibility_preview"]
    assert (
        preview_job["if"]
        == "github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'"
    )
    preview_steps = {step["name"] for step in preview_job["steps"]}
    assert "Upgrade Home Assistant preview dependency set" in preview_steps
    assert "Run compatibility preview smoke" in preview_steps
    assert "Record compatibility preview posture" in preview_steps

    preview_summary = next(
        step["run"]
        for step in preview_job["steps"]
        if step.get("name") == "Record compatibility preview posture"
    )
    assert "advisory only" in preview_summary
    assert "stable PR + release contract unchanged" in preview_summary
    assert (
        "DeprecationWarning/PendingDeprecationWarning promoted to errors"
        in preview_summary
    )

    dispatch_inputs = release_workflow["on"]["workflow_dispatch"]["inputs"]
    assert dispatch_inputs["publish_assets"]["type"] == "boolean"
    assert dispatch_inputs["publish_assets"]["default"] is False
    assert "verify-only" in dispatch_inputs["publish_assets"]["description"]

    release_manifest = next(
        step["run"]
        for step in release_workflow["jobs"]["build"]["steps"]
        if step.get("name") == "Write release identity manifest"
    )
    assert (
        "compatibility_preview_lane=ci.yml schedule/workflow_dispatch advisory"
        in release_manifest
    )
    assert (
        "compatibility_preview_semantics=signal-only; stable release and support guarantees stay unchanged"
        in release_manifest
    )
    assert (
        "deprecation_signal=DeprecationWarning/PendingDeprecationWarning promoted to errors in preview smoke"
        in release_manifest
    )

    record_mode = next(
        step["run"]
        for step in release_workflow["jobs"]["build"]["steps"]
        if step.get("name") == "Record release mode"
    )
    publish_step = next(
        step
        for step in release_workflow["jobs"]["build"]["steps"]
        if step.get("name") == "Publish release assets"
    )
    assert "release_mode=verify-only" in record_mode
    assert "Non-publish rehearsal" in record_mode
    assert publish_step["if"] == "${{ github.event_name == 'push' || github.event.inputs.publish_assets == 'true' }}"

    for text_block in (support_text, contributing_text, runbook_text):
        lowered = text_block.lower()
        assert "compatibility preview" in lowered
        assert "schedule" in lowered
        assert "workflow_dispatch" in lowered
        assert "advisory" in lowered


def test_runbook_and_pr_template_capture_break_glass_and_rehearsal_truth() -> None:
    registry = _load_json(_GOVERNANCE_REGISTRY)
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")
    pr_text = _PR_TEMPLATE.read_text(encoding="utf-8")

    for token in (
        registry["release"]["break_glass_verify_only_phrase"],
        registry["release"]["non_publish_rehearsal_phrase"],
    ):
        assert token in runbook_text
        assert token in pr_text


def test_change_type_validation_guidance_is_consistent() -> None:
    contributing_text = _CONTRIBUTING.read_text(encoding="utf-8")
    support_text = _SUPPORT.read_text(encoding="utf-8")
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")

    for token in ("docs-only", "governance-only", "release-only"):
        assert token in contributing_text
    assert "publish_assets=false" in contributing_text
    assert "publish_assets=false" in runbook_text
    assert "release-only" in support_text


def test_quality_scale_and_devcontainer_truth_are_in_sync() -> None:
    quality_scale = _load_yaml(_QUALITY_SCALE)
    known_limitations_comment = quality_scale["rules"]["docs-known-limitations"][
        "comment"
    ]
    match = re.search(r"(\d+) known limitations", known_limitations_comment)
    assert match is not None
    expected_known_limitations = int(match.group(1))

    readme_section = _extract_markdown_section(
        _README.read_text(encoding="utf-8"),
        "Known Limitations",
    )
    assert _count_numbered_markdown_items(readme_section) == expected_known_limitations
    config_flow_comment = quality_scale["rules"]["config-flow-test-coverage"]["comment"]
    for relative_path in (
        "tests/flows/test_flow_schemas.py",
        "tests/flows/test_config_flow_user.py",
        "tests/flows/test_config_flow_reauth.py",
        "tests/flows/test_config_flow_reconfigure.py",
        "tests/flows/test_options_flow.py",
    ):
        assert relative_path in config_flow_comment
        assert (_ROOT / relative_path).exists()

    devcontainer = _load_json(_DEVCONTAINER)
    settings = devcontainer["customizations"]["vscode"]["settings"]
    assert settings["python.defaultInterpreterPath"].endswith("/.venv/bin/python")
