"""Classification registry for file-governance matrix rows."""

from __future__ import annotations

from dataclasses import dataclass


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
    "custom_components/lipro/services/diagnostics/helpers.py": FileGovernanceRow(
        path="custom_components/lipro/services/diagnostics/helpers.py",
        area="Control",
        owner_phase="Phase 3",
        fate="保留",
        residual="diagnostics optional-capability helper reusing shared execution auth chain",
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
        owner_phase="Phase 16 / 60",
        fate="保留",
        residual="thin daily runnable shell for topicized toolchain truth suites",
    ),

"tests/core/ota/test_firmware_manifest.py": FileGovernanceRow(
    path="tests/core/ota/test_firmware_manifest.py",
    area="Domain",
    owner_phase="Phase 4 / 49",
    fate="保留",
    residual="core ota manifest truth home",
),
"tests/core/ota/test_ota_candidate.py": FileGovernanceRow(
    path="tests/core/ota/test_ota_candidate.py",
    area="Domain",
    owner_phase="Phase 4 / 49",
    fate="保留",
    residual="core ota candidate helper home",
),
"tests/core/ota/test_ota_row_selector.py": FileGovernanceRow(
    path="tests/core/ota/test_ota_row_selector.py",
    area="Domain",
    owner_phase="Phase 4 / 49",
    fate="保留",
    residual="core ota row-selector helper home",
),
"tests/core/ota/test_ota_rows_cache.py": FileGovernanceRow(
    path="tests/core/ota/test_ota_rows_cache.py",
    area="Domain",
    owner_phase="Phase 4 / 49",
    fate="保留",
    residual="core ota rows-cache helper home",
),
"tests/core/coordinator/conftest.py": FileGovernanceRow(
    path="tests/core/coordinator/conftest.py",
    area="Runtime",
    owner_phase="Phase 49",
    fate="保留",
    residual="shared coordinator fixture home",
),
"tests/core/coordinator/test_runtime_root.py": FileGovernanceRow(
    path="tests/core/coordinator/test_runtime_root.py",
    area="Runtime",
    owner_phase="Phase 49",
    fate="保留",
    residual="runtime-root topic suite",
),
"tests/core/coordinator/test_runtime_polling.py": FileGovernanceRow(
    path="tests/core/coordinator/test_runtime_polling.py",
    area="Runtime",
    owner_phase="Phase 49",
    fate="保留",
    residual="runtime-polling topic suite",
),
"tests/core/coordinator/test_update_flow.py": FileGovernanceRow(
    path="tests/core/coordinator/test_update_flow.py",
    area="Runtime",
    owner_phase="Phase 49",
    fate="保留",
    residual="coordinator update-flow topic suite",
),
"tests/core/test_coordinator.py": FileGovernanceRow(
    path="tests/core/test_coordinator.py",
    area="Runtime",
    owner_phase="Phase 5 / 49",
    fate="保留",
    residual="service / entity-lifecycle smoke shell",
),
"tests/core/test_coordinator_entry.py": FileGovernanceRow(
    path="tests/core/test_coordinator_entry.py",
    area="Runtime",
    owner_phase="Phase 49",
    fate="保留",
    residual="entry/runtime public-surface smoke home",
),
"tests/core/test_diagnostics.py": FileGovernanceRow(
    path="tests/core/test_diagnostics.py",
    area="Control",
    owner_phase="Phase 3 / 49",
    fate="保留",
    residual="shared helper / cross-surface smoke anchor",
),
"tests/core/test_diagnostics_config_entry.py": FileGovernanceRow(
    path="tests/core/test_diagnostics_config_entry.py",
    area="Control",
    owner_phase="Phase 49",
    fate="保留",
    residual="config-entry diagnostics topic suite",
),
"tests/core/test_diagnostics_device.py": FileGovernanceRow(
    path="tests/core/test_diagnostics_device.py",
    area="Control",
    owner_phase="Phase 49",
    fate="保留",
    residual="device diagnostics topic suite",
),
"tests/core/test_diagnostics_redaction.py": FileGovernanceRow(
    path="tests/core/test_diagnostics_redaction.py",
    area="Control",
    owner_phase="Phase 49",
    fate="保留",
    residual="redaction diagnostics topic suite",
),
"tests/meta/test_governance_closeout_guards.py": FileGovernanceRow(
    path="tests/meta/test_governance_closeout_guards.py",
    area="Assurance",
    owner_phase="Phase 27 / 44 / 49",
    fate="保留",
    residual="helper + promoted-manifest smoke anchor",
),
"tests/meta/test_governance_promoted_phase_assets.py": FileGovernanceRow(
    path="tests/meta/test_governance_promoted_phase_assets.py",
    area="Assurance",
    owner_phase="Phase 49",
    fate="保留",
    residual="promoted-asset topic suite",
),
"tests/meta/test_public_surface_guards.py": FileGovernanceRow(
    path="tests/meta/test_public_surface_guards.py",
    area="Assurance",
    owner_phase="Phase 6",
    fate="保留",
    residual="thin shell after public-surface topicization",
),
"tests/meta/public_surface_architecture_policy.py": FileGovernanceRow(
    path="tests/meta/public_surface_architecture_policy.py",
    area="Assurance",
    owner_phase="Phase 59",
    fate="保留",
    residual="public-surface architecture/policy topic home",
),
"tests/meta/public_surface_phase_notes.py": FileGovernanceRow(
    path="tests/meta/public_surface_phase_notes.py",
    area="Assurance",
    owner_phase="Phase 59",
    fate="保留",
    residual="public-surface phase-note topic home",
),
"tests/meta/public_surface_runtime_contracts.py": FileGovernanceRow(
    path="tests/meta/public_surface_runtime_contracts.py",
    area="Assurance",
    owner_phase="Phase 59",
    fate="保留",
    residual="public-surface runtime-contract topic home",
),
"tests/meta/test_governance_followup_route.py": FileGovernanceRow(
    path="tests/meta/test_governance_followup_route.py",
    area="Assurance",
    owner_phase="Phase 49",
    fate="保留",
    residual="thin shell after followup-route topicization",
),
"tests/meta/governance_followup_route_closeouts.py": FileGovernanceRow(
    path="tests/meta/governance_followup_route_closeouts.py",
    area="Assurance",
    owner_phase="Phase 59",
    fate="保留",
    residual="followup-route closeout topic home",
),
"tests/meta/governance_followup_route_continuation.py": FileGovernanceRow(
    path="tests/meta/governance_followup_route_continuation.py",
    area="Assurance",
    owner_phase="Phase 59",
    fate="保留",
    residual="followup-route continuation topic home",
),
"tests/meta/governance_followup_route_current_milestones.py": FileGovernanceRow(
    path="tests/meta/governance_followup_route_current_milestones.py",
    area="Assurance",
    owner_phase="Phase 59",
    fate="保留",
    residual="followup-route current-milestone topic home",
),
"tests/meta/test_governance_milestone_archives.py": FileGovernanceRow(
    path="tests/meta/test_governance_milestone_archives.py",
    area="Assurance",
    owner_phase="Phase 49",
    fate="保留",
    residual="milestone-archive topic suite",
),
"tests/platforms/test_update.py": FileGovernanceRow(
    path="tests/platforms/test_update.py",
    area="Domain",
    owner_phase="Phase 4 / 49",
    fate="保留",
    residual="thin setup / happy-path smoke shell",
),
"tests/platforms/test_update_entity_refresh.py": FileGovernanceRow(
    path="tests/platforms/test_update_entity_refresh.py",
    area="Domain",
    owner_phase="Phase 49",
    fate="保留",
    residual="update refresh / row-selection topic suite",
),
"tests/platforms/test_update_install_flow.py": FileGovernanceRow(
    path="tests/platforms/test_update_install_flow.py",
    area="Domain",
    owner_phase="Phase 49",
    fate="保留",
    residual="update install-flow topic suite",
),
"tests/platforms/test_update_certification_policy.py": FileGovernanceRow(
    path="tests/platforms/test_update_certification_policy.py",
    area="Domain",
    owner_phase="Phase 49",
    fate="保留",
    residual="update certification-policy topic suite",
),
"tests/platforms/test_update_background_tasks.py": FileGovernanceRow(
    path="tests/platforms/test_update_background_tasks.py",
    area="Domain",
    owner_phase="Phase 49",
    fate="保留",
    residual="update background-task topic suite",
),
"tests/platforms/test_firmware_update_entity_edges.py": FileGovernanceRow(
    path="tests/platforms/test_firmware_update_entity_edges.py",
    area="Domain",
    owner_phase="Phase 4 / 49",
    fate="保留",
    residual="edge-branch shell after topic extraction",
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
    "tests/core/mqtt/test_transport_runtime.py": FileGovernanceRow(
        path="tests/core/mqtt/test_transport_runtime.py",
        area="Protocol",
        owner_phase="Phase 2.5 / 6",
        fate="保留",
        residual="thin shell after transport-runtime topicization",
    ),
    "tests/platforms/test_fan.py": FileGovernanceRow(
        path="tests/platforms/test_fan.py",
        area="Domain",
        owner_phase="Phase 4",
        fate="保留",
        residual="thin shell after fan topic extraction",
    ),
    "tests/platforms/test_light.py": FileGovernanceRow(
        path="tests/platforms/test_light.py",
        area="Domain",
        owner_phase="Phase 4",
        fate="保留",
        residual="thin shell after light topic extraction",
    ),
    "tests/platforms/test_select.py": FileGovernanceRow(
        path="tests/platforms/test_select.py",
        area="Domain",
        owner_phase="Phase 4",
        fate="保留",
        residual="thin shell after select topic extraction",
    ),
    "tests/platforms/test_switch.py": FileGovernanceRow(
        path="tests/platforms/test_switch.py",
        area="Domain",
        owner_phase="Phase 4",
        fate="保留",
        residual="thin shell after switch topic extraction",
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
        residual="thin shell after command-surface topicization",
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
        residual="toolchain + docs navigation + terminology truth guard home",
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
        owner_phase="Phase 3 / 14 / 15 / 37",
        fate="保留",
        residual="public router shell over focused handler/support collaborators",
    ),
    "custom_components/lipro/control/service_router_handlers.py": FileGovernanceRow(
        path="custom_components/lipro/control/service_router_handlers.py",
        area="Control",
        owner_phase="Phase 37",
        fate="保留",
        residual="private control-plane handler implementations home",
    ),
    "custom_components/lipro/control/service_router_support.py": FileGovernanceRow(
        path="custom_components/lipro/control/service_router_support.py",
        area="Control",
        owner_phase="Phase 37",
        fate="保留",
        residual="router lookup/logging/runtime-iterator helper home",
    ),
    "custom_components/lipro/core/api/auth_recovery.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/auth_recovery.py",
        area="Protocol",
        owner_phase="Phase 2 / 35",
        fate="重构",
        residual="REST auth-recovery collaborator home",
    ),
    "custom_components/lipro/core/utils/backoff.py": FileGovernanceRow(
        path="custom_components/lipro/core/utils/backoff.py",
        area="Cross-cutting",
        owner_phase="Phase 56",
        fate="保留",
        residual="neutral shared exponential backoff helper home",
    ),
    "custom_components/lipro/core/api/session_state.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/session_state.py",
        area="Protocol",
        owner_phase="Phase 2 / 15 / 17",
        fate="重构",
        residual="RestSessionState formal REST session-state home",
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
    "custom_components/lipro/core/api/request_gateway.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/request_gateway.py",
        area="Protocol",
        owner_phase="Phase 2",
        fate="重构",
        residual="REST request-gateway collaborator home",
    ),
    "custom_components/lipro/core/api/request_policy.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/request_policy.py",
        area="Protocol",
        owner_phase="Phase 2",
        fate="重构",
        residual="formal 429 / busy / pacing policy home",
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
    "custom_components/lipro/core/coordinator/lifecycle.py": FileGovernanceRow(
        path="custom_components/lipro/core/coordinator/lifecycle.py",
        area="Runtime",
        owner_phase="Phase 36 / 37",
        fate="保留",
        residual="update-cycle / MQTT-setup / shutdown lifecycle helper home",
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
        residual="typed command-result contract classification / retry / delayed-refresh policy home",
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
    "custom_components/lipro/core/api/transport_executor.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/transport_executor.py",
        area="Protocol",
        owner_phase="Phase 2 / 35",
        fate="重构",
        residual="REST signed transport execution + response normalization home",
    ),
    "custom_components/lipro/core/api/endpoint_surface.py": FileGovernanceRow(
        path="custom_components/lipro/core/api/endpoint_surface.py",
        area="Protocol",
        owner_phase="Phase 35",
        fate="保留",
        residual="REST endpoint operations collaborator home",
    ),
    "custom_components/lipro/core/protocol/protocol_facade_rest_methods.py": FileGovernanceRow(
        path="custom_components/lipro/core/protocol/protocol_facade_rest_methods.py",
        area="Protocol",
        owner_phase="Phase 2.5",
        fate="保留",
        residual="support-only REST child-facing method surface for protocol root",
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
    "tests/core/test_device_refresh_filter.py": FileGovernanceRow(
        path="tests/core/test_device_refresh_filter.py",
        area="Cross-cutting",
        owner_phase="Phase 7",
        fate="保留",
        residual="device-refresh filter-semantics topic home",
    ),
    "tests/core/test_device_refresh_parsing.py": FileGovernanceRow(
        path="tests/core/test_device_refresh_parsing.py",
        area="Cross-cutting",
        owner_phase="Phase 7",
        fate="保留",
        residual="device-refresh parsing/normalization topic home",
    ),
    "tests/core/test_device_refresh_runtime.py": FileGovernanceRow(
        path="tests/core/test_device_refresh_runtime.py",
        area="Cross-cutting",
        owner_phase="Phase 7",
        fate="保留",
        residual="device-refresh runtime decision topic home",
    ),
    "tests/core/test_device_refresh_snapshot.py": FileGovernanceRow(
        path="tests/core/test_device_refresh_snapshot.py",
        area="Cross-cutting",
        owner_phase="Phase 7",
        fate="保留",
        residual="device-refresh snapshot-builder topic home",
    ),
    "tests/meta/test_governance_phase_history.py": FileGovernanceRow(
        path="tests/meta/test_governance_phase_history.py",
        area="Assurance",
        owner_phase="Phase 33 / 37",
        fate="保留",
        residual="thin shell after phase-history topicization",
    ),
    "tests/meta/governance_phase_history_archive_execution.py": FileGovernanceRow(
        path="tests/meta/governance_phase_history_archive_execution.py",
        area="Assurance",
        owner_phase="Phase 59",
        fate="保留",
        residual="phase-history archive/execution topic home",
    ),
    "tests/meta/governance_phase_history_current_milestones.py": FileGovernanceRow(
        path="tests/meta/governance_phase_history_current_milestones.py",
        area="Assurance",
        owner_phase="Phase 59",
        fate="保留",
        residual="phase-history current-milestone topic home",
    ),
    "tests/meta/governance_phase_history_mid_closeouts.py": FileGovernanceRow(
        path="tests/meta/governance_phase_history_mid_closeouts.py",
        area="Assurance",
        owner_phase="Phase 59",
        fate="保留",
        residual="phase-history mid-closeout topic home",
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
    "custom_components/lipro/core/mqtt/transport.py": FileGovernanceRow(
        path="custom_components/lipro/core/mqtt/transport.py",
        area="Protocol",
        owner_phase="Phase 2.5 / 15",
        fate="重构",
        residual="concrete MQTT transport home; package no-export keeps locality explicit",
    ),
    "scripts/check_file_matrix.py": FileGovernanceRow(
        path="scripts/check_file_matrix.py",
        area="Assurance",
        owner_phase="Phase 6 / 7 / 60",
        fate="保留",
        residual="thin governance checker root; sibling modules own inventory/classification/markdown/validation truth families",
    ),
    "scripts/check_file_matrix_inventory.py": FileGovernanceRow(
        path="scripts/check_file_matrix_inventory.py",
        area="Assurance",
        owner_phase="Phase 60",
        fate="保留",
        residual="checker inventory walk and repo-root helper home",
    ),
    "scripts/check_file_matrix_registry.py": FileGovernanceRow(
        path="scripts/check_file_matrix_registry.py",
        area="Assurance",
        owner_phase="Phase 60",
        fate="保留",
        residual="file-governance row registry and classification override home",
    ),
    "scripts/check_file_matrix_markdown.py": FileGovernanceRow(
        path="scripts/check_file_matrix_markdown.py",
        area="Assurance",
        owner_phase="Phase 60",
        fate="保留",
        residual="FILE_MATRIX render and parse helper home",
    ),
    "scripts/check_file_matrix_validation.py": FileGovernanceRow(
        path="scripts/check_file_matrix_validation.py",
        area="Assurance",
        owner_phase="Phase 60",
        fate="保留",
        residual="file-governance drift validators and run_checks home",
    ),
    "tests/meta/toolchain_truth_python_stack.py": FileGovernanceRow(
        path="tests/meta/toolchain_truth_python_stack.py",
        area="Assurance",
        owner_phase="Phase 60",
        fate="保留",
        residual="Python pin, devcontainer, and pre-commit toolchain truth family",
    ),
    "tests/meta/toolchain_truth_release_contract.py": FileGovernanceRow(
        path="tests/meta/toolchain_truth_release_contract.py",
        area="Assurance",
        owner_phase="Phase 60",
        fate="保留",
        residual="release workflow and identity-evidence truth family",
    ),
    "tests/meta/toolchain_truth_docs_fast_path.py": FileGovernanceRow(
        path="tests/meta/toolchain_truth_docs_fast_path.py",
        area="Assurance",
        owner_phase="Phase 60",
        fate="保留",
        residual="docs fast-path, continuity, and machine-readable governance truth family",
    ),
    "tests/meta/toolchain_truth_ci_contract.py": FileGovernanceRow(
        path="tests/meta/toolchain_truth_ci_contract.py",
        area="Assurance",
        owner_phase="Phase 60",
        fate="保留",
        residual="CI lane, pre-push, lint, and pytest contract truth family",
    ),
    "tests/meta/toolchain_truth_testing_governance.py": FileGovernanceRow(
        path="tests/meta/toolchain_truth_testing_governance.py",
        area="Assurance",
        owner_phase="Phase 60",
        fate="保留",
        residual="testing-map and derived-governance topology truth family",
    ),
    "tests/meta/toolchain_truth_checker_paths.py": FileGovernanceRow(
        path="tests/meta/toolchain_truth_checker_paths.py",
        area="Assurance",
        owner_phase="Phase 60",
        fate="保留",
        residual="checker-path and local-develop smoke truth family",
    ),
}


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
    if path.startswith("tests/core/mqtt/"):
        return _row_for_path(path, "Protocol", "Phase 2.5 / 6")
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
    if path == "tests/core/test_auth_bootstrap.py":
        return _row_for_path(path, "Cross-cutting", "Phase 18")
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
