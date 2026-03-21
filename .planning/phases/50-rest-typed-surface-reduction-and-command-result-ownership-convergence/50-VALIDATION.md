---
phase: 50
slug: rest-typed-surface-reduction-and-command-result-ownership-convergence
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-21
---

# Phase 50 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + meta guards |
| **Config file** | `pyproject.toml` |
| **Smoke command** | `uv run pytest -q tests/core/api/test_api_command_surface.py tests/core/api/test_api_status_service.py tests/core/test_command_result.py` |
| **Quick run command** | `uv run pytest -q tests/core/api/test_api_command_surface.py tests/core/api/test_api_status_service.py tests/core/test_command_result.py tests/services/test_execution.py tests/services/test_services_diagnostics.py tests/core/api/test_api_diagnostics_service.py tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py` |
| **Phase gate command** | `uv run pytest -q tests/core/api/test_api_command_surface.py tests/core/api/test_api_status_service.py tests/core/test_command_result.py tests/services/test_execution.py tests/services/test_services_diagnostics.py tests/core/api/test_api_diagnostics_service.py tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py && uv run python scripts/check_file_matrix.py --check` |
| **Estimated runtime** | `~45-90s` |

## Wave Structure

- **Wave 1:** `50-01` endpoint typed-surface reduction + `50-02` request/mapping helper honesty tightening
- **Wave 2:** `50-03` command-result ownership convergence
- **Wave 3:** `50-04` diagnostics auth-error convergence + typed-budget / truth guards

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 50-01-01 | 01 | 1 | TYP-12 | REST endpoint behavior | `uv run pytest -q tests/core/api/test_api_status_service.py` | ⬜ pending |
| 50-02-01 | 02 | 1 | TYP-12 | request/mapping helper behavior | `uv run pytest -q tests/core/api/test_api_command_surface.py` | ⬜ pending |
| 50-03-01 | 03 | 2 | ARC-07 | command-result policy convergence | `uv run pytest -q tests/core/test_command_result.py` | ⬜ pending |
| 50-04-01 | 04 | 3 | ARC-07 | diagnostics auth chain | `uv run pytest -q tests/services/test_execution.py tests/services/test_services_diagnostics.py tests/core/api/test_api_diagnostics_service.py` | ⬜ pending |
| 50-04-02 | 04 | 3 | TYP-12, ARC-07 | touched-zone guards + truth freeze | `uv run pytest -q tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py && uv run python scripts/check_file_matrix.py --check` | ⬜ pending |

## Wave Commands

### Wave 1 Gate

- `uv run pytest -q tests/core/api/test_api_command_surface.py tests/core/api/test_api_status_service.py`

### Wave 2 Gate

- `uv run pytest -q tests/core/test_command_result.py`

### Wave 3 Gate

- `uv run pytest -q tests/services/test_execution.py tests/services/test_services_diagnostics.py tests/core/api/test_api_diagnostics_service.py`
- `uv run pytest -q tests/meta/test_phase50_rest_typed_budget_guards.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py`
- `uv run python scripts/check_file_matrix.py --check`

## Manual-Only Verifications

- 确认 `LiproRestFacade` 仍是唯一 canonical REST child façade，`request_gateway.py` / `endpoint_surface.py` 没有被 public-surface 文档或 imports 偷渡提升为第二 root。
- 确认 `services/execution.py` 仍被 baseline/review assets 记录为 formal shared execution facade，而不是 residual / kill target。
- 确认 `result.py` 与 `result_policy.py` 的职责分工从“实现双持”收敛为“stable exports vs implementation home”，且对现有 importers 行为无破坏。
- 确认 typed-budget guard 明确区分 `sanctioned_any` 与 `backlog_any`，并且对 touched zone 至少做到 no-growth，最好 net-reduction。
- 确认 diagnostics multi-coordinator capability degrade-and-continue 语义保持不变，没有因 auth convergence 变成 fail-fast 行为漂移。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `typed surface -> ownership convergence -> guard/truth freeze`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [ ] Execution evidence pending.

**Approval:** ready for plan generation and plan-check verification
