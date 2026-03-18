"""Topicized governance regression coverage extracted from `tests/meta/test_governance_guards.py` (test_governance_release_contract)."""

from __future__ import annotations

from .test_governance_guards import (
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
    re,
)

_CODEQL_WORKFLOW = _ROOT / ".github" / "workflows" / "codeql.yml"


def test_ci_and_release_workflows_share_governance_and_version_gates() -> None:
    ci_workflow = _load_yaml(_CI_WORKFLOW)
    release_workflow = _load_yaml(_RELEASE_WORKFLOW)
    codeql_workflow = _load_yaml(_CODEQL_WORKFLOW)

    assert "workflow_call" in ci_workflow["on"]

    governance_steps = ci_workflow["jobs"]["governance"]["steps"]
    governance_runs = "\n".join(step.get("run", "") for step in governance_steps)
    assert "tests/meta/test_governance*.py" in governance_runs
    assert "tests/meta/test_version_sync.py" in governance_runs

    security_job = ci_workflow["jobs"]["security"]
    security_step_names = {step["name"] for step in security_job["steps"]}
    assert "Export runtime requirements" in security_step_names
    assert "Run pip-audit (runtime)" in security_step_names

    test_job = ci_workflow["jobs"]["test"]
    test_step_names = {step["name"] for step in test_job["steps"]}
    assert "Run snapshot tests" not in test_step_names
    assert "Record test lane contract" in test_step_names

    benchmark_job = ci_workflow["jobs"]["benchmark"]
    benchmark_steps = benchmark_job["steps"]
    benchmark_step_names = {step["name"] for step in benchmark_steps}
    assert "Run advisory benchmarks" in benchmark_step_names
    assert "Upload advisory benchmark artifact" in benchmark_step_names
    assert "Record benchmark advisory posture" in benchmark_step_names
    benchmark_run = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Run advisory benchmarks"
    )
    assert benchmark_run["continue-on-error"] is True
    assert benchmark_run["id"] == "benchmark_run"
    upload_step = next(
        step
        for step in benchmark_steps
        if step.get("name") == "Upload advisory benchmark artifact"
    )
    assert (
        upload_step["uses"]
        == "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
    )
    assert upload_step["with"]["path"] == ".benchmarks/benchmark.json"

    validate_job = release_workflow["jobs"]["validate"]
    assert validate_job["uses"] == "./.github/workflows/ci.yml"
    assert validate_job["secrets"] == "inherit"

    security_gate = release_workflow["jobs"]["security_gate"]
    assert security_gate["needs"] == "validate"
    security_gate_steps = {step["name"] for step in security_gate["steps"]}
    assert "Checkout tagged release ref" in security_gate_steps
    assert "Run pip-audit (runtime, tagged release)" in security_gate_steps

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
    assert set(build_job["needs"]) == {"validate", "security_gate", "code_scanning_gate"}
    step_names = {step["name"] for step in build_job["steps"]}
    assert "Checkout tagged release ref" in step_names
    assert "Verify tag matches project version" in step_names
    assert "Build zip, installer, and checksums" in step_names
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
    codeql_on = codeql_workflow.get("on", codeql_workflow.get(True))
    assert isinstance(codeql_on, dict)
    assert "workflow_dispatch" in codeql_on
    assert "push" in codeql_on
    assert "v*" in codeql_on["push"]["tags"]
    assert codeql_workflow["permissions"]["security-events"] == "write"
    codeql_steps = {step["name"] for step in codeql_workflow["jobs"]["analyze"]["steps"]}
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
    assert "tests/benchmarks/" in contributing_bullets["benchmark"]
    assert ".benchmarks/benchmark.json" in contributing_bullets["benchmark"]


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
        "bash ./install.sh --archive-file ./lipro-hass-v1.0.0.zip --checksum-file ./SHA256SUMS"
        in readme_text
    )
    assert (
        "bash ./install.sh --archive-file ./lipro-hass-v1.0.0.zip --checksum-file ./SHA256SUMS"
        in readme_zh_text
    )
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

    for token in ("single-maintainer", "release custody", "freeze", "best effort", "delegate"):
        assert token in runbook_text
    assert "Continuity Drill Checklist" in runbook_text
    assert "triage owner" in support_text
    assert "best effort" in support_text
    assert "no documented delegate exists today" in support_text
    assert "freeze new tagged releases" in security_text
    assert "Documented delegate: none currently" in security_text
    assert "release custodian" in codeowners_text
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
    assert (
        "tests/flows/test_config_flow.py"
        in quality_scale["rules"]["config-flow-test-coverage"]["comment"]
    )
    assert (_ROOT / "tests" / "flows" / "test_config_flow.py").exists()

    devcontainer = _load_json(_DEVCONTAINER)
    settings = devcontainer["customizations"]["vscode"]["settings"]
    assert settings["python.defaultInterpreterPath"].endswith("/.venv/bin/python")
