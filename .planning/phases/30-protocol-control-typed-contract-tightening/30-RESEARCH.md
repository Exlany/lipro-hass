# Phase 30 Research

**Status:** `research complete`
**Date:** `2026-03-17`
**Requirement:** `TYP-06`, `ERR-04`

## Executive Judgment

`Phase 30` 最优是 `3 plans / 3 waves`，顺序应为：

1. `REST response/result spine tightening`
2. `protocol boundary/root contract tightening`
3. `control lifecycle exception arbitration`

原因是本范围内 `Any` 粗量化约为 `core/api=176`、`core/protocol=84`、`control=12`；`core/api` 是传播源，`core/protocol` 是 formal root，`control` 则是小而关键的 exception choke point。

## Current Typed / Exception Snapshot

### 1. REST typed spine 是第一优先

- `auth_recovery.py`、`transport_executor.py`、`endpoints/payloads.py`、`request_codec.py` 是 `Any` 与宽口 result-code/payload unwrap 的根源。
- `client.py` 本身更像签名回写和桥接 home，不应在本 phase 继续做结构拆根；那是 `Phase 29` 的事。

### 2. protocol boundary/root 是第二优先

- `protocol/contracts.py`、`boundary/rest_decoder.py`、`boundary/mqtt_decoder.py`、`protocol/facade.py`、`protocol/session.py` 同时携带 canonical contract、decoder 输出、唯一 `type: ignore` 与多处 broad-catch。
- 这里的 tightening 必须优先用现有 `TypedDict` / `JsonValue` / canonical contracts，而不是造新 root。

### 3. control lifecycle 是第三优先

- `entry_lifecycle_controller.py` 的 `ConfigEntry[Any]` 与 setup/unload catch-all 虽然数量不多，但直接位于 control root，价值远高于一些 diagnostics payload Any。
- `system_health_surface` 可作为必要时最小同步，不应扩成 diagnostics/noise cleanup phase。

## Recommended Plan Structure

### Plan 30-01 — REST response/result spine tightening

**File focus:**
- `custom_components/lipro/core/api/auth_recovery.py`
- `custom_components/lipro/core/api/transport_executor.py`
- `custom_components/lipro/core/api/endpoints/payloads.py`
- `custom_components/lipro/core/api/request_codec.py`
- `custom_components/lipro/core/api/client.py`
- `tests/core/api/test_auth_recovery_telemetry.py`
- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/core/api/test_api_status_service.py`
- `tests/core/api/test_api_schedule_service.py`
- `tests/core/api/test_api_diagnostics_service.py`

### Plan 30-02 — protocol boundary/root contract tightening

**File focus:**
- `custom_components/lipro/core/protocol/contracts.py`
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/protocol/session.py`
- `tests/core/api/test_protocol_replay_rest.py`
- `tests/core/mqtt/test_protocol_replay_mqtt.py`
- `tests/integration/test_protocol_replay_harness.py`
- `tests/core/coordinator/test_entity_protocol.py`

### Plan 30-03 — control lifecycle exception arbitration and guard freeze

**File focus:**
- `custom_components/lipro/control/entry_lifecycle_controller.py`
- `custom_components/lipro/control/system_health_surface.py`
- `tests/core/test_init.py`
- `tests/core/test_init_edge_cases.py`
- `tests/core/test_control_plane.py`
- `tests/core/test_system_health.py`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_public_surface_guards.py`

## Validation Architecture

- `uv run pytest -q tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_status_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_diagnostics_service.py`
- `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/core/coordinator/test_entity_protocol.py`
- `uv run pytest -q tests/core/test_init.py tests/core/test_init_edge_cases.py tests/core/test_control_plane.py tests/core/test_system_health.py`
- `uv run ruff check custom_components/lipro/core/api custom_components/lipro/core/protocol custom_components/lipro/control tests/meta`

## High-Risk Truths To Lock

- diagnostics/developer payload 的低杠杆 `Any` 不应在本 phase 混入主战场。
- broad-catch 的保留项必须是 typed arbitration / documented defer，而不是 generic swallow。
- `Phase 31` 的 runtime/service/platform budget 仍需保留为独立收官相位。
