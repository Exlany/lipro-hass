---
phase: 56
slug: shared-backoff-neutralization-and-cross-plane-retry-hygiene
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-22
---

# Phase 56 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + focused protocol/runtime/MQTT regressions + meta guards |
| **Config file** | `pyproject.toml` |
| **Smoke command** | `uv run pytest -q tests/core/api/test_api_request_policy.py tests/core/mqtt/test_mqtt_backoff.py tests/core/test_command_result.py` |
| **Quick run command** | `uv run pytest -q tests/core/api/test_api_request_policy.py tests/core/mqtt/test_mqtt_backoff.py tests/core/test_command_result.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance_followup_route.py tests/meta/test_governance_phase_history.py` |
| **Phase gate command** | `uv run pytest -q tests/core/api/test_api_request_policy.py tests/core/mqtt/test_mqtt_backoff.py tests/core/test_command_result.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance_followup_route.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_guards.py && uv run python scripts/check_file_matrix.py --check && uv run ruff check custom_components/lipro/core/utils/backoff.py custom_components/lipro/core/api/request_policy.py custom_components/lipro/core/api/request_policy_support.py custom_components/lipro/core/command/result_policy.py custom_components/lipro/core/coordinator/runtime/command/retry.py custom_components/lipro/core/mqtt/setup_backoff.py tests/core/api/test_api_request_policy.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance_followup_route.py tests/meta/test_governance_phase_history.py scripts/check_file_matrix.py` |
| **Estimated runtime** | `~30-90s` |

## Wave Structure

- **Wave 1:** `56-01` create neutral shared backoff helper home and route API-local usage through it
- **Wave 2:** `56-02` rewire command/runtime/MQTT callers and close request-policy utility leakage
- **Wave 3:** `56-03` freeze residual closure via tests, baselines, review truth, and milestone current-story updates

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 56-01-01 | 01 | 1 | RES-13 | shared helper primitive behavior | `uv run pytest -q tests/core/mqtt/test_mqtt_backoff.py tests/core/test_command_result.py` | ✅ passed |
| 56-01-02 | 01 | 1 | ARC-09 | request-policy API-local behavior intact | `uv run pytest -q tests/core/api/test_api_request_policy.py` | ✅ passed |
| 56-02-01 | 02 | 2 | ARC-09 | cross-plane callers import neutral helper without semantic drift | `uv run pytest -q tests/core/mqtt/test_mqtt_backoff.py tests/core/test_command_result.py tests/core/api/test_api_request_policy.py` | ✅ passed |
| 56-03-01 | 03 | 3 | GOV-40 | governance truth + meta guards freeze residual closure | `uv run pytest -q tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance_followup_route.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_guards.py && uv run python scripts/check_file_matrix.py --check` | ✅ passed |

## Wave Commands

### Wave 1 Gate
- `uv run pytest -q tests/core/api/test_api_request_policy.py tests/core/mqtt/test_mqtt_backoff.py tests/core/test_command_result.py`

### Wave 2 Gate
- `uv run pytest -q tests/core/api/test_api_request_policy.py tests/core/mqtt/test_mqtt_backoff.py tests/core/test_command_result.py`

### Wave 3 Gate
- `uv run pytest -q tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance_followup_route.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_guards.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check custom_components/lipro/core/utils/backoff.py custom_components/lipro/core/api/request_policy.py custom_components/lipro/core/api/request_policy_support.py custom_components/lipro/core/command/result_policy.py custom_components/lipro/core/coordinator/runtime/command/retry.py custom_components/lipro/core/mqtt/setup_backoff.py tests/core/api/test_api_request_policy.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance_followup_route.py tests/meta/test_governance_phase_history.py scripts/check_file_matrix.py`

## Manual-Only Verifications

- 确认 `RequestPolicy` 依旧是 API-local `429` / busy / pacing truth，而非 generic backoff export home。
- 确认 `core/utils/backoff.py` 没有膨胀为 retry-policy manager，只保留 pure primitive 身份。
- 确认 command/runtime/MQTT callers 只共享 primitive，不共享 policy owner 或 second public story。
- 确认 residual ledger 已把 `Generic backoff helper leak` 从 active family 迁入 closed family。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `neutral helper home -> caller rewiring -> truth freeze`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded.

**Approval:** execution verified and promoted.
