---
phase: 11
slug: control-router-formalization-wiring-residual-demotion
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-14
updated: 2026-03-14
---

# Phase 11 — Validation Strategy

> Executed validation record for full Phase 11 closeout.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + `ruff` |
| **Config file** | `pyproject.toml` |
| **Primary command** | `uv run ruff check .` |
| **Governance checks** | `uv run python scripts/check_architecture_policy.py --check` + `uv run python scripts/check_file_matrix.py --check` |
| **Phase closeout suite** | `uv run pytest -q tests/core/test_init.py tests/services/test_service_resilience.py tests/services/test_services_registry.py tests/core/api/test_protocol_contract_matrix.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/coordinator/runtime/test_status_runtime.py tests/core/test_control_plane.py tests/core/test_coordinator.py tests/core/test_coordinator_integration.py tests/core/test_diagnostics.py tests/services/test_maintenance.py tests/services/test_device_lookup.py tests/services/test_services_diagnostics.py tests/core/test_system_health.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/platforms/test_switch.py tests/platforms/test_select.py tests/platforms/test_platform_entities_behavior.py tests/platforms/test_update.py tests/platforms/test_firmware_update_entity_edges.py tests/core/ota/test_firmware_manifest.py tests/benchmarks/test_coordinator_performance.py` |

---

## Executed Verification Map

| Task ID | Plan | Wave | Requirement | Automated Command | Status |
|---------|------|------|-------------|-------------------|--------|
| `11-01-01` | `11-01` | 1 | `CTRL-01`, `CTRL-02` | `uv run pytest -q tests/core/test_init.py tests/services/test_service_resilience.py tests/services/test_services_registry.py tests/meta/test_public_surface_guards.py` | ✅ green |
| `11-02-01` | `11-02` | 2 | `CTRL-01`, `CTRL-02` | `uv run pytest -q tests/core/test_init.py tests/services/test_service_resilience.py tests/services/test_services_registry.py tests/meta/test_public_surface_guards.py` | ✅ green |
| `11-03-01` | `11-03` | 3 | `CTRL-03` | `uv run ruff check .` + `uv run python scripts/check_architecture_policy.py --check` + `uv run python scripts/check_file_matrix.py --check` | ✅ green |
| `11-04-01` | `11-04` | 4 | `SURF-01` | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_coordinator.py tests/core/test_coordinator_integration.py tests/meta/test_public_surface_guards.py tests/benchmarks/test_coordinator_performance.py` | ✅ green |
| `11-05-01` | `11-05` | 5 | `CTRL-04`, `RUN-01` | `uv run pytest -q tests/core/coordinator/runtime/test_status_runtime.py tests/core/test_control_plane.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/services/test_maintenance.py tests/services/test_device_lookup.py tests/services/test_services_diagnostics.py tests/meta/test_dependency_guards.py` | ✅ green |
| `11-06-01` | `11-06` | 6 | `ENT-01` | `uv run pytest -q tests/platforms/test_switch.py tests/platforms/test_select.py tests/platforms/test_platform_entities_behavior.py tests/platforms/test_update.py` | ✅ green |
| `11-07-01` | `11-07` | 6 | `ENT-02` | `uv run pytest -q tests/platforms/test_update.py tests/platforms/test_firmware_update_entity_edges.py tests/core/ota/test_firmware_manifest.py tests/core/test_diagnostics.py` | ✅ green |
| `11-08-01` | `11-08` | 7 | `GOV-08` | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | ✅ green |
| `11-closeout-01` | `11` | 7 | `CTRL-01`~`GOV-08` | `uv run ruff check .` + governance checks + phase closeout suite | ✅ `551 passed` |

---

## Wave 0 Requirements

- [x] `tests/core/test_init.py` — control-plane service regression baseline
- [x] `tests/services/test_service_resilience.py` — service resilience baseline
- [x] `tests/services/test_services_registry.py` — formal router binding baseline
- [x] `tests/core/api/test_protocol_contract_matrix.py` — protocol surface baseline
- [x] `tests/core/coordinator/runtime/test_device_runtime.py` — runtime refresh-path baseline
- [x] `tests/core/coordinator/runtime/test_status_runtime.py` — status isolation baseline
- [x] `tests/core/test_control_plane.py` — control-plane runtime-access baseline
- [x] `tests/core/test_diagnostics.py` — diagnostics degradation baseline
- [x] `tests/meta/test_dependency_guards.py` — dependency guard baseline
- [x] `tests/meta/test_public_surface_guards.py` — public surface guard baseline
- [x] `tests/meta/test_governance_guards.py` — governance structure baseline
- [x] `tests/meta/test_version_sync.py` — release/version sync baseline
- [x] `tests/platforms/test_switch.py` / `tests/platforms/test_select.py` / `tests/platforms/test_platform_entities_behavior.py` — entity/platform truth baseline
- [x] `tests/platforms/test_update.py` / `tests/platforms/test_firmware_update_entity_edges.py` / `tests/core/ota/test_firmware_manifest.py` — OTA helper-cluster baseline

---

## Manual Review Items

| Behavior | Requirement | Verdict |
|----------|-------------|---------|
| formal router 与 compat wiring 身份保持单一主链 | `CTRL-01`, `CTRL-02`, `CTRL-03` | passed |
| REST/runtime surface 不再由 dynamic child / compat fallback 定义 | `SURF-01` | passed |
| runtime-access、diagnostics 与 public typing 归属单一正式故事线 | `CTRL-04`, `RUN-01` | passed |
| supplemental entity 与 OTA truth 由 formal helpers / projections 承载 | `ENT-01`, `ENT-02` | passed |
| release、CI、contributing、security disclosure 对外说同一种话 | `GOV-08` | passed |

---

## Validation Sign-Off

- [x] All plans have automated verification coverage
- [x] Wave sequencing preserved (`11-01` → `11-08`)
- [x] Plan summaries, roadmap, requirements, state, verification and validation assets are all present
- [x] No watch-mode flags
- [x] `nyquist_compliant: true` kept in frontmatter

**Approval:** validation passed (2026-03-14)
