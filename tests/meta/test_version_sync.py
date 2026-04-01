"""Version metadata consistency checks."""

from __future__ import annotations

import json
from pathlib import Path
import re
import tomllib
from typing import Any

import yaml

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_runbook_points_to_latest_evidence
from .governance_current_truth import LATEST_ARCHIVED_EVIDENCE_FILENAME

_ROOT = repo_root(Path(__file__))
_PYPROJECT = _ROOT / "pyproject.toml"
_MANIFEST = _ROOT / "custom_components" / "lipro" / "manifest.json"
_HACS = _ROOT / "hacs.json"
_BASE_CONST = _ROOT / "custom_components" / "lipro" / "const" / "base.py"
_BUG_TEMPLATE = _ROOT / ".github" / "ISSUE_TEMPLATE" / "bug.yml"
_FEATURE_TEMPLATE = _ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml"
_README = _ROOT / "README.md"
_README_ZH = _ROOT / "README_zh.md"
_CONTRIBUTING = _ROOT / "CONTRIBUTING.md"
_SUPPORT = _ROOT / "SUPPORT.md"
_SECURITY = _ROOT / "SECURITY.md"
_TROUBLESHOOTING = _ROOT / "docs" / "TROUBLESHOOTING.md"
_RUNBOOK = _ROOT / "docs" / "MAINTAINER_RELEASE_RUNBOOK.md"
_CI_WORKFLOW = _ROOT / ".github" / "workflows" / "ci.yml"
_ISSUE_CONFIG = _ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"
_PR_TEMPLATE = _ROOT / ".github" / "pull_request_template.md"
_GOVERNANCE_REGISTRY = _ROOT / ".planning" / "baseline" / "GOVERNANCE_REGISTRY.json"

_BASE_VERSION_RE = re.compile(r'^VERSION:\s+Final\s*=\s*"(?P<version>[^"]+)"\s*$')


def _read_base_version() -> str:
    for line in _BASE_CONST.read_text(encoding="utf-8").splitlines():
        if match := _BASE_VERSION_RE.match(line.strip()):
            return match.group("version")
    raise AssertionError("Could not find VERSION constant in const/base.py")


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _load_governance_registry() -> dict[str, Any]:
    registry = json.loads(_GOVERNANCE_REGISTRY.read_text(encoding="utf-8"))
    assert isinstance(registry, dict)
    return registry


