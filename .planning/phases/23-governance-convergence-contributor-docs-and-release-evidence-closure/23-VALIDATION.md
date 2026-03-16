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
| **Full suite command** | `uv run pytest -q && uv run ruff check . && uv run mypy` |
| **Estimated runtime** | ~180-300 seconds |

## Sampling Rate

- **After every task commit:** run the task-level command in the table below.
- **After every plan wave:** run the relevant combined phase slice.
- **Before `$gsd-verify-work`:** full suite must be green.
- **Max feedback latency:** 300 seconds.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 23-01-01 | 01 | 1 | GOV-16 | focused | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check` | ✅ | ⬜ pending |
| 23-02-01 | 02 | 1 | GOV-16 / GOV-17 | focused | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | ✅ | ⬜ pending |
| 23-03-01 | 03 | 2 | GOV-17 | focused | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | ✅ | ⬜ pending |

## Wave 0 Requirements

- [x] Existing repo infrastructure already covers this phase; no separate Wave 0 bootstrap is required.

## Manual-Only Verifications

- 复核 phase scope 与 `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` / `.planning/STATE.md` 的 requirement mapping 是否仍一致。
- 复核此 phase 是否没有偷跑前后相位职责。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] No watch-mode flags.
- [x] `nyquist_compliant: true` set in frontmatter.
- [ ] Execution evidence pending.

**Approval:** pending execution
