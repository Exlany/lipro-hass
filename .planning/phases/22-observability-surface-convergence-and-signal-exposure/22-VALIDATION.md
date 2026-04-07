---
phase: 22
slug: observability-surface-convergence-and-signal-exposure
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-16
---

# Phase 22 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + ruff + mypy |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q` |
| **Wave gate command** | `uv run ruff check . && uv run pytest -q` |
| **Final phase gate** | `uv run pytest -q && uv run ruff check . && uv run mypy` |
| **Estimated runtime** | ~240-360 seconds |

## Wave Structure

- **Wave 1:** `22-01` —— diagnostics / system health signal convergence
- **Wave 2:** `22-02` —— developer / support / report consumer convergence
- **Wave 3:** `22-03` —— observability contract freeze + governance / integration guards
- **Wave 0:** 无需 bootstrap；现有 control / telemetry / diagnostics test slices 已具备执行条件

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 22-01-01 | 01 | 1 | OBS-03 | focused | `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_control_plane.py tests/integration/test_telemetry_exporter_integration.py tests/core/telemetry/test_sinks.py` | ⬜ pending |
| 22-02-01 | 02 | 2 | OBS-03 | focused | `uv run pytest -q tests/core/test_developer_report.py tests/core/test_report_builder.py tests/services/test_services_diagnostics.py tests/services/test_services_share.py` | ⬜ pending |
| 22-03-01 | 03 | 3 | OBS-03 | focused | `uv run pytest -q tests/integration/test_ai_debug_evidence_pack.py tests/integration/test_telemetry_exporter_integration.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py` | ⬜ pending |
| 22-03-02 | 03 | 3 | OBS-03 | final | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py && uv run mypy` | ⬜ pending |

## Wave Commands

### Wave 1 Gate

- `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_control_plane.py tests/integration/test_telemetry_exporter_integration.py tests/core/telemetry/test_sinks.py`
- `uv run ruff check custom_components/lipro/control/diagnostics_surface.py custom_components/lipro/control/system_health_surface.py custom_components/lipro/control/runtime_access.py custom_components/lipro/core/telemetry/sinks.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_control_plane.py tests/core/telemetry/test_sinks.py tests/integration/test_telemetry_exporter_integration.py`

### Wave 2 Gate

- `uv run pytest -q tests/core/test_developer_report.py tests/core/test_report_builder.py tests/services/test_services_diagnostics.py tests/services/test_services_share.py`
- `uv run ruff check custom_components/lipro/services/diagnostics/helpers.py custom_components/lipro/services/diagnostics/handlers.py custom_components/lipro/control/developer_router_support.py custom_components/lipro/core/anonymous_share/report_builder.py tests/core/test_developer_report.py tests/core/test_report_builder.py tests/services/test_services_diagnostics.py tests/services/test_services_share.py tests/services/test_execution.py tests/integration/test_ai_debug_evidence_pack.py`

### Wave 3 Gate

- `uv run pytest -q tests/integration/test_ai_debug_evidence_pack.py tests/integration/test_telemetry_exporter_integration.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/integration/test_telemetry_exporter_integration.py tests/integration/test_ai_debug_evidence_pack.py`
- `uv run mypy`

## Manual-Only Verifications

- 确认 `Phase 22` 没有重新定义 failure taxonomy，只是把 `Phase 21` contract 暴露给 consumers。
- 确认 diagnostics / system health / developer / support / evidence consumers 使用的是同一 normalized summary vocabulary，而非同义不同 key。
- 确认 raw `error_type` / `code` / detail 只作为附加 debug 信息存在，不重新成为 normalized truth。
- 确认本 phase 没有偷跑 `Phase 23` 的 docs/templates/release workflow 更新。
- 若新增 consumer contract / retained residual rationale，确认 `.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md` 同步更新。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave 1 / Wave 2 / Wave 3 dependency split is explicit.
- [x] `nyquist_compliant: true` set in frontmatter.
- [ ] Execution evidence pending.

**Approval:** ready for execution after plan verification
