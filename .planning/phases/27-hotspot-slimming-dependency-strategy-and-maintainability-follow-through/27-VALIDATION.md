---
phase: 27
slug: hotspot-slimming-dependency-strategy-and-maintainability-follow-through
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-17
---

# Phase 27 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest targeted slices + governance docs sync + runtime/public-surface guards |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/core/test_init.py tests/core/test_init_service_handlers.py tests/services/test_services_diagnostics.py tests/services/test_service_resilience.py tests/test_coordinator_public.py` |
| **Phase gate command** | `uv run pytest -q tests/core/test_init.py tests/core/test_init_service_handlers.py tests/services/test_services_diagnostics.py tests/services/test_service_resilience.py tests/test_coordinator_public.py tests/core/test_coordinator.py && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py && uv run python scripts/check_file_matrix.py --check && uv run ruff check custom_components/lipro/runtime_types.py custom_components/lipro/services/schedule.py custom_components/lipro/services/diagnostics/handlers.py custom_components/lipro/entities/firmware_update.py custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/core/coordinator/runtime_context.py custom_components/lipro/core/coordinator/orchestrator.py tests/conftest.py tests/core/test_init.py tests/core/test_init_service_handlers.py tests/services/test_services_diagnostics.py tests/services/test_service_resilience.py tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_toolchain_truth.py scripts/check_file_matrix.py` |
| **Estimated runtime** | ~30-90 seconds |

## Wave Structure

- **Wave 1:** `27-01` —— protocol-service contract surfacing + consumer migration
- **Wave 2:** `27-02` —— coordinator forwarder removal + phase-residue cleanup
- **Wave 3:** `27-03` —— baseline/dependency/residual truth sync
- **Wave 4:** `27-04` —— test monolith split + TESTING/toolchain truth refresh

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 27-01-01 | 01 | 1 | HOT-05, RES-04 | focused | `uv run pytest -q tests/services/test_services_diagnostics.py tests/services/test_service_resilience.py tests/platforms/test_update.py tests/platforms/test_firmware_update_entity_edges.py tests/platforms/test_update_task_callback.py` | ✅ passed |
| 27-01-02 | 01 | 1 | HOT-05, RES-04 | focused | `uv run pytest -q tests/core/test_init.py tests/core/test_init_service_handlers.py tests/services/test_services_diagnostics.py tests/services/test_service_resilience.py tests/test_coordinator_public.py tests/core/test_coordinator.py` | ✅ passed |
| 27-02-01 | 02 | 2 | HOT-05, RES-04 | focused | `uv run pytest -q tests/core/test_init.py tests/core/test_init_service_handlers.py tests/services/test_services_diagnostics.py tests/services/test_service_resilience.py tests/test_coordinator_public.py tests/core/test_coordinator.py` | ✅ passed |
| 27-02-02 | 02 | 2 | HOT-05, RES-04 | focused | `uv run ruff check custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/core/coordinator/runtime_context.py custom_components/lipro/core/coordinator/orchestrator.py tests/core/test_init.py tests/core/test_init_service_handlers.py tests/core/test_coordinator.py tests/test_coordinator_public.py` | ✅ passed |
| 27-03-01 | 03 | 3 | HOT-05, RES-04 | focused | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` | ✅ passed |
| 27-03-02 | 03 | 3 | HOT-05, RES-04 | focused | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` | ✅ passed |
| 27-04-01 | 04 | 4 | TST-02 | focused | `uv run pytest -q tests/core/test_init.py tests/core/test_init_service_handlers.py tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_toolchain_truth.py` | ✅ passed |
| 27-04-02 | 04 | 4 | TST-02 | final | `uv run pytest -q tests/core/test_init.py tests/core/test_init_service_handlers.py tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` | ✅ passed |

## Manual-Only Verifications

- 确认 `Coordinator` 仍是唯一正式 runtime root，`protocol_service` 只是 runtime-owned capability port，而不是第二 root。
- 确认 pure protocol forwarders 已从 `Coordinator` 退场，而不是换名保留。
- 确认测试拆分后仍保留锚点套件，不通过 shared hidden helpers 偷渡第二真源。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `contract -> slimming -> truth sync -> test split`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded in `27-VERIFICATION.md`.

**Approval:** phase executed and verified

## Execution Evidence

- `106 passed` on service/diagnostics/firmware-update regression slice
- `245 passed` on runtime + coordinator + service-handler phase gate slice
- `74 passed` on governance/public-surface/version/toolchain gate
- `All checks passed!` on targeted Ruff gate
- `uv run python scripts/check_file_matrix.py --check` exited `0`

