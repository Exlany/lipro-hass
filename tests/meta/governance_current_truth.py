"""Shared machine-readable current-route and archived-baseline truth for governance tests."""

from __future__ import annotations

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


PLANNING_ROUTE_CONTRACT: dict[str, object] = {
    "contract_version": 1,
    "contract_name": "governance-route",
    "active_milestone": {
        "version": "v1.31",
        "name": "Boundary Sealing, Governance Truth & Quality Hardening",
        "status": "active / phase 111 complete; phase 112 discussion-ready (2026-03-31)",
        "phase": "112",
        "phase_title": "Formal-home discoverability and governance-anchor normalization",
        "phase_dir": "112-formal-home-discoverability-and-governance-anchor-normalization",
    },
    "latest_archived": {
        "version": "v1.30",
        "name": "Protocol Hotspot Convergence, Transport De-friendization & Snapshot Surface Slimming",
        "status": "archived / evidence-ready (2026-03-30)",
        "phase": "110",
        "phase_title": "Runtime snapshot surface reduction and milestone closeout",
        "phase_dir": "110-runtime-snapshot-surface-reduction-and-milestone-closeout",
        "audit_path": ".planning/v1.30-MILESTONE-AUDIT.md",
        "evidence_path": ".planning/reviews/V1_30_EVIDENCE_INDEX.md",
        "evidence_label": "latest archived evidence index",
    },
    "previous_archived": {
        "version": "v1.29",
        "name": "Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization",
        "evidence_path": ".planning/reviews/V1_29_EVIDENCE_INDEX.md",
    },
    "bootstrap": {
        "current_route": "v1.31 active milestone route / starting from latest archived baseline = v1.30",
        "default_next_command": "$gsd-discuss-phase 112",
        "latest_archived_evidence_pointer": ".planning/reviews/V1_30_EVIDENCE_INDEX.md",
    },
}


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


def assert_machine_readable_route_contracts() -> dict[str, dict[str, object]]:
    contracts = load_planning_route_contracts()
    for doc_name, contract in contracts.items():
        assert contract == PLANNING_ROUTE_CONTRACT, f"{doc_name} route contract drifted"
    return contracts


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
    CURRENT_ROUTE_MODE = CURRENT_ROUTE

CURRENT_MILESTONE_PHASES = ("111", "112", "113", "114")
CURRENT_MILESTONE_COMPLETED_PHASES = ("111",)
CURRENT_MILESTONE_PENDING_PHASES: tuple[str, ...] = ("112", "113", "114")
CURRENT_MILESTONE_PLAN_COUNT_BY_PHASE = {"111": 3, "112": 0, "113": 0, "114": 0}
CURRENT_MILESTONE_PLAN_COUNT = CURRENT_MILESTONE_PLAN_COUNT_BY_PHASE[CURRENT_PHASE]
CURRENT_MILESTONE_SUMMARY_COUNT_BY_PHASE = {"111": 4, "112": 0, "113": 0, "114": 0}
CURRENT_MILESTONE_SUMMARY_COUNT = CURRENT_MILESTONE_SUMMARY_COUNT_BY_PHASE[CURRENT_PHASE]
CURRENT_ROUTE_FOCUSED_GUARDS = (
    "tests/meta/test_governance_bootstrap_smoke.py",
    "tests/meta/test_governance_route_handoff_smoke.py",
    "tests/meta/test_phase90_hotspot_map_guards.py",
    "tests/meta/test_phase91_typed_boundary_guards.py",
    "tests/meta/test_phase92_redaction_convergence_guards.py",
    "tests/meta/test_phase94_typed_boundary_guards.py",
    "tests/meta/test_phase95_hotspot_decomposition_guards.py",
    "tests/meta/test_phase96_sanitizer_burndown_guards.py",
    "tests/meta/test_phase97_governance_assurance_freeze_guards.py",
    "tests/meta/test_phase98_route_reactivation_guards.py",
    "tests/meta/test_phase99_runtime_hotspot_support_guards.py",
    "tests/meta/test_phase100_runtime_schedule_support_guards.py",
    "tests/meta/test_phase101_anonymous_share_rest_boundary_guards.py",
    "tests/meta/test_phase102_governance_portability_guards.py",
    "tests/meta/test_phase103_root_thinning_guards.py",
    "tests/meta/test_phase104_service_router_runtime_split_guards.py",
    "tests/meta/test_phase105_governance_freeze_guards.py",
    "tests/meta/test_phase107_rest_status_hotspot_guards.py",
    "tests/meta/test_phase108_mqtt_transport_de_friendization_guards.py",
    "tests/meta/test_phase109_anonymous_share_manager_inward_decomposition_guards.py",
    "tests/meta/test_phase110_runtime_snapshot_closeout_guards.py",
    "tests/meta/test_phase111_runtime_boundary_guards.py",
    "tests/meta/test_public_surface_guards.py",
    "tests/meta/test_dependency_guards.py",
)


