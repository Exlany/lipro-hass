---
phase: 21
slug: replay-exception-taxonomy-hardening
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-16
---

# Phase 21 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + ruff |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q` |
| **Phase gate command** | `uv run ruff check . && uv run pytest -q` |
| **Estimated runtime** | ~180-360 seconds |

## Wave Structure

- **Wave 1**: `21-01` + `21-02` 可并行推进
- **Wave 2**: `21-03` 依赖 `21-01` 与 `21-02` 都完成
- **Wave 0**: 无需额外 bootstrap；现有 infra、fixtures、guards 已具备执行条件

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 21-01-01 | 01 | 1 | SIM-04 | focused | `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/meta/test_protocol_replay_assets.py` | ⬜ pending |
| 21-01-02 | 01 | 1 | SIM-04 | focused | `uv run pytest -q tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py` | ⬜ pending |
| 21-02-01 | 02 | 1 | ERR-02 | focused | `uv run pytest -q tests/core/coordinator/runtime/test_mqtt_runtime.py tests/integration/test_mqtt_coordinator_integration.py tests/core/test_init.py` | ⬜ pending |
| 21-02-02 | 02 | 1 | ERR-02 | focused | `uv run pytest -q tests/services/test_service_resilience.py tests/services/test_services_diagnostics.py tests/services/test_maintenance.py tests/services/test_execution.py` | ⬜ pending |
| 21-03-01 | 03 | 2 | ERR-02 | focused | `uv run pytest -q tests/core/telemetry/test_sinks.py tests/core/telemetry/test_exporter.py tests/integration/test_telemetry_exporter_integration.py` | ⬜ pending |
| 21-03-02 | 03 | 2 | SIM-04 / ERR-02 | focused | `uv run pytest -q tests/core/test_system_health.py tests/core/test_diagnostics.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_protocol_replay_assets.py tests/meta/test_evidence_pack_authority.py` | ⬜ pending |

## Wave Commands

### Wave 1 Gate

- `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/meta/test_protocol_replay_assets.py tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py`
- `uv run pytest -q tests/core/coordinator/runtime/test_mqtt_runtime.py tests/integration/test_mqtt_coordinator_integration.py tests/core/test_init.py tests/services/test_service_resilience.py tests/services/test_services_diagnostics.py tests/services/test_maintenance.py tests/services/test_execution.py`

### Wave 2 Gate

- `uv run pytest -q tests/core/telemetry/test_sinks.py tests/core/telemetry/test_exporter.py tests/integration/test_telemetry_exporter_integration.py tests/core/test_system_health.py tests/core/test_diagnostics.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_protocol_replay_assets.py tests/meta/test_evidence_pack_authority.py`
- `uv run ruff check custom_components/lipro/core/protocol custom_components/lipro/core/coordinator custom_components/lipro/core/telemetry custom_components/lipro/control custom_components/lipro/services/diagnostics tests/harness/protocol tests/harness/evidence_pack tests/integration tests/core/telemetry tests/meta`

## Manual-Only Verifications

- 确认 `Phase 21` 没有重新承担 `Phase 20` boundary formalization 或 `Phase 22/23` 的 consumer/docs scope。
- 确认 retained catch-all 均保留 cancellation passthrough，且已补 stage/reason/detail contract。
- 确认 replay/evidence 对四个 `Phase 20` families 的断言是 **family-level**，而不是继续只依赖 generic loop。
- 确认 taxonomy 采用“stable family + raw detail”分层，不把异常类名继续当成唯一 category。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave 1 / Wave 2 dependency split is explicit.
- [x] `nyquist_compliant: true` set in frontmatter.
- [ ] Execution evidence pending.

**Approval:** pending execution
