---
phase: 67
slug: typed-contract-convergence-toolchain-hardening-and-mypy-closure
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-24
---

# Phase 67 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `uv run pytest -q ...` focused suite verification + repo-wide quality bundle |
| **Config file** | `pyproject.toml` |
| **Smoke command** | `uv run pytest -q tests/core/telemetry/test_models.py tests/core/telemetry/test_sinks.py tests/core/telemetry/test_exporter.py tests/core/api/test_api_status_service.py tests/core/api/test_api_transport_executor.py tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py tests/core/test_init_service_handlers_device_resolution.py tests/core/test_init_service_handlers_schedules.py tests/core/test_init_service_handlers_sensor_feedback.py tests/services/test_services_schedule.py tests/core/test_control_plane.py tests/services/test_services_registry.py tests/platforms/test_update_background_tasks.py tests/core/test_init.py tests/meta/toolchain_truth_ci_contract.py tests/meta/toolchain_truth_release_contract.py tests/meta/toolchain_truth_python_stack.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_version_sync.py tests/meta/test_blueprints.py` |
| **Phase gate command** | `uv run mypy --follow-imports=silent . && uv run ruff check . && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/governance_followup_route_current_milestones.py tests/meta/governance_phase_history_current_milestones.py tests/meta/test_governance_milestone_archives.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_phase_history_runtime.py tests/meta/test_governance_phase_history_topology.py tests/meta/test_version_sync.py && uv run pytest -q` |
| **Estimated runtime** | `~15-120s` |

## Wave Structure

- **Wave 1:** `67-01` converge telemetry typed contracts and replay/exporter truth
- **Wave 2:** `67-02` normalize REST/auth/share contracts
- **Wave 3:** `67-03` and `67-04` close service-handler fixtures plus runtime/control wiring seams
- **Wave 4:** `67-05` and `67-06` harden toolchain/meta typing, freeze governance truth, and prove repo-wide gates

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 67-01-01 | 01 | 1 | TYP-19 | telemetry typed-contract convergence | `uv run pytest -q tests/core/telemetry/test_models.py tests/core/telemetry/test_sinks.py tests/core/telemetry/test_exporter.py` | ✅ passed |
| 67-02-01 | 02 | 2 | ARC-14 | REST/auth/share contract closure | `uv run pytest -q tests/core/api/test_api_status_service.py tests/core/api/test_api_transport_executor.py` | ✅ passed |
| 67-03-01 | 03 | 3 | HOT-23 | service-handler typed fixture closure | `uv run pytest -q tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py tests/core/test_init_service_handlers_device_resolution.py tests/core/test_init_service_handlers_schedules.py tests/core/test_init_service_handlers_sensor_feedback.py tests/services/test_services_schedule.py` | ✅ passed |
| 67-04-01 | 04 | 3 | HOT-23 | runtime/control wiring callable closure | `uv run pytest -q tests/core/test_control_plane.py tests/services/test_services_registry.py tests/platforms/test_update_background_tasks.py tests/core/test_init.py` | ✅ passed |
| 67-05-01 | 05 | 4 | TST-17 | toolchain/meta typed loader hardening | `uv run pytest -q tests/meta/toolchain_truth_ci_contract.py tests/meta/toolchain_truth_release_contract.py tests/meta/toolchain_truth_python_stack.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_version_sync.py tests/meta/test_blueprints.py` | ✅ passed |
| 67-06-01 | 06 | 4 | GOV-51, QLT-25 | governance freeze and repo-wide quality bundle | `uv run mypy --follow-imports=silent . && uv run ruff check . && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/governance_followup_route_current_milestones.py tests/meta/governance_phase_history_current_milestones.py tests/meta/test_governance_milestone_archives.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_phase_history_runtime.py tests/meta/test_governance_phase_history_topology.py tests/meta/test_version_sync.py && uv run pytest -q` | ✅ passed |

## Manual-Only Verifications

- 确认 typed-contract convergence 只沿既有 formal homes inward 收口，没有回流新的 compat shell、second root 或 broad mapping folklore。
- 确认 archived `v1.15` truth 只通过 `.planning/reviews/V1_15_EVIDENCE_INDEX.md` 作为 latest closeout pointer，对外 docs 与 current-story docs 不再宣称 active route。
- 确认 telemetry / REST / share / service-handler / toolchain 五条证据链在 milestone audit、evidence index、verification bundle 中能互相印证。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows telemetry -> REST/share -> fixtures/wiring -> toolchain/governance freeze.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded.

**Approval:** ✅ passed — validation assets, verification bundles, and archived milestone evidence are now consistent.
