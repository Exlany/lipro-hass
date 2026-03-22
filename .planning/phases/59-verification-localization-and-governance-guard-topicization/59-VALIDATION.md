---
phase: 59
slug: verification-localization-and-governance-guard-topicization
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-22
---

# Phase 59 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `uv run pytest -q ...` focused suite verification + `uv run python scripts/check_file_matrix.py --check` |
| **Config file** | `pyproject.toml` |
| **Smoke command** | `uv run pytest -q tests/meta/test_public_surface_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_followup_route.py tests/core/test_device_refresh_parsing.py tests/core/test_device_refresh_filter.py tests/core/test_device_refresh_snapshot.py tests/core/test_device_refresh_runtime.py` |
| **Phase gate command** | `uv run pytest -q tests/meta/test_public_surface_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_followup_route.py tests/meta/test_dependency_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_version_sync.py tests/core/test_device_refresh_parsing.py tests/core/test_device_refresh_filter.py tests/core/test_device_refresh_snapshot.py tests/core/test_device_refresh_runtime.py && uv run python scripts/check_file_matrix.py --check` |
| **Estimated runtime** | `~10-90s` |

## Wave Structure

- **Wave 1:** `59-01` topicize governance/public-surface/follow-up-route megaguards
- **Wave 2:** `59-02` split `test_device_refresh.py`
- **Wave 3:** `59-03` freeze localized verification topology into docs / matrices / guards

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 59-01-01 | 01 | 1 | TST-11 | meta-guard topicization preserves semantics | `uv run pytest -q tests/meta/test_public_surface_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_followup_route.py` | ✅ passed |
| 59-02-01 | 02 | 2 | QLT-19 | device-refresh suite split preserves current behavior | `uv run pytest -q tests/core/test_device_refresh_parsing.py tests/core/test_device_refresh_filter.py tests/core/test_device_refresh_snapshot.py tests/core/test_device_refresh_runtime.py` | ✅ passed |
| 59-03-01 | 03 | 3 | GOV-43 | docs/matrix/current-story truth freeze stays coherent | `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_version_sync.py && uv run python scripts/check_file_matrix.py --check` | ✅ passed |

## Manual-Only Verifications

- 确认 thin-shell meta roots 只是收敛 truth-family imports，而不是把断言逻辑偷偷迁到新的 second governance story。
- 确认 `device_refresh` split 后 failure messages 与 file ownership 更易定位，而不是只把 giant bucket 平移成多个噪音文件。
- 确认 current-story docs、verification matrix 与 review truth 记录的是 runnable focused suites，而不是已经退场的 mega-suite 路径。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `guard topicization -> core mega split -> truth freeze`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded.

**Approval:** ✅ passed — execution evidence and focused verification topology are consistent.
