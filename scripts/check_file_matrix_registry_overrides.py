"""Override truth families for file-matrix registry rows."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.check_file_matrix_registry_shared import OverrideTruthFamily
elif __package__ in {None, ""}:
    from check_file_matrix_registry_shared import OverrideTruthFamily
else:
    from scripts.check_file_matrix_registry_shared import OverrideTruthFamily


BASE_OVERRIDE_TRUTH_FAMILIES = (
    OverrideTruthFamily(area="Protocol", owner_phase="Phase 14", fate="保留", rows=(
        ("custom_components/lipro/core/api/status_fallback.py", "status fallback outward home with support-backed binary-split implementation"),
    )),

    OverrideTruthFamily(area="Runtime", owner_phase="Phase 14", fate="保留", rows=(
        ("custom_components/lipro/core/coordinator/services/protocol_service.py", "protocol-facing runtime service surface"),
    )),

    OverrideTruthFamily(area="Control", owner_phase="Phase 14 / 15", fate="保留", rows=(
        ("custom_components/lipro/control/developer_router_support.py", "developer diagnostics glue + typed helper home"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 16 / 60", fate="保留", rows=(
        ("tests/meta/test_toolchain_truth.py", "thin daily runnable shell for topicized toolchain truth suites"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2", fate="重构", rows=(
        ("custom_components/lipro/core/api/request_gateway.py", "REST request-gateway collaborator home"),
        ("custom_components/lipro/core/api/request_policy.py", "formal 429 / busy / pacing policy home"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2 / 13 / 14", fate="重构", rows=(
        ("custom_components/lipro/core/api/status_service.py", "public status orchestration home"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2 / 14", fate="重构", rows=(
        ("custom_components/lipro/core/api/schedule_service.py", "candidate-query / mutation schedule collaborator home after inward split"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2 / 15 / 17", fate="重构", rows=(
        ("custom_components/lipro/core/api/session_state.py", "RestSessionState formal REST session-state home"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2 / 35", fate="重构", rows=(
        ("custom_components/lipro/core/api/auth_recovery.py", "REST auth-recovery refresh / replay collaborator home"),
        ("custom_components/lipro/core/api/transport_executor.py", "REST signed transport execution + response normalization home"),
        ("custom_components/lipro/core/protocol/facade.py", "formal protocol root with localized REST/MQTT child-façade wiring"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2 / 7 / 12 / 14 / 35", fate="重构", rows=(
        ("custom_components/lipro/core/api/client.py", "stable REST façade import shell / home"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2.5", fate="保留", rows=(
        ("custom_components/lipro/core/protocol/protocol_facade_rest_methods.py", "canonical protocol live-verb normalization home over REST child ports"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2.5 / 12", fate="重构", rows=(
        ("custom_components/lipro/core/api/__init__.py", "-"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2.5 / 15", fate="重构", rows=(
        ("custom_components/lipro/core/mqtt/transport.py", "concrete MQTT transport home with explicit runtime owner/state contract projection; package no-export keeps locality explicit"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2.5 / 6", fate="保留", rows=(
        ("tests/core/mqtt/test_transport_runtime.py", "thin shell after transport-runtime topicization"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2.5 / 7 / 17", fate="迁移适配", rows=(
        ("custom_components/lipro/core/mqtt/__init__.py", "package export intentionally minimal; no concrete transport export"),
    )),

    OverrideTruthFamily(area="Control", owner_phase="Phase 27 / 37", fate="保留", rows=(
        ("tests/core/test_init_service_handlers.py", "shared helper root for topicized init service-handler regressions"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 6 / 77 / 79 / 105", fate="保留", rows=(
        ("tests/meta/governance_contract_helpers.py", "shared governance route/doc helper home"),
        ("tests/meta/governance_current_truth.py", "governance-route contract + shared current/latest archive truth helper"),
        ("tests/meta/test_version_sync.py", "version/runtime metadata sync guard home"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 77", fate="保留", rows=(
        ("tests/meta/governance_promoted_assets.py", "shared promoted-phase-asset helper home"),
        ("tests/meta/test_governance_bootstrap_smoke.py", "focused bootstrap smoke guard home"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 27 / 44 / 49 / 77 / 88 / 105", fate="保留", rows=(
        ("tests/meta/test_governance_closeout_guards.py", "closeout + promoted-asset manifest smoke anchor + milestone-freeze exit-contract bridge"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 88", fate="保留", rows=(
        ("tests/meta/test_phase88_governance_quality_freeze_guards.py", "focused guard home for phase-88 governance/evidence freeze"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2 / 85 / 87", fate="保留", rows=(
        ("tests/core/api/test_api_diagnostics_service.py", "thin anchor after diagnostics API hotspot topicization"),
        ("tests/core/api/test_protocol_contract_matrix.py", "thin anchor after protocol-contract hotspot topicization"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 87", fate="保留", rows=(
        ("tests/core/api/test_api_diagnostics_service_support.py", "local inward helper home for diagnostics API topical suites"),
    )),

    OverrideTruthFamily(area="Runtime", owner_phase="Phase 5 / 6 / 85 / 87", fate="保留", rows=(
        ("tests/core/coordinator/runtime/test_mqtt_runtime.py", "thin shell after MQTT runtime hotspot topicization"),
    )),

    OverrideTruthFamily(area="Runtime", owner_phase="Phase 87", fate="保留", rows=(
        ("tests/core/coordinator/runtime/test_mqtt_runtime_support.py", "local support helper home for topicized MQTT runtime suites"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 87", fate="保留", rows=(
        ("tests/meta/test_phase87_assurance_hotspot_guards.py", "focused no-regrowth guard home for Phase 87 assurance hotspot topicization"),
    )),

    OverrideTruthFamily(area="Control", owner_phase="Phase 3", fate="保留", rows=(
        ("custom_components/lipro/services/diagnostics/helpers.py", "diagnostics optional-capability helper reusing shared execution auth chain"),
    )),

    OverrideTruthFamily(area="Control", owner_phase="Phase 3 / 14 / 15 / 37", fate="保留", rows=(
        ("custom_components/lipro/control/service_router.py", "public router shell over focused handler/support collaborators"),
    )),

    OverrideTruthFamily(area="Control", owner_phase="Phase 3 / 49", fate="保留", rows=(
        ("tests/core/test_diagnostics.py", "shared helper / cross-surface smoke anchor"),
    )),

    OverrideTruthFamily(area="Control", owner_phase="Phase 3 / 5 / 7", fate="保留", rows=(
        ("custom_components/lipro/services/execution.py", "formal service execution facade; private auth seam closed"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 33 / 77 / 79", fate="保留", rows=(
        ("tests/meta/test_governance_guards.py", "inventory / policy governance topic root"),
        ("tests/meta/test_governance_release_contract.py", "release/governance workflow anchor suite"),
    )),

    OverrideTruthFamily(area="Control", owner_phase="Phase 33", fate="保留", rows=(
        ("tests/core/test_init.py", "topic root for init contract regressions"),
        ("tests/core/test_init_schema_validation.py", "schema-focused init regression home"),
    )),

    OverrideTruthFamily(area="Cross-cutting", owner_phase="Phase 33", fate="保留", rows=(
        ("custom_components/lipro/core/command/result_policy.py", "typed command-result contract classification / retry / delayed-refresh policy home"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 33", fate="保留", rows=(
        ("custom_components/lipro/core/protocol/boundary/rest_decoder_support.py", "REST decoder canonicalization helper home"),
        ("tests/core/api/test_api.py", "topic root for auth/init REST regressions"),
        ("tests/core/api/test_api_command_surface.py", "thin shell after command-surface topicization"),
        ("tests/core/api/test_api_device_surface.py", "thin shell after device-surface topicization"),
        ("tests/core/api/test_api_device_surface_devices.py", "device-list API regression topic home"),
        ("tests/core/api/test_api_device_surface_status.py", "device-status API regression topic home"),
        ("tests/core/api/test_api_device_surface_mesh_groups.py", "mesh-group status API regression topic home"),
        ("tests/core/api/test_api_device_surface_connect_status.py", "connect-status API regression topic home"),
        ("tests/core/api/test_api_device_surface_outlet_power.py", "outlet-power API regression topic home"),
        ("tests/core/api/test_api_device_surface_optional_capabilities.py", "optional-capability API regression topic home"),
        ("tests/core/api/test_api_transport_and_schedule.py", "thin shell after transport/schedule topicization"),
        ("tests/core/api/test_api_transport_and_schedule_transport_boundary.py", "transport-boundary API regression topic home"),
        ("tests/core/api/test_api_transport_and_schedule_mqtt.py", "MQTT-config API regression topic home"),
        ("tests/core/api/test_api_transport_and_schedule_close.py", "client-close API regression topic home"),
        ("tests/core/api/test_api_transport_and_schedule_schedules.py", "schedule API regression topic home"),
    )),

    OverrideTruthFamily(area="Runtime", owner_phase="Phase 33", fate="保留", rows=(
        ("custom_components/lipro/core/coordinator/runtime/device/snapshot_models.py", "typed snapshot container + rejection contract home"),
        ("custom_components/lipro/core/coordinator/runtime/mqtt/adapters.py", "MQTT callback adapter helper home"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 33 / 37", fate="保留", rows=(
        ("tests/meta/test_governance_phase_history.py", "thin shell after phase-history topicization"),
    )),

    OverrideTruthFamily(area="Control", owner_phase="Phase 33 / 37", fate="保留", rows=(
        ("tests/core/test_init_runtime_behavior.py", "shared helper root for topicized init runtime regressions"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 35", fate="保留", rows=(
        ("custom_components/lipro/core/api/endpoint_surface.py", "REST endpoint operations collaborator home"),
        ("custom_components/lipro/core/protocol/mqtt_facade.py", "MQTT child façade home under the unified protocol root"),
        ("custom_components/lipro/core/protocol/rest_port.py", "typed REST child-façade port home"),
    )),

    OverrideTruthFamily(area="Runtime", owner_phase="Phase 90", fate="重构", rows=(
        ("custom_components/lipro/core/coordinator/runtime/command_runtime.py", "formal command-runtime orchestration home with inward trace / failure helpers and support-backed request / failure helpers"),
        ("custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py", "formal MQTT-runtime orchestration home with localized transport / notification helpers"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 90", fate="重构", rows=(
        ("custom_components/lipro/core/api/rest_facade.py", "canonical REST child-façade composition home"),
        ("custom_components/lipro/core/anonymous_share/manager.py", "formal anonymous-share aggregate manager home with scope-state support collaborators"),
    )),

    OverrideTruthFamily(area="Control", owner_phase="Phase 90", fate="保留", rows=(
        ("custom_components/lipro/__init__.py", "protected thin HA root adapter / lazy wiring shell"),
        ("custom_components/lipro/control/runtime_access.py", "protected thin runtime read-model / typed access home"),
    )),

    OverrideTruthFamily(area="Domain", owner_phase="Phase 90", fate="保留", rows=(
        ("custom_components/lipro/entities/base.py", "protected thin entity command / state projection shell"),
        ("custom_components/lipro/entities/firmware_update.py", "protected thin OTA projection shell after runtime-boundary tightening"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 91", fate="保留", rows=(
        ("custom_components/lipro/core/protocol/boundary/result.py", "typed protocol-boundary decode result home"),
        ("custom_components/lipro/core/protocol/boundary/schema_registry.py", "typed boundary decoder registry home"),
    )),

    OverrideTruthFamily(area="Cross-cutting", owner_phase="Phase 91", fate="保留", rows=(
        ("custom_components/lipro/runtime_types.py", "runtime/control public protocol surface and telemetry projection type home"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 91", fate="保留", rows=(
        ("tests/meta/test_phase91_typed_boundary_guards.py", "focused no-regrowth guard home for Phase 91 typed-boundary hardening"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 89", fate="保留", rows=(
        ("scripts/agent_worker.py", "retired fail-fast migration stub only; not the runtime orchestrator"),
        ("scripts/orchestrator.py", "retired fail-fast migration stub only; not the runtime orchestrator"),
    )),

    OverrideTruthFamily(area="Control", owner_phase="Phase 92", fate="保留", rows=(
        ("custom_components/lipro/control/redaction.py", "diagnostics-facing redaction adapter on shared redaction contract with inward recursion helpers"),
        ("tests/services/test_services_diagnostics.py", "thin shell after diagnostics-services topicization"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 92", fate="保留", rows=(
        ("custom_components/lipro/core/anonymous_share/sanitize.py", "structure-preserving anonymous-share sanitizer on shared redaction contract; structure-preserving anonymous-share sanitizer with container/scalar helper split"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 92", fate="保留", rows=(
        ("custom_components/lipro/core/telemetry/exporter.py", "shared-policy telemetry exporter with pseudonymous alias + marker summary budget contract; shared-policy telemetry exporter with localized sanitize helper split"),
    )),

    OverrideTruthFamily(area="Runtime", owner_phase="Phase 36", fate="保留", rows=(
        ("custom_components/lipro/core/coordinator/services/polling_service.py", "polling/status/outlet/snapshot orchestration helper home"),
        ("tests/core/coordinator/services/test_polling_service.py", "polling-service regression home"),
    )),

    OverrideTruthFamily(area="Runtime", owner_phase="Phase 36 / 37", fate="保留", rows=(
        ("custom_components/lipro/core/coordinator/lifecycle.py", "update-cycle / MQTT-setup / shutdown lifecycle helper home"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 37", fate="保留", rows=(
        ("tests/meta/test_governance_phase_history_runtime.py", "runtime closeout phase-history topic home"),
        ("tests/meta/test_governance_phase_history_topology.py", "thin shell after topology phase-history topicization"),
        ("tests/meta/governance_phase_history_topology_foundations.py", "foundation/early-route phase-history topology topic home"),
        ("tests/meta/governance_phase_history_topology_execution.py", "archived execution phase-history topology topic home"),
        ("tests/meta/governance_phase_history_topology_closeouts.py", "closeout/promoted-asset phase-history topology topic home"),
    )),

    OverrideTruthFamily(area="Cross-cutting", owner_phase="Phase 112", fate="保留", rows=(("custom_components/lipro/runtime_infra.py", "shared runtime infra formal home"),)),

    OverrideTruthFamily(area="Cross-cutting", owner_phase="Phase 112 / 124", fate="保留", rows=(("custom_components/lipro/entry_auth.py", "config-entry auth/bootstrap formal home + persisted auth-seed single-source + token persistence truth"),)),

    OverrideTruthFamily(area="Control", owner_phase="Phase 3 / 124", fate="保留", rows=(("custom_components/lipro/config_flow.py", "HA config-flow thin adapter over localized flow step handlers"), ("custom_components/lipro/flow/login.py", "config-entry login projection consuming entry_auth seed truth"), ("custom_components/lipro/flow/submission.py", "flow submission normalization consuming entry_auth remembered-hash truth"), ("custom_components/lipro/services/contracts.py", "schedule direct-call normalization / result-typing truth home"), ("custom_components/lipro/services/schedule.py", "schedule service helper consuming shared contracts truth"),)),

    OverrideTruthFamily(area="Control", owner_phase="Phase 124", fate="保留", rows=(("custom_components/lipro/flow/step_handlers.py", "localized user / reauth / reconfigure orchestration home behind config_flow thin adapter"), ("custom_components/lipro/services/schedule_support.py", "schedule payload validation / row normalization support home behind shared contracts truth"),)),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 124", fate="保留", rows=(("tests/meta/test_phase124_flow_auth_schedule_contract_guards.py", "focused closeout guard home for Phase 124 auth/flow/schedule contract closure"),)),

    OverrideTruthFamily(area="Control", owner_phase="Phase 123", fate="保留", rows=(
        ("custom_components/lipro/control/service_router_handlers.py", "control-local callback family home for command/schedule/share/maintenance service-router handlers"),
        ("custom_components/lipro/control/service_router_support.py", "router lookup/logging/runtime-iterator helper home"),
        ("tests/core/test_init_runtime_bootstrap.py", "bootstrap/infrastructure topic home"),
        ("tests/core/test_init_runtime_registry_refresh.py", "registry-refresh topic home"),
        ("tests/core/test_init_runtime_setup_entry.py", "setup-entry topic home"),
        ("tests/core/test_init_runtime_setup_entry_failures.py", "setup-entry failure topic home"),
        ("tests/core/test_init_runtime_unload_reload.py", "unload/reload topic home"),
        ("tests/core/test_init_service_handlers_commands.py", "command-dispatch topic home"),
        ("tests/core/test_init_service_handlers_debug_queries.py", "debug-query topic home"),
        ("tests/core/test_init_service_handlers_device_resolution.py", "device-resolution topic home"),
        ("tests/core/test_init_service_handlers_schedules.py", "schedule-validation topic home"),
        ("tests/core/test_init_service_handlers_share_reports.py", "share-report topic home"),
    )),

    OverrideTruthFamily(area="Domain", owner_phase="Phase 4", fate="保留", rows=(
        ("tests/platforms/test_fan.py", "thin shell after fan topic extraction"),
        ("tests/platforms/test_light.py", "thin shell after light topic extraction"),
        ("tests/platforms/test_select.py", "thin shell after select topic extraction"),
        ("tests/platforms/test_switch.py", "thin shell after switch topic extraction"),
    )),

    OverrideTruthFamily(area="Domain", owner_phase="Phase 4 / 49", fate="保留", rows=(
        ("tests/core/ota/test_firmware_manifest.py", "core ota manifest truth home"),
        ("tests/core/ota/test_ota_candidate.py", "core ota candidate helper home"),
        ("tests/core/ota/test_ota_row_selector.py", "core ota row-selector helper home"),
        ("tests/core/ota/test_ota_rows_cache.py", "core ota rows-cache helper home"),
        ("tests/platforms/test_firmware_update_entity_edges.py", "edge-branch shell after topic extraction"),
        ("tests/platforms/test_update.py", "thin setup / happy-path smoke shell"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 49", fate="保留", rows=(
        ("tests/meta/test_governance_followup_route.py", "thin shell after followup-route topicization"),
        ("tests/meta/test_governance_milestone_archives.py", "thin shell after milestone-archive topicization"),
        ("tests/meta/governance_milestone_archives_assets.py", "milestone-archive asset existence topic home"),
        ("tests/meta/test_governance_promoted_phase_assets.py", "promoted-asset topic suite"),
    )),

    OverrideTruthFamily(area="Control", owner_phase="Phase 49", fate="保留", rows=(
        ("tests/core/test_diagnostics_config_entry.py", "config-entry diagnostics topic suite"),
        ("tests/core/test_diagnostics_device.py", "device diagnostics topic suite"),
        ("tests/core/test_diagnostics_redaction.py", "redaction diagnostics topic suite"),
    )),

    OverrideTruthFamily(area="Domain", owner_phase="Phase 49", fate="保留", rows=(
        ("tests/platforms/test_update_background_tasks.py", "update background-task topic suite"),
        ("tests/platforms/test_update_certification_policy.py", "update certification-policy topic suite"),
        ("tests/platforms/test_update_entity_refresh.py", "update refresh / row-selection topic suite"),
        ("tests/platforms/test_update_install_flow.py", "update install-flow topic suite"),
    )),

    OverrideTruthFamily(area="Runtime", owner_phase="Phase 49", fate="保留", rows=(
        ("tests/core/coordinator/conftest.py", "shared coordinator fixture home"),
        ("tests/core/coordinator/test_runtime_polling.py", "runtime-polling topic suite"),
        ("tests/core/coordinator/test_runtime_root.py", "runtime-root topic suite"),
        ("tests/core/coordinator/test_update_flow.py", "coordinator update-flow topic suite"),
        ("tests/core/test_coordinator_entry.py", "entry/runtime public-surface smoke home"),
    )),

    OverrideTruthFamily(area="Runtime", owner_phase="Phase 5 / 14 / 36", fate="重构", rows=(
        ("custom_components/lipro/core/coordinator/coordinator.py", "HA-facing runtime façade with polling ballast reduced"),
    )),

    OverrideTruthFamily(area="Runtime", owner_phase="Phase 5 / 49", fate="保留", rows=(
        ("tests/core/test_coordinator.py", "service / entity-lifecycle smoke shell"),
    )),

    OverrideTruthFamily(area="Cross-cutting", owner_phase="Phase 56", fate="保留", rows=(
        ("custom_components/lipro/core/utils/backoff.py", "neutral shared exponential backoff helper home"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 59", fate="保留", rows=(
        ("tests/meta/governance_followup_route_closeouts.py", "followup-route closeout topic home"),
        ("tests/meta/governance_followup_route_continuation.py", "followup-route continuation topic home"),
        ("tests/meta/governance_phase_history_archive_execution.py", "phase-history archive/execution topic home"),
        ("tests/meta/governance_phase_history_current_milestones.py", "phase-history current-milestone topic home"),
        ("tests/meta/governance_phase_history_mid_closeouts.py", "phase-history mid-closeout topic home"),
        ("tests/meta/public_surface_architecture_policy.py", "public-surface architecture/policy topic home"),
        ("tests/meta/public_surface_phase_notes.py", "public-surface phase-note topic home"),
        ("tests/meta/public_surface_runtime_contracts.py", "public-surface runtime-contract topic home"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 6", fate="保留", rows=(
        ("tests/meta/test_public_surface_guards.py", "thin shell after public-surface topicization"),
        ("tests/meta/test_dependency_guards.py", "thin shell after dependency-guard topicization"),
        ("tests/meta/dependency_guard_helpers.py", "shared dependency-guard structural-rule helper home"),
        ("tests/meta/dependency_guards_policy.py", "architecture-policy structural-rule guard family"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 6 / 7 / 60", fate="保留", rows=(
        ("scripts/check_file_matrix.py", "thin governance checker root; sibling modules own inventory/classification/markdown/validation truth families"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 60", fate="保留", rows=(
        ("scripts/check_file_matrix_inventory.py", "checker inventory walk and repo-root helper home"),
        ("scripts/check_file_matrix_markdown.py", "FILE_MATRIX render and parse helper home"),
        ("scripts/check_file_matrix_registry.py", "file-governance row registry and classification override home"),
        ("scripts/check_file_matrix_validation.py", "file-governance drift validators and run_checks home"),
        ("tests/meta/toolchain_truth_checker_paths.py", "checker-path and local-develop smoke truth family"),
        ("tests/meta/toolchain_truth_ci_contract.py", "CI lane, pre-push, lint, and pytest contract truth family"),
                ("tests/meta/toolchain_truth_python_stack.py", "Python pin, devcontainer, and pre-commit toolchain truth family"),
        ("tests/meta/toolchain_truth_release_contract.py", "release workflow and identity-evidence truth family"),
        ("tests/meta/toolchain_truth_testing_governance.py", "testing-map and derived-governance topology truth family"),
    )),

    OverrideTruthFamily(area="Cross-cutting", owner_phase="Phase 7", fate="保留", rows=(
        ("tests/core/test_device_refresh_filter.py", "device-refresh filter-semantics topic home"),
        ("tests/core/test_device_refresh_parsing.py", "device-refresh parsing/normalization topic home"),
        ("tests/core/test_device_refresh_runtime.py", "device-refresh runtime decision topic home"),
        ("tests/core/test_device_refresh_snapshot.py", "device-refresh snapshot-builder topic home"),
    )),


OverrideTruthFamily(area="Cross-cutting", owner_phase="Phase 7 / 74", fate="保留", rows=(
    ("tests/core/test_share_client.py", "thin shell after ShareWorkerClient topicization"),
    ("tests/core/test_share_client_support.py", "shared helper root for ShareWorkerClient topicized suites"),
    ("tests/core/test_share_client_primitives.py", "ShareWorkerClient primitive/token topic home"),
    ("tests/core/test_share_client_refresh.py", "ShareWorkerClient token-refresh topic home"),
    ("tests/core/test_share_client_submit.py", "ShareWorkerClient submit/outcome topic home"),
    ("tests/core/test_share_client_boundary.py", "ShareWorkerClient external-boundary proof home"),
)),

OverrideTruthFamily(area="Runtime", owner_phase="Phase 5 / 6 / 74", fate="保留", rows=(
    ("tests/core/coordinator/runtime/test_command_runtime.py", "thin shell after CommandRuntime topicization"),
    ("tests/core/coordinator/runtime/test_command_runtime_support.py", "shared helper root for CommandRuntime topicized suites"),
    ("tests/core/coordinator/runtime/test_command_runtime_builder_retry.py", "CommandRuntime builder/retry topic home"),
    ("tests/core/coordinator/runtime/test_command_runtime_sender.py", "CommandRuntime sender topic home"),
    ("tests/core/coordinator/runtime/test_command_runtime_confirmation.py", "CommandRuntime confirmation topic home"),
    ("tests/core/coordinator/runtime/test_command_runtime_orchestration.py", "CommandRuntime orchestration topic home"),
)),

    OverrideTruthFamily(area="Runtime", owner_phase="Phase 7", fate="删除候选", rows=(
        ("custom_components/lipro/core/coordinator/device_registry_sync.py", "shadow helper"),
        ("custom_components/lipro/core/coordinator/runtime/group_lookup_runtime.py", "shadow helper"),
        ("custom_components/lipro/core/coordinator/runtime/room_sync_runtime.py", "shadow helper"),
        ("custom_components/lipro/core/coordinator/runtime/state_batch_runtime.py", "shadow helper"),
        ("custom_components/lipro/core/coordinator/runtime/status_strategy.py", "shadow helper / dead strategy"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 7.2", fate="保留", rows=(
        ("scripts/check_architecture_policy.py", "-"),
        ("tests/helpers/architecture_policy.py", "-"),
        ("tests/helpers/ast_guard_utils.py", "-"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 49 / 77 / 80", fate="保留", rows=(
        ("tests/meta/governance_milestone_archives_truth.py", "milestone-archive authority/pointer truth topic home"),
        ("tests/meta/governance_milestone_archives_ordering.py", "milestone-archive snapshot ordering + historical-route topic home"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 40 / 43 / 50 / 53 / 68", fate="保留", rows=(
        ("tests/meta/dependency_guards_service_runtime.py", "service/runtime dependency-story guard family"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 40 / 52 / 57", fate="保留", rows=(
        ("tests/meta/dependency_guards_protocol_contracts.py", "protocol/schedule dependency-story guard family"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 48 / 49 / 54 / 55 / 56 / 58 / 62", fate="保留", rows=(
        ("tests/meta/dependency_guards_review_ledgers.py", "dependency-note / verification / naming topic guard family"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 44 / 60", fate="保留", rows=(
        ("tests/meta/toolchain_truth_docs_fast_path.py", "docs fast-path, continuity, and machine-readable governance truth family; toolchain + docs navigation + terminology truth guard home"),
    )),
)

PHASE_79_OVERRIDE_TRUTH_FAMILIES = (
    OverrideTruthFamily(area="Assurance", owner_phase="Phase 79", fate="保留", rows=(
        ("scripts/check_file_matrix_registry_shared.py", "registry shared type + row builder home"),
        ("scripts/check_file_matrix_registry_overrides.py", "registry override-family home"),
        ("scripts/check_file_matrix_registry_classifiers.py", "registry classifier-rule home"),
        ("tests/meta/test_governance_release_docs.py", "release/docs topic suite home"),
        ("tests/meta/test_governance_release_continuity.py", "release continuity/custody topic suite home"),
    )),
    OverrideTruthFamily(area="Assurance", owner_phase="Phase 94 / 95 / 96 / 97 / 98 / 99 / 100 / 101 / 102", fate="保留", rows=(
        ("custom_components/lipro/core/anonymous_share/manager_support.py", "anonymous-share scope-state / pending aggregation helper home"),
        ("custom_components/lipro/core/api/status_fallback_support.py", "status fallback local recursion/logging support collaborator"),
        ("custom_components/lipro/core/api/schedule_service_support.py", "schedule-service local candidate batching/timeout/request support collaborator"),
        ("custom_components/lipro/core/coordinator/runtime/command_runtime_support.py", "command-runtime local request/summary support collaborator"),
        ("custom_components/lipro/core/coordinator/runtime/mqtt_runtime_support.py", "MQTT-runtime local transport/notification/background-task support collaborator"),
        ("tests/meta/test_phase94_typed_boundary_guards.py", "focused no-regrowth guard home for Phase 94 typed payload contraction"),
        ("tests/meta/test_phase95_hotspot_decomposition_guards.py", "focused no-regrowth guard home for Phase 95 hotspot inward decomposition"),
        ("tests/meta/test_phase96_sanitizer_burndown_guards.py", "focused no-regrowth guard home for Phase 96 sanitizer burn-down"),
        ("tests/meta/test_phase97_governance_assurance_freeze_guards.py", "focused closeout guard home for Phase 97 governance / assurance freeze"),
        ("tests/meta/test_phase98_route_reactivation_guards.py", "focused predecessor guard home for Phase 98 reactivation / carry-forward closure"),
        ("tests/meta/test_phase99_runtime_hotspot_support_guards.py", "focused predecessor guard home for Phase 99 runtime hotspot support extraction / governance freeze"),
        ("tests/meta/test_phase100_runtime_schedule_support_guards.py", "focused predecessor guard home for Phase 100 MQTT/runtime schedule support extraction / governance freeze"),
        ("tests/meta/test_phase101_anonymous_share_rest_boundary_guards.py", "focused predecessor guard home for Phase 101 anonymous-share / REST-boundary hotspot decomposition / governance freeze"),
        ("tests/meta/test_phase102_governance_portability_guards.py", "focused archived-continuity guard home for Phase 102 governance portability / verification stratification / open-source continuity hardening"),
    )),
    OverrideTruthFamily(area="Protocol", owner_phase="Phase 101", fate="保留", rows=(
        ("custom_components/lipro/core/anonymous_share/manager_submission.py", "anonymous-share submit-flow inward collaborator home"),
        ("custom_components/lipro/core/protocol/boundary/rest_decoder.py", "REST boundary decoder family home"),
        ("custom_components/lipro/core/api/mqtt_api_service.py", "MQTT-config boundary-truth reuse helper"),
        ("custom_components/lipro/core/api/rest_facade_endpoint_methods.py", "REST child-facing typed endpoint wording helper"),
    )),
)

OVERRIDE_TRUTH_FAMILIES = BASE_OVERRIDE_TRUTH_FAMILIES + PHASE_79_OVERRIDE_TRUTH_FAMILIES
