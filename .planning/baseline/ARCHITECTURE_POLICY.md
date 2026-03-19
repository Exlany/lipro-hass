# Architecture Policy

**Purpose:** 把 north-star 与 baseline 的结构约束翻译成单一、可执行、可扩展的 architecture enforcement baseline。
**Status:** Formal baseline asset (`ENF-01` / `ENF-02` policy truth source)
**Updated:** 2026-03-16 (Phase 18 nucleus locality aligned)

## Formal Role

- 本文件是 `Phase 7.2` 起 architecture enforcement 的正式 baseline 真源。
- `scripts/check_architecture_policy.py`、`tests/meta/*guards*.py` 与 CI governance gate 只能消费本文件与上游 baseline，不得各自维护第二套规则真相。
- 本文件只定义 **规则真源**；helper / script / tests 只是执行与仲裁层。
- 结构性规则与 targeted regression bans 必须分开：前者表达长期架构边界，后者只阻断已知回归洞位，不得偷偷扩成新架构。

## Taxonomy Overview

| Taxonomy | Scope | Primary source docs | Execution home | Future hook |
|----------|-------|---------------------|----------------|-------------|
| Plane | 五平面依赖方向 | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `TARGET_TOPOLOGY.md`, `DEPENDENCY_MATRIX.md` | architecture policy script + dependency guards | 07.3 observer-only surfaces |
| Root | 单一正式 protocol/runtime root | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `PUBLIC_SURFACES.md` | public-surface guards + governance CI | 07.3 / 07.4 component registration |
| Surface | canonical / transitional / forbidden public surfaces | `PUBLIC_SURFACES.md` | public-surface guards | compat demotion / delete gates |
| Boundary-local | `core/protocol/boundary/*` 只在 protocol/assurance 内合法消费 | `DEPENDENCY_MATRIX.md`, `PUBLIC_SURFACES.md`, `AUTHORITY_MATRIX.md` | import guards + replay/authority handoff | 07.4 assurance-only boundary consumers |
| Raw-payload | raw vendor payload 不得穿透 protocol boundary | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `VERIFICATION_MATRIX.md` | contract guards + replay proof | 07.4 deterministic replay assertions |
| Compat | compat 只能显式、可计数、可删除 | `PUBLIC_SURFACES.md`, `RESIDUAL_LEDGER.md` | governance + public-surface guards | delete gates / cleanup phases |
| Authority | truth-source 顺序与 sync direction | `AUTHORITY_MATRIX.md`, `VERIFICATION_MATRIX.md` | policy script + governance guards | future baseline families |
| Backdoor | runtime/private seam/bypass surface | `PUBLIC_SURFACES.md`, `RESIDUAL_LEDGER.md` | targeted regression bans | future runtime/control seams |

## Structural Rules

