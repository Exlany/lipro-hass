---
phase: 55
slug: mega-test-topicization-round-2-and-repo-wide-typing-metric-stratification
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-21
---

# Phase 55 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + meta guards |
| **Config file** | `pyproject.toml` |
| **Smoke command** | `uv run pytest -q tests/core/api/test_api_command_surface.py tests/core/mqtt/test_transport_runtime.py -k "429 or ConnectAndDecode or lifecycle"` |
| **Quick run command** | `uv run pytest -q tests/core/api/test_api_command_surface*.py tests/core/mqtt/test_transport_runtime*.py tests/platforms/test_light*.py tests/platforms/test_fan*.py tests/platforms/test_select*.py tests/platforms/test_switch*.py tests/meta/test_phase31_runtime_budget_guards.py` |
| **Phase gate command** | `uv run pytest -q tests/core/api/test_api_command_surface*.py tests/core/api/test_api_request_policy.py tests/core/api/test_api_transport_executor.py tests/core/mqtt/test_transport_runtime*.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_connection_manager.py tests/platforms/test_light*.py tests/platforms/test_fan*.py tests/platforms/test_select*.py tests/platforms/test_switch*.py tests/platforms/test_platform_entities_behavior.py tests/platforms/test_entity_base.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py && uv run python scripts/check_file_matrix.py --check` |
| **Estimated runtime** | `~90-180s` |

## Wave Structure

- **Wave 1:** `55-01` API mega-test topicization
- **Wave 2:** `55-02` MQTT mega-test topicization
- **Wave 3:** `55-03` platform light/fan topicization
- **Wave 4:** `55-04` platform select/switch topicization
- **Wave 5:** `55-05` typing metric stratification + truth freeze

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 55-01-01 | 01 | 1 | TST-10 | API command-surface topology | `uv run pytest -q tests/core/api/test_api_command_surface*.py tests/core/api/test_api_request_policy.py tests/core/api/test_api_transport_executor.py` | ✅ passed |
| 55-02-01 | 02 | 2 | TST-10 | MQTT transport topology | `uv run pytest -q tests/core/mqtt/test_transport_runtime*.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_connection_manager.py` | ✅ passed |
| 55-03-01 | 03 | 3 | TST-10 | light/fan platform topology | `uv run pytest -q tests/platforms/test_light*.py tests/platforms/test_fan*.py tests/platforms/test_platform_entities_behavior.py tests/platforms/test_entity_base.py` | ✅ passed |
| 55-04-01 | 04 | 4 | TST-10 | select/switch platform topology | `uv run pytest -q tests/platforms/test_select*.py tests/platforms/test_switch*.py tests/platforms/test_platform_entities_behavior.py` | ✅ passed |
| 55-05-01 | 05 | 5 | TYP-13 | typing metric stratification / governance | `uv run pytest -q tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py && uv run python scripts/check_file_matrix.py --check` | ✅ passed |

## Wave Commands

### Wave 1 Gate
- `uv run pytest -q tests/core/api/test_api_command_surface*.py tests/core/api/test_api_request_policy.py tests/core/api/test_api_transport_executor.py`

### Wave 2 Gate
- `uv run pytest -q tests/core/mqtt/test_transport_runtime*.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_connection_manager.py`

### Wave 3 Gate
- `uv run pytest -q tests/platforms/test_light*.py tests/platforms/test_fan*.py tests/platforms/test_platform_entities_behavior.py tests/platforms/test_entity_base.py`

### Wave 4 Gate
- `uv run pytest -q tests/platforms/test_select*.py tests/platforms/test_switch*.py tests/platforms/test_platform_entities_behavior.py`

### Wave 5 Gate
- `uv run pytest -q tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py`
- `uv run python scripts/check_file_matrix.py --check`

## Manual-Only Verifications

- 确认所有 topicized test files 都围绕清晰 concern family，而不是任意拆行数。
- 确认原 mega suites 若保留薄壳/anchor，其角色仅为 continuity，不再继续膨胀。
- 确认 typing buckets 真能区分 production debt 与 test/meta literal debt，且 production no-growth 仍是 hard fail。
- 确认 testing docs / file matrix / guards 对新 topology 与 bucket truth 的叙述一致。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `API -> MQTT -> platform A -> platform B -> typing truth freeze`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded.

**Approval:** execution completed and verified.
