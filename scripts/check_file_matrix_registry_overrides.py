"""Override truth families for file-matrix registry rows."""

from __future__ import annotations

from scripts.check_file_matrix_registry_shared import OverrideTruthFamily

BASE_OVERRIDE_TRUTH_FAMILIES = (
    OverrideTruthFamily(area="Protocol", owner_phase="Phase 14", fate="保留", rows=(
        ("custom_components/lipro/core/api/status_fallback.py", "status fallback kernel home"),
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
        ("custom_components/lipro/core/api/schedule_service.py", "helper-only schedule support"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2 / 15 / 17", fate="重构", rows=(
        ("custom_components/lipro/core/api/session_state.py", "RestSessionState formal REST session-state home"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2 / 35", fate="重构", rows=(
        ("custom_components/lipro/core/api/auth_recovery.py", "REST auth-recovery collaborator home"),
        ("custom_components/lipro/core/api/transport_executor.py", "REST signed transport execution + response normalization home"),
        ("custom_components/lipro/core/protocol/facade.py", "formal protocol root with localized REST/MQTT child-façade wiring"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2 / 7 / 12 / 14 / 35", fate="重构", rows=(
        ("custom_components/lipro/core/api/client.py", "thin REST child-façade composition root"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2.5", fate="保留", rows=(
        ("custom_components/lipro/core/protocol/protocol_facade_rest_methods.py", "support-only REST child-facing method surface for protocol root"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2.5 / 12", fate="重构", rows=(
        ("custom_components/lipro/core/api/__init__.py", "-"),
    )),

    OverrideTruthFamily(area="Protocol", owner_phase="Phase 2.5 / 15", fate="重构", rows=(
        ("custom_components/lipro/core/mqtt/transport.py", "concrete MQTT transport home; package no-export keeps locality explicit"),
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

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 6 / 77 / 79", fate="保留", rows=(
        ("tests/meta/governance_contract_helpers.py", "shared governance route/doc helper home"),
        ("tests/meta/governance_current_truth.py", "governance-route contract + shared current/latest archive truth helper"),
        ("tests/meta/test_version_sync.py", "version/runtime metadata sync guard home"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 77", fate="保留", rows=(
        ("tests/meta/governance_promoted_assets.py", "shared promoted-phase-asset helper home"),
        ("tests/meta/test_governance_bootstrap_smoke.py", "focused bootstrap smoke guard home"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 27 / 44 / 49 / 77", fate="保留", rows=(
        ("tests/meta/test_governance_closeout_guards.py", "closeout + promoted-asset manifest smoke anchor"),
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
        ("tests/core/api/test_api_device_surface.py", "topicized device / capability regression home"),
        ("tests/core/api/test_api_transport_and_schedule.py", "topicized transport / schedule regression home"),
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

    OverrideTruthFamily(area="Runtime", owner_phase="Phase 36", fate="保留", rows=(
        ("custom_components/lipro/core/coordinator/services/polling_service.py", "polling/status/outlet/snapshot orchestration helper home"),
        ("tests/core/coordinator/services/test_polling_service.py", "polling-service regression home"),
    )),

    OverrideTruthFamily(area="Runtime", owner_phase="Phase 36 / 37", fate="保留", rows=(
        ("custom_components/lipro/core/coordinator/lifecycle.py", "update-cycle / MQTT-setup / shutdown lifecycle helper home"),
    )),

    OverrideTruthFamily(area="Assurance", owner_phase="Phase 37", fate="保留", rows=(
        ("tests/meta/test_governance_phase_history_runtime.py", "runtime closeout phase-history topic home"),
        ("tests/meta/test_governance_phase_history_topology.py", "topology closeout phase-history topic home"),
    )),

    OverrideTruthFamily(area="Control", owner_phase="Phase 37", fate="保留", rows=(
        ("custom_components/lipro/control/service_router_handlers.py", "private control-plane handler implementations home"),
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
)

OVERRIDE_TRUTH_FAMILIES = BASE_OVERRIDE_TRUTH_FAMILIES + PHASE_79_OVERRIDE_TRUTH_FAMILIES