| Rule ID | Taxonomy | Mode | Governed Paths / File | Forbidden Signals | Allowed / Required Signals | Source Refs | Enforcement | Future Hook |
|--------|----------|------|------------------------|-------------------|----------------------------|-------------|-------------|-------------|
| `ENF-IMP-ENTITY-PROTOCOL-INTERNALS` | Plane | `imports_disjoint` | `custom_components/lipro/binary_sensor.py`<br>`custom_components/lipro/climate.py`<br>`custom_components/lipro/cover.py`<br>`custom_components/lipro/fan.py`<br>`custom_components/lipro/light.py`<br>`custom_components/lipro/select.py`<br>`custom_components/lipro/sensor.py`<br>`custom_components/lipro/switch.py`<br>`custom_components/lipro/update.py`<br>`custom_components/lipro/helpers/platform.py`<br>`custom_components/lipro/entities/*.py` | `custom_components.lipro.core.api`<br>`custom_components.lipro.core.mqtt`<br>`custom_components.lipro.core.protocol.boundary` | `-` | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md §2.2`<br>`.planning/baseline/DEPENDENCY_MATRIX.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_dependency_guards.py` | none |
| `ENF-IMP-CONTROL-NO-BYPASS` | Plane | `imports_disjoint` | `custom_components/lipro/runtime_infra.py`<br>`custom_components/lipro/diagnostics.py`<br>`custom_components/lipro/system_health.py`<br>`custom_components/lipro/services/registry.py`<br>`custom_components/lipro/services/registrations.py`<br>`custom_components/lipro/control/entry_lifecycle_controller.py`<br>`custom_components/lipro/control/runtime_access.py`<br>`custom_components/lipro/control/service_registry.py`<br>`custom_components/lipro/control/service_router.py`<br>`custom_components/lipro/control/developer_router_support.py`<br>`custom_components/lipro/control/diagnostics_surface.py`<br>`custom_components/lipro/control/system_health_surface.py` | `custom_components.lipro.core.api`<br>`custom_components.lipro.core.mqtt`<br>`custom_components.lipro.core.protocol.boundary`<br>`custom_components.lipro.core.coordinator` | `-` | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md §2.2`<br>`.planning/baseline/DEPENDENCY_MATRIX.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_dependency_guards.py` | none |
| `ENF-IMP-NUCLEUS-NO-HOMEASSISTANT-IMPORT` | Plane | `imports_disjoint` | `custom_components/lipro/core/auth/**/*.py`<br>`custom_components/lipro/core/capability/**/*.py`<br>`custom_components/lipro/core/device/**/*.py` | `homeassistant` | `-` | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md §2.2`<br>`.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/baseline/DEPENDENCY_MATRIX.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_dependency_guards.py` | none |
| `ENF-IMP-NUCLEUS-NO-PLATFORM-BACKFLOW` | Plane | `imports_disjoint` | `custom_components/lipro/core/auth/**/*.py`<br>`custom_components/lipro/core/capability/**/*.py`<br>`custom_components/lipro/core/device/**/*.py` | `custom_components.lipro.helpers.platform` | `-` | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md §2.2`<br>`.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/baseline/DEPENDENCY_MATRIX.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_dependency_guards.py` | none |
| `ENF-IMP-HEADLESS-PROOF-LOCALITY` | Plane | `imports_disjoint` | `custom_components/lipro/headless/**/*.py` | `homeassistant`<br>`custom_components.lipro.control`<br>`custom_components.lipro.coordinator_entry`<br>`custom_components.lipro.helpers.platform` | `-` | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md §2.2`<br>`.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/baseline/DEPENDENCY_MATRIX.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_dependency_guards.py` | none |
| `ENF-IMP-PLATFORM-SHELL-NO-CONTROL-LOCATOR` | Plane | `imports_disjoint` | `custom_components/lipro/cover.py`<br>`custom_components/lipro/fan.py`<br>`custom_components/lipro/light.py`<br>`custom_components/lipro/select.py`<br>`custom_components/lipro/switch.py`<br>`custom_components/lipro/update.py`<br>`custom_components/lipro/helpers/platform.py` | `custom_components.lipro.control.runtime_access` | `-` | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md §2.2`<br>`.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/baseline/DEPENDENCY_MATRIX.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_dependency_guards.py` | none |
| `ENF-IMP-BOUNDARY-LOCALITY` | Boundary-local | `imports_disjoint` | `custom_components/lipro/**/*.py` | `custom_components.lipro.core.protocol.boundary` | `custom_components/lipro/core/protocol/**/*.py`<br>`custom_components/lipro/core/api/**/*.py`<br>`custom_components/lipro/core/mqtt/**/*.py` | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md §3.1`<br>`.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/baseline/AUTHORITY_MATRIX.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_dependency_guards.py` | `07.4` 若新增 assurance-only boundary consumer，必须先在此登记 allowed exception |
| `ENF-GOV-DEPENDENCY-POLICY-REF` | Authority | `file_contains` | `.planning/baseline/DEPENDENCY_MATRIX.md` | `-` | `.planning/baseline/ARCHITECTURE_POLICY.md` | `.planning/baseline/AUTHORITY_MATRIX.md` | `scripts/check_architecture_policy.py` | none |
| `ENF-GOV-PUBLIC-SURFACE-POLICY-REF` | Authority | `file_contains` | `.planning/baseline/PUBLIC_SURFACES.md` | `-` | `.planning/baseline/ARCHITECTURE_POLICY.md` | `.planning/baseline/AUTHORITY_MATRIX.md` | `scripts/check_architecture_policy.py` | none |
| `ENF-GOV-AUTHORITY-POLICY-REF` | Authority | `file_contains` | `.planning/baseline/AUTHORITY_MATRIX.md` | `-` | `.planning/baseline/ARCHITECTURE_POLICY.md` | `.planning/baseline/AUTHORITY_MATRIX.md` | `scripts/check_architecture_policy.py` | none |
| `ENF-GOV-VERIFICATION-POLICY-REF` | Authority | `file_contains` | `.planning/baseline/VERIFICATION_MATRIX.md` | `-` | `.planning/baseline/ARCHITECTURE_POLICY.md` | `.planning/baseline/AUTHORITY_MATRIX.md` | `scripts/check_architecture_policy.py` | none |
| `ENF-GOV-CI-FAIL-FAST` | Authority | `ordered_tokens` | `.github/workflows/ci.yml` | `-` | `Check architecture policy`<br>`Check file matrix and active authority docs`<br>`Run governance and architecture guards` | `.planning/ROADMAP.md`<br>`.planning/phases/07.2-architecture-enforcement/07.2-VALIDATION.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_governance_guards.py` | future governance jobs must keep architecture gate before functional suites |
| `ENF-GOV-RELEASE-CI-REUSE` | Authority | `file_contains` | `.github/workflows/release.yml` | `-` | `./.github/workflows/ci.yml`<br>`needs: validate`<br>`Verify tag matches project version` | `.planning/ROADMAP.md`<br>`.planning/baseline/VERIFICATION_MATRIX.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_governance_guards.py` | release pipeline must keep CI reuse + version gate |
| `ENF-IMP-API-LEGACY-SPINE-LOCALITY` | Compat | `imports_disjoint` | `custom_components/lipro/**/*.py` | `custom_components.lipro.core.api.session_state`<br>`custom_components.lipro.core.api.client_pacing`<br>`custom_components.lipro.core.api.auth_recovery`<br>`custom_components.lipro.core.api.transport_executor` | `custom_components/lipro/core/api/**/*.py` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_dependency_guards.py` | Phase 2 delete gates may shrink allowed locality, but must not expand consumers |
| `ENF-IMP-MQTT-TRANSPORT-LOCALITY` | Compat | `imports_disjoint` | `custom_components/lipro/**/*.py` | `custom_components.lipro.core.mqtt.transport` | `custom_components/lipro/core/protocol/**/*.py`<br>`custom_components/lipro/core/mqtt/**/*.py` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_dependency_guards.py` | concrete transport must stay localized and non-public |
| `ENF-IMP-ASSURANCE-NO-PRODUCTION-BACKFLOW` | Authority | `imports_disjoint` | `custom_components/lipro/**/*.py` | `tests.harness.protocol`<br>`tests.harness.evidence_pack`<br>`scripts.export_ai_debug_evidence_pack` | `-` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/baseline/VERIFICATION_MATRIX.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_dependency_guards.py` | assurance-only artifacts stay pull-only and must not become production truth |

