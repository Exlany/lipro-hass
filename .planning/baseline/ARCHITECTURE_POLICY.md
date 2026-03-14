# Architecture Policy

**Purpose:** 把 north-star 与 baseline 的结构约束翻译成单一、可执行、可扩展的 architecture enforcement baseline。
**Status:** Formal baseline asset (`ENF-01` / `ENF-02` policy truth source)
**Updated:** 2026-03-13

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
| `ENF-IMP-CONTROL-NO-BYPASS` | Plane | `imports_disjoint` | `custom_components/lipro/runtime_infra.py`<br>`custom_components/lipro/diagnostics.py`<br>`custom_components/lipro/system_health.py`<br>`custom_components/lipro/services/registry.py`<br>`custom_components/lipro/services/registrations.py`<br>`custom_components/lipro/control/entry_lifecycle_controller.py`<br>`custom_components/lipro/control/runtime_access.py`<br>`custom_components/lipro/control/service_registry.py`<br>`custom_components/lipro/control/service_router.py`<br>`custom_components/lipro/control/diagnostics_surface.py`<br>`custom_components/lipro/control/system_health_surface.py` | `custom_components.lipro.core.api`<br>`custom_components.lipro.core.mqtt`<br>`custom_components.lipro.core.protocol.boundary`<br>`custom_components.lipro.core.coordinator` | `-` | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md §2.2`<br>`.planning/baseline/DEPENDENCY_MATRIX.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_dependency_guards.py` | none |
| `ENF-IMP-BOUNDARY-LOCALITY` | Boundary-local | `imports_disjoint` | `custom_components/lipro/**/*.py` | `custom_components.lipro.core.protocol.boundary` | `custom_components/lipro/core/protocol/**/*.py`<br>`custom_components/lipro/core/api/**/*.py`<br>`custom_components/lipro/core/mqtt/**/*.py` | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md §3.1`<br>`.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/baseline/AUTHORITY_MATRIX.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_dependency_guards.py` | `07.4` 若新增 assurance-only boundary consumer，必须先在此登记 allowed exception |
| `ENF-GOV-DEPENDENCY-POLICY-REF` | Authority | `file_contains` | `.planning/baseline/DEPENDENCY_MATRIX.md` | `-` | `.planning/baseline/ARCHITECTURE_POLICY.md` | `.planning/baseline/AUTHORITY_MATRIX.md` | `scripts/check_architecture_policy.py` | none |
| `ENF-GOV-PUBLIC-SURFACE-POLICY-REF` | Authority | `file_contains` | `.planning/baseline/PUBLIC_SURFACES.md` | `-` | `.planning/baseline/ARCHITECTURE_POLICY.md` | `.planning/baseline/AUTHORITY_MATRIX.md` | `scripts/check_architecture_policy.py` | none |
| `ENF-GOV-AUTHORITY-POLICY-REF` | Authority | `file_contains` | `.planning/baseline/AUTHORITY_MATRIX.md` | `-` | `.planning/baseline/ARCHITECTURE_POLICY.md` | `.planning/baseline/AUTHORITY_MATRIX.md` | `scripts/check_architecture_policy.py` | none |
| `ENF-GOV-VERIFICATION-POLICY-REF` | Authority | `file_contains` | `.planning/baseline/VERIFICATION_MATRIX.md` | `-` | `.planning/baseline/ARCHITECTURE_POLICY.md` | `.planning/baseline/AUTHORITY_MATRIX.md` | `scripts/check_architecture_policy.py` | none |
| `ENF-GOV-CI-FAIL-FAST` | Authority | `ordered_tokens` | `.github/workflows/ci.yml` | `-` | `Check architecture policy`<br>`Check file matrix and active authority docs`<br>`Run governance and architecture guards` | `.planning/ROADMAP.md`<br>`.planning/phases/07.2-architecture-enforcement/07.2-VALIDATION.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_governance_guards.py` | future governance jobs must keep architecture gate before functional suites |

## Targeted Regression Bans