def _template_field_ids(path: Path) -> set[str]:
    body = _load_yaml(path)["body"]
    assert isinstance(body, list)
    return {
        item["id"]
        for item in body
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _read_python_requires() -> str:
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    requires_python = pyproject["project"]["requires-python"]
    assert isinstance(requires_python, str)
    return requires_python


def _assert_uses_tagged_release_projection(url: str, version: str) -> None:
    assert f"/blob/v{version}/" in url
    assert "/blob/main/" not in url


def _read_homeassistant_version() -> str:
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    dev_deps: list[str] = pyproject["project"]["optional-dependencies"]["dev"]
    ha_pin = next(dep for dep in dev_deps if dep.startswith("homeassistant=="))
    return ha_pin.split("==", 1)[1]


def _assert_contains_version(path: Path, version: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert version in text, f"{path} does not mention canonical HA version {version}"


def _assert_contains_private_repo_hacs_caveat(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert "HACS" in text
    assert ("private" in text.lower()) or ("私有" in text)
    assert ("public GitHub repositories" in text) or ("公开 GitHub 仓库" in text)


def test_integration_version_is_consistent() -> None:
    """pyproject.toml, manifest.json and const/base.py should agree on version."""
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))

    assert (
        manifest["version"] == pyproject["project"]["version"] == _read_base_version()
    )


def test_project_and_manifest_doc_urls_track_release_tag() -> None:
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    version = pyproject["project"]["version"]
    urls = pyproject["project"]["urls"]

    for key in ("Documentation", "Access Mode", "Support", "Security", "Changelog"):
        _assert_uses_tagged_release_projection(urls[key], version)

    for url in (manifest["documentation"], manifest["issue_tracker"]):
        _assert_uses_tagged_release_projection(url, version)


def test_homeassistant_min_version_is_consistent() -> None:
    """Keep Home Assistant version pin consistent across repo metadata."""
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    hacs = json.loads(_HACS.read_text(encoding="utf-8"))
    ha_version = _read_homeassistant_version()

    assert "homeassistant" not in manifest
    assert hacs["homeassistant"] == ha_version


def test_bug_report_template_tracks_homeassistant_min_version() -> None:
    """Bug report template should show the canonical minimum supported HA version."""
    template = _load_yaml(_BUG_TEMPLATE)
    body = template["body"]
    ha_field = next(item for item in body if item.get("id") == "ha-version")
    attributes = ha_field["attributes"]
    ha_version = _read_homeassistant_version()

    assert ha_version in attributes["description"]
    assert ha_version in attributes["placeholder"]


def test_bug_report_template_lists_supported_install_methods() -> None:
    """Bug report template should cover the supported installation paths."""
    template = _load_yaml(_BUG_TEMPLATE)
    body = template["body"]
    install_method_field = next(
        item for item in body if item.get("id") == "install-method"
    )
    options = install_method_field["attributes"]["options"]

    assert any("HACS" in option for option in options)
    assert any("Shell" in option for option in options)
    assert any("shell_command" in option for option in options)
    assert any("Manual" in option for option in options)


def test_governance_registry_tracks_version_and_install_defaults() -> None:
    registry = _load_governance_registry()
    install_text = (_ROOT / "install.sh").read_text(encoding="utf-8")

    assert registry["homeassistant"]["minimum_version"] == _read_homeassistant_version()
    assert registry["homeassistant"]["source"] == "hacs.json"
    assert registry["homeassistant"]["sync_source"] == "pyproject.toml"
    assert registry["python"]["requires_python"] == _read_python_requires()
    assert registry["install"]["remote_default_archive_tag"] == "latest"
    assert registry["install"]["private_repo_skips_hacs_validation"] is True
    assert 'ARCHIVE_TAG="latest"' in install_text


def test_docs_index_route_is_consistent() -> None:
    registry = _load_governance_registry()
    issue_config = _load_yaml(_ISSUE_CONFIG)
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    docs_link = next(
        link for link in issue_config["contact_links"] if "Documentation" in link["name"]
    )

    assert registry["docs"]["index_route"] == "docs/README.md"
    assert registry["support"]["documentation_route"] == "docs/README.md"
    assert registry["continuity"]["drill_name"] == "maintainer-unavailable drill"
    assert pyproject["project"]["urls"]["Documentation"].endswith("/docs/README.md")
    assert manifest["documentation"].endswith("/docs/README.md")
    assert manifest["issue_tracker"].endswith("/SUPPORT.md")
    assert docs_link["url"].endswith("/docs/README.md")


def test_public_fast_path_and_documentation_contact_link_stay_aligned() -> None:
    registry = _load_governance_registry()
    docs = registry["docs"]
    assert isinstance(docs, dict)

    assert docs["public_fast_path"] == [
        "README.md",
        "README_zh.md",
        "CONTRIBUTING.md",
        "docs/TROUBLESHOOTING.md",
        "SUPPORT.md",
        "SECURITY.md",
    ]
    for relative_path in docs["public_fast_path"]:
        assert (_ROOT / relative_path).exists()

    issue_config = _load_yaml(_ISSUE_CONFIG)
    docs_link = next(
        link for link in issue_config["contact_links"] if "Documentation" in link["name"]
    )
    assert docs_link["url"].endswith(f"/{docs['index_route']}")
    assert "docs-first route stays canonical" in docs_link["about"]
    assert "repository access" in docs_link["about"]


def test_governance_registry_projection_targets_are_current() -> None:
    registry = _load_governance_registry()

    assert registry["continuity"]["projection_targets"] == [
        "CONTRIBUTING.md",
        "docs/README.md",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/pull_request_template.md",
    ]
    for relative_path in registry["continuity"]["projection_targets"]:
        assert (_ROOT / relative_path).exists()


def test_community_health_registry_tracks_intake_contract_surfaces() -> None:
    registry = _load_governance_registry()
    community_health = registry["community_health"]
    assert isinstance(community_health, dict)

    bug_required_ids = {
        "problem-type",
        "device-type",
        "affected-area",
        "description",
        "steps",
        "impact-scope",
        "ha-version",
        "integration-version",
        "install-method",
        "troubleshooting-tried",
        "logs",
    }
    feature_required_ids = {
        "feature-type",
        "device-type",
        "affected-area",
        "solution",
        "use-case-impact",
        "acceptance-signal",
    }

    assert set(community_health["pr_sections"]) == {
        "Affected boundary / scope",
        "Risk / impact",
        "Validation commands",
    }
    assert bug_required_ids <= set(community_health["bug_form_required_ids"])
    assert feature_required_ids <= set(community_health["feature_form_required_ids"])
    assert community_health["projection_targets"] == [
        "CONTRIBUTING.md",
        "SUPPORT.md",
        "SECURITY.md",
        "docs/README.md",
        ".github/ISSUE_TEMPLATE/bug.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        ".github/pull_request_template.md",
    ]

    assert set(community_health["bug_form_required_ids"]) <= _template_field_ids(_BUG_TEMPLATE)
    assert set(community_health["feature_form_required_ids"]) <= _template_field_ids(
        _FEATURE_TEMPLATE
    )

    security_text = _SECURITY.read_text(encoding="utf-8")
    pr_text = _PR_TEMPLATE.read_text(encoding="utf-8")
    for token in community_health["security_intake_evidence"]:
        assert token in security_text
    for heading in community_health["pr_sections"]:
        assert f"## {heading}" in pr_text
    for relative_path in community_health["projection_targets"]:
        assert (_ROOT / relative_path).exists()


def test_bug_report_template_keeps_developer_report_as_optional_escalation_path() -> (
    None
):
    """Developer report should remain an escalation path, not a hard bug-report gate."""
    template = _load_yaml(_BUG_TEMPLATE)
    checklist = next(item for item in template["body"] if item["type"] == "checkboxes")
    labels = {
        option["label"]: option.get("required", False)
        for option in checklist["attributes"]["options"]
    }
    optional_label = next(
        label
        for label in labels
        if "diagnostics were not enough" in label or "diagnostics 不足" in label
    )

    assert labels[optional_label] is False

    method_field = next(
        item
        for item in template["body"]
        if item.get("id") == "developer-feedback-method"
    )
    report_field = next(
        item for item in template["body"] if item.get("id") == "developer-report"
    )

    assert any(
        "Not available" in option for option in method_field["attributes"]["options"]
    )
    assert report_field["validations"]["required"] is False
    assert (
        "Optional unless diagnostics still cannot explain the issue"
        in report_field["attributes"]["description"]
    )


def test_public_docs_track_homeassistant_min_version() -> None:
    """User-facing docs should surface the canonical minimum supported HA version."""
    ha_version = _read_homeassistant_version()

    for path in (
        _README,
        _README_ZH,
        _CONTRIBUTING,
        _SUPPORT,
        _SECURITY,
        _TROUBLESHOOTING,
        _RUNBOOK,
    ):
        _assert_contains_version(path, ha_version)


def test_private_repo_hacs_caveat_is_consistent() -> None:
    """Docs and CI should say the same thing about private-repo HACS validation."""
    for path in (
        _README,
        _README_ZH,
        _CONTRIBUTING,
        _SUPPORT,
        _SECURITY,
        _TROUBLESHOOTING,
        _RUNBOOK,
        _BUG_TEMPLATE,
        _CI_WORKFLOW,
    ):
        _assert_contains_private_repo_hacs_caveat(path)


def test_release_runbook_references_v1_19_evidence_index() -> None:
    """Maintainer runbook should point at the canonical latest closeout evidence index."""
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")

    assert_runbook_points_to_latest_evidence(
        runbook_text,
        LATEST_ARCHIVED_EVIDENCE_FILENAME,
        deprecated=("V1_18_EVIDENCE_INDEX.md", "V1_6_EVIDENCE_INDEX.md"),
    )


def test_runbook_and_contributing_capture_blocking_release_security_gate() -> None:
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")
    contributing_text = _CONTRIBUTING.read_text(encoding="utf-8")

    assert "tagged release security gate" in runbook_text
    assert "CodeQL" in runbook_text
    assert "gh attestation verify" in runbook_text
    assert "cosign verify-blob --bundle" in runbook_text
    assert "release identity manifest" in runbook_text
    assert "tagged release security gate" in contributing_text
    assert "CodeQL" in contributing_text
    assert "cosign" in contributing_text
    assert "release identity manifest" in contributing_text


def test_runbook_captures_release_artifact_install_smoke_contract() -> None:
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")

    for token in (
        "release artifact install smoke",
        "temporary Home Assistant-style target tree",
        "configuration.yaml",
        ".storage",
        "--archive-file",
        "--checksum-file",
    ):
        assert token in runbook_text


def test_preview_lane_docs_keep_stable_contract_honest() -> None:
    support_text = _SUPPORT.read_text(encoding="utf-8")
    contributing_text = _CONTRIBUTING.read_text(encoding="utf-8")
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")

    for text in (support_text, contributing_text, runbook_text):
        lowered = text.lower()
        assert "compatibility preview" in lowered
        assert "schedule" in lowered
        assert "workflow_dispatch" in lowered
        assert "advisory" in lowered
    assert "stable support target" in support_text
    assert "stable PR / release / support contract" in contributing_text
    assert "stable release contract" in runbook_text
    assert "DeprecationWarning" in contributing_text
    assert "deprecationwarning" in runbook_text.lower()


def test_release_docs_capture_supply_chain_posture_and_latest_closeout_contract() -> None:
    """Runbook keeps release hardening truth while still pointing at the latest archived closeout index."""
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")

    for token in ("SHA256SUMS", "provenance", "SBOM", "signing"):
        assert token in runbook_text
    assert_runbook_points_to_latest_evidence(
        runbook_text,
        LATEST_ARCHIVED_EVIDENCE_FILENAME,
        deprecated=("V1_6_EVIDENCE_INDEX.md",),
    )
    assert "release artifact install smoke" in runbook_text
    assert "CodeQL" in runbook_text
    assert "cosign" in runbook_text
    assert "gh attestation verify" in runbook_text
    assert "release identity manifest" in runbook_text
    assert "tagged release security gate" in runbook_text
    assert "firmware_support_manifest.json" in runbook_text


def test_issue_config_routes_docs_to_index() -> None:
    """Issue contact links should route documentation requests to the docs index."""
    config = _load_yaml(_ISSUE_CONFIG)
    doc_link = next(
        link for link in config["contact_links"] if "Documentation" in link["name"]
    )

    assert doc_link["url"].endswith("docs/README.md")


def test_project_urls_keep_private_access_routes_honest() -> None:
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    urls = pyproject["project"]["urls"]

    assert urls["Documentation"].endswith("docs/README.md")
    assert urls["Access Mode"].endswith("README.md")
    assert urls["Support"].endswith("SUPPORT.md")
    assert urls["Security"].endswith("SECURITY.md")
    assert "Discussions" not in urls
    assert "Issues" not in urls


def test_open_source_surface_registry_marks_schema_limited_metadata() -> None:
    registry = _load_governance_registry()
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    surface = registry["open_source_surface"]

    assert surface["access_mode"] == "private-access"
    assert surface["access_mode_entrypoint"] == "README.md"
    assert surface["docs_first"] is True
    assert surface["github_surfaces_conditional"] is True
    assert surface["non_github_private_fallback_documented"] is False
    assert surface["developer_services_debug_mode_only"] is True
    assert surface["developer_report_redaction"] == "partial"
    assert surface["anonymous_share_terms"] == ["sanitized", "pseudonymous"]
    assert surface["schema_limited_projections"] == [
        "pyproject.toml::project.urls",
        "custom_components/lipro/manifest.json::documentation",
        "custom_components/lipro/manifest.json::issue_tracker",
        ".github/ISSUE_TEMPLATE/config.yml::contact_links",
    ]
    assert pyproject["project"]["urls"]["Access Mode"].endswith("/README.md")
    assert manifest["documentation"].endswith("/docs/README.md")
    assert manifest["issue_tracker"].endswith("/SUPPORT.md")


def test_package_metadata_marks_stable_release_posture() -> None:
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    classifiers = pyproject["project"]["classifiers"]

    assert "Development Status :: 5 - Production/Stable" in classifiers
    assert "Development Status :: 4 - Beta" not in classifiers


def test_runtime_dependency_bounds_are_explicit_and_manifest_aligned() -> None:
    """Runtime dependency bounds should stay explicit across package metadata."""
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))

    runtime_deps = set(pyproject["project"]["dependencies"])
    manifest_requirements = set(manifest["requirements"])

    assert runtime_deps == {
        "aiohttp>=3.12.0,<4.0.0",
        "aiomqtt>=2.0.0,<3.0.0",
        "pycryptodome>=3.19.0,<4.0.0",
        "voluptuous>=0.15.2,<1.0.0",
    }
    assert manifest_requirements == {
        "aiomqtt>=2.0.0,<3.0.0",
        "pycryptodome>=3.19.0,<4.0.0",
    }
    assert manifest_requirements <= runtime_deps
