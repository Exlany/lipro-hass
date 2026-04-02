"""Release continuity and custody governance contract suite."""

from __future__ import annotations

from .conftest import (
    _CODEOWNERS,
    _CONTRIBUTING,
    _DOCS_README,
    _ISSUE_CONFIG,
    _MANIFEST,
    _PR_TEMPLATE,
    _README,
    _README_ZH,
    _ROOT,
    _RUNBOOK,
    _SECURITY,
    _SUPPORT,
    _as_mapping,
    _as_mapping_list,
    _as_str,
    _extract_markdown_section,
    _load_json,
    _load_yaml,
    _parse_codeowners_handles,
)
from .governance_contract_helpers import _assert_public_docs_hide_internal_route_story
from .governance_current_truth import (
    LATEST_ARCHIVED_EVIDENCE_FILENAME,
    LATEST_ARCHIVED_EVIDENCE_LABEL,
    LATEST_ARCHIVED_EVIDENCE_PATH,
)

_CODEQL_WORKFLOW = _ROOT / ".github" / "workflows" / "codeql.yml"
_GOVERNANCE_REGISTRY = _ROOT / ".planning" / "baseline" / "GOVERNANCE_REGISTRY.json"

def test_latest_closeout_pointer_and_archived_route_stay_current() -> None:
    milestones_text = (_ROOT / ".planning" / "MILESTONES.md").read_text(encoding="utf-8")
    docs_text = _DOCS_README.read_text(encoding="utf-8")
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")

    _assert_public_docs_hide_internal_route_story(docs_text)
    assert LATEST_ARCHIVED_EVIDENCE_FILENAME in runbook_text
    assert "V1_6_EVIDENCE_INDEX.md" not in runbook_text
    assert "## v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement" in milestones_text
    assert f"{LATEST_ARCHIVED_EVIDENCE_LABEL} = `{LATEST_ARCHIVED_EVIDENCE_PATH}`" in milestones_text
    assert "v1.11" not in docs_text
    assert "v1.11" not in runbook_text

def test_security_disclosure_path_is_present() -> None:
    security_text = _SECURITY.read_text(encoding="utf-8")
    registry = _load_json(_GOVERNANCE_REGISTRY)
    open_source_surface = _as_mapping(registry["open_source_surface"])
    issue_config = _load_yaml(_ISSUE_CONFIG)
    contact_links = _as_mapping_list(issue_config["contact_links"])
    docs_link = next(
        link for link in contact_links if "Documentation" in _as_str(link["name"])
    )
    security_link = next(
        link for link in contact_links if "Security" in _as_str(link["name"])
    )

    assert "/security/advisories/new" in security_text
    assert "public GitHub issue" in security_text
    assert "private-access" in security_text
    assert "no guaranteed non-github private fallback is documented today" in security_text.lower()
    assert open_source_surface["access_mode"] == "private-access"
    assert open_source_surface["non_github_private_fallback_documented"] is False
    assert _as_str(docs_link["url"]).endswith("/docs/README.md")
    assert "access mode" in _as_str(security_link["about"]).lower()
    assert "no guaranteed non-github private fallback" in _as_str(security_link["about"]).lower()

def test_manifest_codeowners_match_repo_codeowners() -> None:
    manifest = _load_json(_MANIFEST)
    assert manifest.get("codeowners") == _parse_codeowners_handles(
        _CODEOWNERS.read_text(encoding="utf-8")
    )

def test_release_runbook_and_support_docs_expose_continuity_truth() -> None:
    registry = _load_json(_GOVERNANCE_REGISTRY)
    continuity = _as_mapping(registry["continuity"])
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

    for text in (support_text, security_text):
        assert ".github/CODEOWNERS" in text
        assert _as_str(continuity["restore_phrase"]) in text.lower()

    for drill_text in (
        _extract_markdown_section(support_text, "Maintainer-Unavailable Drill"),
        _extract_markdown_section(security_text, "Maintainer-Unavailable Drill"),
    ):
        numbered_lines = [
            line.strip()
            for line in drill_text.splitlines()
            if line.strip().startswith(("1. ", "2. ", "3. ", "4. "))
        ]
        assert len(numbered_lines) == 4
        assert any(
            _as_str(continuity["freeze_phrase"]).lower() in line.lower()
            for line in numbered_lines
        )
        assert any("private" in line.lower() and "path" in line.lower() for line in numbered_lines)
        assert any("continuity gap" in line.lower() for line in numbered_lines)
        assert any(
            _as_str(continuity["restore_phrase"]).lower() in line.lower()
            for line in numbered_lines
        )

