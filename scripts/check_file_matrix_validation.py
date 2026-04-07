"""Validation passes for file-governance truth and derived map drift."""

from __future__ import annotations

from pathlib import Path
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.check_file_matrix_inventory import iter_python_files
    from scripts.check_file_matrix_markdown import (
        extract_reported_total,
        parse_file_matrix_paths,
    )
    from scripts.check_file_matrix_registry import (
        OVERRIDES,
        iter_override_truth_families,
    )
elif __package__ in {None, ""}:
    from check_file_matrix_inventory import iter_python_files
    from check_file_matrix_markdown import (
        extract_reported_total,
        parse_file_matrix_paths,
    )
    from check_file_matrix_registry import OVERRIDES, iter_override_truth_families
else:
    from scripts.check_file_matrix_inventory import iter_python_files
    from scripts.check_file_matrix_markdown import (
        extract_reported_total,
        parse_file_matrix_paths,
    )
    from scripts.check_file_matrix_registry import (
        OVERRIDES,
        iter_override_truth_families,
    )


FILE_MATRIX_PATH = Path(".planning/reviews/FILE_MATRIX.md")

PROJECT_PATH = Path(".planning/PROJECT.md")

ROADMAP_PATH = Path(".planning/ROADMAP.md")

STATE_PATH = Path(".planning/STATE.md")

REQUIREMENTS_PATH = Path(".planning/REQUIREMENTS.md")

VERIFICATION_MATRIX_PATH = Path(".planning/baseline/VERIFICATION_MATRIX.md")

AGENTS_PATH = Path("AGENTS.md")

CLAUDE_COMPAT_PATH = Path("CLAUDE.md")

GITIGNORE_PATH = Path(".gitignore")

CODEBASE_MAP_DIR = Path(".planning/codebase")

CODEBASE_MAP_README_PATH = CODEBASE_MAP_DIR / "README.md"

CODEBASE_MAP_PATHS = [
    CODEBASE_MAP_README_PATH,
    CODEBASE_MAP_DIR / "ARCHITECTURE.md",
    CODEBASE_MAP_DIR / "CONCERNS.md",
    CODEBASE_MAP_DIR / "CONVENTIONS.md",
    CODEBASE_MAP_DIR / "INTEGRATIONS.md",
    CODEBASE_MAP_DIR / "STACK.md",
    CODEBASE_MAP_DIR / "STRUCTURE.md",
    CODEBASE_MAP_DIR / "TESTING.md",
]

ACTIVE_DOC_PATHS = [
    PROJECT_PATH,
    ROADMAP_PATH,
    STATE_PATH,
    REQUIREMENTS_PATH,
    Path("docs/NORTH_STAR_TARGET_ARCHITECTURE.md"),
    Path("docs/developer_architecture.md"),
    Path("docs/adr/README.md"),
    Path(".planning/baseline/ARCHITECTURE_POLICY.md"),
    AGENTS_PATH,
    CLAUDE_COMPAT_PATH,
]

HISTORICAL_DOC_PATHS: list[Path] = []

COUNT_PATTERN = re.compile(
    r"(?:全部 `|Python files total:\*\* |Python files total: )(\d+)"
)

DISALLOWED_AUTHORITY_PHRASES = (
    "当前唯一权威",
    "唯一权威审计",
    "当前权威审计",
)

SECTION_SOURCE_PATH_HEADINGS: dict[Path, tuple[str, ...]] = {
    PROJECT_PATH: ("Primary Sources",),
    STATE_PATH: ("Governance Truth Sources", "Session Continuity"),
}

GLOB_CHARS = ("*", "?", "[")

BACKTICK_TOKEN_PATTERN = re.compile(r"`([^`]+)`")



def validate_file_matrix(root: Path) -> list[str]:
    """Validate FILE_MATRIX coverage, counts, and duplicate rows."""
    errors: list[str] = []
    inventory = iter_python_files(root)
    matrix_text = (root / FILE_MATRIX_PATH).read_text(encoding="utf-8")
    matrix_paths = parse_file_matrix_paths(matrix_text)
    reported_total = extract_reported_total(matrix_text)

    if reported_total != len(inventory):
        errors.append(
            f"FILE_MATRIX total mismatch: header={reported_total}, inventory={len(inventory)}"
        )

    inventory_set = set(inventory)
    matrix_set = set(matrix_paths)
    missing = sorted(inventory_set - matrix_set)
    extra = sorted(matrix_set - inventory_set)
    duplicates = sorted({path for path in matrix_paths if matrix_paths.count(path) > 1})

    if missing:
        errors.append(
            f"FILE_MATRIX missing {len(missing)} files: {', '.join(missing[:10])}"
        )
    if extra:
        errors.append(
            f"FILE_MATRIX contains {len(extra)} non-inventory files: {', '.join(extra[:10])}"
        )
    if duplicates:
        errors.append(
            f"FILE_MATRIX duplicates {len(duplicates)} files: {', '.join(duplicates[:10])}"
        )
    if "remainder" in matrix_text.lower():
        errors.append("FILE_MATRIX still contains remainder bucket")

    return errors



