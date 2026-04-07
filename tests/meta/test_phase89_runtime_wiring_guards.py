"""Phase 89 runtime-wiring regression guards."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_COORDINATOR = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "coordinator.py"
_FACTORY = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "factory.py"
_ORCHESTRATOR = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "orchestrator.py"
_RUNTIME_WIRING = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "runtime_wiring.py"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase89_coordinator_init_binds_one_bootstrap_artifact_only() -> None:
    coordinator_text = _read_text(_COORDINATOR)

    assert coordinator_text.count("build_bootstrap_artifact(") == 1
    assert "CoordinatorAuthService(" not in coordinator_text
    assert "CoordinatorProtocolService(" not in coordinator_text
    assert "CoordinatorSignalService(" not in coordinator_text
    assert "bootstrap.support_services.auth_service" in coordinator_text
    assert "bootstrap.support_services.protocol_service" in coordinator_text
    assert "bootstrap.support_services.signal_service" in coordinator_text


def test_phase89_bootstrap_artifact_owns_support_service_contract() -> None:
    factory_text = _read_text(_FACTORY)
    orchestrator_text = _read_text(_ORCHESTRATOR)
    runtime_wiring_text = _read_text(_RUNTIME_WIRING)

    assert "support_services: CoordinatorSupportServices" in factory_text
    assert "support_services = initialize_support_services(" in orchestrator_text
    assert "CoordinatorSupportServices" in runtime_wiring_text
    assert "def initialize_support_services(" in runtime_wiring_text
