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
    runtime_views_text = (_ROOT / "custom_components" / "lipro" / "control" / "runtime_access_support_views.py").read_text(encoding="utf-8")
    runtime_devices_text = (_ROOT / "custom_components" / "lipro" / "control" / "runtime_access_support_devices.py").read_text(encoding="utf-8")
    runtime_telemetry_text = (_ROOT / "custom_components" / "lipro" / "control" / "runtime_access_support_telemetry.py").read_text(encoding="utf-8")

    assert "class CommandServiceLike(Protocol):" in runtime_types_text
    assert "from .service_types import CommandFailureSummary, ServicePropertyList" in runtime_types_text
    assert "from .services.contracts import" not in runtime_types_text
    assert "type CommandProperties = ServicePropertyList" in runtime_types_text
    assert "type ProtocolDiagnosticsSnapshot = JsonObject" in runtime_types_text
    assert "def last_failure(self) -> CommandFailureSummary | None:" in runtime_types_text
    assert "properties: CommandProperties | None = None" in runtime_types_text
    assert "fallback_device_id: str | None = None" in runtime_types_text

    assert "type CoordinatorAuthSurface = RuntimeAuthServiceLike" in execution_text
    assert "type AuthenticatedCoordinator = LiproCoordinator" in execution_text
    assert "class CoordinatorAuthSurface(Protocol):" not in execution_text
    assert "class AuthenticatedCoordinator(Protocol):" not in execution_text

    assert "type CommandService = CommandServiceLike" in command_text
    assert "type CommandCoordinator = LiproCoordinator" in command_text
    assert "normalize_send_command_payload(payload)" in command_text
    assert "_validate_send_command_payload_types" not in command_text
    assert "class CommandService(Protocol):" not in command_text
    assert "class CommandCoordinator(Protocol):" not in command_text

    assert "from ..coordinator_entry import Coordinator" not in lifecycle_text
    assert "class CoordinatorRuntimeLike(LiproCoordinator, Protocol):" in lifecycle_text
    assert "coordinator: CoordinatorRuntimeLike" in lifecycle_text

    assert '_get_explicit_member(coordinator, "protocol")' in runtime_views_text
    assert '_get_explicit_member(coordinator, "mqtt_service")' in runtime_views_text
    assert '_get_explicit_mapping_member(coordinator, "devices")' in runtime_views_text
    assert '_get_explicit_member(entry, "entry_id")' in runtime_views_text
    assert '_get_explicit_mapping_member(entry, "options")' in runtime_views_text
    assert "type(entry).__getattribute__" not in runtime_views_text
    assert "type(coordinator).__getattribute__" not in runtime_views_text

    assert "_get_explicit_member(coordinator, getter_name)" not in runtime_devices_text
    assert '"config_entry")' not in runtime_devices_text
    assert "_get_explicit_member(self._protocol" not in runtime_telemetry_text
    assert "_get_explicit_member(telemetry_service" not in runtime_telemetry_text
