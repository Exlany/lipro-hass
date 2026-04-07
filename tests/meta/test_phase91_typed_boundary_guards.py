"""Focused no-regrowth guards for Phase 91 typed-boundary hardening."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_PROTOCOL_METHODS = (
    _ROOT / "custom_components" / "lipro" / "core" / "protocol" / "protocol_facade_rest_methods.py"
)
_REST_PORT = _ROOT / "custom_components" / "lipro" / "core" / "protocol" / "rest_port.py"
_SNAPSHOT = (
    _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "runtime" / "device" / "snapshot.py"
)
_ORCHESTRATOR = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "orchestrator.py"
_RUNTIME_TYPES = _ROOT / "custom_components" / "lipro" / "runtime_types.py"
_COORDINATOR_TYPES = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "types.py"
_REST_DECODER_SUPPORT = (
    _ROOT / "custom_components" / "lipro" / "core" / "protocol" / "boundary" / "rest_decoder_support.py"
)
_BOUNDARY_RESULT = (
    _ROOT / "custom_components" / "lipro" / "core" / "protocol" / "boundary" / "result.py"
)
_BOUNDARY_REGISTRY = (
    _ROOT / "custom_components" / "lipro" / "core" / "protocol" / "boundary" / "schema_registry.py"
)
_TRACE = _ROOT / "custom_components" / "lipro" / "core" / "command" / "trace.py"
_RUNTIME_ACCESS = _ROOT / "custom_components" / "lipro" / "control" / "runtime_access.py"
_ENTITY_BASE = _ROOT / "custom_components" / "lipro" / "entities" / "base.py"
_FIRMWARE_UPDATE = _ROOT / "custom_components" / "lipro" / "entities" / "firmware_update.py"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_VERIFICATION = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase91_protocol_live_path_stays_canonical_at_protocol_root() -> None:
    protocol_text = _read_text(_PROTOCOL_METHODS)
    rest_port_text = _read_text(_REST_PORT)
    snapshot_text = _read_text(_SNAPSHOT)
    orchestrator_text = _read_text(_ORCHESTRATOR)

    for needle in (
        "normalize_device_list_page(payload, offset=offset)",
        "normalize_device_status_rows(payload)",
        "normalize_mesh_group_status_rows(payload)",
        "normalize_mqtt_config(payload)",
    ):
        assert needle in protocol_text

    for needle in (
        "DeviceListResponse",
        "DeviceStatusItem",
        "MqttConfigResponse",
        "CommandResultApiResponse",
    ):
        assert needle in rest_port_text

    assert "normalize_mesh_group_status_rows(" not in snapshot_text
    assert "build_device_status_map(rows)" not in orchestrator_text


def test_phase91_typed_boundary_files_keep_any_budget_closed() -> None:
    runtime_types_text = _read_text(_RUNTIME_TYPES)
    coordinator_types_text = _read_text(_COORDINATOR_TYPES)
    result_text = _read_text(_BOUNDARY_RESULT)
    registry_text = _read_text(_BOUNDARY_REGISTRY)

    forbidden_any = "A" "ny"

    for path in (
        _RUNTIME_TYPES,
        _COORDINATOR_TYPES,
        _REST_DECODER_SUPPORT,
        _BOUNDARY_RESULT,
        _BOUNDARY_REGISTRY,
        _TRACE,
    ):
        assert forbidden_any not in _read_text(path), f"typed wildcard regrew in {path.name}"

    assert 'type CommandTrace = TracePayload' in coordinator_types_text
    assert 'class RuntimeTelemetrySnapshot(TypedDict, total=False):' in coordinator_types_text
    assert 'scheduler: MetricMapping' in coordinator_types_text
    assert 'strategy: MetricMapping' in coordinator_types_text
    assert 'def build_snapshot(self) -> RuntimeTelemetrySnapshot: ...' in runtime_types_text
    assert 'CanonicalT_co = TypeVar("CanonicalT_co", covariant=True)' in result_text
    assert 'CanonicalT_co = TypeVar("CanonicalT_co", covariant=True)' in registry_text
    assert 'BoundaryDecoder(Protocol[CanonicalT_co])' in registry_text


def test_phase91_protected_thin_shells_stay_on_named_runtime_verbs() -> None:
    runtime_access_text = _read_text(_RUNTIME_ACCESS)
    entity_text = _read_text(_ENTITY_BASE)
    firmware_text = _read_text(_FIRMWARE_UPDATE)

    assert 'runtime_access_support' in runtime_access_text
    assert 'core.coordinator' not in runtime_access_text
    assert 'coordinator.command_service' not in entity_text
    assert 'coordinator.protocol_service' not in entity_text
    assert 'get_device_lock' not in entity_text
    assert 'coordinator.async_send_command(' in entity_text
    assert 'coordinator.async_apply_optimistic_state(' in entity_text
    assert 'coordinator.protocol_service' not in firmware_text
    assert 'coordinator.async_send_command(' in firmware_text
    assert 'coordinator.async_query_device_ota_info(' in firmware_text


def test_phase91_governance_truth_registers_typed_boundary_closeout() -> None:
    verification_text = _read_text(_VERIFICATION)
    file_matrix_text = _read_text(_FILE_MATRIX)

    assert '## Phase 91 Protocol/Runtime Canonicalization and Typed Boundary Hardening' in verification_text
    assert 'tests/meta/test_phase91_typed_boundary_guards.py' in verification_text
    for needle in (
        'canonical protocol live-verb normalization home',
        'typed protocol-boundary decode result home',
        'typed boundary decoder registry home',
        'runtime/control public protocol surface and telemetry projection type home',
        'focused no-regrowth guard home for Phase 91 typed-boundary hardening',
    ):
        assert needle in file_matrix_text
