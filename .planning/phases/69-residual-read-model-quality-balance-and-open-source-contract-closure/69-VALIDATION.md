---
phase: 69
slug: residual-read-model-quality-balance-and-open-source-contract-closure
status: planned
nyquist_compliant: true
review_gate_required: false
created: 2026-03-24
---

# Phase 69 — Validation Strategy

## Route Contract

本 phase 来自 `Phase 68` closeout 后的显式 residual carry-forward，因此默认路线为：

1. seed future milestone / phase definition
2. `$gsd-plan-phase 69`
3. `$gsd-next`（若 `v1.16` 仍是 current milestone，则继续 closeout；若 future route 被激活，则进入 execute）

`$gsd-review` 不是强制前置门，但若计划在执行前明显扩张 scope，可作为加严手段重新引入。

## Wave Structure

- **Wave 1:** `69-01`, `69-02`
- **Wave 2:** `69-03`, `69-04`
- **Wave 3:** `69-05`

## Per-Plan Verification Map

| Plan | Wave | Primary scope | Automated command |
|------|------|---------------|-------------------|
| `69-01` | 1 | runtime-access read model + runtime infra slimming | `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_unload_reload.py tests/services/test_maintenance.py tests/meta/test_dependency_guards.py` |
| `69-02` | 1 | schedule/service de-protocolization + wrapper residue | `uv run pytest -q tests/services/test_services_schedule.py tests/core/api/test_api_request_policy.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_topics.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py` |
| `69-03` | 2 | checker coverage + integration balance + meta-shell maintainability | `uv run pytest -q tests/test_refactor_tools.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py tests/integration/test_telemetry_exporter_integration.py tests/services/test_maintenance.py` |
| `69-04` | 2 | open-source metadata/docs/support contract alignment | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` |
| `69-05` | 3 | governance sync + planned-route verification freeze | `uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py` |

## Full Phase Gate

```bash
uv run ruff check .
uv run mypy --follow-imports=silent .
uv run python scripts/check_architecture_policy.py --check
uv run python scripts/check_file_matrix.py --check
uv run pytest -q tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_unload_reload.py tests/services/test_maintenance.py tests/services/test_services_schedule.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_topics.py tests/test_refactor_tools.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/integration/test_telemetry_exporter_integration.py
```

## Sign-Off Checklist

- [ ] `runtime_access_support.py` no longer behaves like a shadow public runtime API.
- [ ] schedule/service path no longer owns protocol-shaped argument choreography.
- [ ] wrapper/shim/lazy-import residue is either reduced or explicitly documented with owner + delete gate.
- [ ] checker coverage / integration depth materially increase relative to meta-only protection.
- [ ] docs/metadata/support/security continuity tells one honest open-source story.
- [ ] governance docs and verification assets agree on `v1.16 closeout-ready baseline` versus `v1.17 planned residual route`.
