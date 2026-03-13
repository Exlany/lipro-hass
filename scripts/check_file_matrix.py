"""Governance checker for Python inventory, file-matrix coverage, and doc drift."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

EXCLUDED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
}
FILE_MATRIX_PATH = Path(".planning/reviews/FILE_MATRIX.md")
ROADMAP_PATH = Path(".planning/ROADMAP.md")
STATE_PATH = Path(".planning/STATE.md")
REQUIREMENTS_PATH = Path(".planning/REQUIREMENTS.md")
AGENTS_PATH = Path("AGENTS.md")
AGENT_POINTER_PATH = Path("agent.md")
ACTIVE_DOC_PATHS = [
    ROADMAP_PATH,
    STATE_PATH,
    REQUIREMENTS_PATH,
    Path("docs/NORTH_STAR_TARGET_ARCHITECTURE.md"),
    Path("docs/developer_architecture.md"),
    Path("docs/adr/README.md"),
    Path(".planning/baseline/ARCHITECTURE_POLICY.md"),
    AGENTS_PATH,
    AGENT_POINTER_PATH,
]
HISTORICAL_DOC_PATHS = [
    Path("docs/COMPREHENSIVE_AUDIT_2026-03-12.md"),
    Path("docs/NORTH_STAR_EXECUTION_PLAN_2026-03-12.md"),
]
COUNT_PATTERN = re.compile(r"(?:全部 `|Python files total:\*\* |Python files total: )(\d+)")
FILE_MATRIX_HEADER_PATTERN = re.compile(r"\*\*Python files total:\*\*\s+(\d+)")
FILE_MATRIX_ROW_PATTERN = re.compile(r"^\| `([^`]+\.py)` \|", re.MULTILINE)
DISALLOWED_AUTHORITY_PHRASES = (
    "当前唯一权威",
    "唯一权威审计",
    "当前权威审计",
)


@dataclass(frozen=True, slots=True)
class FileGovernanceRow:
    path: str
    area: str
    owner_phase: str
    fate: str
    residual: str


OVERRIDES: dict[str, FileGovernanceRow] = {
    "custom_components/lipro/core/api/__init__.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/__init__.py",
        area="Protocol",
        owner_phase="Phase 2.5",
        fate="迁移适配",
        residual="LiproClient compat export",
    ),
    "custom_components/lipro/core/api/client.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/client.py",
        area="Protocol",
        owner_phase="Phase 2 / 7",
        fate="迁移适配",
        residual="LiproClient compat shell",
    ),
    "custom_components/lipro/core/mqtt/__init__.py": FileGovernanceRow(
        path="custom_components/lipro/core/mqtt/__init__.py",
        area="Protocol",
        owner_phase="Phase 2.5 / 7",
        fate="迁移适配",
        residual="LiproMqttClient legacy root name",
    ),
    "custom_components/lipro/services/wiring.py": FileGovernanceRow(
        path="custom_components/lipro/services/wiring.py",
        area="Control",
        owner_phase="Phase 7",
        fate="删除候选",
        residual="legacy implementation carrier",
    ),
    "custom_components/lipro/services/execution.py": FileGovernanceRow(
        path="custom_components/lipro/services/execution.py",
        area="Control",
        owner_phase="Phase 5 / 7",
        fate="迁移适配",
        residual="runtime-auth seam",
    ),
    "custom_components/lipro/core/device/capabilities.py": FileGovernanceRow(
        path="custom_components/lipro/core/device/capabilities.py",
        area="Domain",
        owner_phase="Phase 7",
        fate="迁移适配",
        residual="DeviceCapabilities compat name",
    ),
    "custom_components/lipro/core/coordinator/runtime/status_strategy.py": FileGovernanceRow(
        path="custom_components/lipro/core/coordinator/runtime/status_strategy.py",
        area="Runtime",
        owner_phase="Phase 7",
        fate="删除候选",
        residual="shadow helper / dead strategy",
    ),
    "custom_components/lipro/core/coordinator/runtime/group_lookup_runtime.py": FileGovernanceRow(
        path="custom_components/lipro/core/coordinator/runtime/group_lookup_runtime.py",
        area="Runtime",
        owner_phase="Phase 7",
        fate="删除候选",
        residual="shadow helper",
    ),
    "custom_components/lipro/core/coordinator/runtime/room_sync_runtime.py": FileGovernanceRow(
        path="custom_components/lipro/core/coordinator/runtime/room_sync_runtime.py",
        area="Runtime",
        owner_phase="Phase 7",
        fate="删除候选",
        residual="shadow helper",
    ),
    "custom_components/lipro/core/coordinator/runtime/state_batch_runtime.py": FileGovernanceRow(
        path="custom_components/lipro/core/coordinator/runtime/state_batch_runtime.py",
        area="Runtime",
        owner_phase="Phase 7",
        fate="删除候选",
        residual="shadow helper",
    ),
    "custom_components/lipro/core/coordinator/device_registry_sync.py": FileGovernanceRow(
        path="custom_components/lipro/core/coordinator/device_registry_sync.py",
        area="Runtime",
        owner_phase="Phase 7",
        fate="删除候选",
        residual="shadow helper",
    ),
    "scripts/check_architecture_policy.py": FileGovernanceRow(
        path="scripts/check_architecture_policy.py",
        area="Assurance",
        owner_phase="Phase 7.2",
        fate="保留",
        residual="-",
    ),
    "tests/helpers/architecture_policy.py": FileGovernanceRow(
        path="tests/helpers/architecture_policy.py",
        area="Assurance",
        owner_phase="Phase 7.2",
        fate="保留",
        residual="-",
    ),
    "tests/helpers/ast_guard_utils.py": FileGovernanceRow(
        path="tests/helpers/ast_guard_utils.py",
        area="Assurance",
        owner_phase="Phase 7.2",
        fate="保留",
        residual="-",
    ),
}


def repo_root(start: Path | None = None) -> Path:
    candidate = (start or Path(__file__)).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for parent in (candidate, *candidate.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    msg = "Could not locate repository root"
    raise FileNotFoundError(msg)


def iter_python_files(root: Path) -> list[str]:
    files: list[str] = []
    for path in root.rglob("*.py"):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIR_NAMES for part in relative.parts):
            continue
        files.append(relative.as_posix())
    return sorted(files)


def classify_path(path: str) -> FileGovernanceRow:
    if path in OVERRIDES:
        return OVERRIDES[path]

    def row(area: str, owner_phase: str, fate: str = "保留", residual: str = "-") -> FileGovernanceRow:
        return FileGovernanceRow(path=path, area=area, owner_phase=owner_phase, fate=fate, residual=residual)

    if path.startswith("custom_components/lipro/core/api/"):
        return row("Protocol", "Phase 2", "重构")
    if path.startswith("custom_components/lipro/core/protocol/boundary/"):
        return row("Protocol", "Phase 7.1", "保留")
    if path.startswith("custom_components/lipro/core/protocol/"):
        return row("Protocol", "Phase 2.5", "保留")
    if path.startswith("custom_components/lipro/core/mqtt/"):
        return row("Protocol", "Phase 2.5", "重构")
    if path.startswith("custom_components/lipro/core/anonymous_share/"):
        return row("Protocol", "Phase 2.6", "保留")
    if path.startswith("custom_components/lipro/control/"):
        return row("Control", "Phase 3", "保留")
    if path in {
        "custom_components/lipro/__init__.py",
        "custom_components/lipro/diagnostics.py",
        "custom_components/lipro/system_health.py",
        "custom_components/lipro/config_flow.py",
        "custom_components/lipro/runtime_infra.py",
        "custom_components/lipro/coordinator_entry.py",
    }:
        return row("Control", "Phase 3", "保留")
    if path.startswith("custom_components/lipro/services/"):
        return row("Control", "Phase 3", "保留")
    if path.startswith("custom_components/lipro/flow/"):
        return row("Control", "Phase 3", "保留")
    if path.startswith("custom_components/lipro/core/capability/"):
        return row("Domain", "Phase 4", "保留")
    if path.startswith("custom_components/lipro/core/device/"):
        return row("Domain", "Phase 4", "重构")
    if path.startswith("custom_components/lipro/entities/"):
        return row("Domain", "Phase 4", "保留")
    if path in {
        "custom_components/lipro/binary_sensor.py",
        "custom_components/lipro/climate.py",
        "custom_components/lipro/cover.py",
        "custom_components/lipro/fan.py",
        "custom_components/lipro/helpers/platform.py",
        "custom_components/lipro/light.py",
        "custom_components/lipro/select.py",
        "custom_components/lipro/sensor.py",
        "custom_components/lipro/switch.py",
        "custom_components/lipro/update.py",
    }:
        return row("Domain", "Phase 4", "保留")
    if path.startswith("custom_components/lipro/core/coordinator/"):
        return row("Runtime", "Phase 5", "重构")
    if path.startswith("tests/meta/"):
        return row("Assurance", "Phase 6", "保留")
    if path.startswith("tests/snapshots/"):
        return row("Assurance", "Phase 6", "保留")
    if path.startswith("tests/core/coordinator/") or path == "tests/core/test_coordinator.py" or path == "tests/core/test_coordinator_integration.py" or path.startswith("tests/integration/"):
        return row("Runtime", "Phase 5 / 6", "保留")
    if path.startswith("tests/core/api/"):
        return row("Protocol", "Phase 2", "保留")
    if path.startswith("tests/core/capability/") or path.startswith("tests/core/device/") or path.startswith("tests/entities/") or path.startswith("tests/platforms/"):
        return row("Domain", "Phase 4", "保留")
    if path.startswith("tests/services/") or path.startswith("tests/flows/") or path.startswith("tests/core/test_init.py"):
        return row("Control", "Phase 3 / 7", "保留")
    if path.startswith("tests/helpers/") or path in {"tests/conftest.py", "tests/conftest_shared.py"}:
        return row("Assurance", "Phase 6", "保留")
    if path.startswith("scripts/"):
        return row("Assurance", "Phase 6 / 7", "保留")
    return row("Cross-cutting", "Phase 7", "保留")


def generate_file_matrix_markdown(files: Iterable[str]) -> str:
    rows = [classify_path(path) for path in files]
    lines = [
        "# File Matrix",
        "",
        f"**Python files total:** {len(rows)}",
        "**Status:** File-level governance authority",
        "**Rule:** workspace inventory excluding caches / virtual env / tooling artifacts",
        "",
        "## File-Level Governance Matrix",
        "",
        "| Path | Area | Owner phase | Fate | Residual / delete gate |",
        "|------|------|-------------|------|-------------------------|",
    ]
    for row in rows:
        lines.append(
            f"| `{row.path}` | {row.area} | {row.owner_phase} | {row.fate} | {row.residual} |"
        )
    return "\n".join(lines) + "\n"


def parse_file_matrix_paths(text: str) -> list[str]:
    return FILE_MATRIX_ROW_PATTERN.findall(text)


def extract_reported_total(text: str) -> int:
    match = FILE_MATRIX_HEADER_PATTERN.search(text)
    if match is None:
        msg = "FILE_MATRIX missing '**Python files total:** <n>' header"
        raise ValueError(msg)
    return int(match.group(1))


def validate_file_matrix(root: Path) -> list[str]:
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
        errors.append(f"FILE_MATRIX missing {len(missing)} files: {', '.join(missing[:10])}")
    if extra:
        errors.append(f"FILE_MATRIX contains {len(extra)} non-inventory files: {', '.join(extra[:10])}")
    if duplicates:
        errors.append(f"FILE_MATRIX duplicates {len(duplicates)} files: {', '.join(duplicates[:10])}")
    if "remainder" in matrix_text.lower():
        errors.append("FILE_MATRIX still contains remainder bucket")

    return errors


def validate_active_doc_counts(root: Path) -> list[str]:
    errors: list[str] = []
    total = len(iter_python_files(root))
    for relative_path in [ROADMAP_PATH, STATE_PATH, REQUIREMENTS_PATH, FILE_MATRIX_PATH]:
        text = (root / relative_path).read_text(encoding="utf-8")
        counts = {int(match) for match in COUNT_PATTERN.findall(text)}
        stale = sorted(count for count in counts if count not in {total})
        if stale:
            errors.append(f"{relative_path} contains stale Python count(s): {stale}")
    return errors


def validate_doc_authority(root: Path) -> list[str]:
    errors: list[str] = []
    for relative_path in ACTIVE_DOC_PATHS:
        path = root / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        hit = [phrase for phrase in DISALLOWED_AUTHORITY_PHRASES if phrase in text]
        if hit:
            errors.append(f"{relative_path} still contains disallowed authority phrases: {hit}")
    for relative_path in HISTORICAL_DOC_PATHS:
        path = root / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "历史" not in text and "Historical" not in text:
            errors.append(f"{relative_path} is not clearly marked as historical")
    return errors


def run_checks(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_file_matrix(root))
    errors.extend(validate_active_doc_counts(root))
    errors.extend(validate_doc_authority(root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="rewrite FILE_MATRIX.md from current inventory")
    parser.add_argument("--check", action="store_true", help="validate governance artifacts")
    parser.add_argument("--report", action="store_true", help="print current inventory summary")
    args = parser.parse_args()

    root = repo_root()
    inventory = iter_python_files(root)

    if args.write:
        (root / FILE_MATRIX_PATH).write_text(
            generate_file_matrix_markdown(inventory),
            encoding="utf-8",
        )

    if args.report:
        print(f"python_files_total={len(inventory)}")
        phase_counts: dict[str, int] = {}
        for path in inventory:
            phase = classify_path(path).owner_phase
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        for phase, count in sorted(phase_counts.items()):
            print(f"{phase}={count}")

    if args.check:
        errors = run_checks(root)
        if errors:
            for error in errors:
                print(error)
            return 1

    if not any((args.write, args.check, args.report)):
        parser.print_help()
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