## Targeted Regression Bans

| Rule ID | Taxonomy | Mode | Governed File | Required Signals | Forbidden Signals | Source Refs | Enforcement |
|--------|----------|------|---------------|------------------|-------------------|-------------|-------------|
| `ENF-SURFACE-COORDINATOR-ENTRY` | Root | `all_exact` | `custom_components/lipro/coordinator_entry.py` | `Coordinator` | `-` | `.planning/baseline/PUBLIC_SURFACES.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-SURFACE-API-EXPORTS` | Surface | `all_contains_disjoint` | `custom_components/lipro/core/api/__init__.py` | `LiproRestFacade` | `auth_recovery`<br>`endpoint_surface`<br>`session_state`<br>`request_codec`<br>`request_policy`<br>`response_safety`<br>`transport_executor`<br>`transport_core`<br>`transport_retry`<br>`transport_signing`<br>`_COMMAND_PACING_CACHE_MAX_SIZE`<br>`_mask_sensitive_data`<br>`_normalize_response_code` | `.planning/baseline/PUBLIC_SURFACES.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-SURFACE-PROTOCOL-EXPORTS` | Surface | `all_contains_disjoint` | `custom_components/lipro/core/protocol/__init__.py` | `LiproProtocolFacade`<br>`LiproMqttFacade` | `BoundaryDecodeResult`<br>`BoundaryDecoderKey`<br>`BoundaryDecoderRegistry`<br>`build_protocol_boundary_registry`<br>`decode_mqtt_config_payload`<br>`decode_mqtt_properties_payload` | `.planning/baseline/PUBLIC_SURFACES.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-BACKDOOR-COORDINATOR-PROPERTIES` | Backdoor | `property_contains_disjoint` | `custom_components/lipro/core/coordinator/coordinator.py::Coordinator` | `devices` | `command_runtime`<br>`device_runtime`<br>`mqtt_runtime`<br>`state_runtime`<br>`status_runtime`<br>`tuning_runtime`<br>`background_task_manager`<br>`mqtt_transport`<br>`biz_id` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-BACKDOOR-SERVICE-AUTH` | Backdoor | `file_contains_disjoint` | `custom_components/lipro/services/execution.py` | `auth_service` | `getattr(coordinator, "_async_ensure_authenticated"`<br>`getattr(coordinator, "_trigger_reauth"` | `.planning/reviews/RESIDUAL_LEDGER.md`<br>`.planning/baseline/PUBLIC_SURFACES.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-COMPAT-ROOT-NO-LEGACY-CLIENT` | Compat | `top_level_bindings_disjoint` | `custom_components/lipro/__init__.py` | `LiproProtocolFacade`<br>`LiproAuthManager` | `LiproClient`<br>`LiproMqttClient`<br>`MqttTransport` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-COMPAT-CONFIG-FLOW-NO-LEGACY-CLIENT` | Compat | `top_level_bindings_disjoint` | `custom_components/lipro/config_flow.py` | `LiproProtocolFacade` | `LiproClient`<br>`LiproMqttClient`<br>`MqttTransport` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-COMPAT-CORE-PACKAGE-NO-LEGACY-CLIENTS` | Compat | `top_level_bindings_disjoint` | `custom_components/lipro/core/__init__.py` | `LiproProtocolFacade`<br>`LiproMqttFacade`<br>`AuthSessionSnapshot` | `LiproClient`<br>`LiproMqttClient`<br>`MqttTransport`<br>`Coordinator` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-COMPAT-MQTT-PACKAGE-NO-LEGACY-CLIENT` | Compat | `top_level_bindings_disjoint` | `custom_components/lipro/core/mqtt/__init__.py` | `decrypt_mqtt_credential` | `LiproMqttClient`<br>`MqttTransport` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-ADAPTER-CONFIG-FLOW-USES-AUTH-PROJECTION` | Adapter | `file_contains_disjoint` | `custom_components/lipro/config_flow.py` | `ConfigEntryLoginProjection`<br>`build_headless_boot_context` | `LoginResult`<br>`auth_manager.login(` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-ADAPTER-ENTRY-AUTH-USES-BOOTSTRAP` | Adapter | `file_contains_disjoint` | `custom_components/lipro/entry_auth.py` | `_build_entry_auth_seed`<br>`build_headless_boot_context` | `auth_manager.set_tokens(`<br>`auth_manager.set_credentials(` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-HOSTPROJ-CATEGORIES-NO-HA-PLATFORMS` | Projection | `file_contains_disjoint` | `custom_components/lipro/const/categories.py` | `DeviceCategory`<br>`get_device_category` | `CATEGORY_TO_PLATFORMS`<br>`get_platforms_for_category` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-HOSTPROJ-CAPABILITY-NO-PLATFORM-FIELD` | Projection | `file_contains_disjoint` | `custom_components/lipro/core/capability/models.py` | `CapabilitySnapshot`<br>`supports_color_temp` | `platforms`<br>`supports_platform` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-HOSTPROJ-DEVICE-VIEWS-NO-PLATFORM-PROJECTION` | Projection | `file_contains_disjoint` | `custom_components/lipro/core/device/device_views.py` | `category`<br>`unique_id` | `def platforms` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-PROOF-HEADLESS-PACKAGE-NO-EXPORTS` | Proof | `top_level_bindings_disjoint` | `custom_components/lipro/headless/__init__.py` | `__all__` | `HeadlessBootContext`<br>`build_headless_boot_context`<br>`build_password_boot_seed` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-PROOF-HEADLESS-BOOT-NO-SECOND-ROOT-BACKFLOW` | Proof | `file_contains_disjoint` | `custom_components/lipro/headless/boot.py` | `HeadlessBootContext`<br>`build_headless_boot_context` | `homeassistant`<br>`Coordinator`<br>`runtime_access`<br>`ConfigEntryLoginProjection`<br>`persist_entry_tokens_if_changed`<br>`helpers.platform` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |

## Extension Hooks

- `07.3 telemetry exporter` 只能作为 `observer-only surface` 接入：消费正式 telemetry truth，不得获得 runtime 编排权。
- `07.4 replay harness` 只能作为 `assurance-only boundary consumer` 接入：复用正式 façade / decoder path，不得复制第二套 protocol implementation。
- 若未来新增例外、allowlist 或 extra root，必须先回写本文件与相关 baseline docs，再改 helper / script / tests。

## Review Checklist

- [ ] 新规则是否来自 north-star / baseline，而不是临时实现事实
- [ ] 结构性规则与 targeted regression bans 是否已分开
- [ ] helper / script / tests 是否消费同一 rule id 与 source refs
- [ ] 例外是否带 residual gate / future hook
- [ ] 是否避免把 compat、observer、replay tool 误提升为正式 root

## Phase 15 Policy Follow-Through

- `ENF-IMP-API-LEGACY-SPINE-LOCALITY` 在 Phase 15 只负责把 `core/api` 残余 helper spine 局部化，不允许向 control/runtime/domain 扩散。
- `ENF-IMP-MQTT-TRANSPORT-LOCALITY` 在 Phase 15 只负责把 direct transport 限定在 `core/mqtt` + protocol seam，不恢复 concrete transport public semantics。

## Phase 17 Policy Follow-Through

- `ENF-IMP-API-LEGACY-SPINE-LOCALITY` 现在锁定的是 `session_state.py`、`client_pacing.py`、`auth_recovery.py`、`transport_executor.py` 这些 local helper/session homes；legacy mixin classes 已全部退场。
- `ENF-IMP-MQTT-TRANSPORT-LOCALITY` 现在锁定 `MqttTransport` concrete transport 的 locality；targeted bans 同时禁止 `LiproMqttClient` 与 `MqttTransport` 从 root/core package 回流成导出面。

## Phase 19 Policy Follow-Through

- `ENF-IMP-HEADLESS-PROOF-LOCALITY` 锁定 `custom_components/lipro/headless/boot.py` 只能停留在 host-neutral auth/protocol proof seam，不得长出 `homeassistant`、control、runtime 或 platform backflow。
- `ENF-IMP-PLATFORM-SHELL-NO-CONTROL-LOCATOR` 与 `helpers/platform.add_entry_entities()` 一起锁定平台 `async_setup_entry()` 只允许保留 thin headless setup shell。
- `ENF-PROOF-HEADLESS-PACKAGE-NO-EXPORTS` 与 `ENF-PROOF-HEADLESS-BOOT-NO-SECOND-ROOT-BACKFLOW` 共同阻断 headless boot helper 被 package export、authority source 或 second-root 叙事重新合法化。

---
*Used by: Phase 7.2 enforcement execution, local-fast architecture checks, and CI fail-fast gates*