def _count_test_inventory() -> tuple[int, int, int]:
    tests_root = _ROOT / "tests"
    python_files = tuple(tests_root.rglob("*.py"))
    runnable_files = tuple(path for path in python_files if path.name.startswith("test_"))
    meta_suites = tuple((tests_root / "meta").glob("test_*.py"))
    return len(python_files), len(runnable_files), len(meta_suites)


TESTS_PYTHON_FILE_COUNT, TESTS_RUNNABLE_FILE_COUNT, TESTS_META_SUITE_COUNT = _count_test_inventory()

CURRENT_ROUTE_PROSE_FORBIDDEN = (
    "v1.20 active route / Phase 75 complete / latest archived baseline = v1.19",
    "v1.21 active route / Phase 76 execution-ready / latest archived baseline = v1.20",
    "v1.21 active route / Phase 78 complete / latest archived baseline = v1.20",
    "v1.21 active route / Phase 79 complete / latest archived baseline = v1.20",
    "v1.21 active route / Phase 80 complete / latest archived baseline = v1.20",
    "v1.22 active route / Phase 83 complete / latest archived baseline = v1.21",
    "v1.22 active route / Phase 84 complete / latest archived baseline = v1.21",
    "v1.23 active route / Phase 85 complete / latest archived baseline = v1.22",
    "v1.23 active route / Phase 85 planning-ready / latest archived baseline = v1.22",
    "v1.23 active route / Phase 87 execution-ready / latest archived baseline = v1.22",
    "v1.23 active route / Phase 87 in progress / latest archived baseline = v1.22",
    "v1.23 active route / Phase 87 complete / latest archived baseline = v1.22",
    "v1.23 active route / Phase 88 complete / latest archived baseline = v1.22",
    "v1.25 active route / Phase 90 planning-ready / latest archived baseline = v1.24",
    "v1.25 active route / Phase 92 complete / latest archived baseline = v1.24",
    "v1.25 active route / Phase 93 complete / latest archived baseline = v1.24",
    "v1.26 active route / Phase 94 planning-ready / latest archived baseline = v1.25",
    "v1.26 active route / Phase 95 execution-ready / latest archived baseline = v1.25",
    "v1.26 active route / Phase 95 planning-ready / latest archived baseline = v1.25",
    "v1.26 active route / Phase 95 complete / latest archived baseline = v1.25",
    "v1.26 active route / Phase 96 planning-ready / latest archived baseline = v1.25",
    "v1.26 active route / Phase 97 complete / latest archived baseline = v1.25",
    "v1.27 active route / Phase 98 complete / latest archived baseline = v1.26",
    "v1.27 active route / Phase 99 complete / latest archived baseline = v1.26",
    "v1.27 active route / Phase 100 complete / latest archived baseline = v1.26",
    "v1.27 active route / Phase 101 complete / latest archived baseline = v1.26",
    "v1.29 active route / Phase 104 complete / latest archived baseline = v1.28",
    "v1.29 active route / Phase 105 complete / latest archived baseline = v1.28",
    "v1.30 active route / Phase 107 complete / latest archived baseline = v1.29",
    "v1.30 active route / Phase 109 complete / latest archived baseline = v1.29",
    "v1.30 active route / Phase 110 complete / latest archived baseline = v1.29",
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
    "`no active milestone route / latest archived baseline = v1.30`"
)
HISTORICAL_ARCHIVE_TRANSITION_ROUTE_TRUTH = (
    "historical archive-transition route truth = "
    "`no active milestone route / latest archived baseline = v1.29`"
)


__all__ = [
    "CURRENT_MILESTONE",
    "CURRENT_MILESTONE_COMPLETED_PHASES",
    "CURRENT_MILESTONE_DEFAULT_NEXT",
    "CURRENT_MILESTONE_HEADER",
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
    "CURRENT_PHASE",
    "CURRENT_PHASE_HEADING",
    "CURRENT_PHASE_TITLE",
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
    "assert_machine_readable_route_contracts",
    "load_planning_route_contract",
    "load_planning_route_contracts",
]
