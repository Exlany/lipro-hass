# File Matrix

**Python files total:** 449
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
| `custom_components/lipro/control/models.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/redaction.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/runtime_access.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/service_registry.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/service_router.py` | Control | Phase 3 / 14 / 15 | 保留 | public handler home; upload/report glue kept out-of-line |
| `custom_components/lipro/control/system_health_surface.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/control/telemetry_surface.py` | Control | Phase 7.3 | 保留 | - |
| `custom_components/lipro/coordinator_entry.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/core/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/__init__.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/capabilities.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/collector.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/const.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/manager.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/models.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/report_builder.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/sanitize.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/share_client.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/anonymous_share/storage.py` | Protocol | Phase 2.6 | 保留 | - |
| `custom_components/lipro/core/api/__init__.py` | Protocol | Phase 2.5 / 12 | 重构 | - |
| `custom_components/lipro/core/api/auth_service.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/client.py` | Protocol | Phase 2 / 7 / 12 / 14 | 重构 | internal typing spine only |
| `custom_components/lipro/core/api/client_auth_recovery.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/client_base.py` | Protocol | Phase 2 / 15 | 重构 | internal typing spine only; locality limited to core/api |
| `custom_components/lipro/core/api/client_pacing.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/client_transport.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/command_api_service.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/diagnostics_api_service.py` | Protocol | Phase 2 | 重构 | - |
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
| `custom_components/lipro/core/api/request_policy.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/response_safety.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/schedule_codec.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/schedule_endpoint.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/schedule_service.py` | Protocol | Phase 2 / 14 | 重构 | helper-only schedule support |
| `custom_components/lipro/core/api/status_fallback.py` | Protocol | Phase 14 | 保留 | status fallback kernel home |
| `custom_components/lipro/core/api/status_service.py` | Protocol | Phase 2 / 13 / 14 | 重构 | public status orchestration home |
| `custom_components/lipro/core/api/transport_core.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/transport_retry.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/transport_signing.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/api/types.py` | Protocol | Phase 2 | 重构 | - |
| `custom_components/lipro/core/auth/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
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
| `custom_components/lipro/core/command/trace.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/coordinator/__init__.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/coordinator.py` | Runtime | Phase 5 / 14 | 重构 | HA-facing runtime façade hotspot |
| `custom_components/lipro/core/coordinator/entity_protocol.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/factory.py` | Runtime | Phase 5 | 重构 | - |
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
| `custom_components/lipro/core/coordinator/runtime/device_runtime.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/runtime/mqtt/__init__.py` | Runtime | Phase 5 | 重构 | - |
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
| `custom_components/lipro/core/coordinator/services/__init__.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/auth_service.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/command_service.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/device_refresh_service.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/mqtt_service.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/protocol_service.py` | Runtime | Phase 14 | 保留 | protocol-facing runtime service surface |
| `custom_components/lipro/core/coordinator/services/state_service.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/services/telemetry_service.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/coordinator/types.py` | Runtime | Phase 5 | 重构 | - |
| `custom_components/lipro/core/device/__init__.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/device.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/device_factory.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/device_runtime.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/device_snapshots.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/device_views.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/extra_support.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/extras.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/extras_features.py` | Domain | Phase 4 | 重构 | - |
| `custom_components/lipro/core/device/extras_payloads.py` | Domain | Phase 4 | 重构 | - |
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
| `custom_components/lipro/core/mqtt/__init__.py` | Protocol | Phase 2.5 / 7 | 迁移适配 | LiproMqttClient legacy root name |
| `custom_components/lipro/core/mqtt/client_runtime.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/connection_manager.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/credentials.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/message.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/message_processor.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/mqtt_client.py` | Protocol | Phase 2.5 / 15 | 重构 | direct transport residual; locality limited to core/mqtt + protocol seam |
| `custom_components/lipro/core/mqtt/payload.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/setup_backoff.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/subscription_manager.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/topic_builder.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/mqtt/topics.py` | Protocol | Phase 2.5 | 重构 | - |
| `custom_components/lipro/core/ota/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/ota/candidate.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/ota/manifest.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/ota/row_selector.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/ota/rows_cache.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/protocol/__init__.py` | Protocol | Phase 2.5 | 保留 | - |
| `custom_components/lipro/core/protocol/boundary/__init__.py` | Protocol | Phase 7.1 | 保留 | - |
| `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py` | Protocol | Phase 7.1 | 保留 | - |
| `custom_components/lipro/core/protocol/boundary/rest_decoder.py` | Protocol | Phase 7.1 | 保留 | - |
| `custom_components/lipro/core/protocol/boundary/result.py` | Protocol | Phase 7.1 | 保留 | - |
| `custom_components/lipro/core/protocol/boundary/schema_registry.py` | Protocol | Phase 7.1 | 保留 | - |
| `custom_components/lipro/core/protocol/compat.py` | Protocol | Phase 2.5 | 保留 | - |
| `custom_components/lipro/core/protocol/contracts.py` | Protocol | Phase 2.5 | 保留 | - |
| `custom_components/lipro/core/protocol/diagnostics_context.py` | Protocol | Phase 2.5 | 保留 | - |
| `custom_components/lipro/core/protocol/facade.py` | Protocol | Phase 2.5 | 保留 | - |
| `custom_components/lipro/core/protocol/session.py` | Protocol | Phase 2.5 | 保留 | - |
| `custom_components/lipro/core/protocol/telemetry.py` | Protocol | Phase 2.5 | 保留 | - |
| `custom_components/lipro/core/telemetry/__init__.py` | Assurance | Phase 7.3 | 保留 | - |
| `custom_components/lipro/core/telemetry/exporter.py` | Assurance | Phase 7.3 | 保留 | - |
| `custom_components/lipro/core/telemetry/models.py` | Assurance | Phase 7.3 | 保留 | - |
| `custom_components/lipro/core/telemetry/ports.py` | Assurance | Phase 7.3 | 保留 | - |
| `custom_components/lipro/core/telemetry/sinks.py` | Assurance | Phase 7.3 | 保留 | - |
| `custom_components/lipro/core/utils/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/background_task_manager.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/boollike.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/coerce.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/debounce.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/core/utils/developer_report.py` | Cross-cutting | Phase 7 | 保留 | - |
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
| `custom_components/lipro/helpers/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/helpers/platform.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/light.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/runtime_infra.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/runtime_types.py` | Cross-cutting | Phase 7 | 保留 | - |
| `custom_components/lipro/select.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/sensor.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/services/__init__.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/command.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/contracts.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/device_lookup.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/diagnostics/__init__.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/diagnostics/handlers.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/diagnostics/helpers.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/diagnostics/types.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/errors.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/execution.py` | Control | Phase 3 / 5 / 7 | 保留 | formal service execution facade; private auth seam closed |
| `custom_components/lipro/services/maintenance.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/registrations.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/registry.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/schedule.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/services/share.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/switch.py` | Domain | Phase 4 | 保留 | - |
| `custom_components/lipro/system_health.py` | Control | Phase 3 | 保留 | - |
| `custom_components/lipro/update.py` | Domain | Phase 4 | 保留 | - |
| `scripts/__init__.py` | Assurance | Phase 6 / 7 | 保留 | - |
| `scripts/agent_worker.py` | Assurance | Phase 6 / 7 | 保留 | - |
| `scripts/check_architecture_policy.py` | Assurance | Phase 7.2 | 保留 | - |
| `scripts/check_file_matrix.py` | Assurance | Phase 6 / 7 | 保留 | - |
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
| `tests/core/api/__init__.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_client_transport.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_command_service.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_diagnostics_service.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_schedule_candidate_mutations.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_schedule_candidate_queries.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_schedule_endpoints.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_schedule_service.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_status_endpoints.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_status_service.py` | Protocol | Phase 2 | 保留 | - |
| `tests/core/api/test_api_status_service_regressions.py` | Protocol | Phase 2 | 保留 | - |
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
| `tests/core/coordinator/mqtt/__init__.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/runtime/__init__.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/runtime/test_command_runtime.py` | Runtime | Phase 5 / 6 | 保留 | - |
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
| `tests/core/coordinator/services/test_state_service.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/services/test_telemetry_service.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/coordinator/test_entity_protocol.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/device/__init__.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_capabilities.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_device.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_extras_features.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_identity.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_network_info.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/device/test_state.py` | Domain | Phase 4 | 保留 | - |
| `tests/core/mqtt/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/mqtt/test_client_refactored.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/mqtt/test_connection_manager.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/mqtt/test_message_processor.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/mqtt/test_mqtt.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/mqtt/test_mqtt_backoff.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/mqtt/test_mqtt_message.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/mqtt/test_mqtt_payload.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/mqtt/test_mqtt_setup.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/mqtt/test_protocol_replay_mqtt.py` | Protocol | Phase 7.4 | 保留 | - |
| `tests/core/mqtt/test_topic_builder.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/ota/__init__.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/ota/test_firmware_manifest.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/ota/test_ota_candidate.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/ota/test_ota_row_selector.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/ota/test_ota_rows_cache.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/ota/test_ota_utils.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/telemetry/__init__.py` | Assurance | Phase 7.3 | 保留 | - |
| `tests/core/telemetry/test_exporter.py` | Assurance | Phase 7.3 | 保留 | - |
| `tests/core/telemetry/test_models.py` | Assurance | Phase 7.3 | 保留 | - |
| `tests/core/telemetry/test_sinks.py` | Assurance | Phase 7.3 | 保留 | - |
| `tests/core/test_anonymous_share.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_anonymous_share_cov_missing.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_anonymous_share_storage.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_auth.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_background_task_manager.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_boundary_conditions.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_categories.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_command_confirmation_helpers.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_command_dispatch.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_command_result.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_command_trace.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_control_plane.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_coordinator.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/test_coordinator_integration.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/core/test_debounce.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_developer_report.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_device.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_device_list_snapshot.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_device_refresh.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_diagnostics.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_entry_update_listener.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_exceptions.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_group_status.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_helpers.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_identity_index.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_init.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/core/test_init_edge_cases.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_log_safety.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_outlet_power.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_outlet_power_runtime.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_property_normalization.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_report_builder.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_runtime_support.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_share_client.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_system_health.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_token_persistence.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_utils_coerce.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_utils_identifiers.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/core/test_utils_redaction.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/entities/__init__.py` | Domain | Phase 4 | 保留 | - |
| `tests/entities/test_commands.py` | Domain | Phase 4 | 保留 | - |
| `tests/entities/test_descriptors.py` | Domain | Phase 4 | 保留 | - |
| `tests/flows/__init__.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/flows/test_config_flow.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/flows/test_flow_credentials.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/flows/test_options_flow_utils.py` | Control | Phase 3 / 7 | 保留 | - |
| `tests/harness/__init__.py` | Assurance | Phase 7.4 | 保留 | - |
| `tests/harness/evidence_pack/__init__.py` | Assurance | Phase 8 | 保留 | - |
| `tests/harness/evidence_pack/collector.py` | Assurance | Phase 8 | 保留 | - |
| `tests/harness/evidence_pack/redaction.py` | Assurance | Phase 8 | 保留 | - |
| `tests/harness/evidence_pack/schema.py` | Assurance | Phase 8 | 保留 | - |
| `tests/harness/evidence_pack/sources.py` | Assurance | Phase 8 | 保留 | - |
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
| `tests/integration/test_mqtt_coordinator_integration.py` | Runtime | Phase 5 / 6 | 保留 | - |
| `tests/integration/test_protocol_replay_harness.py` | Assurance | Phase 7.4 | 保留 | - |
| `tests/integration/test_telemetry_exporter_integration.py` | Runtime | Phase 7.3 | 保留 | - |
| `tests/meta/__init__.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_blueprints.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_dependency_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_evidence_pack_authority.py` | Assurance | Phase 8 | 保留 | - |
| `tests/meta/test_external_boundary_authority.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_external_boundary_fixtures.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_firmware_support_manifest_repo_asset.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_governance_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_install_sh_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_modularization_surfaces.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_protocol_replay_assets.py` | Assurance | Phase 7.4 | 保留 | - |
| `tests/meta/test_public_surface_guards.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_service_translation_sync.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_toolchain_truth.py` | Assurance | Phase 16 | 保留 | - |
| `tests/meta/test_translation_tree_sync.py` | Assurance | Phase 6 | 保留 | - |
| `tests/meta/test_version_sync.py` | Assurance | Phase 6 | 保留 | - |
| `tests/platforms/__init__.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_binary_sensor.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_climate.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_cover.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_entity_base.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_entity_behavior.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_fan.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_firmware_update_entity_edges.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_light.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_platform_entities_behavior.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_select.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_sensor.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_switch.py` | Domain | Phase 4 | 保留 | - |
| `tests/platforms/test_update.py` | Domain | Phase 4 | 保留 | - |
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
| `tests/test_coordinator_public.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/test_coordinator_runtime.py` | Cross-cutting | Phase 7 | 保留 | - |
| `tests/test_refactor_tools.py` | Cross-cutting | Phase 7 | 保留 | - |
