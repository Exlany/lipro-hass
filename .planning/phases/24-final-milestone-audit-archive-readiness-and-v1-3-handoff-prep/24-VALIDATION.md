---
phase: 24
slug: final-milestone-audit-archive-readiness-and-v1-3-handoff-prep
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-16
---

# Phase 24 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + ruff + mypy |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q` |
| **Phase gate command** | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` |
| **Estimated runtime** | ~180-300 seconds |

## Wave Structure

- **Wave 1:** `24-01` —— final repo audit and residual arbitration
- **Wave 2:** `24-02` —— milestone audit and archive-ready bundle
- **Wave 3:** `24-03` —— v1.3 handoff and lifecycle transition truth

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 24-01-01 | 01 | 1 | GOV-18 | focused | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check` | ⬜ pending |
| 24-01-02 | 01 | 1 | GOV-18 | focused | `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | ⬜ pending |
| 24-02-01 | 02 | 2 | GOV-18 | focused | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | ⬜ pending |
| 24-03-01 | 03 | 3 | GOV-18 | focused | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py` | ⬜ pending |
| 24-03-02 | 03 | 3 | GOV-18 | final | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py && uv run ruff check . && uv run mypy` | ⬜ pending |

## Wave Commands

### Wave 1 Gate

- `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`

### Wave 2 Gate

- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`
- `uv run ruff check .`

### Wave 3 Gate

- `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`
- `uv run ruff check .`
- `uv run mypy`

## Manual-Only Verifications

- 确认 final repo audit 对所有 remaining item 给出 close / retain / defer disposition，而不是把 unresolved debt 留给口头说明。
- 确认 `v1.2-MILESTONE-AUDIT.md`、`V1_2_EVIDENCE_INDEX.md`、`MILESTONES.md` 与 `v1.3-HANDOFF.md` 之间相互引用、口径一致。
- 确认 `Phase 24` 不再修改 contributor docs / release workflow narrative 本体，除非为了 closeout truth 做最小必要同步。
- 确认 `archive-ready` 与“立即执行 archival”被清楚区分。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `audit -> archive-ready bundle -> handoff`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [ ] Execution evidence pending.

**Approval:** ready for execution after plan verification
