---
phase: 16
slug: post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-15
---

# Phase 16 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + `ruff` + `mypy` + repo governance scripts |
| **Config file** | `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml` |
| **Quick run command** | `uv run ruff check . && uv run mypy && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` |
| **Full suite command** | `uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing` |
| **Estimated runtime** | ~120 seconds |

---

## Sampling Rate

- **After every plan-local commit:** Run the targeted automated command listed for the active plan below.
- **After every wave:** Run the quick run command.
- **Before `$gsd-verify-work`:** Run the full suite command plus `uv run pytest tests/snapshots/ -v`.
- **Max feedback latency:** 120 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 16-01-00 | 16-01 | 1 | GOV-14 | governance/meta/script guards | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check` | ✅ | ⬜ pending |
| 16-02-00 | 16-02 | 1 | QLT-02 / DOC-02 | config/tooling/docs guard | `uv run ruff check . && uv run mypy && uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py tests/meta/test_governance_guards.py && shellcheck scripts/develop` | ✅ | ⬜ pending |
| 16-03-00 | 16-03 | 2 | CTRL-06 / ERR-01 / TYP-04 | focused control/service regression + typing | `uv run pytest -q tests/core/test_control_plane.py tests/core/test_init.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/services/test_services_registry.py tests/services/test_service_resilience.py tests/flows/test_config_flow.py tests/services/test_services_share.py tests/services/test_services_diagnostics.py && uv run mypy` | ✅ | ⬜ pending |
| 16-04-00 | 16-04 | 2 | HOT-04 / TYP-04 / RES-02 / ERR-01 | protocol/runtime + typing | `uv run pytest -q tests/core/api tests/core/mqtt tests/core/coordinator tests/integration/test_mqtt_coordinator_integration.py && uv run mypy && uv run python scripts/check_architecture_policy.py --check` | ✅ | ⬜ pending |
| 16-05-00 | 16-05 | 3 | DOM-03 / OTA-01 | domain/entity/OTA focused regression | `uv run pytest -q tests/core/device tests/core/ota tests/entities tests/platforms/test_entity_behavior.py tests/platforms/test_update.py tests/platforms/test_firmware_update_entity_edges.py tests/platforms/test_entity_base.py` | ✅ | ⬜ pending |
| 16-06-00 | 16-06 | 3 | TST-01 / DOC-02 | test-layer + DX docs/runbook regression | `uv run pytest -q tests/platforms tests/flows/test_config_flow.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py && uv run python scripts/check_file_matrix.py --check` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] Existing infrastructure already covers governance/meta checks.
- [x] Existing focused suites already cover control/service, protocol/runtime, device/OTA, and platform paths.
- [x] No new test framework or watch-mode tooling is required.
- [x] `uv run ruff check .`, `uv run mypy`, `uv run python scripts/check_architecture_policy.py --check`, and `uv run python scripts/check_file_matrix.py --check` are part of the wave-end gate.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Active governance docs tell one coherent Phase 16 story | GOV-14 | Human readability matters beyond regex/AST pass | Read `AGENTS.md`, `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, and `.planning/reviews/KILL_LIST.md` together and confirm there is no contradictory residual or phase-status wording |
| Toolchain truth is understandable to contributors | QLT-02 / DOC-02 | Users need one clear mental model, not just green CI | Review `pyproject.toml`, `.pre-commit-config.yaml`, `.devcontainer.json`, `CONTRIBUTING.md`, and any new runbook/troubleshooting docs together |
| DX guidance matches real local maintenance flow | DOC-02 | Placement and clarity are user-facing quality, not just structural data | Walk through `scripts/develop`, troubleshooting docs, and maintainer runbook from a fresh-reader perspective |

---

## Validation Sign-Off

- [x] All requirement groups have an automated verify path or explicit manual gate.
- [x] Sampling continuity exists across all three waves.
- [x] Wave 0 uses existing infrastructure; no missing framework setup remains.
- [x] No watch-mode flags are present.
- [x] `nyquist_compliant: true` is set in frontmatter.
- [ ] Plan-local execution evidence has not yet been collected.

**Approval:** pending
