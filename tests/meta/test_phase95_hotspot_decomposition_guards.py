"""Focused no-regrowth guards for Phase 95 hotspot inward decomposition."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_SCHEDULE_SERVICE = _ROOT / "custom_components" / "lipro" / "core" / "api" / "schedule_service.py"
_SCHEDULE_ENDPOINTS = _ROOT / "custom_components" / "lipro" / "core" / "api" / "endpoints" / "schedule.py"
_COMMAND_RUNTIME = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "runtime" / "command_runtime.py"
_MQTT_RUNTIME = _ROOT / "custom_components" / "lipro" / "core" / "coordinator" / "runtime" / "mqtt_runtime.py"
_AUTH_RECOVERY = _ROOT / "custom_components" / "lipro" / "core" / "api" / "auth_recovery.py"
_PHASE_DIR = _ROOT / ".planning" / "phases" / "95-schedule-runtime-and-boundary-hotspot-inward-decomposition"
_PHASE_VERIFICATION = _PHASE_DIR / "95-VERIFICATION.md"
_PHASE_VALIDATION = _PHASE_DIR / "95-VALIDATION.md"
_VERIFICATION_MATRIX = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
_DEPENDENCY_MATRIX = _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase95_schedule_hotspot_helpers_stay_localized() -> None:
    schedule_text = _read(_SCHEDULE_SERVICE)
    endpoints_text = _read(_SCHEDULE_ENDPOINTS)

    for needle in (
        "def _collect_schedule_rows_from_batch(",
        "def _add_mesh_schedule_for_candidate(",
        "def _delete_mesh_schedule_batch(",
        "def _refresh_mesh_schedule_rows(",
    ):
        assert needle in schedule_text

    assert "async def _typed_iot_request" not in endpoints_text
    assert "iot_request=self._schedule_iot_request" in endpoints_text


def test_phase95_runtime_and_auth_hotspots_keep_single_root_story() -> None:
    command_text = _read(_COMMAND_RUNTIME)
    mqtt_text = _read(_MQTT_RUNTIME)
    auth_text = _read(_AUTH_RECOVERY)

    for needle in (
        "def _build_trace_for_request(",
        "def _handle_command_dispatch_result(",
        "def _verify_delivery_and_finalize(",
    ):
        assert needle in command_text
    assert "class CommandRuntime" in command_text

    for needle in (
        "def _await_transport_connection(",
        "def _schedule_disconnect_notification(",
        "def _finalize_connect_attempt(",
    ):
        assert needle in mqtt_text
    assert mqtt_text.count("def _disconnect_notification_minutes(") == 1

    for needle in (
        "def _resolve_result_message(",
        "def _has_reusable_access_token(",
        "def _record_refresh_reuse(",
        "def _record_refresh_failure(",
        "def _complete_refresh_attempt(",
        "async def _retry_mapping_request_if_allowed(",
    ):
        assert needle in auth_text


def test_phase95_governance_truth_registers_hotspot_closeout() -> None:
    verification_text = _read(_PHASE_VERIFICATION)
    validation_text = _read(_PHASE_VALIDATION)
    verification_matrix_text = _read(_VERIFICATION_MATRIX)
    dependency_matrix_text = _read(_DEPENDENCY_MATRIX)
    file_matrix_text = _read(_FILE_MATRIX)

    assert "# Phase 95 Verification" in verification_text
    assert "v1.26 active route / Phase 96 planning-ready / latest archived baseline = v1.25" in verification_text
    assert "tests/meta/test_phase95_hotspot_decomposition_guards.py" in verification_text
    assert "# Phase 95 Validation Contract" in validation_text
    assert "$gsd-plan-phase 96" in validation_text
    assert "## Phase 95 Schedule/Runtime Hotspot Inward Decomposition" in verification_matrix_text
    assert "tests/meta/test_phase95_hotspot_decomposition_guards.py" in verification_matrix_text

    for needle in (
        "schedule_service.py` 继续是 protocol-local schedule helper home",
        "command_runtime.py` 与 `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` 继续分别承担 command-runtime / MQTT-runtime orchestration truth",
        "auth_recovery.py` 继续是 protocol-local auth classification / refresh / replay collaborator",
    ):
        assert needle in dependency_matrix_text

    for needle in (
        "candidate-query / mutation schedule collaborator home after inward split",
        "formal command-runtime orchestration home with inward trace / failure helpers",
        "formal MQTT-runtime orchestration home with localized transport / notification helpers",
        "REST auth-recovery refresh / replay collaborator home",
        "focused no-regrowth guard home for Phase 95 hotspot inward decomposition",
    ):
        assert needle in file_matrix_text
