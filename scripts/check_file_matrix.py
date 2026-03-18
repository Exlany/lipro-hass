"""Governance checker for Python inventory, file-matrix coverage, and doc drift."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
import re
import sys

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
PROJECT_PATH = Path(".planning/PROJECT.md")
ROADMAP_PATH = Path(".planning/ROADMAP.md")
STATE_PATH = Path(".planning/STATE.md")
REQUIREMENTS_PATH = Path(".planning/REQUIREMENTS.md")
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
FILE_MATRIX_HEADER_PATTERN = re.compile(r"\*\*Python files total:\*\*\s+(\d+)")
FILE_MATRIX_ROW_PATTERN = re.compile(r"^\| `([^`]+\.py)` \|", re.MULTILINE)
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
PROJECT_WORKSPACE_INPUTS_HEADER = "## Current Execution Workspace Inputs"


@dataclass(frozen=True, slots=True)
class FileGovernanceRow:
    """One normalized file-governance record from the matrix inventory."""

    path: str
    area: str
    owner_phase: str
    fate: str
    residual: str


OVERRIDES: dict[str, FileGovernanceRow] = {
    "custom_components/lipro/core/api/__init__.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/__init__.py",
        area="Protocol",
        owner_phase="Phase 2.5 / 12",
        fate="重构",
        residual="-",
    ),
    "custom_components/lipro/core/api/client.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/client.py",
        area="Protocol",
        owner_phase="Phase 2 / 7 / 12 / 14 / 35",
        fate="重构",
        residual="thin REST child-façade composition root",
    ),
    "custom_components/lipro/core/mqtt/__init__.py": FileGovernanceRow(
        path="custom_components/lipro/core/mqtt/__init__.py",
        area="Protocol",
        owner_phase="Phase 2.5 / 7 / 17",
        fate="迁移适配",
        residual="package export intentionally minimal; no concrete transport export",
    ),
    "custom_components/lipro/services/execution.py": FileGovernanceRow(
        path="custom_components/lipro/services/execution.py",
        area="Control",
        owner_phase="Phase 3 / 5 / 7",
        fate="保留",
        residual="formal service execution facade; private auth seam closed",
    ),
    "tests/meta/test_toolchain_truth.py": FileGovernanceRow(
        path="tests/meta/test_toolchain_truth.py",
        area="Assurance",
        owner_phase="Phase 16",
        fate="保留",
        residual="-",
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
    "tests/core/api/test_api.py": FileGovernanceRow(
        path="tests/core/api/test_api.py",
        area="Protocol",
        owner_phase="Phase 33",
        fate="保留",
        residual="topic root for auth/init REST regressions",
    ),
    "tests/core/api/test_api_command_surface.py": FileGovernanceRow(
        path="tests/core/api/test_api_command_surface.py",
        area="Protocol",
        owner_phase="Phase 33",
        fate="保留",
        residual="topicized command / request-edge regression home",
    ),
    "tests/core/api/test_api_device_surface.py": FileGovernanceRow(
        path="tests/core/api/test_api_device_surface.py",
        area="Protocol",
        owner_phase="Phase 33",
        fate="保留",
        residual="topicized device / capability regression home",
    ),
    "tests/core/api/test_api_transport_and_schedule.py": FileGovernanceRow(
        path="tests/core/api/test_api_transport_and_schedule.py",
        area="Protocol",
        owner_phase="Phase 33",
        fate="保留",
        residual="topicized transport / schedule regression home",
    ),
    "tests/core/test_init.py": FileGovernanceRow(
        path="tests/core/test_init.py",
        area="Control",
        owner_phase="Phase 33",
        fate="保留",
        residual="topic root for init contract regressions",
    ),
    "tests/core/test_init_schema_validation.py": FileGovernanceRow(
        path="tests/core/test_init_schema_validation.py",
        area="Control",
        owner_phase="Phase 33",
        fate="保留",
        residual="schema-focused init regression home",
    ),
    "tests/meta/test_governance_guards.py": FileGovernanceRow(
        path="tests/meta/test_governance_guards.py",
        area="Assurance",
        owner_phase="Phase 33",
        fate="保留",
        residual="inventory / policy governance topic root",
    ),
    "tests/meta/test_governance_release_contract.py": FileGovernanceRow(
        path="tests/meta/test_governance_release_contract.py",
        area="Assurance",
        owner_phase="Phase 33",
        fate="保留",
        residual="release / contributor contract governance topic home",
    ),
    "custom_components/lipro/control/developer_router_support.py": FileGovernanceRow(
        path="custom_components/lipro/control/developer_router_support.py",
        area="Control",
        owner_phase="Phase 14 / 15",
        fate="保留",
        residual="developer diagnostics glue + typed helper home",
    ),
    "custom_components/lipro/control/service_router.py": FileGovernanceRow(
        path="custom_components/lipro/control/service_router.py",
        area="Control",
        owner_phase="Phase 3 / 14 / 15",
        fate="保留",
        residual="public handler home; upload/report glue kept out-of-line",
    ),
    "custom_components/lipro/core/api/client_base.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/client_base.py",
        area="Protocol",
        owner_phase="Phase 2 / 15 / 17",
        fate="重构",
        residual="ClientSessionState formal REST session-state home",
    ),
    "custom_components/lipro/core/api/schedule_service.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/schedule_service.py",
        area="Protocol",
        owner_phase="Phase 2 / 14",
        fate="重构",
        residual="helper-only schedule support",
    ),
    "custom_components/lipro/core/api/status_fallback.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/status_fallback.py",
        area="Protocol",
        owner_phase="Phase 14",
        fate="保留",
        residual="status fallback kernel home",
    ),
    "custom_components/lipro/core/api/status_service.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/status_service.py",
        area="Protocol",
        owner_phase="Phase 2 / 13 / 14",
        fate="重构",
        residual="public status orchestration home",
    ),
    "custom_components/lipro/core/coordinator/coordinator.py": FileGovernanceRow(
        path="custom_components/lipro/core/coordinator/coordinator.py",
        area="Runtime",
        owner_phase="Phase 5 / 14 / 36",
        fate="重构",
        residual="HA-facing runtime façade with polling ballast reduced",
    ),
    "custom_components/lipro/core/coordinator/services/protocol_service.py": FileGovernanceRow(
        path="custom_components/lipro/core/coordinator/services/protocol_service.py",
        area="Runtime",
        owner_phase="Phase 14",
        fate="保留",
        residual="protocol-facing runtime service surface",
    ),
    "custom_components/lipro/core/command/result_policy.py": FileGovernanceRow(
        path="custom_components/lipro/core/command/result_policy.py",
        area="Cross-cutting",
        owner_phase="Phase 33",
        fate="保留",
        residual="command-result classification / retry / delayed-refresh policy home",
    ),
    "custom_components/lipro/core/coordinator/runtime/device/snapshot_models.py": FileGovernanceRow(
        path="custom_components/lipro/core/coordinator/runtime/device/snapshot_models.py",
        area="Runtime",
        owner_phase="Phase 33",
        fate="保留",
        residual="typed snapshot container + rejection contract home",
    ),
    "custom_components/lipro/core/coordinator/runtime/mqtt/adapters.py": FileGovernanceRow(
        path="custom_components/lipro/core/coordinator/runtime/mqtt/adapters.py",
        area="Runtime",
        owner_phase="Phase 33",
        fate="保留",
        residual="MQTT callback adapter helper home",
    ),
    "custom_components/lipro/core/protocol/boundary/rest_decoder_support.py": FileGovernanceRow(
        path="custom_components/lipro/core/protocol/boundary/rest_decoder_support.py",
        area="Protocol",
        owner_phase="Phase 33",
        fate="保留",
        residual="REST decoder canonicalization helper home",
    ),
    "custom_components/lipro/core/api/client_request_gateway.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/client_request_gateway.py",
        area="Protocol",
        owner_phase="Phase 35",
        fate="保留",
        residual="REST request-pipeline collaborator home",
    ),
    "custom_components/lipro/core/api/client_endpoint_surface.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/client_endpoint_surface.py",
        area="Protocol",
        owner_phase="Phase 35",
        fate="保留",
        residual="REST endpoint forwarding collaborator home",
    ),
    "custom_components/lipro/core/protocol/facade.py": FileGovernanceRow(
        path="custom_components/lipro/core/protocol/facade.py",
        area="Protocol",
        owner_phase="Phase 2 / 35",
        fate="重构",
        residual="formal protocol root with localized REST/MQTT child-façade wiring",
    ),
    "custom_components/lipro/core/protocol/rest_port.py": FileGovernanceRow(
        path="custom_components/lipro/core/protocol/rest_port.py",
        area="Protocol",
        owner_phase="Phase 35",
        fate="保留",
        residual="typed REST child-façade port home",
    ),
    "custom_components/lipro/core/protocol/mqtt_facade.py": FileGovernanceRow(
        path="custom_components/lipro/core/protocol/mqtt_facade.py",
        area="Protocol",
        owner_phase="Phase 35",
        fate="保留",
        residual="MQTT child façade home under the unified protocol root",
    ),
    "custom_components/lipro/core/coordinator/services/polling_service.py": FileGovernanceRow(
        path="custom_components/lipro/core/coordinator/services/polling_service.py",
        area="Runtime",
        owner_phase="Phase 36",
        fate="保留",
        residual="polling/status/outlet/snapshot orchestration helper home",
    ),
    "tests/core/coordinator/services/test_polling_service.py": FileGovernanceRow(
        path="tests/core/coordinator/services/test_polling_service.py",
        area="Runtime",
        owner_phase="Phase 36",
        fate="保留",
        residual="polling-service regression home",
    ),
    "tests/core/test_init_service_handlers.py": FileGovernanceRow(
        path="tests/core/test_init_service_handlers.py",
        area="Control",
        owner_phase="Phase 27 / 37",
        fate="保留",
        residual="shared helper root for topicized init service-handler regressions",
    ),
    "tests/core/test_init_service_handlers_device_resolution.py": FileGovernanceRow(
        path="tests/core/test_init_service_handlers_device_resolution.py",
        area="Control",
        owner_phase="Phase 37",
        fate="保留",
        residual="device-resolution topic home",
    ),
    "tests/core/test_init_service_handlers_share_reports.py": FileGovernanceRow(
        path="tests/core/test_init_service_handlers_share_reports.py",
        area="Control",
        owner_phase="Phase 37",
        fate="保留",
        residual="share-report topic home",
    ),
    "tests/core/test_init_service_handlers_debug_queries.py": FileGovernanceRow(
        path="tests/core/test_init_service_handlers_debug_queries.py",
        area="Control",
        owner_phase="Phase 37",
        fate="保留",
        residual="debug-query topic home",
    ),
    "tests/core/test_init_service_handlers_commands.py": FileGovernanceRow(
        path="tests/core/test_init_service_handlers_commands.py",
        area="Control",
        owner_phase="Phase 37",
        fate="保留",
        residual="command-dispatch topic home",
    ),
    "tests/core/test_init_service_handlers_schedules.py": FileGovernanceRow(
        path="tests/core/test_init_service_handlers_schedules.py",
        area="Control",
        owner_phase="Phase 37",
        fate="保留",
        residual="schedule-validation topic home",
    ),
    "tests/core/test_init_runtime_behavior.py": FileGovernanceRow(
        path="tests/core/test_init_runtime_behavior.py",
        area="Control",
        owner_phase="Phase 33 / 37",
        fate="保留",
        residual="shared helper root for topicized init runtime regressions",
    ),
    "tests/core/test_init_runtime_bootstrap.py": FileGovernanceRow(
        path="tests/core/test_init_runtime_bootstrap.py",
        area="Control",
        owner_phase="Phase 37",
        fate="保留",
        residual="bootstrap/infrastructure topic home",
    ),
    "tests/core/test_init_runtime_setup_entry.py": FileGovernanceRow(
        path="tests/core/test_init_runtime_setup_entry.py",
        area="Control",
        owner_phase="Phase 37",
        fate="保留",
        residual="setup-entry topic home",
    ),
    "tests/core/test_init_runtime_setup_entry_failures.py": FileGovernanceRow(
        path="tests/core/test_init_runtime_setup_entry_failures.py",
        area="Control",
        owner_phase="Phase 37",
        fate="保留",
        residual="setup-entry failure topic home",
    ),
    "tests/core/test_init_runtime_unload_reload.py": FileGovernanceRow(
        path="tests/core/test_init_runtime_unload_reload.py",
        area="Control",
        owner_phase="Phase 37",
        fate="保留",
        residual="unload/reload topic home",
    ),
    "tests/core/test_init_runtime_registry_refresh.py": FileGovernanceRow(
        path="tests/core/test_init_runtime_registry_refresh.py",
        area="Control",
        owner_phase="Phase 37",
        fate="保留",
        residual="registry-refresh topic home",
    ),
    "tests/meta/test_governance_phase_history.py": FileGovernanceRow(
        path="tests/meta/test_governance_phase_history.py",
        area="Assurance",
        owner_phase="Phase 33 / 37",
        fate="保留",
        residual="phase-history planning/closeout topic root",
    ),
    "tests/meta/test_governance_phase_history_runtime.py": FileGovernanceRow(
        path="tests/meta/test_governance_phase_history_runtime.py",
        area="Assurance",
        owner_phase="Phase 37",
        fate="保留",
        residual="runtime closeout phase-history topic home",
    ),
    "tests/meta/test_governance_phase_history_topology.py": FileGovernanceRow(
        path="tests/meta/test_governance_phase_history_topology.py",
        area="Assurance",
        owner_phase="Phase 37",
        fate="保留",
        residual="topology closeout phase-history topic home",
    ),
    "custom_components/lipro/core/mqtt/mqtt_client.py": FileGovernanceRow(
        path="custom_components/lipro/core/mqtt/mqtt_client.py",
        area="Protocol",
        owner_phase="Phase 2.5 / 15",
        fate="重构",
        residual="direct transport residual; locality limited to core/mqtt + protocol seam",
    ),
}


def repo_root(start: Path | None = None) -> Path:
    """Locate the repository root by walking upward to ``pyproject.toml``."""
    candidate = (start or Path(__file__)).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for parent in (candidate, *candidate.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    msg = "Could not locate repository root"
    raise FileNotFoundError(msg)


def iter_python_files(root: Path) -> list[str]:
    """Return the sorted Python file inventory for governance checks."""
    files: list[str] = []
    for path in root.rglob("*.py"):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIR_NAMES for part in relative.parts):
            continue
        files.append(relative.as_posix())
    return sorted(files)


def _row_for_path(
    path: str,
    area: str,
    owner_phase: str,
    fate: str = "保留",
    residual: str = "-",
) -> FileGovernanceRow:
    return FileGovernanceRow(
        path=path,
        area=area,
        owner_phase=owner_phase,
        fate=fate,
        residual=residual,
    )


def _classify_component_path(path: str) -> FileGovernanceRow | None:
    control_root_files = {
        "custom_components/lipro/__init__.py",
        "custom_components/lipro/diagnostics.py",
        "custom_components/lipro/system_health.py",
        "custom_components/lipro/config_flow.py",
        "custom_components/lipro/runtime_infra.py",
        "custom_components/lipro/coordinator_entry.py",
    }
    domain_platform_files = {
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
    }

    if path.startswith("custom_components/lipro/core/api/"):
        return _row_for_path(path, "Protocol", "Phase 2", "重构")
    if path.startswith("custom_components/lipro/core/protocol/boundary/"):
        return _row_for_path(path, "Protocol", "Phase 7.1")
    if path.startswith("custom_components/lipro/core/protocol/"):
        return _row_for_path(path, "Protocol", "Phase 2.5")
    if path.startswith("custom_components/lipro/core/mqtt/"):
        return _row_for_path(path, "Protocol", "Phase 2.5", "重构")
    if path.startswith("custom_components/lipro/core/anonymous_share/"):
        return _row_for_path(path, "Protocol", "Phase 2.6")
    if path.startswith("custom_components/lipro/core/telemetry/"):
        return _row_for_path(path, "Assurance", "Phase 7.3")
    if path == "custom_components/lipro/control/telemetry_surface.py":
        return _row_for_path(path, "Control", "Phase 7.3")
    if path.startswith("custom_components/lipro/control/"):
        return _row_for_path(path, "Control", "Phase 3")
    if path in control_root_files:
        return _row_for_path(path, "Control", "Phase 3")
    if path.startswith("custom_components/lipro/services/"):
        return _row_for_path(path, "Control", "Phase 3")
    if path.startswith("custom_components/lipro/flow/"):
        return _row_for_path(path, "Control", "Phase 3")
    if path.startswith("custom_components/lipro/core/capability/"):
        return _row_for_path(path, "Domain", "Phase 4")
    if path.startswith("custom_components/lipro/core/device/"):
        return _row_for_path(path, "Domain", "Phase 4", "重构")
    if path.startswith("custom_components/lipro/entities/"):
        return _row_for_path(path, "Domain", "Phase 4")
    if path in domain_platform_files:
        return _row_for_path(path, "Domain", "Phase 4")
    if path.startswith("custom_components/lipro/core/coordinator/"):
        return _row_for_path(path, "Runtime", "Phase 5", "重构")
    return None


def _classify_test_path(path: str) -> FileGovernanceRow | None:
    runtime_test_files = {
        "tests/core/test_coordinator.py",
        "tests/core/test_coordinator_integration.py",
    }
    domain_test_prefixes = (
        "tests/core/capability/",
        "tests/core/device/",
        "tests/entities/",
        "tests/platforms/",
    )
    control_test_prefixes = ("tests/services/", "tests/flows/")

    if path == "tests/meta/test_protocol_replay_assets.py":
        return _row_for_path(path, "Assurance", "Phase 7.4")
    if path == "tests/meta/test_evidence_pack_authority.py":
        return _row_for_path(path, "Assurance", "Phase 8")
    if path == "tests/meta/test_governance_closeout_guards.py":
        return _row_for_path(path, "Assurance", "Phase 27")
    if path.startswith("tests/meta/"):
        return _row_for_path(path, "Assurance", "Phase 6")
    if path.startswith("tests/harness/evidence_pack/"):
        return _row_for_path(path, "Assurance", "Phase 8")
    if (
        path.startswith("tests/harness/protocol/")
        or path == "tests/harness/__init__.py"
    ):
        return _row_for_path(path, "Assurance", "Phase 7.4")
    if path.startswith("tests/snapshots/"):
        return _row_for_path(path, "Assurance", "Phase 6")
    if path == "tests/integration/test_ai_debug_evidence_pack.py":
        return _row_for_path(path, "Assurance", "Phase 8")
    if path == "tests/integration/test_telemetry_exporter_integration.py":
        return _row_for_path(path, "Runtime", "Phase 7.3")
    if path == "tests/integration/test_protocol_replay_harness.py":
        return _row_for_path(path, "Assurance", "Phase 7.4")
    if path == "tests/core/api/test_protocol_replay_rest.py":
        return _row_for_path(path, "Protocol", "Phase 7.4")
    if path == "tests/core/mqtt/test_protocol_replay_mqtt.py":
        return _row_for_path(path, "Protocol", "Phase 7.4")
    if (
        path.startswith(("tests/core/coordinator/", "tests/integration/"))
        or path in runtime_test_files
    ):
        return _row_for_path(path, "Runtime", "Phase 5 / 6")
    if path.startswith("tests/core/api/"):
        return _row_for_path(path, "Protocol", "Phase 2")
    if path.startswith("tests/core/telemetry/"):
        return _row_for_path(path, "Assurance", "Phase 7.3")
    if path.startswith(domain_test_prefixes):
        return _row_for_path(path, "Domain", "Phase 4")
    if path == "tests/core/test_init_service_handlers.py":
        return _row_for_path(path, "Control", "Phase 27")
    if path.startswith(control_test_prefixes) or path == "tests/core/test_init.py":
        return _row_for_path(path, "Control", "Phase 3 / 7")
    if path.startswith("tests/helpers/") or path in {
        "tests/conftest.py",
        "tests/conftest_shared.py",
    }:
        return _row_for_path(path, "Assurance", "Phase 6")
    return None


def _classify_script_path(path: str) -> FileGovernanceRow | None:
    if path == "scripts/export_ai_debug_evidence_pack.py":
        return _row_for_path(path, "Assurance", "Phase 8")
    if path.startswith("scripts/"):
        return _row_for_path(path, "Assurance", "Phase 6 / 7")
    return None


def classify_path(path: str) -> FileGovernanceRow:
    """Map one Python file path to its governed area and phase ownership."""
    if path in OVERRIDES:
        return OVERRIDES[path]

    for classifier in (
        _classify_component_path,
        _classify_test_path,
        _classify_script_path,
    ):
        row = classifier(path)
        if row is not None:
            return row
    return _row_for_path(path, "Cross-cutting", "Phase 7")


def generate_file_matrix_markdown(files: Iterable[str]) -> str:
    """Render the current Python inventory into ``FILE_MATRIX.md`` markdown."""
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
    """Extract Python file paths from the file-matrix markdown table."""
    return FILE_MATRIX_ROW_PATTERN.findall(text)


def extract_reported_total(text: str) -> int:
    """Extract the declared Python file count from file-matrix markdown."""
    match = FILE_MATRIX_HEADER_PATTERN.search(text)
    if match is None:
        msg = "FILE_MATRIX missing '**Python files total:** <n>' header"
        raise ValueError(msg)
    return int(match.group(1))


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
    errors.extend(validate_codebase_map_policy(root))
    return errors


def _write_line(message: str) -> None:
    sys.stdout.write(f"{message}\n")


def main() -> int:
    """Run the governance CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="rewrite FILE_MATRIX.md from current inventory",
    )
    parser.add_argument(
        "--check", action="store_true", help="validate governance artifacts"
    )
    parser.add_argument(
        "--report", action="store_true", help="print current inventory summary"
    )
    args = parser.parse_args()

    root = repo_root()
    inventory = iter_python_files(root)

    if args.write:
        (root / FILE_MATRIX_PATH).write_text(
            generate_file_matrix_markdown(inventory),
            encoding="utf-8",
        )

    if args.report:
        _write_line(f"python_files_total={len(inventory)}")
        phase_counts: dict[str, int] = {}
        for path in inventory:
            phase = classify_path(path).owner_phase
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        for phase, count in sorted(phase_counts.items()):
            _write_line(f"{phase}={count}")

    if args.check:
        errors = run_checks(root)
        if errors:
            for error in errors:
                _write_line(error)
            return 1

    if not any((args.write, args.check, args.report)):
        parser.print_help()
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
