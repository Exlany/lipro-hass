---
phase: 51
slug: continuity-automation-governance-registry-projection-and-release-rehearsal-hardening
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-21
---

# Phase 51 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + governance/meta guards |
| **Config file** | `pyproject.toml` |
| **Smoke command** | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_toolchain_truth.py` |
| **Quick run command** | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_followup_route.py tests/meta/test_version_sync.py` |
| **Phase gate command** | `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` |
| **Estimated runtime** | `~15-40s` |

## Wave Structure

- **Wave 1:** `51-01` continuity drill / maintainer-unavailable contract
- **Wave 2:** `51-02` governance-registry projection + lower-drift contributor guidance
- **Wave 3:** `51-03` verify-only release rehearsal + change-type validation guidance

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 51-01-01 | 01 | 1 | GOV-38 | continuity / custody / delegate truth | `uv run pytest -q tests/meta/test_governance_release_contract.py` | ✅ passed |
| 51-02-01 | 02 | 2 | GOV-39 | registry projection / tooling truth | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` | ✅ passed |
| 51-03-01 | 03 | 3 | QLT-18 | release rehearsal + planning truth | `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` | ✅ passed |

## Wave Commands

### Wave 1 Gate
- `uv run pytest -q tests/meta/test_governance_release_contract.py`

### Wave 2 Gate
- `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py`

### Wave 3 Gate
- `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`

## Manual-Only Verifications

- continuity drill 仍保持 single-maintainer honesty，不引入 hidden delegate / second maintainer story；
- governance registry projection 降低手工同步成本，但没有让 registry 反向变成第二 public truth；
- verify-only / non-publish rehearsal 确实不会发布正式 release 产物；
- `v1.6` shipped baseline 与 `v1.7` closeout truth 未被 `v1.8` planning overwrite。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `continuity -> projection -> rehearsal hardening`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded.

**Approval:** execution verified and promoted.
