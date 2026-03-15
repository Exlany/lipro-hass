---
phase: 17
slug: final-residual-retirement-typed-contract-tightening-and-milestone-closeout
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-15
---

# Phase 17 — Validation Strategy

> Per-phase validation contract for final residual retirement and milestone closeout.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + `ruff` + `mypy` + repo governance scripts |
| **Config file** | `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml` |
| **Quick run command** | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_evidence_pack_authority.py` |
| **Residual audit command set** | `rg -n 'except Exception|type: ignore' custom_components/lipro && rg -n '\bAny\b' custom_components/lipro || true` |
| **Full suite command** | `uv run ruff check . && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run mypy && uv run pytest -q` |
| **Estimated runtime** | ~120 seconds |

---

## Sampling Rate

- **After every plan-local change:** Run the targeted command listed for the active plan below.
- **After every wave:** Run the quick run command plus the residual audit command set.
- **Before phase closeout sign-off:** Run the full suite command and reconcile output with `RESIDUAL_LEDGER.md` / `KILL_LIST.md`.
- **Max feedback latency:** 120 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 17-01-00 | 17-01 | 1 | RES-03 | focused API regression + typing | `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_helper_modules.py && uv run mypy custom_components/lipro/core/api && uv run ruff check custom_components/lipro/core/api tests/core/api` | ✅ | ✅ green |
| 17-02-00 | 17-02 | 2 | TYP-05 | auth/init/power typed-contract regression | `uv run pytest -q tests/core/test_init.py tests/core/test_auth.py tests/core/api/test_api.py tests/core/api/test_helper_modules.py tests/core/test_outlet_power_runtime.py && uv run mypy custom_components/lipro/entry_auth.py custom_components/lipro/core/auth/manager.py custom_components/lipro/core/api/power_service.py custom_components/lipro/core/protocol custom_components/lipro/core/coordinator/runtime/outlet_power_runtime.py` | ✅ | ✅ green |
| 17-03-00 | 17-03 | 2 | MQT-01 | mqtt locality + transport regression | `uv run pytest -q tests/core/mqtt tests/core/coordinator/runtime/test_mqtt_runtime.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py && uv run mypy custom_components/lipro/core/mqtt custom_components/lipro/core/protocol` | ✅ | ✅ green |
| 17-04-00 | 17-04 | 3 | GOV-15 | governance sync + final repo audit | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_evidence_pack_authority.py && uv run ruff check . && uv run mypy && uv run pytest -q` | ✅ | ✅ green |

---

## Automated UAT Checklist

- [x] Every requirement maps to at least one automated gate.
- [x] Every wave ends with governance-backed proof, not just local green tests.
- [x] Final closeout includes residual recount and no-silent-defer arbitration.
- [x] `nyquist_compliant: true` is set in frontmatter.
- [x] Final closeout proof includes runnable whole-repo evidence, not just focused slices.

**Approval:** passed

---

## Final Closeout Evidence

- Final rerun on `2026-03-15` completed with one coherent gate: `uv run ruff check .`, `uv run python scripts/check_architecture_policy.py --check`, `uv run python scripts/check_file_matrix.py --check`, `uv run mypy`, `uv run pytest -q`.
- Result summary: `ruff` ✅, governance scripts ✅, `mypy` ✅ (`Success: no issues found in 440 source files`), full `pytest` ✅ (`2196 passed in 38.32s`).
- Focused Phase 17 verification slices: API/auth/power `383 passed in 5.19s`, MQTT/locality `174 passed in 2.51s`, governance/meta `59 passed in 4.23s`.
- Final repo audit recount for `custom_components/lipro`: `Any=0`, `except Exception=36`, `type: ignore=1`.
- Remaining debt is restricted to explicit de-scope / out-of-scope items already registered in `.planning/v1.1-MILESTONE-AUDIT.md`; no new silent defer surfaced during closeout.
