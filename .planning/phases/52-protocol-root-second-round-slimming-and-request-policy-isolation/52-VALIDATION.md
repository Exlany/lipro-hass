---
phase: 52
slug: protocol-root-second-round-slimming-and-request-policy-isolation
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-21
---

# Phase 52 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + protocol/API regressions + meta guards |
| **Config file** | `pyproject.toml` |
| **Smoke command** | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_request_policy.py` |
| **Quick run command** | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_transport_and_schedule.py tests/core/api/test_api_request_policy.py tests/core/api/test_api_transport_executor.py tests/core/api/test_api_command_service.py tests/core/api/test_api_command_surface.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py` |
| **Phase gate command** | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_transport_and_schedule.py tests/core/api/test_api_request_policy.py tests/core/api/test_api_transport_executor.py tests/core/api/test_api_command_service.py tests/core/api/test_api_command_surface.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py && uv run python scripts/check_file_matrix.py --check` |
| **Estimated runtime** | `~45-100s` |

## Wave Structure

- **Wave 1:** `52-01` protocol-root topicization + narrower REST child-facing ports + MQTT attach/diagnostics inward localization
- **Wave 2:** `52-02` request-policy implementation isolation (`429` / busy / pacing / request ownership convergence)
- **Wave 3:** `52-03` protocol/API regression hardening + guard/baseline/review truth freeze

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 52-01-01 | 01 | 1 | ARC-08 | protocol-root contract / public identity | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/meta/test_public_surface_guards.py` | ✅ passed |
| 52-01-02 | 01 | 1 | ARC-08 | MQTT attach / diagnostics root behavior | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_transport_and_schedule.py` | ✅ passed |
| 52-02-01 | 02 | 2 | ARC-08 | 429 / rate-limit ownership | `uv run pytest -q tests/core/api/test_api_request_policy.py tests/core/api/test_api_command_surface.py -k "429 or rate_limit"` | ✅ passed |
| 52-02-02 | 02 | 2 | ARC-08 | busy / pacing ownership | `uv run pytest -q tests/core/api/test_api_request_policy.py tests/core/api/test_api_command_service.py -k "busy or CHANGE_STATE or pacing"` | ✅ passed |
| 52-02-03 | 02 | 2 | ARC-08 | mapping/auth-aware request ownership | `uv run pytest -q tests/core/api/test_api_transport_executor.py tests/core/api/test_api_command_surface.py` | ✅ passed |
| 52-03-01 | 03 | 3 | ARC-08 | protocol/API truth freeze + dependency/public-surface guards | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py && uv run python scripts/check_file_matrix.py --check` | ✅ passed |

## Wave Commands

### Wave 1 Gate
- `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_transport_and_schedule.py tests/meta/test_public_surface_guards.py`

### Wave 2 Gate
- `uv run pytest -q tests/core/api/test_api_request_policy.py tests/core/api/test_api_command_service.py tests/core/api/test_api_transport_executor.py tests/core/api/test_api_command_surface.py`

### Wave 3 Gate
- `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py`
- `uv run python scripts/check_file_matrix.py --check`

## Manual-Only Verifications

- 确认 `LiproProtocolFacade` 仍是唯一正式 protocol-plane root；新增 collaborator 只被叙述为 localized/support seams。
- 确认 `LiproRestFacade` / `LiproMqttFacade` 继续只是 child façade，没有被新的 exports、docs wording 或 imports 偷渡提升为第二根。
- 确认 `RequestPolicy` 最终成为 `429` / busy / pacing formal truth，而不是与 `TransportRetry` / `command_api_service.py` / `rest_facade.py` 并行持有决策。
- 确认 `RestTransportExecutor` 被收窄回 transport/signing/response validation 职责，mapping/auth-aware request flow 不再 dual-home。
- 确认 generic backoff 若未在本 phase 内迁出，已被显式登记为 deferred residual，而不是继续隐性跨 plane 泄漏。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `protocol-root slimming -> request-policy isolation -> truth freeze`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded.

**Approval:** execution verified and promoted.
