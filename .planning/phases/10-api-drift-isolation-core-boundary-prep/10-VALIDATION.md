---
phase: 10
slug: api-drift-isolation-core-boundary-prep
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-14
updated: 2026-03-14
---

# Phase 10 — Validation Strategy

> Executed validation record for API drift isolation and core-boundary prep.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + `ruff` |
| **Config file** | `pyproject.toml` |
| **Primary command** | `uv run ruff check custom_components/lipro tests` |
| **Targeted regression suite** | `uv run pytest -q -x tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/core/test_auth.py tests/core/test_init.py tests/flows/test_config_flow.py tests/meta/test_modularization_surfaces.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance_guards.py tests/meta/test_protocol_replay_assets.py tests/test_coordinator_public.py tests/core/test_diagnostics.py tests/core/test_system_health.py` |
| **Governance checks** | `uv run python scripts/check_architecture_policy.py --check` + `uv run python scripts/check_file_matrix.py --check` |

---

## Executed Verification Map

| Task ID | Plan | Wave | Requirement | Automated Command | Status |
|---------|------|------|-------------|-------------------|--------|
| `10-01-01` | `10-01` | 1 | `ISO-01` | `uv run pytest -q -x tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_replay_rest.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_coordinator_integration.py tests/core/api/test_api_status_endpoints.py tests/core/mqtt/test_protocol_replay_mqtt.py` | ✅ green |
| `10-02-01` | `10-02` | 2 | `ISO-02` | `uv run pytest -q -x tests/core/test_auth.py tests/core/test_init.py tests/flows/test_config_flow.py` | ✅ green |
| `10-03-01` | `10-03` | 3 | `ISO-03` | `uv run pytest -q -x tests/meta/test_modularization_surfaces.py tests/meta/test_public_surface_guards.py tests/test_coordinator_public.py tests/core/test_diagnostics.py tests/core/test_system_health.py` | ✅ green |
| `10-04-01` | `10-04` | 4 | `ISO-04` | `uv run ruff check custom_components/lipro tests` + targeted regression suite + governance checks | ✅ green |

---

## Wave 0 Requirements

- [x] `tests/core/api/test_protocol_contract_matrix.py` — protocol contract matrix baseline
- [x] `tests/core/api/test_protocol_replay_rest.py` — REST replay baseline
- [x] `tests/core/mqtt/test_protocol_replay_mqtt.py` — MQTT replay baseline
- [x] `tests/core/test_auth.py` — auth contract baseline
- [x] `tests/flows/test_config_flow.py` — flow regression baseline
- [x] `tests/meta/test_modularization_surfaces.py` — modularization guard baseline
- [x] `tests/meta/test_public_surface_guards.py` — public surface guard baseline
- [x] `tests/meta/test_dependency_guards.py` — dependency guard baseline
- [x] `tests/meta/test_governance_guards.py` — governance truth baseline
- [x] `tests/meta/test_protocol_replay_assets.py` — replay authority / asset baseline

---

## Manual Review Items

| Behavior | Requirement | Verdict |
|----------|-------------|---------|
| future host narrative remains boundary-first, not SDK-first | `ISO-03`, `ISO-04` | passed |
| `Coordinator` runtime-home wording stays outside host-neutral core truth | `ISO-03` | passed |
| governance docs explain what future CLI / other host may reuse | `ISO-04` | passed |

---

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies
- [x] Sampling continuity preserved across 4 waves
- [x] Governance guards are now part of the phase closeout chain
- [x] No watch-mode flags
- [x] `nyquist_compliant: true` kept in frontmatter

**Approval:** validation passed (2026-03-14)
