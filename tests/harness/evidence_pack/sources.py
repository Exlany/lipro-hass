"""Formal-source adapters for the AI Debug Evidence Pack."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_REPO_ROOT = repo_root(Path(__file__))
HAS_INTERNAL_PLANNING = (_REPO_ROOT / ".governance").exists()

TELEMETRY_EXPORTER_ROOT = "custom_components/lipro/core/telemetry"
REPLAY_HARNESS_ROOT = "tests/harness/protocol"
REPLAY_FIXTURE_ROOT = "tests/fixtures/protocol_replay"
API_CONTRACT_ROOT = "tests/fixtures/api_contracts"
BOUNDARY_FIXTURE_ROOT = "tests/fixtures/protocol_boundary"
NON_AUTHORITY_PROOF_PATHS = (
    "tests/harness/headless_consumer.py",
    "tests/integration/test_headless_consumer_proof.py",
)

if HAS_INTERNAL_PLANNING:
    BOUNDARY_INVENTORY_PATH = ".governance/phases/07.1-protocol-boundary-schema-decoder/07.1-01-BOUNDARY-INVENTORY.md"
    TELEMETRY_VALIDATION_PATH = (
        ".governance/phases/07.3-runtime-telemetry-exporter/07.3-VALIDATION.md"
    )
    REPLAY_VALIDATION_PATH = (
        ".governance/phases/07.4-protocol-replay-simulator-harness/07.4-VALIDATION.md"
    )
    EVIDENCE_INDEX_PATH = ".governance/reviews/V1_1_EVIDENCE_INDEX.md"
    AUTHORITY_MATRIX_PATH = ".governance/baseline/AUTHORITY_MATRIX.md"
    PUBLIC_SURFACES_PATH = ".governance/baseline/PUBLIC_SURFACES.md"
    VERIFICATION_MATRIX_PATH = ".governance/baseline/VERIFICATION_MATRIX.md"
    RESIDUAL_LEDGER_PATH = ".governance/reviews/RESIDUAL_LEDGER.md"
    KILL_LIST_PATH = ".governance/reviews/KILL_LIST.md"
    ROADMAP_PATH = ".governance/ROADMAP.md"
    REQUIREMENTS_PATH = ".governance/REQUIREMENTS.md"
    STATE_PATH = ".governance/STATE.md"
else:
    BOUNDARY_INVENTORY_PATH = "docs/NORTH_STAR_TARGET_ARCHITECTURE.md"
    TELEMETRY_VALIDATION_PATH = (
        "tests/integration/test_telemetry_exporter_integration.py"
    )
    REPLAY_VALIDATION_PATH = "tests/integration/test_protocol_replay_harness.py"
    EVIDENCE_INDEX_PATH = "docs/README.md"
    AUTHORITY_MATRIX_PATH = "docs/developer_architecture.md"
    PUBLIC_SURFACES_PATH = "README.md"
    VERIFICATION_MATRIX_PATH = "CONTRIBUTING.md"
    RESIDUAL_LEDGER_PATH = "docs/TROUBLESHOOTING.md"
    KILL_LIST_PATH = "SUPPORT.md"
    ROADMAP_PATH = "CONTRIBUTING.md"
    REQUIREMENTS_PATH = "README.md"
    STATE_PATH = "README_zh.md"

ALLOWED_FORMAL_SOURCE_PATHS = (
    BOUNDARY_INVENTORY_PATH,
    TELEMETRY_EXPORTER_ROOT,
    TELEMETRY_VALIDATION_PATH,
    REPLAY_HARNESS_ROOT,
    REPLAY_VALIDATION_PATH,
    EVIDENCE_INDEX_PATH,
    AUTHORITY_MATRIX_PATH,
    PUBLIC_SURFACES_PATH,
    VERIFICATION_MATRIX_PATH,
    RESIDUAL_LEDGER_PATH,
    KILL_LIST_PATH,
    ROADMAP_PATH,
    REQUIREMENTS_PATH,
    STATE_PATH,
    REPLAY_FIXTURE_ROOT,
    API_CONTRACT_ROOT,
    BOUNDARY_FIXTURE_ROOT,
)


def repo_relative(path: Path) -> str:
    """Return one repository-relative path string."""
    return path.relative_to(_REPO_ROOT).as_posix()


def formal_source_path(relative_path: str) -> Path:
    """Resolve one allowed formal source path."""
    if relative_path not in ALLOWED_FORMAL_SOURCE_PATHS:
        msg = f"Evidence pack source is not a registered formal source: {relative_path}"
        raise ValueError(msg)
    return _REPO_ROOT / relative_path


def read_formal_text(relative_path: str) -> str:
    """Read one formal text source."""
    return formal_source_path(relative_path).read_text(encoding="utf-8")


def telemetry_source_paths() -> tuple[str, ...]:
    return (
        TELEMETRY_EXPORTER_ROOT,
        TELEMETRY_VALIDATION_PATH,
        EVIDENCE_INDEX_PATH,
        AUTHORITY_MATRIX_PATH,
    )


def replay_source_paths() -> tuple[str, ...]:
    return (
        REPLAY_HARNESS_ROOT,
        REPLAY_FIXTURE_ROOT,
        API_CONTRACT_ROOT,
        BOUNDARY_FIXTURE_ROOT,
        REPLAY_VALIDATION_PATH,
        EVIDENCE_INDEX_PATH,
    )


def boundary_source_paths() -> tuple[str, ...]:
    return (
        BOUNDARY_INVENTORY_PATH,
        AUTHORITY_MATRIX_PATH,
        REPLAY_FIXTURE_ROOT,
        API_CONTRACT_ROOT,
        BOUNDARY_FIXTURE_ROOT,
        RESIDUAL_LEDGER_PATH,
    )


def governance_source_paths() -> tuple[str, ...]:
    return (
        EVIDENCE_INDEX_PATH,
        AUTHORITY_MATRIX_PATH,
        PUBLIC_SURFACES_PATH,
        VERIFICATION_MATRIX_PATH,
        RESIDUAL_LEDGER_PATH,
        KILL_LIST_PATH,
        ROADMAP_PATH,
        REQUIREMENTS_PATH,
        STATE_PATH,
    )
