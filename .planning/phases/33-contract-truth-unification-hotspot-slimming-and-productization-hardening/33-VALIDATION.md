---
phase: 33
slug: contract-truth-unification-hotspot-slimming-and-productization-hardening
status: planned
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-18
---

# Phase 33 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest core/meta/integration suites + workflow/toolchain guards + `ruff` + `mypy` + release/translation scripts |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run ruff check . && uv run pytest -q tests/meta/test_public_surface_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` |
| **Phase gate command** | `uv run ruff check . && uv run mypy && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run python scripts/check_translations.py && uv run pytest -q tests/meta/test_public_surface_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_version_sync.py` |
| **Estimated runtime** | ~120-360 seconds |

## Wave Structure

- **Wave 1:** `33-01` + `33-02` —— runtime contract single-truth, pure snapshots, acyclic control ports, shrunk control exports
- **Wave 2:** `33-03` —— giant roots / helper hotspots / forwarding clusters
- **Wave 3:** `33-04` —— exception arbitration, no-growth broad-catch guards, residual naming truth
- **Wave 4:** `33-05` —— local/CI/release/perf/reproducibility gate convergence
- **Wave 5:** `33-06` —— mega-test topicization and deep-doc / continuity productization follow-through

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 33-01-01 | 01 | 1 | ARC-03 | focused meta | `uv run pytest -q tests/meta/test_public_surface_guards.py` | planned |
| 33-01-02 | 01 | 1 | CTRL-07 | focused core | `uv run pytest -q tests/core/test_control_plane.py tests/core/test_init.py` | planned |
| 33-02-01 | 02 | 1 | CTRL-07 | focused integration | `uv run pytest -q tests/integration/test_telemetry_exporter_integration.py tests/core/test_system_health.py` | planned |
| 33-02-02 | 02 | 1 | GOV-27 | focused meta | `uv run pytest -q tests/meta/test_public_surface_guards.py tests/core/test_system_health.py` | planned |
| 33-03-01 | 03 | 2 | HOT-08 | focused API/runtime | `uv run pytest -q tests/core/api/test_api.py tests/core/test_coordinator.py` | planned |
| 33-03-02 | 03 | 2 | HOT-08 | focused helper hotspots | `uv run pytest -q tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_device_refresh.py` | planned |
| 33-03-03 | 03 | 2 | HOT-08 | focused mqtt/boundary | `uv run pytest -q tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_replay_rest.py tests/integration/test_mqtt_coordinator_integration.py` | planned |
| 33-04-01 | 04 | 3 | ERR-07 | focused runtime/service | `uv run pytest -q tests/services/test_service_resilience.py tests/services/test_maintenance.py tests/core/test_background_task_manager.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_coordinator.py` | planned |
| 33-04-02 | 04 | 3 | GOV-27 | focused meta | `uv run pytest -q tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_governance_guards.py -k "phase31 or residue or compat"` | planned |
| 33-05-01 | 05 | 4 | QLT-06 | focused meta | `uv run python scripts/check_translations.py && uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py` | planned |
| 33-05-02 | 05 | 4 | QLT-07 / GOV-28 | focused version/toolchain | `uv run pytest -q tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py` | planned |
| 33-06-01 | 06 | 5 | TST-05 | focused topic suites | `uv run pytest -q tests/core/api/test_api.py tests/core/test_init.py tests/core/test_init_service_handlers.py tests/meta/test_governance_guards.py` | planned |
| 33-06-02 | 06 | 5 | GOV-28 | focused public-doc/meta | `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | planned |

## Manual-Only Verifications

- 确认 `runtime_types.py` 真正成为唯一 formal runtime contract truth，而不是通过 alias 包装继续保留两套 authority wording。
- 确认 `RuntimeCoordinatorSnapshot` 变成纯 DTO 后，support/system-health/telemetry consumers 仍可在不偷渡 live coordinator 的前提下获取需要的数据。
- 确认 giant roots 的拆分确实下沉到现有 formal seams，而不是新增 shadow façade / second-root story。
- 确认 benchmark posture 已被固定为“PR 非阻塞、schedule/manual budget-tracked advisory lane”，且 docs + workflow + guards 对此没有二义。
- 确认 `attestation / provenance / signing / code scanning` 的对外状态在 README、SECURITY、runbook、workflow 与 guards 中完全同口径。
- 确认 deep bilingual/support/security/release docs 的 parity 是深层路径 parity，而不是 README 入口表面同步。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `contract truth -> hotspot slimming -> exception/residual -> assurance gates -> tests/docs/productization`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Quick run and phase gate commands align with current repo toolchain truth.
- [ ] Execution evidence recorded after implementation.
