"""Focused guards for Phase 114 open-source surface honesty."""

from __future__ import annotations

import json
from pathlib import Path
import tomllib

import yaml

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot

_ROOT = repo_root(Path(__file__))
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_GOVERNANCE_REGISTRY = _ROOT / ".planning" / "baseline" / "GOVERNANCE_REGISTRY.json"
_ISSUE_CONFIG = _ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"
_LINT = _ROOT / "scripts" / "lint"
_PYPROJECT = _ROOT / "pyproject.toml"
_README = _ROOT / "README.md"
_README_ZH = _ROOT / "README_zh.md"
_SECURITY = _ROOT / "SECURITY.md"
_SERVICES = _ROOT / "custom_components" / "lipro" / "services.yaml"
_SUPPORT = _ROOT / "SUPPORT.md"
_TESTING = _ROOT / ".planning" / "codebase" / "TESTING.md"
_VERIFICATION_MATRIX = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> dict[str, object]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _load_yaml(path: Path) -> dict[str, object]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_phase114_registry_and_metadata_keep_projection_truth() -> None:
    registry = _load_json(_GOVERNANCE_REGISTRY)
    pyproject = tomllib.loads(_read(_PYPROJECT))
    issue_config = _load_yaml(_ISSUE_CONFIG)
    surface = registry["open_source_surface"]
    security_link = next(
        link for link in issue_config["contact_links"] if "Security" in str(link["name"])
    )

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
    assert "no guaranteed non-github private fallback" in str(security_link["about"]).lower()


def test_phase114_public_docs_and_services_keep_honest_wording() -> None:
    readme_text = _read(_README)
    readme_zh_text = _read(_README_ZH)
    support_text = _read(_SUPPORT)
    security_text = _read(_SECURITY)
    services_text = _read(_SERVICES)

    for token in (
        "private-access",
        "future public mirror",
        "sanitized/pseudonymous",
        "credential-equivalent secret",
        "debug-mode-only",
    ):
        assert token in readme_text

    for token in (
        "已脱敏/伪匿名",
        "public mirror",
    ):
        assert token in readme_zh_text

    assert "No guaranteed non-GitHub private fallback is documented today." in support_text
    assert "no guaranteed non-github private fallback is documented today" in security_text.lower()
    assert "Debug-mode-only capability" in services_text
    assert "partially redacted runtime diagnostics report" in services_text
    assert "sanitized/pseudonymous" in services_text


def test_phase114_scripts_lint_help_keeps_changed_surface_truth() -> None:
    lint_text = _read(_LINT)

    assert "Runs local static + translation + docs-route + shell + runtime security checks." in lint_text
    assert "It may also run focused pytest/governance assurance when matching changed surfaces are touched." in lint_text


def test_phase114_ledgers_record_honesty_guard_chain() -> None:
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)
    file_matrix_text = _read(_FILE_MATRIX)

    assert_testing_inventory_snapshot(testing_text)
    for text in (testing_text, verification_text, file_matrix_text):
        assert "Phase 114" in text
        assert "tests/meta/test_phase114_open_source_surface_honesty_guards.py" in text

    assert "schema-limited metadata projection" in testing_text
    assert "schema-limited metadata projections" in verification_text
