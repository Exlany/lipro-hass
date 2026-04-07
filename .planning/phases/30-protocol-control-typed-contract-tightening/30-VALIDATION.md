---
phase: 30
slug: protocol-control-typed-contract-tightening
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-17
---

# Phase 30 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest API/protocol/control suites + meta guards + focused ruff static gate |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_protocol_contract_matrix.py tests/core/test_control_plane.py && uv run ruff check custom_components/lipro/core/api custom_components/lipro/core/protocol custom_components/lipro/control tests/meta` |
| **Phase gate command** | `uv run pytest -q tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_status_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_diagnostics_service.py tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/core/coordinator/test_entity_protocol.py tests/core/test_init.py tests/core/test_init_edge_cases.py tests/core/test_control_plane.py tests/core/test_system_health.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_closeout_guards.py && uv run ruff check custom_components/lipro/core/api custom_components/lipro/core/protocol custom_components/lipro/control tests/meta` |
| **Estimated runtime** | ~45-120 seconds |

## Wave Structure

- **Wave 1:** `30-01` —— REST response/result spine tightening
- **Wave 2:** `30-02` —— protocol boundary/root contract tightening
- **Wave 3:** `30-03` —— control lifecycle arbitration + guard freeze

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 30-01-01 | 01 | 1 | TYP-06 | focused | `uv run pytest -q tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_status_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_diagnostics_service.py` | ✅ passed |
| 30-01-02 | 01 | 1 | ERR-04 | focused | `uv run pytest -q tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_status_service.py -k "auth or busy or rate or result"` | ✅ passed |
| 30-02-01 | 02 | 2 | TYP-06 | focused | `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/core/coordinator/test_entity_protocol.py` | ✅ passed |
| 30-02-02 | 02 | 2 | ERR-04 | focused | `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/core/coordinator/test_entity_protocol.py -k "protocol or replay or session"` | ✅ passed |
| 30-03-01 | 03 | 3 | ERR-04 | focused | `uv run pytest -q tests/core/test_init.py tests/core/test_init_edge_cases.py tests/core/test_control_plane.py tests/core/test_system_health.py` | ✅ passed |
| 30-03-02 | 03 | 3 | TYP-06, ERR-04 | phase-gate + static | `uv run pytest -q tests/core/test_init.py tests/core/test_init_edge_cases.py tests/core/test_control_plane.py tests/core/test_system_health.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_closeout_guards.py && uv run ruff check custom_components/lipro/core/api custom_components/lipro/core/protocol custom_components/lipro/control tests/meta` | ✅ passed |

## Manual-Only Verifications

- 确认 REST typed spine tightening 没有把 `client.py` 重新变回所有类型逻辑的 home。
- 确认 protocol boundary/root 收紧时没有新建 root 或平行 boundary pipeline。
- 确认 `system_health_surface.py` 仍只同步 shared `failure_summary` 最小载荷，没有被错误抬升为 diagnostics cleanup home。
- 确认 `STATE.md` 与 `v1.3-HANDOFF.md` 已显式写清 `Phase 30` closeout truth，并把 `Phase 31` 限定为 runtime/service/platform no-growth follow-through。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `REST spine -> protocol root -> control lifecycle`.
- [x] Static gate includes `uv run ruff check ...` for touched typed-contract zones.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded in `30-VERIFICATION.md`.
