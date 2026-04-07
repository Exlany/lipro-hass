"""Meta guards for external-boundary authority truth."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_AUTHORITY_MATRIX = _ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md"
_BOUNDARY_INVENTORY = (
    _ROOT
    / ".planning"
    / "phases"
    / "02.6-external-boundary-convergence"
    / "02.6-BOUNDARY-INVENTORY.md"
)


def test_authority_matrix_records_generated_and_external_boundary_truth() -> None:
    authority_matrix = _AUTHORITY_MATRIX.read_text(encoding="utf-8")

    assert "generated artifacts | fixture families + canonical normalization rules" in authority_matrix
    assert "share/support payload families" in authority_matrix
    assert "firmware trust-root/advisory families" in authority_matrix
    assert "diagnostics external endpoints" in authority_matrix
    assert "local trust root -> advisory remote -> adapters/tests" in authority_matrix


def test_boundary_inventory_records_required_external_boundary_families() -> None:
    inventory = _BOUNDARY_INVENTORY.read_text(encoding="utf-8")

    assert "ShareWorkerBoundary" in inventory
    assert "SupportPayloadBoundary" in inventory
    assert "FirmwareAdvisoryBoundary" in inventory
    assert "DiagnosticsCapabilityBoundary" in inventory
    assert "tests/fixtures/external_boundaries/share_worker" in inventory
    assert "tests/fixtures/api_contracts/get_city.success.json" in inventory
    assert "tests/fixtures/api_contracts/query_user_cloud.success.json" in inventory
