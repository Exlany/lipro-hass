"""Version metadata consistency checks."""

from __future__ import annotations

import json
from pathlib import Path
import re
import tomllib
from typing import Any

import yaml

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_PYPROJECT = _ROOT / "pyproject.toml"
_MANIFEST = _ROOT / "custom_components" / "lipro" / "manifest.json"
_HACS = _ROOT / "hacs.json"
_BASE_CONST = _ROOT / "custom_components" / "lipro" / "const" / "base.py"
_BUG_TEMPLATE = _ROOT / ".github" / "ISSUE_TEMPLATE" / "bug.yml"
_README = _ROOT / "README.md"
_README_ZH = _ROOT / "README_zh.md"
_CONTRIBUTING = _ROOT / "CONTRIBUTING.md"
_SUPPORT = _ROOT / "SUPPORT.md"
_SECURITY = _ROOT / "SECURITY.md"
_TROUBLESHOOTING = _ROOT / "docs" / "TROUBLESHOOTING.md"
_RUNBOOK = _ROOT / "docs" / "MAINTAINER_RELEASE_RUNBOOK.md"
_CI_WORKFLOW = _ROOT / ".github" / "workflows" / "ci.yml"
_ISSUE_CONFIG = _ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"
_V1_2_EVIDENCE_INDEX = _ROOT / ".planning" / "reviews" / "V1_2_EVIDENCE_INDEX.md"
_PHASE_15_PRD = (
    _ROOT
    / ".planning"
    / "phases"
    / "15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through"
    / "15-PRD.md"
)
_PHASE_15_CONTEXT = (
    _ROOT
    / ".planning"
    / "phases"
    / "15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through"
    / "15-CONTEXT.md"
)

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
    install_method_field = next(item for item in body if item.get("id") == "install-method")
    options = install_method_field["attributes"]["options"]

    assert "HACS" in options
    assert any("Shell" in option for option in options)
    assert any("shell_command" in option for option in options)
    assert any("Manual" in option for option in options)


def test_bug_report_template_keeps_developer_report_as_optional_escalation_path() -> None:
    """Developer report should remain an escalation path, not a hard bug-report gate."""
    template = _load_yaml(_BUG_TEMPLATE)
    checklist = next(item for item in template["body"] if item["type"] == "checkboxes")
    labels = {option["label"]: option.get("required", False) for option in checklist["attributes"]["options"]}
    optional_label = next(label for label in labels if "diagnostics were not enough" in label or "diagnostics 不足" in label)

    assert labels[optional_label] is False

    method_field = next(item for item in template["body"] if item.get("id") == "developer-feedback-method")
    report_field = next(item for item in template["body"] if item.get("id") == "developer-report")

    assert any("Not available" in option for option in method_field["attributes"]["options"])
    assert report_field["validations"]["required"] is False
    assert "Optional unless diagnostics still cannot explain the issue" in report_field["attributes"]["description"]


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
        _PHASE_15_PRD,
        _PHASE_15_CONTEXT,
    ):
        _assert_contains_version(path, ha_version)


def test_private_repo_hacs_caveat_is_consistent() -> None:
    """Docs and CI should say the same thing about private-repo HACS validation."""
    for path in (_README, _README_ZH, _CONTRIBUTING, _SUPPORT, _SECURITY, _TROUBLESHOOTING, _RUNBOOK, _BUG_TEMPLATE, _CI_WORKFLOW):
        _assert_contains_private_repo_hacs_caveat(path)



def test_release_runbook_references_v1_2_evidence_index() -> None:
    """Maintainer runbook should point at the canonical v1.2 evidence index."""
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")
    evidence_text = _V1_2_EVIDENCE_INDEX.read_text(encoding="utf-8")

    assert "V1_2_EVIDENCE_INDEX.md" in runbook_text
    assert "## Pull Contract" in evidence_text
    assert "archive-ready" in evidence_text


def test_release_docs_capture_supply_chain_posture_and_firmware_defer() -> None:
    """Runbook and closeout index should keep current release hardening plus explicit defers visible."""
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")
    evidence_text = _V1_2_EVIDENCE_INDEX.read_text(encoding="utf-8")

    for token in ("SHA256SUMS", "provenance", "SBOM", "signing", "code scanning"):
        assert token in runbook_text
        assert token in evidence_text
    assert "firmware_support_manifest.json" in runbook_text
    assert "firmware manifest metadata" in evidence_text
    assert "23-01~23-08-SUMMARY.md" in evidence_text


def test_issue_config_routes_docs_to_troubleshooting() -> None:
    """Issue contact links should route documentation requests to troubleshooting."""
    config = _load_yaml(_ISSUE_CONFIG)
    doc_link = next(link for link in config["contact_links"] if "Documentation" in link["name"])

    assert doc_link["url"].endswith("docs/TROUBLESHOOTING.md")
