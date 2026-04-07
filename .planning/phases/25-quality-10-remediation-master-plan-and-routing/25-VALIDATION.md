---
phase: 25
slug: quality-10-remediation-master-plan-and-routing
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-17
---

# Phase 25 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + governance scripts + roadmap parser |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` |
| **Phase gate command** | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` |
| **Estimated runtime** | ~10-40 seconds |

## Wave Structure

- **Wave 1:** `25-01` —— final review -> routed requirement ledger
- **Wave 2:** `25-02` —— route-map boundaries / ordering / success gates
- **Wave 3:** `25-03` —— active truth + handoff sync
- **Wave 4:** `25-04` —— validation freeze / no-return rules / next-command handoff

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 25-01-01 | 01 | 1 | GOV-19 | focused | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | ✅ passed |
| 25-02-01 | 02 | 2 | GOV-19 | focused | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check` | ✅ passed |
| 25-03-01 | 03 | 3 | GOV-19 | focused | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` | ✅ passed |
| 25-04-01 | 04 | 4 | GOV-19 | final | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` | ✅ passed |

## Wave Commands

### Wave 1 Gate

- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`

### Wave 2 Gate

- `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check`

### Wave 3 Gate

- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`

### Wave 4 Gate

- `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`

## Manual-Only Verifications

- 确认终极复审中的全部问题都已被映射到 `25.1 / 25.2 / 26 / 27` 或被显式排除。
- 确认 `MD5` 登录哈希的“协议约束而非仓库债务”裁决已进入真源。
- 确认 next command 已从旧版单 tranche `Phase 25` 切到 `Phase 25.1` planning 入口。
- 确认 `Phase 25` 没有偷跑 child-phase 实现，而只是完成总路线图与 no-return rules。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently for Python tooling.
- [x] Wave order follows `route -> boundaries -> truth sync -> freeze`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded in `25-VERIFICATION.md`.

**Approval:** ready for execution after plan verification
