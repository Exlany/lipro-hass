# Phase 29 Research

**Status:** `research complete`
**Date:** `2026-03-17`
**Requirement:** `HOT-06`, `RES-05`, `TST-03`

## Executive Judgment

`Phase 29` 最优是 `3 plans / 3 waves`：

1. `request/auth/transport bridge` slimming
2. `command/pacing` family slimming + API mega-test topicization
3. `capability wrapper` 收尾 + residual/public-surface truth closeout

这比分“先拆 façade、再把所有测试/治理巨石都扫一遍”更精准，也更符合 `HOT-06 / RES-05 / TST-03` 的真 home。

## Current Hotspot Snapshot

### 1. `transport/auth/result-arbitration bridge` 是最高优先级

`client.py` 的 `_request_smart_home_mapping` / `_request_iot_mapping` / `_iot_request` 与 `transport_executor.py`、`auth_recovery.py`、`endpoints/payloads.py` 之间仍有重叠，导致 `LiproRestFacade` 继续像万能适配器。

### 2. `command pacing / busy-retry cluster` 是第二优先级

`request_policy.py` 与 `command_api_service.py` 已经是 focused home，但 façade 仍保留 `_record_change_state_*`、busy-retry、command wrappers 等高 churn 桥接层，测试也集中在同一大文件里。

### 3. `schedule + misc capability wrappers` 适合作为第三波收尾

`schedule_service.py`、`diagnostics_api_service.py`、`mqtt_api_service.py`、`power_service.py` 已有 focused homes，但 façade 仍保留 capability forwarding 与少量 helper 重影；这些点适合作为最后一波 cleanup，而不是继续放任在 façade 顶层。

### 4. 本 phase 的测试 topicization 应只围绕 REST formal path

- `tests/core/api/test_api.py` 仍是剩余 smoke home，但 capability wave 应优先落到已有 focused suites：`test_api_diagnostics_service.py`、`test_api_schedule_service.py`、`test_api_schedule_endpoints.py`。
- `tests/meta/test_public_surface_guards.py` 与 `tests/meta/test_modularization_surfaces.py` 是本 phase 的 meta home。
- `tests/core/test_init.py`、control/runtime giant suites 只做 fallout smoke，不是主拆对象。

## Recommended Plan Structure

### Plan 29-01 — request/auth/transport bridge slimming

**File focus:**
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/api/transport_executor.py`
- `custom_components/lipro/core/api/auth_recovery.py`
- `custom_components/lipro/core/api/endpoints/payloads.py`
- `tests/core/api/test_api.py`

### Plan 29-02 — command/pacing family slimming and API topicization

**File focus:**
- `custom_components/lipro/core/api/request_policy.py`
- `custom_components/lipro/core/api/command_api_service.py`
- `custom_components/lipro/core/api/client.py`
- `tests/core/api/test_api.py`
- `tests/core/test_command_dispatch.py`

### Plan 29-03 — capability wrapper closeout and residual/public-surface truth sync

**File focus:**
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/api/schedule_service.py`
- `custom_components/lipro/core/api/diagnostics_api_service.py`
- `custom_components/lipro/core/api/mqtt_api_service.py`
- `custom_components/lipro/core/api/power_service.py`
- `tests/core/api/test_api_diagnostics_service.py`
- `tests/core/api/test_api_schedule_service.py`
- `tests/core/api/test_api_schedule_endpoints.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_modularization_surfaces.py`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`

## Validation Architecture

- `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_api_transport_executor.py tests/core/api/test_auth_recovery_telemetry.py`
- `uv run pytest -q tests/core/api/test_api.py tests/core/test_command_dispatch.py -k "command or pacing or busy"`
- `uv run pytest -q tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py tests/meta/test_public_surface_guards.py tests/meta/test_modularization_surfaces.py tests/meta/test_governance_closeout_guards.py`
- `uv run python scripts/check_file_matrix.py --check`

## High-Risk Truths To Lock

- `LiproRestFacade` 继续只做 child façade；不能通过 extraction 再造 root。
- REST meta truth 只动 public-surface / modularization guards，不扩题到全量 governance giant。
- schedule decode / payload normalization 不能从 focused homes 退回 façade 私有 helper。
