"""Release/governance documentation contract suite."""

from __future__ import annotations

import re

from .conftest import (
    _CONTRIBUTING,
    _DEVCONTAINER,
    _DOCS_README,
    _PR_TEMPLATE,
    _QUALITY_SCALE,
    _README,
    _README_ZH,
    _ROOT,
    _RUNBOOK,
    _SECURITY,
    _SUPPORT,
    _TROUBLESHOOTING,
    _as_mapping,
    _as_str,
    _count_numbered_markdown_items,
    _extract_checklist_labels,
    _extract_labeled_bullets,
    _extract_markdown_section,
    _load_json,
    _load_yaml,
)

_CODEQL_WORKFLOW = _ROOT / ".github" / "workflows" / "codeql.yml"
_GOVERNANCE_REGISTRY = _ROOT / ".planning" / "baseline" / "GOVERNANCE_REGISTRY.json"
_CONTRIBUTOR_CHANGE_MAP = _ROOT / "docs" / "CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md"

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
    assert {"lint", "governance", "test", "benchmark", "docs/navigation"} <= set(pr_checklist)
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
    assert re.search(r"for example v\d+\.\d+\.\d+", readme_text) is None
    assert re.search(r"例如 v\d+\.\d+\.\d+", readme_zh_text) is None
    assert (
        "verified GitHub Release assets" in troubleshooting_text
        or "verified release assets" in troubleshooting_text
    )
    assert "ARCHIVE_TAG=main" in readme_text
    assert "ARCHIVE_TAG=main" in readme_zh_text

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

def test_readme_exposes_community_and_governance_entrypoints() -> None:
    for readme_path in (_README, _README_ZH):
        readme_text = readme_path.read_text(encoding="utf-8")
        for asset in (
            "CONTRIBUTING.md",
            "SUPPORT.md",
            "SECURITY.md",
            "CODE_OF_CONDUCT.md",
            "docs/README.md",
            "docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md",
            "custom_components/lipro/quality_scale.yaml",
            ".devcontainer.json",
        ):
            assert asset in readme_text

def test_contributor_architecture_change_map_is_linked_and_scope_honest() -> None:
    assert _CONTRIBUTOR_CHANGE_MAP.exists()
    change_map_text = _CONTRIBUTOR_CHANGE_MAP.read_text(encoding="utf-8")

    for path in (_README, _README_ZH, _DOCS_README, _CONTRIBUTING, _SUPPORT, _SECURITY, _PR_TEMPLATE):
        assert "docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md" in path.read_text(encoding="utf-8")

    for token in (
        "Protocol",
        "Runtime",
        "Control",
        "External-boundary",
        "Governance / docs",
        "docs/NORTH_STAR_TARGET_ARCHITECTURE.md",
        "docs/developer_architecture.md",
        ".planning/baseline/PUBLIC_SURFACES.md",
        ".planning/baseline/VERIFICATION_MATRIX.md",
        ".planning/reviews/FILE_MATRIX.md",
        ".planning/reviews/PROMOTED_PHASE_ASSETS.md",
    ):
        assert token in change_map_text

    lowered = change_map_text.lower()
    assert "$gsd-" not in change_map_text
    assert "phase 81" not in lowered
    assert "latest archived baseline" not in lowered

    pr_template_text = _PR_TEMPLATE.read_text(encoding="utf-8")
    assert "docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md" in pr_template_text
    assert "protocol / runtime / control / external-boundary / governance" in pr_template_text


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
    rules = _as_mapping(quality_scale["rules"])
    known_limitations_rule = _as_mapping(rules["docs-known-limitations"])
    known_limitations_comment = _as_str(known_limitations_rule["comment"])
    match = re.search(r"(\d+) known limitations", known_limitations_comment)
    assert match is not None
    expected_known_limitations = int(match.group(1))

    readme_section = _extract_markdown_section(
        _README.read_text(encoding="utf-8"),
        "Known Limitations",
    )
    assert _count_numbered_markdown_items(readme_section) == expected_known_limitations
    config_flow_rule = _as_mapping(rules["config-flow-test-coverage"])
    config_flow_comment = _as_str(config_flow_rule["comment"])
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
    customizations = _as_mapping(devcontainer["customizations"])
    vscode = _as_mapping(customizations["vscode"])
    settings = _as_mapping(vscode["settings"])
    assert _as_str(settings["python.defaultInterpreterPath"]).endswith("/.venv/bin/python")



def test_maintainer_appendix_routes_to_latest_archived_evidence_without_polluting_public_first_hop() -> None:
    docs_readme_text = _DOCS_README.read_text(encoding="utf-8")
    readme_text = _README.read_text(encoding="utf-8")
    readme_zh_text = _README_ZH.read_text(encoding="utf-8")

    for token in (
        "docs/MAINTAINER_RELEASE_RUNBOOK.md",
        "latest archived evidence index",
        "archived milestone audit",
        "maintainer appendix",
    ):
        assert token in docs_readme_text

    assert ".planning/reviews/V1_21_EVIDENCE_INDEX.md" not in docs_readme_text
    assert ".planning/v1.21-MILESTONE-AUDIT.md" not in docs_readme_text
    assert ".planning/reviews/V1_21_EVIDENCE_INDEX.md" not in readme_text
    assert ".planning/reviews/V1_21_EVIDENCE_INDEX.md" not in readme_zh_text
    assert ".planning/v1.21-MILESTONE-AUDIT.md" not in readme_text
    assert ".planning/v1.21-MILESTONE-AUDIT.md" not in readme_zh_text
