"""Docs, continuity, and machine-readable fast-path truth guards."""

from __future__ import annotations

import json
from pathlib import Path
import tomllib

import yaml

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import _assert_public_docs_hide_internal_route_story
from .governance_current_truth import (
    LATEST_ARCHIVED_EVIDENCE_FILENAME,
    LEGACY_ARCHIVED_CLOSEOUT_POINTER_LABEL,
)

_ROOT = repo_root(Path(__file__))

_PYPROJECT = _ROOT / "pyproject.toml"

_README = _ROOT / "README.md"

_README_ZH = _ROOT / "README_zh.md"

_SUPPORT = _ROOT / "SUPPORT.md"

_SECURITY = _ROOT / "SECURITY.md"

_RUNBOOK = _ROOT / "docs" / "MAINTAINER_RELEASE_RUNBOOK.md"
_TROUBLESHOOTING = _ROOT / "docs" / "TROUBLESHOOTING.md"

_DOCS_README = _ROOT / "docs" / "README.md"

_GOVERNANCE_REGISTRY = _ROOT / ".planning" / "baseline" / "GOVERNANCE_REGISTRY.json"

_ADR_README = _ROOT / "docs" / "adr" / "README.md"

_ADR_0004 = _ROOT / "docs" / "adr" / "0004-explicit-lightweight-boundaries.md"

_PUBLIC_SURFACES = _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"

_DEPENDENCY_MATRIX = _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"

_RESIDUAL_LEDGER = _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"



def _load_yaml(path: Path):
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    if True in loaded and "on" not in loaded:
        loaded["on"] = loaded.pop(True)
    return loaded



def _load_governance_registry():
    loaded = json.loads(_GOVERNANCE_REGISTRY.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded



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




def test_docs_index_keeps_internal_route_story_out_of_public_fast_path() -> None:
    docs_text = _DOCS_README.read_text(encoding="utf-8")

    _assert_public_docs_hide_internal_route_story(
        docs_text,
        LEGACY_ARCHIVED_CLOSEOUT_POINTER_LABEL,
        LATEST_ARCHIVED_EVIDENCE_FILENAME,
    )



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
    assert registry["continuity"]["drill_name"] == "maintainer-unavailable drill"
    assert registry["continuity"]["documented_delegate"] is False
    assert registry["docs"]["index_route"] == "docs/README.md"
    assert registry["tooling"]["retired_stub_exit_code"] == 2
    assert registry["tooling"]["compatibility_stub_role"] == "retired fail-fast migration hint only"
    assert "migration hints" in registry["tooling"]["compatibility_stub_delete_gate"]
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
        assert registry["continuity"]["drill_name"] in text.lower()



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
    open_source_surface = registry["open_source_surface"]
    discussions_link = next(
        link for link in issue_config["contact_links"] if "Discussions" in link["name"]
    )
    security_link = next(
        link for link in issue_config["contact_links"] if "Security" in link["name"]
    )

    assert registry["continuity"]["projection_targets"] == [
        "CONTRIBUTING.md",
        "docs/README.md",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/pull_request_template.md",
    ]
    assert registry["support"]["documentation_route"] == "docs/README.md"
    assert registry["docs"]["index_route"] == "docs/README.md"
    assert open_source_surface["access_mode"] == "private-access"
    assert open_source_surface["access_mode_entrypoint"] == "README.md"
    assert open_source_surface["docs_first"] is True
    assert open_source_surface["github_surfaces_conditional"] is True
    assert open_source_surface["non_github_private_fallback_documented"] is False
    assert open_source_surface["developer_services_debug_mode_only"] is True
    assert open_source_surface["developer_report_redaction"] == "partial"
    assert open_source_surface["anonymous_share_terms"] == ["sanitized", "pseudonymous"]
    assert open_source_surface["schema_limited_projections"] == [
        "pyproject.toml::project.urls",
        "custom_components/lipro/manifest.json::documentation",
        "custom_components/lipro/manifest.json::issue_tracker",
        ".github/ISSUE_TEMPLATE/config.yml::contact_links",
    ]
    assert pyproject["project"]["urls"]["Documentation"].endswith("/docs/README.md")
    assert pyproject["project"]["urls"]["Access Mode"].endswith("/README.md")
    assert pyproject["project"]["urls"]["Support"].endswith("/SUPPORT.md")
    assert pyproject["project"]["urls"]["Security"].endswith("/SECURITY.md")
    assert "Discussions" not in pyproject["project"]["urls"]
    assert "Issues" not in pyproject["project"]["urls"]
    assert docs_link["url"].endswith("/docs/README.md")
    assert "docs-first" in docs_link["about"]
    assert "access mode" in discussions_link["about"].lower()
    assert "access mode" in security_link["about"].lower()
    assert "no guaranteed non-github private fallback" in security_link["about"].lower()
    assert "Community-Health Contract" in docs_text
    assert "private-access" in docs_text
    assert "maintainer appendix" in docs_text.lower()
    assert "internal governance paths" in docs_text
    assert ".planning/baseline/GOVERNANCE_REGISTRY.json" in contributing_text
    assert "private-access" in docs_text
    assert "private-access" in contributing_text
    for token in registry["tooling"]["active_entrypoints"]:
        assert token in docs_text
    for token in registry["tooling"]["compatibility_stubs"]:
        assert token in docs_text
    assert "docs/README.md" in contributing_text
    assert "maintained docs / automation still need those names as migration hints" in contributing_text
    assert "migration hint" in docs_text
    assert "return 2" in worker_text
    assert "return 2" in orchestrator_text
    assert "Use docs/README.md and CONTRIBUTING.md" in worker_text
    assert "Use docs/README.md and CONTRIBUTING.md" in orchestrator_text
    assert "exit successfully" not in worker_text
    assert "exit successfully" not in orchestrator_text
    assert "历史重构档案不再保留在仓库中" not in worker_text
    assert "历史重构档案不再保留在仓库中" not in orchestrator_text