def test_support_and_issue_routing_are_consistent() -> None:
    support_text = _SUPPORT.read_text(encoding="utf-8")
    security_text = _SECURITY.read_text(encoding="utf-8")
    contributing_text = _CONTRIBUTING.read_text(encoding="utf-8")
    readme_text = _README.read_text(encoding="utf-8")
    readme_zh_text = _README_ZH.read_text(encoding="utf-8")
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")
    issue_config = _load_yaml(_ISSUE_CONFIG)
    contact_links = _as_mapping_list(issue_config.get("contact_links", []))
    docs_link = next(
        link for link in contact_links if "Documentation" in _as_str(link["name"])
    )
    contact_abouts = [_as_str(link["about"]) for link in contact_links]

    assert "SUPPORT.md" in contributing_text
    assert "SECURITY.md" in contributing_text
    assert "verified release assets" in contributing_text
    assert _as_str(docs_link["url"]).endswith("/docs/README.md")
    assert any("access mode" in about.lower() for about in contact_abouts)
    assert "Discussion" in support_text or "讨论" in support_text
    assert "SECURITY.md" in support_text
    assert "No guaranteed non-GitHub private fallback is documented today." in support_text
    assert "no guaranteed non-github private fallback is documented today" in security_text.lower()
    assert "single-maintainer" in support_text
    assert "verified GitHub Release assets" in support_text
    assert "private-access" in readme_text
    assert "future public mirror" in readme_text
    assert "verified GitHub Release assets" in readme_text
    assert "private-access" in readme_zh_text
    assert "public mirror" in readme_zh_text
    assert "已校验 GitHub Release 资产" in readme_zh_text
    assert "matching HACS install" in runbook_text
    assert "verified GitHub Release assets" in runbook_text
    assert "reachable in the current access mode" in runbook_text
    assert "real public mirror" in runbook_text or "reachable GitHub Release surface" in runbook_text
    assert "Best effort" in security_text or "best effort" in security_text
    assert "verified GitHub Release assets" in security_text

def test_templates_and_governance_docs_keep_continuity_contract() -> None:
    bug_text = (_ROOT / ".github" / "ISSUE_TEMPLATE" / "bug.yml").read_text(
        encoding="utf-8"
    )
    feature_text = (_ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml").read_text(
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
    assert "single-maintainer" in feature_text
    assert "best-effort" in feature_text
    assert "affected area" in feature_text.lower()
    assert "acceptance signal" in feature_text.lower()
    assert "maintenance budget" in feature_text
    assert "docs/README.md" in pr_text
    assert "docs/MAINTAINER_RELEASE_RUNBOOK.md" in pr_text
    assert ".github/CODEOWNERS" in pr_text
    assert "maintainer-unavailable drill" in bug_text.lower()
    assert "maintainer-unavailable drill" in pr_text.lower()
    assert "undocumented delegate" in pr_text
    assert "do not transfer custody" in codeowners_text


def test_codeowners_keeps_single_wildcard_owner() -> None:
    codeowners_text = _CODEOWNERS.read_text(encoding="utf-8")
    wildcard_lines = [
        line.strip() for line in codeowners_text.splitlines() if line.strip().startswith("* ")
    ]

    assert len(wildcard_lines) == 1
    assert _parse_codeowners_handles(codeowners_text) == ["@Exlany"]

def test_support_and_security_share_four_step_maintainer_unavailable_shape() -> None:
    support_section = _extract_markdown_section(
        _SUPPORT.read_text(encoding="utf-8"),
        "Maintainer-Unavailable Drill",
    )
    security_section = _extract_markdown_section(
        _SECURITY.read_text(encoding="utf-8"),
        "Maintainer-Unavailable Drill",
    )

    for section in (support_section, security_section):
        numbered_lines = [
            line.strip()
            for line in section.splitlines()
            if line.strip().startswith(("1. ", "2. ", "3. ", "4. "))
        ]
        assert len(numbered_lines) == 4
        assert ".github/CODEOWNERS" in section
        assert "docs/MAINTAINER_RELEASE_RUNBOOK.md" in section
        assert "restore custody only after" in section.lower()


def test_runbook_and_pr_template_capture_break_glass_and_rehearsal_truth() -> None:
    registry = _load_json(_GOVERNANCE_REGISTRY)
    release_registry = _as_mapping(registry["release"])
    runbook_text = _RUNBOOK.read_text(encoding="utf-8")
    pr_text = _PR_TEMPLATE.read_text(encoding="utf-8")

    for token in (
        _as_str(release_registry["break_glass_verify_only_phrase"]),
        _as_str(release_registry["non_publish_rehearsal_phrase"]),
    ):
        assert token in runbook_text
        assert token in pr_text
