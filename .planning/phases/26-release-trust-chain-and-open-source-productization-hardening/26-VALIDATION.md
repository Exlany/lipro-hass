---
phase: 26
slug: release-trust-chain-and-open-source-productization-hardening
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-17
---

# Phase 26 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest meta guards + workflow/docs static truth |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/meta/test_install_sh_guards.py tests/meta/test_version_sync.py` |
| **Phase gate command** | `uv run pytest -q tests/meta/test_install_sh_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` |
| **Estimated runtime** | ~15-60 seconds |

## Wave Structure

- **Wave 1:** `26-01` —— installer trust chain + supported shell story
- **Wave 2:** `26-02` —— release workflow assets + runbook hardening
- **Wave 3:** `26-03` —— support/security/contributor/productization sync
- **Wave 4:** `26-04` —— closeout truth and verification evidence

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 26-01-01 | 01 | 1 | GOV-21, QLT-03 | focused | `uv run pytest -q tests/meta/test_install_sh_guards.py` | ✅ passed |
| 26-01-02 | 01 | 1 | GOV-21, QLT-03 | focused | `uv run pytest -q tests/meta/test_governance_guards.py -k "installer or latest or release"` | ✅ passed |
| 26-02-01 | 02 | 2 | GOV-21 | focused | `uv run pytest -q tests/meta/test_governance_guards.py -k "release or workflow" tests/meta/test_toolchain_truth.py` | ✅ passed |
| 26-02-02 | 02 | 2 | GOV-21 | focused | `uv run pytest -q tests/meta/test_version_sync.py tests/meta/test_governance_guards.py -k "runbook or supply_chain"` | ✅ passed |
| 26-03-01 | 03 | 3 | GOV-21, QLT-03 | focused | `uv run pytest -q tests/meta/test_governance_guards.py -k "support or security or codeowners or readme"` | ✅ passed |
| 26-03-02 | 03 | 3 | GOV-21, QLT-03 | focused | `uv run pytest -q tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` | ✅ passed |
| 26-04-01 | 04 | 4 | GOV-21, QLT-03 | focused | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` | ✅ passed |
| 26-04-02 | 04 | 4 | GOV-21, QLT-03 | final | `uv run pytest -q tests/meta/test_install_sh_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` | ✅ passed |

## Manual-Only Verifications

- 确认默认支持故事线已从远程 `wget | bash` 转向 verified release assets。
- 确认 runbook 对 attestation / SBOM / installer assets 的要求已成为当前 posture，而不是 defer note。
- 确认单维护者现实被诚实记录，而不是被伪装成已解决的冗余。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `installer -> release tail -> public docs -> closeout`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded in `26-VERIFICATION.md`.

**Approval:** phase executed and verified

## Execution Evidence

- `56 passed` on installer/workflow/governance/version/toolchain meta gate
- `shellcheck not installed; skipped` on local environment (non-blocking)
