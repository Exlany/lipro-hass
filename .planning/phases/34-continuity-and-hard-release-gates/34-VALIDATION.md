---
phase: 34
slug: continuity-and-hard-release-gates
status: draft
nyquist_compliant: false
wave_0_complete: true
created: 2026-03-18
---

# Phase 34 — Validation Strategy

> Per-phase validation contract for release-hardening and continuity truth.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` |
| **Full suite command** | `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py` |
| **Estimated runtime** | `~5s` |

## Sampling Rate

- **After every task commit:** Run `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`
- **After every plan wave:** Run `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** `10s`

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 34-01-01 | 01 | 1 | GOV-29 | governance | `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py` | ✅ | ⬜ pending |
| 34-02-01 | 02 | 1 | QLT-08 | workflow/governance | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` | ✅ | ⬜ pending |
| 34-03-01 | 03 | 2 | GOV-29, QLT-08 | regression | `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py` | ✅ | ⬜ pending |

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Rendered release page wording stays truthful | QLT-08 | GitHub release UI is external to local test suite | Inspect release notes/checklist wording after workflow changes |
| Maintainer continuity drill reads as operationally usable | GOV-29 | Human review needed for clarity/completeness | Review runbook + SUPPORT + SECURITY + CODEOWNERS as one operator path |

## Validation Sign-Off

- [ ] All tasks have automated verify or existing Wave 0 coverage
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all referenced suites
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set when execution evidence is complete

**Approval:** pending
