"""Helpers for loading and querying architecture policy rules."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

_POLICY_RELATIVE_PATH = Path(".governance/baseline/ARCHITECTURE_POLICY.md")
_SECTION_PATTERN_TEMPLATE = r"^## {heading}$"
_TABLE_SEPARATOR_PATTERN = re.compile(r"^\|(?:\s*:?-{3,}:?\s*\|)+$")


@dataclass(frozen=True, slots=True)
class ArchitecturePolicyRule:
    """One parsed rule row from `ARCHITECTURE_POLICY.md`."""

    rule_id: str
    taxonomy: str
    mode: str
    governed_targets: tuple[str, ...]
    forbidden_signals: tuple[str, ...]
    allowed_or_required_signals: tuple[str, ...]
    source_refs: tuple[str, ...]
    enforcement: tuple[str, ...]
    future_hook: str = "-"


def _repo_root(start: Path | None = None) -> Path:
    candidate = (start or Path(__file__)).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for parent in (candidate, *candidate.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    msg = "Could not locate repository root"
    raise FileNotFoundError(msg)


def policy_root(start: Path | None = None) -> Path:
    """Return repository root for architecture policy helpers."""
    return _repo_root(start or Path(__file__))


def policy_path(root: Path | None = None) -> Path:
    """Return `ARCHITECTURE_POLICY.md` absolute path."""
    resolved_root = root or policy_root()
    return resolved_root / _POLICY_RELATIVE_PATH


def has_policy_text(root: Path | None = None) -> bool:
    """Return whether the architecture policy markdown is present."""
    return policy_path(root).exists()


def load_policy_text(root: Path | None = None) -> str:
    """Read the raw architecture policy markdown."""
    return policy_path(root).read_text(encoding="utf-8")


def _section_between(text: str, heading: str, next_heading: str | None) -> str:
    start_match = re.search(
        _SECTION_PATTERN_TEMPLATE.format(heading=re.escape(heading)),
        text,
        flags=re.MULTILINE,
    )
    if start_match is None:
        msg = f"Could not find section '## {heading}' in architecture policy"
        raise ValueError(msg)
    start = start_match.end()
    if next_heading is None:
        return text[start:]

    end_match = re.search(
        _SECTION_PATTERN_TEMPLATE.format(heading=re.escape(next_heading)),
        text[start:],
        flags=re.MULTILINE,
    )
    if end_match is None:
        msg = f"Could not find section '## {next_heading}' in architecture policy"
        raise ValueError(msg)
    return text[start : start + end_match.start()]


def _strip_code_fences(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith("`") and stripped.endswith("`"):
        return stripped[1:-1].strip()
    return stripped


def _split_multivalue(value: str) -> tuple[str, ...]:
    normalized = value.replace("<br>", "\n")
    items = [
        _strip_code_fences(part).strip()
        for part in normalized.splitlines()
        if _strip_code_fences(part).strip() and _strip_code_fences(part).strip() != "-"
    ]
    return tuple(items)


def _parse_markdown_table(section: str) -> list[dict[str, str]]:
    rows = [
        line.strip() for line in section.splitlines() if line.strip().startswith("|")
    ]
    if len(rows) < 2:
        msg = "Expected markdown table with header and separator"
        raise ValueError(msg)

    header = [cell.strip() for cell in rows[0].strip("|").split("|")]
    if not _TABLE_SEPARATOR_PATTERN.match(rows[1]):
        msg = "Malformed markdown table separator"
        raise ValueError(msg)

    parsed: list[dict[str, str]] = []
    for row in rows[2:]:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != len(header):
            msg = f"Malformed markdown row: {row}"
            raise ValueError(msg)
        parsed.append(dict(zip(header, cells, strict=True)))
    return parsed


def _build_rule(row: dict[str, str]) -> ArchitecturePolicyRule:
    return ArchitecturePolicyRule(
        rule_id=_strip_code_fences(row["Rule ID"]),
        taxonomy=row["Taxonomy"].strip(),
        mode=_strip_code_fences(row["Mode"]),
        governed_targets=_split_multivalue(row["Governed Paths / File"]),
        forbidden_signals=_split_multivalue(row["Forbidden Signals"]),
        allowed_or_required_signals=_split_multivalue(
            row["Allowed / Required Signals"]
        ),
        source_refs=_split_multivalue(row["Source Refs"]),
        enforcement=_split_multivalue(row["Enforcement"]),
        future_hook=row.get("Future Hook", "-").strip() or "-",
    )


def _build_targeted_ban(row: dict[str, str]) -> ArchitecturePolicyRule:
    return ArchitecturePolicyRule(
        rule_id=_strip_code_fences(row["Rule ID"]),
        taxonomy=row["Taxonomy"].strip(),
        mode=_strip_code_fences(row["Mode"]),
        governed_targets=(_strip_code_fences(row["Governed File"]),),
        forbidden_signals=_split_multivalue(row["Forbidden Signals"]),
        allowed_or_required_signals=_split_multivalue(row["Required Signals"]),
        source_refs=_split_multivalue(row["Source Refs"]),
        enforcement=_split_multivalue(row["Enforcement"]),
        future_hook="-",
    )


def load_structural_rules(
    root: Path | None = None,
) -> dict[str, ArchitecturePolicyRule]:
    """Return structural rules keyed by rule id."""
    text = load_policy_text(root)
    section = _section_between(text, "Structural Rules", "Targeted Regression Bans")
    return {
        rule.rule_id: rule
        for rule in (_build_rule(row) for row in _parse_markdown_table(section))
    }


def load_targeted_bans(root: Path | None = None) -> dict[str, ArchitecturePolicyRule]:
    """Return targeted regression bans keyed by rule id."""
    text = load_policy_text(root)
    section = _section_between(text, "Targeted Regression Bans", "Extension Hooks")
    return {
        rule.rule_id: rule
        for rule in (_build_targeted_ban(row) for row in _parse_markdown_table(section))
    }


def resolve_policy_paths(
    patterns: tuple[str, ...],
    *,
    root: Path | None = None,
) -> tuple[list[Path], list[str]]:
    """Resolve one tuple of glob-like patterns against the repository root."""
    resolved_root = root or policy_root()
    resolved: list[Path] = []
    missing: list[str] = []

    for pattern in patterns:
        matches = sorted(resolved_root.glob(pattern))
        if matches:
            resolved.extend(matches)
            continue
        missing.append(pattern)

    unique = sorted({path.resolve() for path in resolved})
    return unique, missing


__all__ = [
    "ArchitecturePolicyRule",
    "has_policy_text",
    "load_policy_text",
    "load_structural_rules",
    "load_targeted_bans",
    "policy_path",
    "policy_root",
    "resolve_policy_paths",
]
