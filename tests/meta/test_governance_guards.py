"""Governance guards for file-matrix coverage and architecture-policy hygiene."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import yaml

from scripts.check_architecture_policy import (
    run_checks as run_architecture_policy_checks,
)
from scripts.check_file_matrix import (
    extract_reported_total,
    iter_python_files,
    parse_file_matrix_paths,
    repo_root,
    run_checks,
)
from tests.helpers.architecture_policy import load_structural_rules, load_targeted_bans

_ROOT = repo_root(Path(__file__))

_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"

_CODEBASE_DIR = _ROOT / ".planning" / "codebase"

_CODEBASE_README = _CODEBASE_DIR / "README.md"

_PRE_COMMIT = _ROOT / ".pre-commit-config.yaml"

_GITIGNORE = _ROOT / ".gitignore"

_DOCS_README = _ROOT / "docs" / "README.md"

_TROUBLESHOOTING = _ROOT / "docs" / "TROUBLESHOOTING.md"

_RUNBOOK = _ROOT / "docs" / "MAINTAINER_RELEASE_RUNBOOK.md"

_README = _ROOT / "README.md"

_README_ZH = _ROOT / "README_zh.md"

_AGENTS = _ROOT / "AGENTS.md"

_CONTRIBUTING = _ROOT / "CONTRIBUTING.md"

_SUPPORT = _ROOT / "SUPPORT.md"

_SECURITY = _ROOT / "SECURITY.md"

_CODE_OF_CONDUCT = _ROOT / "CODE_OF_CONDUCT.md"

_CODEOWNERS = _ROOT / ".github" / "CODEOWNERS"

_MANIFEST = _ROOT / "custom_components" / "lipro" / "manifest.json"

_QUALITY_SCALE = _ROOT / "custom_components" / "lipro" / "quality_scale.yaml"

_DEVCONTAINER = _ROOT / ".devcontainer.json"

_PR_TEMPLATE = _ROOT / ".github" / "pull_request_template.md"

_CI_WORKFLOW = _ROOT / ".github" / "workflows" / "ci.yml"

_RELEASE_WORKFLOW = _ROOT / ".github" / "workflows" / "release.yml"

_ISSUE_CONFIG = _ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"
_GOVERNANCE_REGISTRY = _ROOT / ".planning" / "baseline" / "GOVERNANCE_REGISTRY.json"


def test_file_matrix_covers_workspace_python_inventory() -> None:
    inventory = iter_python_files(_ROOT)
    matrix_text = _FILE_MATRIX.read_text(encoding="utf-8")

    assert extract_reported_total(matrix_text) == len(inventory)
    assert parse_file_matrix_paths(matrix_text) == inventory


def _load_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(?P<frontmatter>.*?)\n---\n", text, flags=re.DOTALL)
    assert match is not None
    loaded = yaml.safe_load(match.group("frontmatter"))
    assert isinstance(loaded, dict)
    return loaded


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    if True in loaded and "on" not in loaded:
        loaded["on"] = loaded.pop(True)
    return loaded


def _load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _extract_markdown_section(text: str, heading_fragment: str) -> str:
    match = re.search(
        rf"^#{{2,}} [^\n]*{re.escape(heading_fragment)}[^\n]*\n(?P<body>.*?)(?=^#{{2,}} |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match, f"Missing section containing heading: {heading_fragment}"
    return match.group("body")


def _extract_labeled_bullets(section_text: str) -> dict[str, str]:
    bullets: dict[str, str] = {}
    for line in section_text.splitlines():
        match = re.match(
            r"- \*\*(?P<label>[^*]+)\*\*[:：]\s*(?P<body>.+)", line.strip()
        )
        if match:
            bullets[match.group("label").strip()] = match.group("body").strip()
    return bullets


def _extract_checklist_labels(text: str) -> dict[str, str]:
    items: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"- \[ \] `(?P<label>[^`]+)`:\s*(?P<body>.+)", line.strip())
        if match:
            items[match.group("label").strip()] = match.group("body").strip()
    return items


def _count_numbered_markdown_items(section_text: str) -> int:
    return len(re.findall(r"^\d+\. ", section_text, flags=re.MULTILINE))


def _parse_codeowners_handles(text: str) -> list[str]:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("* "):
            return stripped.split()[1:]
    raise AssertionError("Missing wildcard CODEOWNERS entry")


def _assert_current_mode_tracks_phase_lifecycle(state_text: str) -> None:
    assert (
        re.search(
            r"\*\*Current mode:\*\* `Phase \d+(?:\.\d+)? [a-z][a-z0-9_ -]+`",
            state_text,
        )
        is not None
        or re.search(r"\*\*Current mode:\*\* `v1\.\d+ archived`", state_text)
        is not None
        or re.search(
            r"\*\*Current mode:\*\* `no active milestone route / latest archived baseline = v1\.\d+`",
            state_text,
        )
        is not None
    )


def _assert_state_preserves_phase_17_closeout_history(state_text: str) -> None:
    assert "`v1.1` 已完成全部计划执行：`15 phases / 58 plans` 全绿落表" in state_text
    assert "- `Phase 17` 已完成：" in state_text

    state_frontmatter = _load_frontmatter(_ROOT / ".planning" / "STATE.md")
    milestone = state_frontmatter["milestone"]
    milestone_name = state_frontmatter["milestone_name"]

    assert f"milestone: {milestone}" in state_text
    assert f"milestone_name: {milestone_name}" in state_text
    if "**Current milestone:** `No active milestone route`" in state_text:
        assert re.search(
            rf"\*\*Current mode:\*\* `no active milestone route / latest archived baseline = {re.escape(str(milestone))}`",
            state_text,
        )
        assert str(milestone_name) in state_text
    else:
        assert f"**Current milestone:** `{milestone} {milestone_name}`" in state_text

    if milestone == "v1.1":
        assert re.search(
            r"\*\*Current mode:\*\* `Phase 17 (?:complete|milestone audit complete)`",
            state_text,
        )
        assert "total_phases: 15" in state_text
        assert "completed_phases: 15" in state_text
        assert "total_plans: 58" in state_text
        assert "completed_plans: 58" in state_text
        return

    if milestone == "v1.2":
        assert re.search(
            r"\*\*Current mode:\*\* `Phase (?:1[89]|[2-9]\d)(?:\.\d+)? [a-z][a-z0-9_ -]+`",
            state_text,
        )
        return

    if milestone == "v1.4":
        assert re.search(
            r"\*\*Current mode:\*\* `Phase 3[4-9](?:\.\d+)? [a-z][a-z0-9_ -]+`",
            state_text,
        )
        return

    _assert_current_mode_tracks_phase_lifecycle(state_text)


def test_governance_checker_reports_no_drift() -> None:
    assert run_checks(_ROOT) == []


def test_architecture_policy_checker_reports_no_drift() -> None:
    assert run_architecture_policy_checks(_ROOT) == []


def test_control_home_truth_is_explicit_and_services_stay_helper_surface() -> None:
    north_star_text = (_ROOT / "docs" / "NORTH_STAR_TARGET_ARCHITECTURE.md").read_text(encoding="utf-8")
    developer_text = (_ROOT / "docs" / "developer_architecture.md").read_text(encoding="utf-8")
    diagnostics_services_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "diagnostics" / "__init__.py"
    ).read_text(encoding="utf-8")

    assert "`custom_components/lipro/control/`" in north_star_text
    assert "formal control-plane home" in developer_text
    assert "`custom_components/lipro/services/`：service declarations" in north_star_text
    assert "helper surface" in developer_text
    assert "legacy carrier" not in diagnostics_services_text


def test_architecture_policy_rule_inventory_is_stable() -> None:
    assert set(load_structural_rules(_ROOT)) == {
        "ENF-IMP-ENTITY-PROTOCOL-INTERNALS",
        "ENF-IMP-CONTROL-NO-BYPASS",
        "ENF-IMP-BOUNDARY-LOCALITY",
        "ENF-GOV-DEPENDENCY-POLICY-REF",
        "ENF-GOV-PUBLIC-SURFACE-POLICY-REF",
        "ENF-GOV-AUTHORITY-POLICY-REF",
        "ENF-GOV-VERIFICATION-POLICY-REF",
        "ENF-GOV-CI-FAIL-FAST",
        "ENF-GOV-RELEASE-CI-REUSE",
        "ENF-IMP-API-LEGACY-SPINE-LOCALITY",
        "ENF-IMP-MQTT-TRANSPORT-LOCALITY",
        "ENF-IMP-NUCLEUS-NO-HOMEASSISTANT-IMPORT",
        "ENF-IMP-NUCLEUS-NO-PLATFORM-BACKFLOW",
        "ENF-IMP-HEADLESS-PROOF-LOCALITY",
        "ENF-IMP-PLATFORM-SHELL-NO-CONTROL-LOCATOR",
        "ENF-IMP-ASSURANCE-NO-PRODUCTION-BACKFLOW",
    }
    assert set(load_targeted_bans(_ROOT)) == {
        "ENF-SURFACE-COORDINATOR-ENTRY",
        "ENF-SURFACE-API-EXPORTS",
        "ENF-SURFACE-PROTOCOL-EXPORTS",
        "ENF-BACKDOOR-COORDINATOR-PROPERTIES",
        "ENF-BACKDOOR-SERVICE-AUTH",
        "ENF-COMPAT-ROOT-NO-LEGACY-CLIENT",
        "ENF-COMPAT-CONFIG-FLOW-NO-LEGACY-CLIENT",
        "ENF-COMPAT-CORE-PACKAGE-NO-LEGACY-CLIENTS",
        "ENF-COMPAT-MQTT-PACKAGE-NO-LEGACY-CLIENT",
        "ENF-ADAPTER-CONFIG-FLOW-USES-AUTH-PROJECTION",
        "ENF-ADAPTER-ENTRY-AUTH-USES-BOOTSTRAP",
        "ENF-HOSTPROJ-CATEGORIES-NO-HA-PLATFORMS",
        "ENF-HOSTPROJ-CAPABILITY-NO-PLATFORM-FIELD",
        "ENF-HOSTPROJ-DEVICE-VIEWS-NO-PLATFORM-PROJECTION",
        "ENF-PROOF-HEADLESS-PACKAGE-NO-EXPORTS",
        "ENF-PROOF-HEADLESS-BOOT-NO-SECOND-ROOT-BACKFLOW",
    }


def test_phase_asset_identity_is_documented_consistently() -> None:
    docs_bullets = _extract_labeled_bullets(
        _extract_markdown_section(
            _DOCS_README.read_text(encoding="utf-8"),
            "Phase 资产身份与开源治理",
        )
    )
    agents_bullets = _extract_labeled_bullets(
        _extract_markdown_section(
            _AGENTS.read_text(encoding="utf-8"),
            "Phase 资产身份与开源治理",
        )
    )

    for bullets in (docs_bullets, agents_bullets):
        assert {"默认身份", "提升条件", "发布门禁", "对外入口"} <= set(bullets)
        assert ".planning/phases/**" in bullets["默认身份"]
        assert ".planning/ROADMAP.md" in bullets["提升条件"]
        assert ".planning/baseline/VERIFICATION_MATRIX.md" in bullets["提升条件"]
        assert ".github/workflows/ci.yml" in bullets["发布门禁"]
        assert ".github/workflows/release.yml" in bullets["发布门禁"]
        assert "CONTRIBUTING.md" in bullets["对外入口"]
        assert "SECURITY.md" in bullets["对外入口"]


def test_codebase_maps_are_explicitly_derived_assets() -> None:
    codebase_readme = _ROOT / ".planning" / "codebase" / "README.md"
    gitignore_text = (_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert codebase_readme.exists()
    readme_text = codebase_readme.read_text(encoding="utf-8")
    assert "Derived collaboration map" in readme_text
    assert "Authority order" in readme_text
    assert "Conflict rule" in readme_text
    assert "!.planning/codebase/" in gitignore_text
    assert "!.planning/codebase/*.md" in gitignore_text

    for relative_path in (
        ".planning/codebase/ARCHITECTURE.md",
        ".planning/codebase/CONCERNS.md",
        ".planning/codebase/CONVENTIONS.md",
        ".planning/codebase/INTEGRATIONS.md",
        ".planning/codebase/STACK.md",
        ".planning/codebase/STRUCTURE.md",
        ".planning/codebase/TESTING.md",
    ):
        text = (_ROOT / relative_path).read_text(encoding="utf-8")
        assert "Derived collaboration map" in text
        assert "协作图谱 / 派生视图" in text


def test_codebase_maps_are_derived_collaboration_views() -> None:
    gitignore_text = (_ROOT / ".gitignore").read_text(encoding="utf-8")
    authority_text = (
        _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
    ).read_text(encoding="utf-8")
    developer_text = (_ROOT / "docs" / "developer_architecture.md").read_text(
        encoding="utf-8"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")

    assert "!.planning/codebase/" in gitignore_text
    assert "!.planning/codebase/*.md" in gitignore_text
    assert "derived collaboration maps" in authority_text
    assert "derived collaboration maps / 协作图谱" in developer_text
    assert "## Current Execution Workspace Inputs" in project_text

    for path in sorted((_ROOT / ".planning" / "codebase").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        assert "Derived collaboration map" in text, path.as_posix()


def test_project_primary_sources_do_not_include_phase_workspace_assets() -> None:
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    primary_sources = _extract_markdown_section(project_text, "Primary Sources")

    assert ".planning/phases/" not in primary_sources
    assert "Current Execution Workspace Inputs" in project_text


def test_phase_60_tooling_closeout_is_frozen_in_current_story_truth() -> None:
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    file_matrix_text = _FILE_MATRIX.read_text(encoding="utf-8")

    assert "archived / evidence-ready (2026-03-22)" in project_text
    assert "**Archive status:** `archived / evidence-ready (2026-03-22)`" in roadmap_text
    assert "| HOT-14 | Phase 60 | Complete |" in requirements_text
    assert "| TST-12 | Phase 60 | Complete |" in requirements_text
    assert "| GOV-44 | Phase 60 | Complete |" in requirements_text
    assert ".planning/v1.13-MILESTONE-AUDIT.md" in state_text
    assert ("$gsd-new-milestone" in state_text or "$gsd-plan-phase 72" in state_text)
    assert "scripts/check_file_matrix_inventory.py" in file_matrix_text
    assert "tests/meta/toolchain_truth_python_stack.py" in file_matrix_text
