# File Matrix

**Python files total:** 667
**Status:** File-level governance authority
**Rule:** workspace inventory excluding caches / virtual env / tooling artifacts

## File-Level Governance Matrix

| Path | Area | Owner phase | Fate | Residual / delete gate |
|------|------|-------------|------|-------------------------|
| `custom_components/lipro/__init__.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/binary_sensor.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/climate.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/config_flow.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/const/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/const/api.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/const/base.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/const/categories.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/const/config.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/const/device_types.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/const/entity_config.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/const/properties.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/control/__init__.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/developer_router_support.py` | Control | Phase 14 / 15 | 保留 | developer diagnostics glue + typed helper home |
| `custom_components/lipro/control/diagnostics_surface.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/entry_lifecycle_controller.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/entry_lifecycle_failures.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/entry_lifecycle_support.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/entry_root_wiring.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/models.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/redaction.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/runtime_access.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/runtime_access_support.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/runtime_access_support_devices.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/runtime_access_support_members.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/runtime_access_support_telemetry.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/runtime_access_support_views.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/runtime_access_types.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/service_registry.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/service_router.py` | Control | Phase 3 / 14 / 15 / 37 | 保留 | public router shell over focused handler/support collaborators |
| `custom_components/lipro/control/service_router_handlers.py` | Control | Phase 37 | 保留 | private control-plane handler implementations home |
| `custom_components/lipro/control/service_router_support.py` | Control | Phase 37 | 保留 | router lookup/logging/runtime-iterator helper home |
| `custom_components/lipro/control/system_health_surface.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/telemetry_surface.py` | Control | Phase 7.3 | 保留 | - |
| `custom_components/lipro/coordinator_entry.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/core/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/__init__.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/capabilities.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/collector.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/const.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/manager.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/manager_submission.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/manager_support.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/models.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/registry.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/report_builder.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/sanitize.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/share_client.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/share_client_flows.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/share_client_ports.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/share_client_refresh.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/share_client_submit.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/share_client_support.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/storage.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/api/__init__.py` | Protocol | Phase 2.5 / 12 | 重构 | - |
| `custom_components/lipro/core/api/auth_recovery.py` | Protocol | Phase 2 / 35 | 重构 | REST auth-recovery collaborator home |
| `custom_components/lipro/core/api/auth_service.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/client.py` | Protocol | Phase 2 / 7 / 12 / 14 / 35 | 重构 | thin REST child-façade composition root |
| `custom_components/lipro/core/api/client_pacing.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/command_api_service.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/diagnostics_api_history.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/diagnostics_api_ota.py` | Protocol | Phase 2 | 重构 | OTA diagnostics outward helper home |
| `custom_components/lipro/core/api/diagnostics_api_ota_support.py` | Protocol | Phase 2 | 重构 | OTA diagnostics mechanics support seam |
| `custom_components/lipro/core/api/diagnostics_api_queries.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/diagnostics_api_service.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/endpoint_surface.py` | Protocol | Phase 35 | 保留 | REST endpoint operations collaborator home |
| `custom_components/lipro/core/api/endpoints/__init__.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/endpoints/auth.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/endpoints/commands.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/endpoints/connect_status.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/endpoints/devices.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/endpoints/misc.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/endpoints/payloads.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/endpoints/schedule.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/endpoints/status.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/errors.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/mqtt_api_service.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/observability.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/power_service.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/request_codec.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/request_gateway.py` | Protocol | Phase 2 | 重构 | REST request-gateway collaborator home |
| `custom_components/lipro/core/api/request_policy.py` | Protocol | Phase 2 | 重构 | formal 429 / busy / pacing policy home |
| `custom_components/lipro/core/api/request_policy_support.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/response_safety.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/rest_facade.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/rest_facade_endpoint_methods.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/rest_facade_request_methods.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/schedule_codec.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/schedule_endpoint.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/schedule_service.py` | Protocol | Phase 2 / 14 | 重构 | helper-only schedule support |
| `custom_components/lipro/core/api/session_state.py` | Protocol | Phase 2 / 15 / 17 | 重构 | RestSessionState formal REST session-state home |
| `custom_components/lipro/core/api/status_fallback.py` | Protocol | Phase 14 | 保留 | status fallback kernel home |
| `custom_components/lipro/core/api/status_service.py` | Protocol | Phase 2 / 13 / 14 | 重构 | public status orchestration home |
| `custom_components/lipro/core/api/transport_core.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/transport_executor.py` | Protocol | Phase 2 / 35 | 重构 | REST signed transport execution + response normalization home |
| `custom_components/lipro/core/api/transport_retry.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/transport_signing.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/types.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/auth/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/auth/bootstrap.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/auth/manager.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/capability/__init__.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/core/capability/models.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/core/capability/registry.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/core/command/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/command/confirmation_tracker.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/command/dispatch.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/command/expectation.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/command/post_refresh.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/command/result.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/command/result_policy.py` | Cross-cutting | Phase 33 | 保留 | typed command-result contract classification / retry / delayed-refresh policy home |
| `custom_components/lipro/core/command/trace.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/coordinator/__init__.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/coordinator.py` | Runtime | Phase 5 / 14 / 36 | 重构 | HA-facing runtime façade with polling ballast reduced |
| `custom_components/lipro/core/coordinator/entity_protocol.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/factory.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/lifecycle.py` | Runtime | Phase 36 / 37 | 保留 | update-cycle / MQTT-setup / shutdown lifecycle helper home |
| `custom_components/lipro/core/coordinator/mqtt/__init__.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/mqtt/setup.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/mqtt_lifecycle.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/orchestrator.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/outlet_power.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/__init__.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/command/__init__.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/command/builder.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/command/confirmation.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/command/retry.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/command/sender.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/command_runtime.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/device/__init__.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/device/batch_optimizer.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/device/filter.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/device/refresh_strategy.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/device/snapshot_models.py` | Runtime | Phase 33 | 保留 | typed snapshot container + rejection contract home |
| `custom_components/lipro/core/coordinator/runtime/device_runtime.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/mqtt/__init__.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/mqtt/adapters.py` | Runtime | Phase 33 | 保留 | MQTT callback adapter helper home |
| `custom_components/lipro/core/coordinator/runtime/mqtt/connection.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/mqtt/dedup.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/mqtt/message_handler.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/mqtt/reconnect.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/outlet_power_runtime.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/state/__init__.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/state/index.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/state/reader.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/state/updater.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/state_runtime.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/status/__init__.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/status/executor.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/status/scheduler.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/status/strategy.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/status_runtime.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/tuning/__init__.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/tuning/adjuster.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/tuning/algorithm.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/tuning/metrics.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/tuning_runtime.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime_context.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime_wiring.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/__init__.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/auth_service.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/command_service.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/device_refresh_service.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/mqtt_service.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/polling_service.py` | Runtime | Phase 36 | 保留 | polling/status/outlet/snapshot orchestration helper home |
| `custom_components/lipro/core/coordinator/services/protocol_service.py` | Runtime | Phase 14 | 保留 | protocol-facing runtime service surface |
| `custom_components/lipro/core/coordinator/services/schedule_service.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/state_service.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/telemetry_service.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/types.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/device/__init__.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/device.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/device_factory.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/device_runtime.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/device_snapshots.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/device_views.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/extras.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/extras_features.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/extras_payloads.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/extras_support.py` | Domain | Phase 4 | 重构 | DeviceExtras payload / panel parsing support helper home |
| `custom_components/lipro/core/device/group_status.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/identity.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/identity_index.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/network_info.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/parsing.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/profile.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/state.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/state_accessors.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/state_fields.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/state_getters.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/state_math.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/exceptions.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/mqtt/__init__.py` | Protocol | Phase 2.5 / 7 / 17 | 迁移适配 | package export intentionally minimal; no concrete transport export |
| `custom_components/lipro/core/mqtt/connection_manager.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/credentials.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/message.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/message_processor.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/payload.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/setup_backoff.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/subscription_manager.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/topic_builder.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/topics.py` | Protocol | Phase 2.5 | 重构 | MQTT boundary-backed topic adapter |
| `custom_components/lipro/core/mqtt/transport.py` | Protocol | Phase 2.5 / 15 | 重构 | concrete MQTT transport home; package no-export keeps locality explicit |
| `custom_components/lipro/core/mqtt/transport_runtime.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/ota/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/ota/candidate.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/ota/candidate_support.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/ota/manifest.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/ota/query_support.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/ota/row_selector.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/ota/rows_cache.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/protocol/__init__.py` | Protocol | Phase 2.5 | 保留 | - |
| `custom_components/lipro/core/protocol/boundary/__init__.py` | Protocol | Phase 7.1 | 保留 | - |
| `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py` | Protocol | Phase 7.1 | 保留 | canonical MQTT topic/payload decode authority |
| `custom_components/lipro/core/protocol/boundary/rest_decoder.py` | Protocol | Phase 7.1 | 保留 | - |
| `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py` | Protocol | Phase 33 | 保留 | REST decoder canonicalization helper home |
| `custom_components/lipro/core/protocol/boundary/result.py` | Protocol | Phase 7.1 | 保留 | - |
| `custom_components/lipro/core/protocol/boundary/schema_registry.py` | Protocol | Phase 7.1 | 保留 | - |
| `custom_components/lipro/core/protocol/contracts.py` | Protocol | Phase 2.5 | 保留 | - |
| `custom_components/lipro/core/protocol/diagnostics_context.py` | Protocol | Phase 2.5 | 保留 | - |
| `custom_components/lipro/core/protocol/facade.py` | Protocol | Phase 2 / 35 | 重构 | formal protocol root with localized REST/MQTT child-façade wiring |
| `custom_components/lipro/core/protocol/mqtt_facade.py` | Protocol | Phase 35 | 保留 | MQTT child façade home under the unified protocol root |
| `custom_components/lipro/core/protocol/protocol_facade_rest_methods.py` | Protocol | Phase 2.5 | 保留 | support-only REST child-facing method surface for protocol root |
| `custom_components/lipro/core/protocol/rest_port.py` | Protocol | Phase 35 | 保留 | typed REST child-façade port home |
| `custom_components/lipro/core/protocol/session.py` | Protocol | Phase 2.5 | 保留 | - |
| `custom_components/lipro/core/protocol/telemetry.py` | Protocol | Phase 2.5 | 保留 | - |
| `custom_components/lipro/core/telemetry/__init__.py` | Assurance | Phase 7.3 | 保留 | - |
| `custom_components/lipro/core/telemetry/exporter.py` | Assurance | Phase 7.3 | 保留 | - |
| `custom_components/lipro/core/telemetry/json_payloads.py` | Assurance | Phase 7.3 | 保留 | telemetry helper home for JSON-safe payload builders |
| `custom_components/lipro/core/telemetry/models.py` | Assurance | Phase 7.3 | 保留 | - |
| `custom_components/lipro/core/telemetry/outcomes.py` | Assurance | Phase 7.3 | 保留 | telemetry helper home for outcome semantics |
| `custom_components/lipro/core/telemetry/ports.py` | Assurance | Phase 7.3 | 保留 | - |
| `custom_components/lipro/core/telemetry/sinks.py` | Assurance | Phase 7.3 | 保留 | - |
| `custom_components/lipro/core/utils/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/background_task_manager.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/backoff.py` | Cross-cutting | Phase 56 | 保留 | neutral shared exponential backoff helper home |
| `custom_components/lipro/core/utils/boollike.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/coerce.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/debounce.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/identifiers.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/log_safety.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/property_normalization.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/redaction.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/retry_after.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/vendor_crypto.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/cover.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/diagnostics.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/domain_data.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/entities/__init__.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/entities/base.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/entities/commands.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/entities/descriptors.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/entities/firmware_update.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/entry_auth.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/entry_options.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/fan.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/firmware_manifest.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/flow/__init__.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/flow/credentials.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/flow/login.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/flow/options_flow.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/flow/schemas.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/flow/submission.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/headless/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/headless/boot.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/helpers/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/helpers/platform.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/light.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/runtime_infra.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/runtime_types.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/select.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/select_internal/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/select_internal/gear.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/select_internal/mapped_property.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/sensor.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/services/__init__.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/command.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/contracts.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/device_lookup.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/diagnostics/__init__.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/diagnostics/capability_handlers.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/diagnostics/command_result_handlers.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/diagnostics/feedback_handlers.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/diagnostics/handlers.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/diagnostics/helper_support.py` | Control | Phase 3 | 保留 | diagnostics service mechanics support seam |
| `custom_components/lipro/services/diagnostics/helpers.py` | Control | Phase 3 | 保留 | diagnostics optional-capability helper reusing shared execution auth chain |
| `custom_components/lipro/services/diagnostics/types.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/errors.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/execution.py` | Control | Phase 3 / 5 / 7 | 保留 | formal service execution facade; private auth seam closed |
| `custom_components/lipro/services/maintenance.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/registry.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/schedule.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/share.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/switch.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/system_health.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/update.py` | Domain | Phase 4 | 保留 | - |
| `scripts/__init__.py` | Assurance | Phase 6 / 7 | 保留 | - |
| `scripts/agent_worker.py` | Assurance | Phase 6 / 7 | 保留 | - |
| `scripts/check_architecture_policy.py` | Assurance | Phase 7.2 | 保留 | - |
| `scripts/check_benchmark_baseline.py` | Assurance | Phase 6 / 7 | 保留 | - |
| `scripts/check_file_matrix.py` | Assurance | Phase 6 / 7 / 60 | 保留 | thin governance checker root; sibling modules own inventory/classification/markdown/validation truth families |
| `scripts/check_file_matrix_inventory.py` | Assurance | Phase 60 | 保留 | checker inventory walk and repo-root helper home |
| `scripts/check_file_matrix_markdown.py` | Assurance | Phase 60 | 保留 | FILE_MATRIX render and parse helper home |
| `scripts/check_file_matrix_registry.py` | Assurance | Phase 60 | 保留 | file-governance row registry and classification override home |
| `scripts/check_file_matrix_registry_classifiers.py` | Assurance | Phase 79 | 保留 | registry classifier-rule home |
| `scripts/check_file_matrix_registry_overrides.py` | Assurance | Phase 79 | 保留 | registry override-family home |
| `scripts/check_file_matrix_registry_shared.py` | Assurance | Phase 79 | 保留 | registry shared type + row builder home |
| `scripts/check_file_matrix_validation.py` | Assurance | Phase 60 | 保留 | file-governance drift validators and run_checks home |
| `scripts/check_translations.py` | Assurance | Phase 6 / 7 | 保留 | - |
| `scripts/coverage_diff.py` | Assurance | Phase 6 / 7 | 保留 | - |
| `scripts/export_ai_debug_evidence_pack.py` | Assurance | Phase 8 | 保留 | - |
| `scripts/orchestrator.py` | Assurance | Phase 6 / 7 | 保留 | - |
| `scripts/refactor_tools.py` | Assurance | Phase 6 / 7 | 保留 | - |
| `tests/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/benchmarks/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/benchmarks/test_command_benchmark.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/benchmarks/test_coordinator_performance.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/benchmarks/test_device_refresh_benchmark.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/benchmarks/test_mqtt_benchmark.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/conftest.py` | Assurance | Phase 6 | 保留 | - |
| `tests/conftest_shared.py` | Assurance | Phase 6 | 保留 | - |
| `tests/core/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/anonymous_share/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/anonymous_share/support.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/anonymous_share/test_capabilities.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/anonymous_share/test_manager_recording.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/anonymous_share/test_manager_submission.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/anonymous_share/test_observability.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/anonymous_share/test_sanitize.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/api/__init__.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/conftest.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api.py` | Protocol | Phase 33 | 保留 | topic root for auth/init REST regressions |
| `tests/core/api/test_api_command_service.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_command_surface.py` | Protocol | Phase 33 | 保留 | thin shell after command-surface topicization |
| `tests/core/api/test_api_command_surface_commands.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_command_surface_misc.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_command_surface_rate_limits.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_command_surface_responses.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_device_surface.py` | Protocol | Phase 33 | 保留 | thin shell after device-surface topicization |
| `tests/core/api/test_api_device_surface_connect_status.py` | Protocol | Phase 33 | 保留 | connect-status API regression topic home |
| `tests/core/api/test_api_device_surface_devices.py` | Protocol | Phase 33 | 保留 | device-list API regression topic home |
| `tests/core/api/test_api_device_surface_mesh_groups.py` | Protocol | Phase 33 | 保留 | mesh-group status API regression topic home |
| `tests/core/api/test_api_device_surface_optional_capabilities.py` | Protocol | Phase 33 | 保留 | optional-capability API regression topic home |
| `tests/core/api/test_api_device_surface_outlet_power.py` | Protocol | Phase 33 | 保留 | outlet-power API regression topic home |
| `tests/core/api/test_api_device_surface_status.py` | Protocol | Phase 33 | 保留 | device-status API regression topic home |
| `tests/core/api/test_api_diagnostics_service.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_request_policy.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_schedule_candidate_mutations.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_schedule_candidate_queries.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_schedule_endpoints.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_schedule_service.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_status_endpoints.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_status_service.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_status_service_regressions.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_transport_and_schedule.py` | Protocol | Phase 33 | 保留 | thin shell after transport/schedule topicization |
| `tests/core/api/test_api_transport_and_schedule_close.py` | Protocol | Phase 33 | 保留 | client-close API regression topic home |
| `tests/core/api/test_api_transport_and_schedule_mqtt.py` | Protocol | Phase 33 | 保留 | MQTT-config API regression topic home |
| `tests/core/api/test_api_transport_and_schedule_schedules.py` | Protocol | Phase 33 | 保留 | schedule API regression topic home |
| `tests/core/api/test_api_transport_and_schedule_transport_boundary.py` | Protocol | Phase 33 | 保留 | transport-boundary API regression topic home |
| `tests/core/api/test_api_transport_executor.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_types_smoke.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_auth_recovery_telemetry.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_helper_modules.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_protocol_contract_matrix.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_protocol_replay_rest.py` | Protocol | Phase 7.4 | 保留 | - |
| `tests/core/api/test_request_codec.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_response_safety.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_schedule_codec.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_schedule_endpoint.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/capability/__init__.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/capability/test_registry.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/coordinator/__init__.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/conftest.py` | Runtime | Phase 49 | 保留 | shared coordinator fixture home |
| `tests/core/coordinator/mqtt/__init__.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/runtime/__init__.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/runtime/test_command_runtime.py` | Runtime | Phase 5 / 6 / 74 | 保留 | thin shell after CommandRuntime topicization |
| `tests/core/coordinator/runtime/test_command_runtime_builder_retry.py` | Runtime | Phase 5 / 6 / 74 | 保留 | CommandRuntime builder/retry topic home |
| `tests/core/coordinator/runtime/test_command_runtime_confirmation.py` | Runtime | Phase 5 / 6 / 74 | 保留 | CommandRuntime confirmation topic home |
| `tests/core/coordinator/runtime/test_command_runtime_orchestration.py` | Runtime | Phase 5 / 6 / 74 | 保留 | CommandRuntime orchestration topic home |
| `tests/core/coordinator/runtime/test_command_runtime_sender.py` | Runtime | Phase 5 / 6 / 74 | 保留 | CommandRuntime sender topic home |
| `tests/core/coordinator/runtime/test_command_runtime_support.py` | Runtime | Phase 5 / 6 / 74 | 保留 | shared helper root for CommandRuntime topicized suites |
| `tests/core/coordinator/runtime/test_device_runtime.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/runtime/test_mqtt_runtime.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/runtime/test_runtime_telemetry_methods.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/runtime/test_state_runtime.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/runtime/test_status_runtime.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/runtime/test_tuning_runtime.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/services/__init__.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/services/test_auth_service.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/services/test_command_service.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/services/test_device_refresh_service.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/services/test_mqtt_service.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/services/test_polling_service.py` | Runtime | Phase 36 | 保留 | polling-service regression home |
| `tests/core/coordinator/services/test_protocol_service.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/services/test_state_service.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/services/test_telemetry_service.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/test_entity_protocol.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/test_runtime_polling.py` | Runtime | Phase 49 | 保留 | runtime-polling topic suite |
| `tests/core/coordinator/test_runtime_root.py` | Runtime | Phase 49 | 保留 | runtime-root topic suite |
| `tests/core/coordinator/test_update_flow.py` | Runtime | Phase 49 | 保留 | coordinator update-flow topic suite |
| `tests/core/device/__init__.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_capabilities.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_device.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_device_surface.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_extras_features.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_extras_payloads.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_identity.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_network_extensions.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_network_info.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_parsing.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_state.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_state_extensions.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/mqtt/__init__.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_connection_manager.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_credentials.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_message_processor.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_mqtt_backoff.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_mqtt_message.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_mqtt_payload.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_mqtt_payload_extended.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_mqtt_setup.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_protocol_replay_mqtt.py` | Protocol | Phase 7.4 | 保留 | - |
| `tests/core/mqtt/test_topic_builder.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_topics.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_transport_refactored.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_transport_runtime.py` | Protocol | Phase 2.5 / 6 | 保留 | thin shell after transport-runtime topicization |
| `tests/core/mqtt/test_transport_runtime_connection_loop.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_transport_runtime_ingress.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_transport_runtime_lifecycle.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/mqtt/test_transport_runtime_subscriptions.py` | Protocol | Phase 2.5 / 6 | 保留 | - |
| `tests/core/ota/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/ota/test_firmware_manifest.py` | Domain | Phase 4 / 49 | 保留 | core ota manifest truth home |
| `tests/core/ota/test_ota_candidate.py` | Domain | Phase 4 / 49 | 保留 | core ota candidate helper home |
| `tests/core/ota/test_ota_row_selector.py` | Domain | Phase 4 / 49 | 保留 | core ota row-selector helper home |
| `tests/core/ota/test_ota_rows_cache.py` | Domain | Phase 4 / 49 | 保留 | core ota rows-cache helper home |
| `tests/core/ota/test_ota_utils.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/protocol/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/protocol/test_facade.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/telemetry/__init__.py` | Assurance | Phase 7.3 | 保留 | - |
| `tests/core/telemetry/test_exporter.py` | Assurance | Phase 7.3 | 保留 | - |
| `tests/core/telemetry/test_models.py` | Assurance | Phase 7.3 | 保留 | - |
| `tests/core/telemetry/test_sinks.py` | Assurance | Phase 7.3 | 保留 | - |
| `tests/core/test_anonymous_share_cov_missing.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_anonymous_share_storage.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_auth.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_auth_bootstrap.py` | Cross-cutting | Phase 18 | 保留 | - |
| `tests/core/test_background_task_manager.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_boundary_conditions.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_categories.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_command_confirmation_helpers.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_command_dispatch.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_command_result.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_command_trace.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_control_plane.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_coordinator.py` | Runtime | Phase 5 / 49 | 保留 | service / entity-lifecycle smoke shell |
| `tests/core/test_coordinator_entry.py` | Runtime | Phase 49 | 保留 | entry/runtime public-surface smoke home |
| `tests/core/test_coordinator_integration.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/test_debounce.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_device_list_snapshot.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_device_refresh_filter.py` | Cross-cutting | Phase 7 | 保留 | device-refresh filter-semantics topic home |
| `tests/core/test_device_refresh_parsing.py` | Cross-cutting | Phase 7 | 保留 | device-refresh parsing/normalization topic home |
| `tests/core/test_device_refresh_runtime.py` | Cross-cutting | Phase 7 | 保留 | device-refresh runtime decision topic home |
| `tests/core/test_device_refresh_snapshot.py` | Cross-cutting | Phase 7 | 保留 | device-refresh snapshot-builder topic home |
| `tests/core/test_diagnostics.py` | Control | Phase 3 / 49 | 保留 | shared helper / cross-surface smoke anchor |
| `tests/core/test_diagnostics_config_entry.py` | Control | Phase 49 | 保留 | config-entry diagnostics topic suite |
| `tests/core/test_diagnostics_device.py` | Control | Phase 49 | 保留 | device diagnostics topic suite |
| `tests/core/test_diagnostics_redaction.py` | Control | Phase 49 | 保留 | redaction diagnostics topic suite |
| `tests/core/test_entry_lifecycle_controller.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_entry_root_wiring.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_entry_update_listener.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_exceptions.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_group_status.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_headless_boot.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_helpers.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_identity_index.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_init.py` | Control | Phase 33 | 保留 | topic root for init contract regressions |
| `tests/core/test_init_edge_cases.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_init_runtime_behavior.py` | Control | Phase 33 / 37 | 保留 | shared helper root for topicized init runtime regressions |
| `tests/core/test_init_runtime_bootstrap.py` | Control | Phase 37 | 保留 | bootstrap/infrastructure topic home |
| `tests/core/test_init_runtime_registry_refresh.py` | Control | Phase 37 | 保留 | registry-refresh topic home |
| `tests/core/test_init_runtime_setup_entry.py` | Control | Phase 37 | 保留 | setup-entry topic home |
| `tests/core/test_init_runtime_setup_entry_failures.py` | Control | Phase 37 | 保留 | setup-entry failure topic home |
| `tests/core/test_init_runtime_unload_reload.py` | Control | Phase 37 | 保留 | unload/reload topic home |
| `tests/core/test_init_schema_validation.py` | Control | Phase 33 | 保留 | schema-focused init regression home |
| `tests/core/test_init_service_handlers.py` | Control | Phase 27 / 37 | 保留 | shared helper root for topicized init service-handler regressions |
| `tests/core/test_init_service_handlers_commands.py` | Control | Phase 37 | 保留 | command-dispatch topic home |
| `tests/core/test_init_service_handlers_debug_queries.py` | Control | Phase 37 | 保留 | debug-query topic home |
| `tests/core/test_init_service_handlers_device_resolution.py` | Control | Phase 37 | 保留 | device-resolution topic home |
| `tests/core/test_init_service_handlers_schedules.py` | Control | Phase 37 | 保留 | schedule-validation topic home |
| `tests/core/test_init_service_handlers_sensor_feedback.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_init_service_handlers_share_reports.py` | Control | Phase 37 | 保留 | share-report topic home |
| `tests/core/test_log_safety.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_outlet_power.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_outlet_power_runtime.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_property_normalization.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_report_builder.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_runtime_access.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_runtime_infra.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_runtime_support.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_share_client.py` | Cross-cutting | Phase 7 / 74 | 保留 | thin shell after ShareWorkerClient topicization |
| `tests/core/test_share_client_boundary.py` | Cross-cutting | Phase 7 / 74 | 保留 | ShareWorkerClient external-boundary proof home |
| `tests/core/test_share_client_primitives.py` | Cross-cutting | Phase 7 / 74 | 保留 | ShareWorkerClient primitive/token topic home |
| `tests/core/test_share_client_refresh.py` | Cross-cutting | Phase 7 / 74 | 保留 | ShareWorkerClient token-refresh topic home |
| `tests/core/test_share_client_submit.py` | Cross-cutting | Phase 7 / 74 | 保留 | ShareWorkerClient submit/outcome topic home |
| `tests/core/test_share_client_support.py` | Cross-cutting | Phase 7 / 74 | 保留 | shared helper root for ShareWorkerClient topicized suites |
| `tests/core/test_system_health.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_token_persistence.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_utils_coerce.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_utils_identifiers.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_utils_redaction.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/entities/__init__.py` | Domain | Phase 4 | 保留 | - |
| `tests/entities/test_commands.py` | Domain | Phase 4 | 保留 | - |
| `tests/entities/test_descriptors.py` | Domain | Phase 4 | 保留 | - |
| `tests/flows/__init__.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/flows/support.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/flows/test_config_flow_reauth.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/flows/test_config_flow_reconfigure.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/flows/test_config_flow_user.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/flows/test_flow_credentials.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/flows/test_flow_schemas.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/flows/test_flow_submission.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/flows/test_options_flow.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/flows/test_options_flow_utils.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/harness/__init__.py` | Assurance | Phase 7.4 | 保留 | - |
| `tests/harness/evidence_pack/__init__.py` | Assurance | Phase 8 | 保留 | - |
| `tests/harness/evidence_pack/collector.py` | Assurance | Phase 8 | 保留 | - |
| `tests/harness/evidence_pack/redaction.py` | Assurance | Phase 8 | 保留 | - |
| `tests/harness/evidence_pack/schema.py` | Assurance | Phase 8 | 保留 | - |
| `tests/harness/evidence_pack/sources.py` | Assurance | Phase 8 | 保留 | - |
| `tests/harness/headless_consumer.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/harness/protocol/__init__.py` | Assurance | Phase 7.4 | 保留 | - |
| `tests/harness/protocol/replay_assertions.py` | Assurance | Phase 7.4 | 保留 | - |
| `tests/harness/protocol/replay_driver.py` | Assurance | Phase 7.4 | 保留 | - |
| `tests/harness/protocol/replay_loader.py` | Assurance | Phase 7.4 | 保留 | - |
| `tests/harness/protocol/replay_models.py` | Assurance | Phase 7.4 | 保留 | - |
| `tests/harness/protocol/replay_report.py` | Assurance | Phase 7.4 | 保留 | - |
| `tests/helpers/__init__.py` | Assurance | Phase 6 | 保留 | - |
| `tests/helpers/architecture_policy.py` | Assurance | Phase 7.2 | 保留 | - |
| `tests/helpers/ast_guard_utils.py` | Assurance | Phase 7.2 | 保留 | - |
| `tests/helpers/external_boundary_fixtures.py` | Assurance | Phase 6 | 保留 | - |
| `tests/helpers/repo_root.py` | Assurance | Phase 6 | 保留 | - |
| `tests/helpers/service_call.py` | Assurance | Phase 6 | 保留 | - |
| `tests/integration/__init__.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/integration/test_ai_debug_evidence_pack.py` | Assurance | Phase 8 | 保留 | - |
| `tests/integration/test_headless_consumer_proof.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/integration/test_mqtt_coordinator_integration.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/integration/test_protocol_replay_harness.py` | Assurance | Phase 7.4 | 保留 | - |
| `tests/integration/test_telemetry_exporter_integration.py` | Runtime | Phase 7.3 | 保留 | - |
| `tests/meta/__init__.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/conftest.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/dependency_guard_helpers.py` | Assurance | Phase 6 | 保留 | shared dependency-guard structural-rule helper home |
| `tests/meta/dependency_guards_policy.py` | Assurance | Phase 6 | 保留 | architecture-policy structural-rule guard family |
| `tests/meta/dependency_guards_protocol_contracts.py` | Assurance | Phase 40 / 52 / 57 | 保留 | protocol/schedule dependency-story guard family |
| `tests/meta/dependency_guards_review_ledgers.py` | Assurance | Phase 48 / 49 / 54 / 55 / 56 / 58 / 62 | 保留 | dependency-note / verification / naming topic guard family |
| `tests/meta/dependency_guards_service_runtime.py` | Assurance | Phase 40 / 43 / 50 / 53 / 68 | 保留 | service/runtime dependency-story guard family |
| `tests/meta/governance_contract_helpers.py` | Assurance | Phase 6 / 77 / 79 | 保留 | shared governance route/doc helper home |
| `tests/meta/governance_current_truth.py` | Assurance | Phase 6 / 77 / 79 | 保留 | governance-route contract + shared current/latest archive truth helper |
| `tests/meta/governance_followup_route_closeouts.py` | Assurance | Phase 59 | 保留 | followup-route closeout topic home |
| `tests/meta/governance_followup_route_continuation.py` | Assurance | Phase 59 | 保留 | followup-route continuation topic home |
| `tests/meta/governance_followup_route_current_milestones.py` | Assurance | Phase 77 / 79 | 保留 | governance-route contract + current/latest archive pointer-drift guard |
| `tests/meta/governance_milestone_archives_assets.py` | Assurance | Phase 49 | 保留 | milestone-archive asset existence topic home |
| `tests/meta/governance_milestone_archives_ordering.py` | Assurance | Phase 49 / 77 / 80 | 保留 | milestone-archive snapshot ordering + historical-route topic home |
| `tests/meta/governance_milestone_archives_truth.py` | Assurance | Phase 49 / 77 / 80 | 保留 | milestone-archive authority/pointer truth topic home |
| `tests/meta/governance_phase_history_archive_execution.py` | Assurance | Phase 59 | 保留 | phase-history archive/execution topic home |
| `tests/meta/governance_phase_history_current_milestones.py` | Assurance | Phase 59 | 保留 | phase-history current-milestone topic home |
| `tests/meta/governance_phase_history_mid_closeouts.py` | Assurance | Phase 59 | 保留 | phase-history mid-closeout topic home |
| `tests/meta/governance_phase_history_topology_closeouts.py` | Assurance | Phase 37 | 保留 | closeout/promoted-asset phase-history topology topic home |
| `tests/meta/governance_phase_history_topology_execution.py` | Assurance | Phase 37 | 保留 | archived execution phase-history topology topic home |
| `tests/meta/governance_phase_history_topology_foundations.py` | Assurance | Phase 37 | 保留 | foundation/early-route phase-history topology topic home |
| `tests/meta/governance_promoted_assets.py` | Assurance | Phase 77 | 保留 | shared promoted-phase-asset helper home |
| `tests/meta/public_surface_architecture_policy.py` | Assurance | Phase 59 | 保留 | public-surface architecture/policy topic home |
| `tests/meta/public_surface_phase_notes.py` | Assurance | Phase 59 | 保留 | public-surface phase-note topic home |
| `tests/meta/public_surface_runtime_contracts.py` | Assurance | Phase 59 | 保留 | public-surface runtime-contract topic home |
| `tests/meta/test_blueprints.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_dependency_guards.py` | Assurance | Phase 6 | 保留 | thin shell after dependency-guard topicization |
| `tests/meta/test_evidence_pack_authority.py` | Assurance | Phase 8 | 保留 | - |
| `tests/meta/test_external_boundary_authority.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_external_boundary_fixtures.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_firmware_support_manifest_repo_asset.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_governance_bootstrap_smoke.py` | Assurance | Phase 77 | 保留 | focused bootstrap smoke guard home |
| `tests/meta/test_governance_closeout_guards.py` | Assurance | Phase 27 / 44 / 49 / 77 | 保留 | closeout + promoted-asset manifest smoke anchor |
| `tests/meta/test_governance_followup_route.py` | Assurance | Phase 49 | 保留 | thin shell after followup-route topicization |
| `tests/meta/test_governance_guards.py` | Assurance | Phase 33 / 77 / 79 | 保留 | inventory / policy governance topic root |
| `tests/meta/test_governance_milestone_archives.py` | Assurance | Phase 49 | 保留 | thin shell after milestone-archive topicization |
| `tests/meta/test_governance_phase_history.py` | Assurance | Phase 33 / 37 | 保留 | thin shell after phase-history topicization |
| `tests/meta/test_governance_phase_history_runtime.py` | Assurance | Phase 37 | 保留 | runtime closeout phase-history topic home |
| `tests/meta/test_governance_phase_history_topology.py` | Assurance | Phase 37 | 保留 | thin shell after topology phase-history topicization |
| `tests/meta/test_governance_promoted_phase_assets.py` | Assurance | Phase 49 | 保留 | promoted-asset topic suite |
| `tests/meta/test_governance_release_continuity.py` | Assurance | Phase 79 | 保留 | release continuity/custody topic suite home |
| `tests/meta/test_governance_release_contract.py` | Assurance | Phase 33 / 77 / 79 | 保留 | release/governance workflow anchor suite |
| `tests/meta/test_governance_release_docs.py` | Assurance | Phase 79 | 保留 | release/docs topic suite home |
| `tests/meta/test_governance_route_handoff_smoke.py` | Assurance | Phase 79 | 保留 | route-handoff gsd fast-path smoke guard home |
| `tests/meta/test_install_sh_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_modularization_surfaces.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase31_runtime_budget_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase45_hotspot_budget_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase50_rest_typed_budget_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase61_formal_home_budget_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase62_naming_discoverability_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase68_hotspot_budget_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase69_support_budget_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase70_governance_hotspot_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase71_hotspot_route_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase72_runtime_bootstrap_route_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase73_service_runtime_convergence_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase74_cleanup_closeout_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase75_access_mode_honesty_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_phase75_governance_closeout_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_protocol_replay_assets.py` | Assurance | Phase 7.4 | 保留 | - |
| `tests/meta/test_public_surface_guards.py` | Assurance | Phase 6 | 保留 | thin shell after public-surface topicization |
| `tests/meta/test_service_translation_sync.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_toolchain_truth.py` | Assurance | Phase 16 / 60 | 保留 | thin daily runnable shell for topicized toolchain truth suites |
| `tests/meta/test_translation_tree_sync.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_version_sync.py` | Assurance | Phase 6 / 77 / 79 | 保留 | version/runtime metadata sync guard home |
| `tests/meta/toolchain_truth_checker_paths.py` | Assurance | Phase 60 | 保留 | checker-path and local-develop smoke truth family |
| `tests/meta/toolchain_truth_ci_contract.py` | Assurance | Phase 60 | 保留 | CI lane, pre-push, lint, and pytest contract truth family |
| `tests/meta/toolchain_truth_docs_fast_path.py` | Assurance | Phase 44 / 60 | 保留 | docs fast-path, continuity, and machine-readable governance truth family; toolchain + docs navigation + terminology truth guard home |
| `tests/meta/toolchain_truth_python_stack.py` | Assurance | Phase 60 | 保留 | Python pin, devcontainer, and pre-commit toolchain truth family |
| `tests/meta/toolchain_truth_release_contract.py` | Assurance | Phase 60 | 保留 | release workflow and identity-evidence truth family |
| `tests/meta/toolchain_truth_testing_governance.py` | Assurance | Phase 60 | 保留 | testing-map and derived-governance topology truth family |
| `tests/platforms/__init__.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/select_gear_behavior_cases.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/select_mapped_behavior_cases.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/select_setup_behavior_cases.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_binary_sensor.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_climate.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_cover.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_entity_base.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_entity_behavior.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_fan.py` | Domain | Phase 4 | 保留 | thin shell after fan topic extraction |
| `tests/platforms/test_fan_entity_behavior.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_fan_model_and_commands.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_firmware_update_entity_edges.py` | Domain | Phase 4 / 49 | 保留 | edge-branch shell after topic extraction |
| `tests/platforms/test_light.py` | Domain | Phase 4 | 保留 | thin shell after light topic extraction |
| `tests/platforms/test_light_entity_behavior.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_light_model_and_commands.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_platform_entities_behavior.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_select.py` | Domain | Phase 4 | 保留 | thin shell after select topic extraction |
| `tests/platforms/test_select_behavior.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_select_models.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_sensor.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_switch.py` | Domain | Phase 4 | 保留 | thin shell after switch topic extraction |
| `tests/platforms/test_switch_behavior.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_switch_models.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_update.py` | Domain | Phase 4 / 49 | 保留 | thin setup / happy-path smoke shell |
| `tests/platforms/test_update_background_tasks.py` | Domain | Phase 49 | 保留 | update background-task topic suite |
| `tests/platforms/test_update_certification_policy.py` | Domain | Phase 49 | 保留 | update certification-policy topic suite |
| `tests/platforms/test_update_entity_refresh.py` | Domain | Phase 49 | 保留 | update refresh / row-selection topic suite |
| `tests/platforms/test_update_install_flow.py` | Domain | Phase 49 | 保留 | update install-flow topic suite |
| `tests/platforms/test_update_task_callback.py` | Domain | Phase 4 | 保留 | - |
| `tests/services/__init__.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/services/test_device_lookup.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/services/test_execution.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/services/test_maintenance.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/services/test_service_resilience.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/services/test_services_diagnostics.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/services/test_services_registry.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/services/test_services_schedule.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/services/test_services_share.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/snapshots/__init__.py` | Assurance | Phase 6 | 保留 | - |
| `tests/snapshots/test_api_snapshots.py` | Assurance | Phase 6 | 保留 | - |
| `tests/snapshots/test_coordinator_public_snapshots.py` | Assurance | Phase 6 | 保留 | - |
| `tests/snapshots/test_device_facade_snapshot.py` | Assurance | Phase 6 | 保留 | - |
| `tests/snapshots/test_device_snapshots.py` | Assurance | Phase 6 | 保留 | - |
| `tests/test_refactor_tools.py` | Cross-cutting | Phase 7 | 保留 | - |
