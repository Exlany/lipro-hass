"""Focused runtime contract single-source truth guards."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))


def test_runtime_types_is_single_source_for_service_facing_runtime_contracts() -> None:
    runtime_types_text = (_ROOT / "custom_components" / "lipro" / "runtime_types.py").read_text(encoding="utf-8")
    execution_text = (_ROOT / "custom_components" / "lipro" / "services" / "execution.py").read_text(encoding="utf-8")
    command_text = (_ROOT / "custom_components" / "lipro" / "services" / "command.py").read_text(encoding="utf-8")
    lifecycle_text = (_ROOT / "custom_components" / "lipro" / "control" / "entry_lifecycle_support.py").read_text(encoding="utf-8")

    assert "class CommandServiceLike(Protocol):" in runtime_types_text
    assert "def last_failure(self) -> CommandFailureSummary | None:" in runtime_types_text
    assert "fallback_device_id: str | None = None" in runtime_types_text

    assert "type CoordinatorAuthSurface = RuntimeAuthServiceLike" in execution_text
    assert "type AuthenticatedCoordinator = LiproCoordinator" in execution_text
    assert "class CoordinatorAuthSurface(Protocol):" not in execution_text
    assert "class AuthenticatedCoordinator(Protocol):" not in execution_text

    assert "type CommandService = CommandServiceLike" in command_text
    assert "type CommandCoordinator = LiproCoordinator" in command_text
    assert "class CommandService(Protocol):" not in command_text
    assert "class CommandCoordinator(Protocol):" not in command_text

    assert "from ..coordinator_entry import Coordinator" not in lifecycle_text
    assert "class CoordinatorRuntimeLike(LiproCoordinator, Protocol):" in lifecycle_text
    assert "coordinator: CoordinatorRuntimeLike" in lifecycle_text
