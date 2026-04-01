"""Shared machine-readable current-route and archived-baseline truth for governance tests."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re

import yaml

from .conftest import _ROOT

_ROUTE_CONTRACT_START = "<!-- governance-route-contract:start -->"
_ROUTE_CONTRACT_END = "<!-- governance-route-contract:end -->"

_ROUTE_CONTRACT_PATHS = {
    "PROJECT": _ROOT / ".planning" / "PROJECT.md",
    "ROADMAP": _ROOT / ".planning" / "ROADMAP.md",
    "REQUIREMENTS": _ROOT / ".planning" / "REQUIREMENTS.md",
    "STATE": _ROOT / ".planning" / "STATE.md",
    "MILESTONES": _ROOT / ".planning" / "MILESTONES.md",
}


@dataclass(frozen=True)
class PhaseAssetSnapshot:
    phase: str
    directory: str
    plan_files: tuple[str, ...]
    plan_summary_files: tuple[str, ...]
    summary_files: tuple[str, ...]

    @property
    def plan_count(self) -> int:
        return len(self.plan_files)

    @property
    def plan_summary_count(self) -> int:
        return len(self.plan_summary_files)

    @property
    def summary_count(self) -> int:
        return len(self.summary_files)


def _as_mapping(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return value


def _as_optional_mapping(value: object) -> dict[str, object] | None:
    if value is None:
        return None
    assert isinstance(value, dict)
    return value


def _as_str(value: object) -> str:
    assert isinstance(value, str)
    return value


def _extract_route_contract(text: str) -> dict[str, object]:
    match = re.search(
        (
            rf"{re.escape(_ROUTE_CONTRACT_START)}\s*```yaml\n"
            r"(?P<body>.*?)\n"
            rf"```\s*{re.escape(_ROUTE_CONTRACT_END)}"
        ),
        text,
        flags=re.DOTALL,
    )
    assert match is not None, "Missing governance route contract block"
    loaded = yaml.safe_load(match.group("body"))
    assert isinstance(loaded, dict)
    return loaded


@lru_cache(maxsize=1)
def load_planning_route_contracts() -> dict[str, dict[str, object]]:
    return {
        doc_name: _extract_route_contract(path.read_text(encoding="utf-8"))
        for doc_name, path in _ROUTE_CONTRACT_PATHS.items()
    }


def load_planning_route_contract(path: Path) -> dict[str, object]:
    return _extract_route_contract(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_canonical_route_contract() -> dict[str, object]:
    return load_planning_route_contracts()["PROJECT"]


def assert_machine_readable_route_contracts() -> dict[str, dict[str, object]]:
    contracts = load_planning_route_contracts()
    canonical = load_canonical_route_contract()
    for doc_name, contract in contracts.items():
        assert contract == canonical, f"{doc_name} route contract drifted"
    return contracts


def _load_phase_asset_snapshot(phase: str, phase_dir_name: str) -> PhaseAssetSnapshot:
    phase_root = _ROOT / ".planning" / "phases" / phase_dir_name
    plan_files = tuple(sorted(path.name for path in phase_root.glob(f"{phase}-*-PLAN.md")))
    plan_summary_files = tuple(
        sorted(
            path.name
            for path in phase_root.glob(f"{phase}-*-SUMMARY.md")
            if path.name != f"{phase}-SUMMARY.md"
        )
    )
    summary_files = tuple(sorted(path.name for path in phase_root.glob(f"{phase}*-SUMMARY.md")))
    return PhaseAssetSnapshot(
        phase=phase,
        directory=phase_dir_name,
        plan_files=plan_files,
        plan_summary_files=plan_summary_files,
        summary_files=summary_files,
    )


PLANNING_ROUTE_CONTRACT: dict[str, object] = load_canonical_route_contract()

_ACTIVE = _as_optional_mapping(PLANNING_ROUTE_CONTRACT["active_milestone"])
_LATEST = _as_mapping(PLANNING_ROUTE_CONTRACT["latest_archived"])
_PREVIOUS = _as_mapping(PLANNING_ROUTE_CONTRACT["previous_archived"])
_BOOTSTRAP = _as_mapping(PLANNING_ROUTE_CONTRACT["bootstrap"])

HAS_ACTIVE_MILESTONE = _ACTIVE is not None
NO_ACTIVE_MILESTONE_LABEL = "No active milestone route"

LATEST_ARCHIVED_MILESTONE = _as_str(_LATEST["version"])
LATEST_ARCHIVED_MILESTONE_NAME = _as_str(_LATEST["name"])
LATEST_ARCHIVED_PROJECT_HEADER = (
    f"## Latest Archived Milestone ({LATEST_ARCHIVED_MILESTONE})"
)
LATEST_ARCHIVED_MILESTONE_STATUS = _as_str(_LATEST["status"])
LATEST_ARCHIVED_PHASE = _as_str(_LATEST["phase"])
LATEST_ARCHIVED_PHASE_TITLE = _as_str(_LATEST["phase_title"])
LATEST_ARCHIVED_PHASE_HEADING = (
    f"### Phase {LATEST_ARCHIVED_PHASE}: {LATEST_ARCHIVED_PHASE_TITLE}"
)
LATEST_ARCHIVED_PHASE_DIR = _as_str(_LATEST["phase_dir"])
LATEST_ARCHIVED_EVIDENCE_FILENAME = Path(_as_str(_LATEST["evidence_path"])).name
LATEST_ARCHIVED_EVIDENCE_PATH = _as_str(_LATEST["evidence_path"])
LATEST_ARCHIVED_EVIDENCE_LABEL = _as_str(_LATEST["evidence_label"])
LEGACY_ARCHIVED_CLOSEOUT_POINTER_LABEL = "latest archived closeout pointer"
LATEST_ARCHIVED_AUDIT_FILENAME = Path(_as_str(_LATEST["audit_path"])).name
LATEST_ARCHIVED_AUDIT_PATH = _as_str(_LATEST["audit_path"])
PREVIOUS_ARCHIVED_MILESTONE = _as_str(_PREVIOUS["version"])
PREVIOUS_ARCHIVED_MILESTONE_NAME = _as_str(_PREVIOUS["name"])
PREVIOUS_ARCHIVED_PROJECT_HEADER = (
    f"## Previous Archived Milestone ({PREVIOUS_ARCHIVED_MILESTONE})"
)
PREVIOUS_ARCHIVED_EVIDENCE_PATH = _as_str(_PREVIOUS["evidence_path"])

CURRENT_ROUTE = _as_str(_BOOTSTRAP["current_route"])
CURRENT_MILESTONE_DEFAULT_NEXT = _as_str(_BOOTSTRAP["default_next_command"])

if HAS_ACTIVE_MILESTONE:
    assert _ACTIVE is not None
    CURRENT_MILESTONE = _as_str(_ACTIVE["version"])
    CURRENT_MILESTONE_NAME = _as_str(_ACTIVE["name"])
    CURRENT_MILESTONE_HEADER = f"## Current Milestone ({CURRENT_MILESTONE})"
    CURRENT_MILESTONE_ROADMAP_HEADER = (
        f"## {CURRENT_MILESTONE}: {CURRENT_MILESTONE_NAME}"
    )
    CURRENT_MILESTONE_STATUS = _as_str(_ACTIVE["status"])
    CURRENT_MILESTONE_LABEL = f"{CURRENT_MILESTONE} {CURRENT_MILESTONE_NAME}"
    CURRENT_MILESTONE_STATE_LABEL = CURRENT_MILESTONE_LABEL
    CURRENT_PHASE = _as_str(_ACTIVE["phase"])
    CURRENT_PHASE_TITLE = _as_str(_ACTIVE["phase_title"])
    CURRENT_PHASE_HEADING = f"### Phase {CURRENT_PHASE}: {CURRENT_PHASE_TITLE}"
    CURRENT_PHASE_DIR = _as_str(_ACTIVE["phase_dir"])
    route_mode = _ACTIVE.get("route_mode", CURRENT_ROUTE)
    CURRENT_ROUTE_MODE = _as_str(route_mode)
else:
    CURRENT_MILESTONE = LATEST_ARCHIVED_MILESTONE
    CURRENT_MILESTONE_NAME = LATEST_ARCHIVED_MILESTONE_NAME
    CURRENT_MILESTONE_HEADER = LATEST_ARCHIVED_PROJECT_HEADER
    CURRENT_MILESTONE_ROADMAP_HEADER = (
        f"## {CURRENT_MILESTONE}: {CURRENT_MILESTONE_NAME}"
    )
    CURRENT_MILESTONE_STATUS = LATEST_ARCHIVED_MILESTONE_STATUS
    CURRENT_MILESTONE_LABEL = f"{CURRENT_MILESTONE} {CURRENT_MILESTONE_NAME}"
    CURRENT_MILESTONE_STATE_LABEL = NO_ACTIVE_MILESTONE_LABEL
    CURRENT_PHASE = LATEST_ARCHIVED_PHASE
    CURRENT_PHASE_TITLE = LATEST_ARCHIVED_PHASE_TITLE
    CURRENT_PHASE_HEADING = LATEST_ARCHIVED_PHASE_HEADING
    CURRENT_PHASE_DIR = LATEST_ARCHIVED_PHASE_DIR
    CURRENT_ROUTE_MODE = CURRENT_ROUTE

_CURRENT_PHASE_ASSETS = _load_phase_asset_snapshot(CURRENT_PHASE, CURRENT_PHASE_DIR)
CURRENT_PHASE_PLAN_FILENAMES = _CURRENT_PHASE_ASSETS.plan_files
CURRENT_PHASE_PLAN_SUMMARY_FILENAMES = _CURRENT_PHASE_ASSETS.plan_summary_files
CURRENT_PHASE_SUMMARY_FILENAMES = _CURRENT_PHASE_ASSETS.summary_files
CURRENT_PHASE_VERIFICATION_FILENAME = f"{CURRENT_PHASE}-VERIFICATION.md"

CURRENT_MILESTONE_PHASES = (CURRENT_PHASE,)
if _CURRENT_PHASE_ASSETS.plan_summary_count >= _CURRENT_PHASE_ASSETS.plan_count:
    CURRENT_MILESTONE_COMPLETED_PHASES = (CURRENT_PHASE,)
    CURRENT_MILESTONE_IN_PROGRESS_PHASES: tuple[str, ...] = ()
else:
    CURRENT_MILESTONE_COMPLETED_PHASES = ()
    CURRENT_MILESTONE_IN_PROGRESS_PHASES = (CURRENT_PHASE,)
CURRENT_MILESTONE_PENDING_PHASES: tuple[str, ...] = ()
CURRENT_MILESTONE_PLAN_COUNT_BY_PHASE = {CURRENT_PHASE: _CURRENT_PHASE_ASSETS.plan_count}
CURRENT_MILESTONE_PLAN_COUNT = CURRENT_MILESTONE_PLAN_COUNT_BY_PHASE[CURRENT_PHASE]
CURRENT_MILESTONE_SUMMARY_COUNT_BY_PHASE = {CURRENT_PHASE: _CURRENT_PHASE_ASSETS.summary_count}
CURRENT_MILESTONE_SUMMARY_COUNT = CURRENT_MILESTONE_SUMMARY_COUNT_BY_PHASE[CURRENT_PHASE]
CURRENT_MILESTONE_TOTAL_PLAN_COUNT = sum(CURRENT_MILESTONE_PLAN_COUNT_BY_PHASE.values())
CURRENT_MILESTONE_COMPLETED_PLAN_COUNT = _CURRENT_PHASE_ASSETS.plan_summary_count
CURRENT_ROUTE_FOCUSED_GUARDS = (
    "tests/meta/test_governance_bootstrap_smoke.py",
    "tests/meta/test_governance_route_handoff_smoke.py",
    "tests/meta/test_phase119_mqtt_boundary_guards.py",
    "tests/meta/test_runtime_contract_truth.py",
    "tests/meta/test_governance_release_contract.py",
    "tests/meta/toolchain_truth_release_contract.py",
    "tests/meta/test_governance_release_docs.py",
    "tests/meta/test_dependency_guards.py",
    "tests/meta/test_phase68_hotspot_budget_guards.py",
)


def _count_test_inventory() -> tuple[int, int, int]:
    tests_root = _ROOT / "tests"
    python_files = tuple(tests_root.rglob("*.py"))
    runnable_files = tuple(path for path in python_files if path.name.startswith("test_"))
    meta_suites = tuple((tests_root / "meta").glob("test_*.py"))
    return len(python_files), len(runnable_files), len(meta_suites)


TESTS_PYTHON_FILE_COUNT, TESTS_RUNNABLE_FILE_COUNT, TESTS_META_SUITE_COUNT = _count_test_inventory()

CURRENT_ROUTE_PROSE_FORBIDDEN = (
    "active / roadmap drafted; phase 119 pending planning (2026-04-01)",
    "$gsd-plan-phase 119",
    "Phase 119 planning pending",
    "v1.31 active milestone route / starting from latest archived baseline = v1.30",
    "v1.32 active milestone route / starting from latest archived baseline = v1.31",
    "no active milestone route / latest archived baseline = v1.20",
    "no active milestone route / latest archived baseline = v1.21",
    "no active milestone route / latest archived baseline = v1.22",
    "no active milestone route / latest archived baseline = v1.23",
    "no active milestone route / latest archived baseline = v1.24",
    "no active milestone route / latest archived baseline = v1.25",
    "no active milestone route / latest archived baseline = v1.26",
    "no active milestone route / latest archived baseline = v1.27",
    "no active milestone route / latest archived baseline = v1.28",
    "no active milestone route / latest archived baseline = v1.29",
    "v1.24 / Phase 89 complete",
)
CURRENT_RUNTIME_ROOT_TEST = "tests/core/coordinator/test_runtime_root.py"

HISTORICAL_CLOSEOUT_ROUTE_TRUTH = (
    "historical closeout route truth = "
    "`no active milestone route / latest archived baseline = v1.32`"
)
HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH = (
    "historical archive-transition route truth = "
    "`no active milestone route / latest archived baseline = v1.31`"
)


__all__ = [
    "CURRENT_MILESTONE",
    "CURRENT_MILESTONE_COMPLETED_PHASES",
    "CURRENT_MILESTONE_COMPLETED_PLAN_COUNT",
    "CURRENT_MILESTONE_DEFAULT_NEXT",
    "CURRENT_MILESTONE_HEADER",
    "CURRENT_MILESTONE_IN_PROGRESS_PHASES",
    "CURRENT_MILESTONE_LABEL",
    "CURRENT_MILESTONE_NAME",
    "CURRENT_MILESTONE_PENDING_PHASES",
    "CURRENT_MILESTONE_PHASES",
    "CURRENT_MILESTONE_PLAN_COUNT",
    "CURRENT_MILESTONE_PLAN_COUNT_BY_PHASE",
    "CURRENT_MILESTONE_ROADMAP_HEADER",
    "CURRENT_MILESTONE_STATE_LABEL",
    "CURRENT_MILESTONE_STATUS",
    "CURRENT_MILESTONE_SUMMARY_COUNT",
    "CURRENT_MILESTONE_SUMMARY_COUNT_BY_PHASE",
    "CURRENT_MILESTONE_TOTAL_PLAN_COUNT",
    "CURRENT_PHASE",
    "CURRENT_PHASE_DIR",
    "CURRENT_PHASE_HEADING",
    "CURRENT_PHASE_PLAN_FILENAMES",
    "CURRENT_PHASE_PLAN_SUMMARY_FILENAMES",
    "CURRENT_PHASE_SUMMARY_FILENAMES",
    "CURRENT_PHASE_TITLE",
    "CURRENT_PHASE_VERIFICATION_FILENAME",
    "CURRENT_ROUTE",
    "CURRENT_ROUTE_FOCUSED_GUARDS",
    "CURRENT_ROUTE_MODE",
    "CURRENT_ROUTE_PROSE_FORBIDDEN",
    "CURRENT_RUNTIME_ROOT_TEST",
    "HAS_ACTIVE_MILESTONE",
    "HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH",
    "HISTORICAL_CLOSEOUT_ROUTE_TRUTH",
    "LATEST_ARCHIVED_AUDIT_FILENAME",
    "LATEST_ARCHIVED_AUDIT_PATH",
    "LATEST_ARCHIVED_EVIDENCE_FILENAME",
    "LATEST_ARCHIVED_EVIDENCE_LABEL",
    "LATEST_ARCHIVED_EVIDENCE_PATH",
    "LATEST_ARCHIVED_MILESTONE",
    "LATEST_ARCHIVED_MILESTONE_NAME",
    "LATEST_ARCHIVED_MILESTONE_STATUS",
    "LATEST_ARCHIVED_PHASE",
    "LATEST_ARCHIVED_PHASE_DIR",
    "LATEST_ARCHIVED_PHASE_HEADING",
    "LATEST_ARCHIVED_PHASE_TITLE",
    "LATEST_ARCHIVED_PROJECT_HEADER",
    "LEGACY_ARCHIVED_CLOSEOUT_POINTER_LABEL",
    "NO_ACTIVE_MILESTONE_LABEL",
    "PLANNING_ROUTE_CONTRACT",
    "PREVIOUS_ARCHIVED_EVIDENCE_PATH",
    "PREVIOUS_ARCHIVED_MILESTONE",
    "PREVIOUS_ARCHIVED_MILESTONE_NAME",
    "PREVIOUS_ARCHIVED_PROJECT_HEADER",
    "TESTS_META_SUITE_COUNT",
    "TESTS_PYTHON_FILE_COUNT",
    "TESTS_RUNNABLE_FILE_COUNT",
    "_as_mapping",
    "_as_optional_mapping",
    "assert_machine_readable_route_contracts",
    "load_canonical_route_contract",
    "load_planning_route_contract",
    "load_planning_route_contracts",
]
