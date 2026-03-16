---
phase: 23
slug: governance-convergence-contributor-docs-and-release-evidence-closure
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-16
---

# Phase 23 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + ruff + mypy |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q` |
| **Phase gate command** | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` |
| **Estimated runtime** | ~180-300 seconds |

## Wave Structure

- **Wave 1:** `23-01` —— long-term governance truth / ledgers sync
- **Wave 2:** `23-02` —— contributor/public entry docs and templates sync
- **Wave 3:** `23-03` —— release evidence index and workflow-gate alignment

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 23-01-01 | 01 | 1 | GOV-16 | focused | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check` | ⬜ pending |
| 23-01-02 | 01 | 1 | GOV-16 | focused | `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py` | ⬜ pending |
| 23-02-01 | 02 | 2 | GOV-16 / GOV-17 | focused | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | ⬜ pending |
| 23-03-01 | 03 | 3 | GOV-17 | focused | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py` | ⬜ pending |
| 23-03-02 | 03 | 3 | GOV-17 | focused | `uv run python scripts/check_file_matrix.py --check` | ⬜ pending |

## Wave Commands

### Wave 1 Gate

- `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py`

### Wave 2 Gate

- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`
- `uv run ruff check .`

### Wave 3 Gate

- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py`
- `uv run ruff check .`
- `uv run mypy`

## Manual-Only Verifications

- 确认 baseline/reviews/roadmap-state 真源先于 README / SUPPORT / SECURITY / templates 被更新。
- 确认 `Phase 23` 没有偷跑 `Phase 24` 的 final audit / archive / handoff 决策。
- 确认 `V1_2_EVIDENCE_INDEX.md`（或等价单一 pointer）成为 maintainer release flow 与 governance tests 的共同引用目标。
- 若 workflow 无需修改，也必须在 runbook / guards / evidence index 中明确说明“为何无需改 workflow”。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `truth -> docs -> release evidence`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [ ] Execution evidence pending.

**Approval:** ready for execution after plan verification
