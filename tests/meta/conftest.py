"""Shared helper home for topicized governance and phase-history suites."""

from __future__ import annotations

import json
from pathlib import Path
import re

import yaml

from scripts.check_file_matrix import repo_root

_ROOT = repo_root(Path(__file__))
_AGENTS = _ROOT / "AGENTS.md"
_PRE_COMMIT = _ROOT / ".pre-commit-config.yaml"
_DOCS_README = _ROOT / "docs" / "README.md"
_TROUBLESHOOTING = _ROOT / "docs" / "TROUBLESHOOTING.md"
_RUNBOOK = _ROOT / "docs" / "MAINTAINER_RELEASE_RUNBOOK.md"
_README = _ROOT / "README.md"
_README_ZH = _ROOT / "README_zh.md"
_CONTRIBUTING = _ROOT / "CONTRIBUTING.md"
_SUPPORT = _ROOT / "SUPPORT.md"
_SECURITY = _ROOT / "SECURITY.md"
_CODEOWNERS = _ROOT / ".github" / "CODEOWNERS"
_MANIFEST = _ROOT / "custom_components" / "lipro" / "manifest.json"
_QUALITY_SCALE = _ROOT / "custom_components" / "lipro" / "quality_scale.yaml"
_DEVCONTAINER = _ROOT / ".devcontainer.json"
_PR_TEMPLATE = _ROOT / ".github" / "pull_request_template.md"
_CI_WORKFLOW = _ROOT / ".github" / "workflows" / "ci.yml"
_RELEASE_WORKFLOW = _ROOT / ".github" / "workflows" / "release.yml"
_ISSUE_CONFIG = _ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"


def _load_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(?P<frontmatter>.*?)\n---\n", text, flags=re.DOTALL)
    assert match is not None
    loaded = yaml.safe_load(match.group("frontmatter"))
    assert isinstance(loaded, dict)
    return loaded


def _load_yaml(path: Path) -> dict[str, object]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    if True in loaded and "on" not in loaded:
        loaded["on"] = loaded.pop(True)
    return loaded


def _load_json(path: Path) -> dict[str, object]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _as_mapping(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return value


def _as_mapping_list(value: object) -> list[dict[str, object]]:
    assert isinstance(value, list)
    assert all(isinstance(item, dict) for item in value)
    return value


def _as_str(value: object) -> str:
    assert isinstance(value, str)
    return value


def _as_bool(value: object) -> bool:
    assert isinstance(value, bool)
    return value


def _as_str_list(value: object) -> list[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return value


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
        or re.search(
            r"\*\*Current mode:\*\* `v1\.\d+ active route / Phase \d+(?:\.\d+)? [a-z][a-z0-9_ /-]+ / latest archived baseline = v1\.\d+`",
            state_text,
        )
        is not None
        or re.search(
            r"\*\*Current mode:\*\* `v1\.\d+ active milestone route / starting from latest archived baseline = v1\.\d+`",
            state_text,
        )
        is not None
        or re.search(
            r"\*\*Current mode:\*\* `v1\.\d+ active milestone route / Phase \d+(?:\.\d+)? (?:complete|[a-z][a-z0-9_ /-]+) / latest archived baseline = v1\.\d+`",
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


__all__ = [
    "_AGENTS",
    "_CI_WORKFLOW",
    "_CODEOWNERS",
    "_CONTRIBUTING",
    "_DEVCONTAINER",
    "_DOCS_README",
    "_ISSUE_CONFIG",
    "_MANIFEST",
    "_PRE_COMMIT",
    "_PR_TEMPLATE",
    "_QUALITY_SCALE",
    "_README",
    "_README_ZH",
    "_RELEASE_WORKFLOW",
    "_ROOT",
    "_RUNBOOK",
    "_SECURITY",
    "_SUPPORT",
    "_TROUBLESHOOTING",
    "_as_bool",
    "_as_mapping",
    "_as_mapping_list",
    "_as_str",
    "_as_str_list",
    "_assert_current_mode_tracks_phase_lifecycle",
    "_assert_state_preserves_phase_17_closeout_history",
    "_count_numbered_markdown_items",
    "_extract_checklist_labels",
    "_extract_labeled_bullets",
    "_extract_markdown_section",
    "_load_frontmatter",
    "_load_json",
    "_load_yaml",
    "_parse_codeowners_handles",
]
