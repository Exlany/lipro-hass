---
phase: 29
slug: rest-child-facade-slimming-and-test-topicization
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-17
---

# Phase 29 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest API suites + REST public-surface/modularization guards + file-matrix tooling |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/core/api/test_api_transport_executor.py tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py` |
| **Phase gate command** | `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_api_transport_executor.py tests/core/api/test_auth_recovery_telemetry.py tests/core/test_command_dispatch.py tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py tests/meta/test_public_surface_guards.py tests/meta/test_modularization_surfaces.py tests/meta/test_governance_closeout_guards.py && uv run python scripts/check_file_matrix.py --check` |
| **Estimated runtime** | ~30-90 seconds |

## Wave Structure

- **Wave 1:** `29-01` —— request/auth/transport bridge slimming
- **Wave 2:** `29-02` —— command/pacing family slimming + API topicization
- **Wave 3:** `29-03` —— capability wrapper closeout + residual/public-surface truth sync

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 29-01-01 | 01 | 1 | HOT-06, RES-05 | focused | `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_api_transport_executor.py tests/core/api/test_auth_recovery_telemetry.py` | ✅ passed |
| 29-01-02 | 01 | 1 | HOT-06, TST-03 | focused | `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_api_transport_executor.py tests/core/api/test_auth_recovery_telemetry.py` | ✅ passed |
| 29-02-01 | 02 | 2 | HOT-06, TST-03 | focused | `uv run pytest -q tests/core/api/test_api.py tests/core/test_command_dispatch.py -k "command or pacing or busy"` | ✅ passed |
| 29-02-02 | 02 | 2 | TST-03 | focused | `uv run pytest -q tests/core/api/test_api.py tests/core/test_command_dispatch.py tests/core/api/test_protocol_contract_matrix.py -k "command or pacing or busy"` | ✅ passed |
| 29-03-01 | 03 | 3 | HOT-06, RES-05 | focused | `uv run pytest -q tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_api.py -k "schedule or mqtt or diagnostics or power"` | ✅ passed |
| 29-03-02 | 03 | 3 | RES-05, TST-03 | focused | `uv run pytest -q tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py tests/meta/test_public_surface_guards.py tests/meta/test_modularization_surfaces.py tests/meta/test_governance_closeout_guards.py && uv run python scripts/check_file_matrix.py --check` | ✅ passed |
| 29-phase-gate | all | all | HOT-06, RES-05, TST-03 | final | `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_api_transport_executor.py tests/core/api/test_auth_recovery_telemetry.py tests/core/test_command_dispatch.py tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py tests/meta/test_public_surface_guards.py tests/meta/test_modularization_surfaces.py tests/meta/test_governance_closeout_guards.py && uv run python scripts/check_file_matrix.py --check` | ✅ passed |

## Manual-Only Verifications

- 确认 `LiproRestFacade` 的瘦身来自 focused collaborator extraction，而不是新 root / compat façade。
- 确认 command/pacing 仍以 REST family 为主语，没有把 control-plane dispatch 错搬 home。
- 确认 capability regressions 已进入 dedicated REST suites，而非继续依赖单个 `test_api.py -k ...` 过滤器。
- 确认 residual/planning truth 明确指出 typed/exception cleanup 仍由 `Phase 30/31` 负责。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `request/auth -> command/pacing -> capability/truth closeout`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded in `29-VERIFICATION.md`.


## Execution Evidence

- `185 passed` on request/auth/transport + request-policy focused slice
- `34 passed, 139 deselected` on command/pacing/busy topic slice
- `171 passed` on capability + public-surface/modularization + closeout slice
- `238 passed` on full phase gate (`REST API + command dispatch + public/modularization truth + FILE_MATRIX`)