def validate_active_doc_counts(root: Path) -> list[str]:
    """Validate that active governance docs report the current file count."""
    errors: list[str] = []
    total = len(iter_python_files(root))
    for relative_path in [
        ROADMAP_PATH,
        STATE_PATH,
        REQUIREMENTS_PATH,
        FILE_MATRIX_PATH,
    ]:
        text = (root / relative_path).read_text(encoding="utf-8")
        counts = {int(match) for match in COUNT_PATTERN.findall(text)}
        stale = sorted(count for count in counts if count != total)
        if stale:
            errors.append(f"{relative_path} contains stale Python count(s): {stale}")
    return errors



def validate_doc_authority(root: Path) -> list[str]:
    """Validate that active and historical docs keep the correct authority labels."""
    errors: list[str] = []
    for relative_path in ACTIVE_DOC_PATHS:
        path = root / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        hit = [phrase for phrase in DISALLOWED_AUTHORITY_PHRASES if phrase in text]
        if hit:
            errors.append(
                f"{relative_path} still contains disallowed authority phrases: {hit}"
            )
    for relative_path in HISTORICAL_DOC_PATHS:
        path = root / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "历史" not in text and "Historical" not in text:
            errors.append(f"{relative_path} is not clearly marked as historical")
    return errors



def _extract_markdown_section(text: str, heading_fragment: str) -> str | None:
    match = re.search(
        rf"^## [^\n]*{re.escape(heading_fragment)}[^\n]*\n(?P<body>.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        return None
    return match.group("body")



def _path_exists_or_matches(root: Path, candidate: str) -> bool:
    if any(char in candidate for char in GLOB_CHARS):
        return any(root.glob(candidate))
    return (root / candidate).exists()



def validate_active_source_paths(root: Path) -> list[str]:
    """Validate that active governance docs only cite real source paths."""
    errors: list[str] = []
    for relative_path, headings in SECTION_SOURCE_PATH_HEADINGS.items():
        text = (root / relative_path).read_text(encoding="utf-8")
        for heading in headings:
            section = _extract_markdown_section(text, heading)
            if section is None:
                errors.append(f"{relative_path} is missing required section: {heading}")
                continue
            for candidate in BACKTICK_TOKEN_PATTERN.findall(section):
                if not _path_exists_or_matches(root, candidate):
                    errors.append(
                        f"{relative_path} references missing source path in '{heading}': {candidate}"
                    )
    return errors



def _looks_like_repo_path(candidate: str) -> bool:
    if candidate == "refs/tags/${RELEASE_TAG}" or " " in candidate:
        return False
    if "{" in candidate or "}" in candidate:
        return False
    prefixes = (".planning/", "custom_components/", "tests/", "docs/", ".github/", "scripts/")
    return candidate.endswith((".py", ".md", ".yml", ".yaml", ".json", ".toml", ".sh")) and candidate.startswith(prefixes)



def validate_verification_matrix_paths(root: Path) -> list[str]:
    """Validate that verification-matrix path references still exist."""
    errors: list[str] = []
    text = (root / VERIFICATION_MATRIX_PATH).read_text(encoding="utf-8")
    for candidate in BACKTICK_TOKEN_PATTERN.findall(text):
        if not _looks_like_repo_path(candidate):
            continue
        if not _path_exists_or_matches(root, candidate):
            errors.append(
                f"{VERIFICATION_MATRIX_PATH} references missing runnable/source path: {candidate}"
            )
    return errors



def validate_registry_truth_families() -> list[str]:
    """Validate that registry overrides stay decomposed into focused truth families."""
    errors: list[str] = []
    families = iter_override_truth_families()

    if len(families) < 6:
        errors.append(
            "check_file_matrix_registry.py override truth families collapsed below maintainability floor"
        )

    family_keys: set[str] = set()
    duplicate_family_keys: set[str] = set()
    family_paths: set[str] = set()
    duplicate_paths: set[str] = set()
    tooling_family_paths: set[str] | None = None

    for family in families:
        family_key = f"{family.owner_phase}|{family.area}|{family.fate}"
        if family_key in family_keys:
            duplicate_family_keys.add(family_key)
        family_keys.add(family_key)

        current_paths = {path for path, _ in family.rows}
        overlap = family_paths & current_paths
        duplicate_paths.update(overlap)
        family_paths.update(current_paths)

        if family.area == "Assurance" and family.owner_phase == "Phase 60":
            tooling_family_paths = current_paths

    if duplicate_family_keys:
        joined = ", ".join(sorted(duplicate_family_keys))
        errors.append(f"check_file_matrix_registry.py has duplicate truth-family keys: {joined}")

    if duplicate_paths:
        joined = ", ".join(sorted(duplicate_paths))
        errors.append(f"check_file_matrix_registry.py duplicates override paths across families: {joined}")

    if len(family_paths) != len(OVERRIDES):
        errors.append(
            "check_file_matrix_registry.py truth-family path total no longer matches OVERRIDES"
        )

    required_tooling_paths = {
        "scripts/check_file_matrix_registry.py",
        "tests/meta/toolchain_truth_ci_contract.py",
    }
    if tooling_family_paths is None or not required_tooling_paths.issubset(tooling_family_paths):
        errors.append(
            "check_file_matrix_registry.py lost the Phase 60 tooling truth family contract"
        )

    return errors



def validate_codebase_map_policy(root: Path) -> list[str]:
    """Validate that local codebase maps stay explicitly derived and non-authoritative."""
    errors: list[str] = []

    gitignore_text = (root / ".gitignore").read_text(encoding="utf-8")
    for token in ("!.planning/codebase/", "!.planning/codebase/*.md"):
        if token not in gitignore_text:
            errors.append(f".gitignore missing codebase-map tracking rule: {token}")

    readme_path = root / CODEBASE_MAP_README_PATH
    if not readme_path.exists():
        errors.append(
            f"missing codebase map authority note: {CODEBASE_MAP_README_PATH}"
        )
        return errors

    readme_text = readme_path.read_text(encoding="utf-8")
    for token in ("Derived collaboration map", "Authority order", "Conflict rule"):
        if token not in readme_text:
            errors.append(f"{CODEBASE_MAP_README_PATH} missing required token: {token}")

    for relative_path in CODEBASE_MAP_PATHS[1:]:
        doc_text = (root / relative_path).read_text(encoding="utf-8")
        for token in ("Derived collaboration map", "协作图谱 / 派生视图"):
            if token not in doc_text:
                errors.append(
                    f"{relative_path} missing derived collaboration disclaimer token: {token}"
                )

    agents_text = (root / AGENTS_PATH).read_text(encoding="utf-8")
    if "仍有 coordinator 私有 auth seam" in agents_text:
        errors.append(
            "AGENTS.md still marks execution.py as an active private auth seam"
        )
    if "Phase 5 已关闭 coordinator 私有 auth seam" not in agents_text:
        errors.append("AGENTS.md missing closed-seam wording for execution.py")

    file_matrix_text = (root / FILE_MATRIX_PATH).read_text(encoding="utf-8")
    expected_row = (
        "| `custom_components/lipro/services/execution.py` | Control | Phase 3 / 5 / 7 | 保留 | "
        "formal service execution facade; private auth seam closed |"
    )
    if expected_row not in file_matrix_text:
        errors.append(
            "FILE_MATRIX execution.py row is not aligned with the closed-seam truth"
        )

    for relative_path in (
        CODEBASE_MAP_DIR / "STRUCTURE.md",
        CODEBASE_MAP_DIR / "ARCHITECTURE.md",
    ):
        doc_text = (root / relative_path).read_text(encoding="utf-8")
        if "runtime-auth seam" in doc_text:
            errors.append(
                f"{relative_path} still treats execution.py as an active runtime-auth seam"
            )

    return errors



def run_checks(root: Path) -> list[str]:
    """Run all governance checks and return the accumulated error list."""
    errors: list[str] = []
    errors.extend(validate_file_matrix(root))
    errors.extend(validate_active_doc_counts(root))
    errors.extend(validate_doc_authority(root))
    errors.extend(validate_active_source_paths(root))
    errors.extend(validate_verification_matrix_paths(root))
    errors.extend(validate_registry_truth_families())
    errors.extend(validate_codebase_map_policy(root))
    return errors
