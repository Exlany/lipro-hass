"""Phase-note public-surface regression guards."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.architecture_policy import load_targeted_bans, policy_root
from tests.helpers.ast_guard_utils import extract_top_level_bindings

_ROOT = policy_root(Path(__file__))
_PUBLIC_SURFACES = _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
_RULES = load_targeted_bans(_ROOT)


def _test_file_count() -> int:
    return len(sorted((_ROOT / "tests").rglob("test_*.py")))


def test_phase_48_public_surface_notes_capture_support_only_helper_and_update_cycle() -> (
    None
):
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "## Phase 48 Formal-Root Hotspot Decomposition Notes" in public_surfaces
    assert "runtime_access_support.py" in public_surfaces
    assert "support-only helper seam" in public_surfaces
    assert "CoordinatorUpdateCycle" in public_surfaces
    assert "module-level alias seam" in public_surfaces


def test_phase_53_public_surface_notes_capture_support_only_runtime_and_entry_root_helpers() -> (
    None
):
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "## Phase 53 Runtime / Entry-Root Throttling Notes" in public_surfaces
    assert "runtime_wiring.py" in public_surfaces
    assert "entry_lifecycle_support.py" in public_surfaces
    assert "entry_root_wiring.py" in public_surfaces
    assert "support-only" in public_surfaces
    assert "lazy composition" in public_surfaces


def test_phase_40_public_surface_notes_capture_runtime_access_and_shared_execution() -> (
    None
):
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "## Phase 40 Governance Truth Surface Notes" in public_surfaces
    assert "GOVERNANCE_REGISTRY.json" in public_surfaces
    assert "唯一正式 read-model home" in public_surfaces
    assert "formal shared service execution facade" in public_surfaces


def test_phase_40_touched_hotspots_keep_port_protocol_and_operation_wording() -> None:
    auth_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "auth_service.py"
    ).read_text(encoding="utf-8")
    endpoint_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "endpoint_surface.py"
    ).read_text(encoding="utf-8")
    endpoint_methods_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "api"
        / "rest_facade_endpoint_methods.py"
    ).read_text(encoding="utf-8")
    snapshot_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "coordinator"
        / "runtime"
        / "device"
        / "snapshot.py"
    ).read_text(encoding="utf-8")
    sender_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "coordinator"
        / "runtime"
        / "command"
        / "sender.py"
    ).read_text(encoding="utf-8")

    assert "AuthPort" in auth_text
    assert "AuthClient" not in auth_text
    assert "endpoint operations collaborator" in endpoint_text
    assert "forwarding" not in endpoint_text
    assert "endpoint-operation surface" in endpoint_methods_text
    assert "Forwarding lives here" not in endpoint_methods_text
    assert "SnapshotProtocolPort" in snapshot_text
    assert "SnapshotProtocolClient" not in snapshot_text
    assert "protocol: LiproProtocolFacade" in sender_text
    assert "client: LiproProtocolFacade" not in sender_text


def test_phase_40_ledgers_keep_service_execution_formal_and_non_delete_target() -> None:
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(
        encoding="utf-8"
    )

    assert "formal service execution facade" in file_matrix_text
    assert "services/execution.py" in residual_text
    assert "formal service execution facade" in residual_text
    assert "## Phase 40 Status Update" in kill_text
    assert "formal service execution facade" in kill_text
    assert "active kill target" in kill_text


def test_phase_43_public_surface_notes_capture_typed_runtime_and_thin_helpers() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "## Phase 43 Control / Runtime Boundary Notes" in public_surfaces
    assert "typed diagnostics/system-health projection" in public_surfaces
    assert "control/service_router_support.py" in public_surfaces
    assert (
        "services/device_lookup.py` 只保留 service-facing `device_id` resolution"
        in public_surfaces
    )
    assert "runtime_infra.py` 继续是 device-registry listener 的 outward formal home" in public_surfaces


def test_phase_49_file_matrix_tracks_topicized_test_topology() -> None:
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )

    for path in (
        "tests/core/test_coordinator_entry.py",
        "tests/core/test_diagnostics_config_entry.py",
        "tests/core/test_diagnostics_device.py",
        "tests/core/test_diagnostics_redaction.py",
        "tests/meta/test_governance_promoted_phase_assets.py",
        "tests/meta/test_governance_followup_route.py",
        "tests/meta/test_governance_milestone_archives.py",
        "tests/platforms/test_update_entity_refresh.py",
        "tests/platforms/test_update_install_flow.py",
        "tests/platforms/test_update_certification_policy.py",
        "tests/platforms/test_update_background_tasks.py",
    ):
        assert path in file_matrix_text

    assert "tests/test_coordinator_public.py" not in file_matrix_text
    assert "tests/test_coordinator_runtime.py" not in file_matrix_text


def test_phase_50_rest_child_facade_and_shared_execution_truth_remain_singular() -> (
    None
):
    request_gateway_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "request_gateway.py"
    ).read_text(encoding="utf-8")
    endpoint_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "endpoint_surface.py"
    ).read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")

    assert "canonical REST child façade" in public_surfaces
    assert "formal shared service execution facade" in public_surfaces
    assert "localized collaborator" in request_gateway_text
    assert "not a second" in request_gateway_text
    assert "public root" in request_gateway_text
    assert "endpoint operations collaborator" in endpoint_text
    assert "forwarding" not in endpoint_text
    assert "REST endpoint operations collaborator home" in file_matrix_text
    assert "REST request-gateway collaborator home" in file_matrix_text
    assert (
        "diagnostics optional-capability helper reusing shared execution auth chain"
        in file_matrix_text
    )
    assert "formal service execution facade" in file_matrix_text


def test_phase_52_public_surface_notes_keep_single_protocol_root_and_request_policy_truth() -> (
    None
):
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )

    assert (
        "## Phase 52 Protocol Root / Request Policy Isolation Notes" in public_surfaces
    )
    assert (
        "protocol_facade_rest_methods.py` 只是 support-only REST child-facing method surface"
        in public_surfaces
    )
    assert (
        "request_policy.py` 现成为 `429` / busy / pacing decision 的 formal truth"
        in public_surfaces
    )
    assert "protocol_facade_rest_methods.py" in file_matrix_text
    assert (
        "canonical protocol live-verb normalization home over REST child ports"
        in file_matrix_text
    )
    assert "formal 429 / busy / pacing policy home" in file_matrix_text
    assert (
        "REST signed transport execution + response normalization home"
        in file_matrix_text
    )
    assert "Generic backoff helper leak" in residual_text


def test_phase_52_internal_request_helpers_do_not_surface_as_top_level_bindings() -> (
    None
):
    forbidden = {"RequestPolicy", "RestRequestGateway", "RestTransportExecutor"}

    for relative_path in (
        "custom_components/lipro/core/api/__init__.py",
        "custom_components/lipro/core/__init__.py",
        "custom_components/lipro/core/protocol/__init__.py",
    ):
        bindings = set(extract_top_level_bindings(_ROOT / relative_path, root=_ROOT))
        assert bindings.isdisjoint(forbidden)


def test_phase_54_helper_hotspot_notes_keep_single_public_homes() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 54 Helper-Hotspot Formalization Notes" in public_surfaces
    assert (
        "manager_support.py` 只允许作为 scope-state / cache / report-submit mechanics 的 support-only seam"
        in public_surfaces
    )
    assert (
        "share_client_support.py` 只承接 token / submit-attempt / outcome mechanics"
        in public_surfaces
    )
    assert (
        "helper_support.py` 只能作为 report / feedback / capability / response mechanics seam inward 使用"
        in public_surfaces
    )
    assert (
        "request_policy_support.py` 只允许作为 pacing/backoff support seam 存在"
        in public_surfaces
    )
    assert "manager_support.py" in file_matrix_text
    assert "share_client_support.py" in file_matrix_text
    assert "helper_support.py" in file_matrix_text
    assert "request_policy_support.py" in file_matrix_text
    assert "已在 Phase 56 关闭" in residual_text


def test_phase_56_neutral_backoff_notes_keep_request_policy_local_and_non_api_callers_off_it() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    request_policy_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "request_policy.py"
    ).read_text(encoding="utf-8")
    backoff_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "utils" / "backoff.py"
    ).read_text(encoding="utf-8")

    assert "## Phase 56 Neutral Backoff Home Notes" in public_surfaces
    assert (
        "core/utils/backoff.py` 是 neutral shared exponential-backoff primitive home"
        in public_surfaces
    )
    assert (
        "request_policy.py` 继续只拥有 API-local `429` / busy / pacing truth"
        in public_surfaces
    )
    assert "custom_components/lipro/core/utils/backoff.py" in file_matrix_text
    assert "neutral shared exponential backoff helper home" in file_matrix_text
    assert "def compute_exponential_retry_wait_time" not in request_policy_text
    assert "Neutral shared exponential backoff helpers" in backoff_text


def test_phase_55_topicized_test_matrix_tracks_thin_shells_and_named_suites() -> None:
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    testing_text = (_ROOT / ".planning" / "codebase" / "TESTING.md").read_text(
        encoding="utf-8"
    )

    for needle in (
        "tests/core/api/test_api_command_surface_commands.py",
        "tests/core/api/test_api_command_surface_misc.py",
        "tests/core/api/test_api_command_surface_rate_limits.py",
        "tests/core/api/test_api_command_surface_responses.py",
        "tests/core/mqtt/test_transport_runtime_connection_loop.py",
        "tests/core/mqtt/test_transport_runtime_ingress.py",
        "tests/core/mqtt/test_transport_runtime_lifecycle.py",
        "tests/core/mqtt/test_transport_runtime_subscriptions.py",
        "tests/platforms/test_light_entity_behavior.py",
        "tests/platforms/test_light_model_and_commands.py",
        "tests/platforms/test_fan_entity_behavior.py",
        "tests/platforms/test_fan_model_and_commands.py",
        "tests/platforms/test_select_behavior.py",
        "tests/platforms/test_select_models.py",
        "tests/platforms/test_switch_behavior.py",
        "tests/platforms/test_switch_models.py",
    ):
        assert needle in file_matrix_text

    for needle in (
        "thin shell after command-surface topicization",
        "thin shell after transport-runtime topicization",
        "thin shell after light topic extraction",
        "thin shell after fan topic extraction",
        "thin shell after select topic extraction",
        "thin shell after switch topic extraction",
    ):
        assert needle in file_matrix_text

    assert f"当前仓库共有 `{_test_file_count()}` 个 `test_*.py` 文件" in testing_text


def test_phase_59_localized_verification_notes_track_topicized_meta_and_device_refresh_suites() -> None:
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    testing_text = (_ROOT / ".planning" / "codebase" / "TESTING.md").read_text(
        encoding="utf-8"
    )
    verification_text = (_ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md").read_text(
        encoding="utf-8"
    )

    for needle in (
        "tests/core/test_device_refresh_parsing.py",
        "tests/core/test_device_refresh_filter.py",
        "tests/core/test_device_refresh_snapshot.py",
        "tests/core/test_device_refresh_runtime.py",
        "tests/meta/public_surface_architecture_policy.py",
        "tests/meta/public_surface_phase_notes.py",
        "tests/meta/public_surface_runtime_contracts.py",
        "tests/meta/governance_phase_history_archive_execution.py",
        "tests/meta/governance_phase_history_mid_closeouts.py",
        "tests/meta/governance_phase_history_current_milestones.py",
        "tests/meta/governance_followup_route_continuation.py",
        "tests/meta/governance_followup_route_closeouts.py",
        "tests/meta/governance_followup_route_current_milestones.py",
    ):
        assert needle in file_matrix_text

    assert "tests/core/test_device_refresh.py" not in file_matrix_text
    assert "Phase 59" in testing_text
    assert "tests/core/test_device_refresh_{parsing,filter,snapshot,runtime}.py" in testing_text

    for needle in (
        "tests/core/test_device_refresh_parsing.py",
        "tests/core/test_device_refresh_filter.py",
        "tests/core/test_device_refresh_snapshot.py",
        "tests/core/test_device_refresh_runtime.py",
        "59-SUMMARY.md",
        "59-VERIFICATION.md",
    ):
        assert needle in verification_text


def test_phase_57_typed_command_result_notes_keep_contract_inside_command_family() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    result_policy_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "command" / "result_policy.py"
    ).read_text(encoding="utf-8")
    result_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "command" / "result.py"
    ).read_text(encoding="utf-8")
    sender_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "coordinator"
        / "runtime"
        / "command"
        / "sender.py"
    ).read_text(encoding="utf-8")
    diagnostics_types_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "diagnostics" / "types.py"
    ).read_text(encoding="utf-8")

    assert "## Phase 57 Typed Command-Result Contract Notes" in public_surfaces
    assert "result_policy.py` 继续是 command-result classification / polling truth home" in public_surfaces
    assert "result.py` 继续是 stable export / failure arbitration home" in public_surfaces
    assert "typed command-result contract" in file_matrix_text
    assert 'type CommandResultState = Literal["confirmed", "failed", "pending", "unknown"]' in result_policy_text
    assert "type CommandFailureReason = Literal[" in result_policy_text
    assert "COMMAND_FAILURE_REASON_COMMAND_RESULT_FAILED" in result_text
    assert "COMMAND_RESULT_STATE_PENDING" in sender_text
    assert "state: CommandResultPollingState" in diagnostics_types_text


def test_phase_58_audit_refresh_notes_keep_public_surface_truth_stable() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")
    architecture_audit_text = (
        _ROOT
        / ".planning"
        / "phases"
        / "58-repository-audit-refresh-and-next-wave-routing"
        / "58-01-ARCHITECTURE-CODE-AUDIT.md"
    ).read_text(encoding="utf-8")

    assert "## Phase 58 Repository Audit Refresh Notes" in public_surfaces
    assert "Phase 58` 不新增 formal root / public surface" in public_surfaces
    assert "## Top Strengths" in architecture_audit_text
    assert "## Hotspot Census" in architecture_audit_text


def test_phase_62_naming_discoverability_notes_are_explicit() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 62 Naming / Discoverability Convergence Notes" in public_surfaces
    assert "extras_support.py` 只承接 payload / panel parsing support mechanics" in public_surfaces
    assert "endpoint_surface.py` 继续只作为 REST endpoint operations localized collaborator" in public_surfaces
    assert "feedback_handlers.py" in public_surfaces
    assert "command_result_handlers.py" in public_surfaces
    assert "capability_handlers.py" in public_surfaces
    assert "custom_components/lipro/core/device/extras_support.py" in file_matrix_text
    assert "DeviceExtras payload / panel parsing support helper home" in file_matrix_text
    assert "diagnostics service mechanics support seam" in file_matrix_text


def test_phase_68_public_surface_notes_capture_hotspot_helpers_and_mqtt_authority() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 68 Review-Fed Hotspot / Docs Closeout Notes" in public_surfaces
    assert "telemetry/outcomes.py" in public_surfaces
    assert "telemetry/json_payloads.py" in public_surfaces
    assert "topics.py` 只保留 boundary-backed adapter" in public_surfaces
    assert "mqtt_decoder.py` 继续是唯一 canonical MQTT topic/payload decode authority" in public_surfaces
    assert "runtime_access_support.py" in public_surfaces
    assert "telemetry helper home for outcome semantics" in file_matrix_text
    assert "telemetry helper home for JSON-safe payload builders" in file_matrix_text
    assert "MQTT boundary-backed topic adapter" in file_matrix_text
    assert "MQTT authority ambiguity" in residual_text



def test_phase_90_hotspot_freeze_public_surface_notes_are_explicit() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 90 Hotspot Routing Freeze Notes" in public_surfaces
    assert "formal homes" in public_surfaces
    assert "client.py` 继续只保留 `LiproRestFacade` stable import shell / home" in public_surfaces
    assert "protected thin adapter / projection / typed-access surfaces" in public_surfaces
    for needle in (
        "formal command-runtime orchestration home",
        "canonical REST child-façade composition home",
        "formal 429 / busy / pacing policy home",
        "formal MQTT-runtime orchestration home",
        "formal anonymous-share aggregate manager home",
        "stable REST façade import shell / home",
        "protected thin runtime read-model / typed access home",
        "protected thin entity command / state projection shell",
        "protected thin OTA projection shell after runtime-boundary tightening",
    ):
        assert needle in file_matrix_text



def test_phase_91_protocol_and_thin_shell_public_surface_notes_are_explicit() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 91 Canonical Boundary Notes" in public_surfaces
    assert "protocol root" in public_surfaces
    assert "rest_port.py` remains the raw REST child-facing port home" in public_surfaces
    assert "protected thin shells / projections" in public_surfaces
    for needle in (
        "canonical protocol live-verb normalization home",
        "typed REST child-façade port home",
        "typed protocol-boundary decode result home",
        "typed boundary decoder registry home",
        "runtime/control public protocol surface and telemetry projection type home",
        "focused no-regrowth guard home for Phase 91 typed-boundary hardening",
    ):
        assert needle in file_matrix_text



def test_phase_93_assurance_freeze_notes_are_explicit() -> None:
    public_surfaces = _PUBLIC_SURFACES.read_text(encoding="utf-8")
    testing_text = (_ROOT / ".planning" / "codebase" / "TESTING.md").read_text(
        encoding="utf-8"
    )
    developer_text = (_ROOT / "docs" / "developer_architecture.md").read_text(
        encoding="utf-8"
    )

    assert "## Phase 93 Assurance Freeze Notes" in public_surfaces
    assert "quality-freeze closeout does not introduce a second public root" in public_surfaces
    assert "tests/meta/test_phase31_runtime_budget_guards.py" in public_surfaces
    assert "## Phase 93 Testing Freeze" in testing_text
    assert "assurance freeze proof" in testing_text
    assert "## Phase 93 Assurance Freeze Notes" in developer_text