| Rule ID | Taxonomy | Mode | Governed File | Required Signals | Forbidden Signals | Source Refs | Enforcement |
|--------|----------|------|---------------|------------------|-------------------|-------------|-------------|
| `ENF-SURFACE-COORDINATOR-ENTRY` | Root | `all_exact` | `custom_components/lipro/coordinator_entry.py` | `Coordinator` | `-` | `.planning/baseline/PUBLIC_SURFACES.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-SURFACE-API-EXPORTS` | Surface | `all_contains_disjoint` | `custom_components/lipro/core/api/__init__.py` | `LiproClient`<br>`LiproRestFacade` | `client_auth_recovery`<br>`client_transport`<br>`request_codec`<br>`request_policy`<br>`response_safety`<br>`transport_core`<br>`transport_retry`<br>`transport_signing`<br>`_COMMAND_PACING_CACHE_MAX_SIZE`<br>`_mask_sensitive_data`<br>`_normalize_response_code` | `.planning/baseline/PUBLIC_SURFACES.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-SURFACE-PROTOCOL-EXPORTS` | Surface | `all_contains_disjoint` | `custom_components/lipro/core/protocol/__init__.py` | `LiproProtocolFacade`<br>`LiproMqttFacade` | `BoundaryDecodeResult`<br>`BoundaryDecoderKey`<br>`BoundaryDecoderRegistry`<br>`build_protocol_boundary_registry`<br>`decode_mqtt_config_payload`<br>`decode_mqtt_properties_payload` | `.planning/baseline/PUBLIC_SURFACES.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-BACKDOOR-COORDINATOR-PROPERTIES` | Backdoor | `property_contains_disjoint` | `custom_components/lipro/core/coordinator/coordinator.py::Coordinator` | `devices` | `command_runtime`<br>`device_runtime`<br>`mqtt_runtime`<br>`state_runtime`<br>`status_runtime`<br>`tuning_runtime`<br>`background_task_manager`<br>`mqtt_client`<br>`biz_id` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-BACKDOOR-SERVICE-AUTH` | Backdoor | `file_contains_disjoint` | `custom_components/lipro/services/execution.py` | `auth_service` | `getattr(coordinator, "_async_ensure_authenticated"`<br>`getattr(coordinator, "_trigger_reauth"` | `.planning/reviews/RESIDUAL_LEDGER.md`<br>`.planning/baseline/PUBLIC_SURFACES.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-COMPAT-ROOT-NO-LEGACY-CLIENT` | Compat | `top_level_bindings_disjoint` | `custom_components/lipro/__init__.py` | `LiproProtocolFacade`<br>`LiproAuthManager` | `LiproClient`<br>`LiproMqttClient` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-COMPAT-CONFIG-FLOW-NO-LEGACY-CLIENT` | Compat | `top_level_bindings_disjoint` | `custom_components/lipro/config_flow.py` | `LiproProtocolFacade` | `LiproClient`<br>`LiproMqttClient` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-COMPAT-CORE-PACKAGE-NO-LEGACY-CLIENTS` | Compat | `top_level_bindings_disjoint` | `custom_components/lipro/core/__init__.py` | `LiproProtocolFacade`<br>`LiproMqttFacade`<br>`AuthSessionSnapshot` | `LiproClient`<br>`LiproMqttClient`<br>`Coordinator` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |
| `ENF-COMPAT-MQTT-PACKAGE-NO-LEGACY-CLIENT` | Compat | `top_level_bindings_disjoint` | `custom_components/lipro/core/mqtt/__init__.py` | `decrypt_mqtt_credential` | `LiproMqttClient` | `.planning/baseline/PUBLIC_SURFACES.md`<br>`.planning/reviews/RESIDUAL_LEDGER.md` | `scripts/check_architecture_policy.py`<br>`tests/meta/test_public_surface_guards.py` |

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

---
*Used by: Phase 7.2 enforcement execution, local-fast architecture checks, and CI fail-fast gates*
