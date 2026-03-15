---
phase: 15
slug: support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-15
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for support feedback hardening, governance truth repair, and maintainability follow-through.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + ruff + mypy |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/core/test_developer_report.py tests/services/test_services_diagnostics.py tests/core/test_anonymous_share.py tests/core/test_report_builder.py` |
| **Wave gate commands** | `uv run ruff check .` + `uv run mypy` + `uv run python scripts/check_architecture_policy.py --check` + `uv run python scripts/check_file_matrix.py --check` |
| **Full suite command** | `uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing` |
| **Estimated runtime** | ~90-120 seconds |

---

## Sampling Rate

- **After every plan-local commit:** Run the targeted automated command listed for the active plan below.
- **After wave 1:** Re-run the quick support/developer-report suite.
- **After wave 2:** Run the wave gate commands plus `uv run pytest -q -x tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_firmware_support_manifest_repo_asset.py`.
- **After wave 3 / before `$gsd-verify-work`:** Run the wave gate commands, `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py`, and the full suite command.
- **Max feedback latency:** 120 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 15-01-00 | 15-01 | 1 | SPT-01 / HOT-03 | focused service + core contract regression | `uv run pytest -q tests/core/test_developer_report.py tests/services/test_services_diagnostics.py tests/core/test_anonymous_share.py tests/core/test_report_builder.py` | ✅ | ✅ green |
| 15-02-00 | 15-02 | 2 | GOV-13 | governance meta + script guards | `uv run pytest -q -x tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_firmware_support_manifest_repo_asset.py && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check` | ✅ | ✅ green |
| 15-03-00 | 15-03 | 2 | DOC-01 | docs/version sync guard | `uv run pytest -q -x tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_firmware_support_manifest_repo_asset.py && uv run python scripts/check_file_matrix.py --check` | ✅ | ✅ green |
| 15-04-00 | 15-04 | 2 | HOT-03 / TYP-03 | hotspot regression + typing | `uv run pytest -q tests/core/test_developer_report.py tests/services/test_services_diagnostics.py tests/core/test_anonymous_share.py tests/core/test_report_builder.py && uv run mypy` | ✅ | ✅ green |
| 15-05-00 | 15-05 | 3 | QLT-01 / RES-01 | tooling/residual arbitration + policy guard | `uv run ruff check . && uv run mypy && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py && uv run python scripts/coverage_diff.py coverage.json --minimum 95` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] Existing infrastructure is mapped to all Phase 15 requirements.
- [x] Placeholder verification row has been replaced by the real 5-plan / 3-wave map.
- [x] `uv run ruff check .`, `uv run mypy`, `uv run python scripts/check_architecture_policy.py --check`, and `uv run python scripts/check_file_matrix.py --check` are part of the wave-end gate.
- [x] Phase 15 currently treats `scripts/coverage_diff.py` as a coverage-floor gate with optional future baseline-diff mode; if Plan 15-05 keeps a real diff workflow or renames the command, `15-05-PLAN.md` and this file must be updated in the same wave.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Developer feedback copy accurately explains retained `iotName` and anonymized user labels | SPT-01 | User-facing wording quality is semantic, not just structural | Review `README.md`, `README_zh.md`, `services.yaml`, and translations for one consistent contract before merge |
| Governance phase/date/footer wording remains legible after guard hardening | GOV-13 | Human readability matters beyond regex pass/fail | Read updated `PROJECT.md`, `STATE.md`, `ROADMAP.md`, and `15-VALIDATION.md` together and confirm they tell one coherent story |
| README / README_zh / SUPPORT visibly front-load the Home Assistant version truth and HACS private-repo caveat | DOC-01 | Placement and emphasis affect user comprehension beyond keyword matching | Open the rendered first-screen sections of `README.md`, `README_zh.md`, and `SUPPORT.md` and confirm version/caveat language appears before troubleshooting details |

---

## Validation Sign-Off

- [x] All plans have an automated verify contract or explicit manual gate.
- [x] Wave 0 covers all Phase 15 requirements.
- [x] Sampling continuity exists across all 3 waves.
- [x] No watch-mode flags are present.
- [x] `nyquist_compliant: true` is set in frontmatter.
- [x] Execution evidence has been collected for all 5 plans.
- [x] Wave-end gates have passed on real code changes.

**Approval:** execution complete
