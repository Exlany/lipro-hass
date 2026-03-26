---
phase: 76
slug: governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation
status: draft
nyquist_compliant: false
wave_0_complete: true
created: 2026-03-26
---

# Phase 76 — Validation Strategy

> Per-phase validation contract for bootstrap-truth and governance-route planning.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + repo governance scripts + GSD smoke CLI |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/test_governance_closeout_guards.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase71_hotspot_route_guards.py tests/meta/test_phase72_runtime_bootstrap_route_guards.py tests/meta/test_phase75_governance_closeout_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` |
| **Full suite command** | `uv run ruff check . && uv run mypy --follow-imports=silent . && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q` |
| **Estimated runtime** | ~75 seconds |

---

## Sampling Rate

- **After every task commit:** Run the relevant focused governance gate and required GSD smoke command
- **After every plan wave:** Run the quick run command plus `uv run python scripts/check_file_matrix.py --check`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 90 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 76-01-01 | 01 | 1 | GOV-57 | smoke | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init new-milestone && node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` | ✅ | ⬜ pending |
| 76-02-01 | 02 | 2 | ARC-20 | focused | `uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/test_phase72_runtime_bootstrap_route_guards.py tests/meta/test_phase75_governance_closeout_guards.py` | ✅ | ⬜ pending |
| 76-03-01 | 03 | 3 | GOV-57 | focused | `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] Existing governance/meta infrastructure already covers this phase
- [x] Existing GSD smoke CLI commands can be used directly; no new harness required

---

## Manual-Only Verifications

All phase behaviors have automated or CLI-checkable verification.

---

## Validation Sign-Off

- [ ] All tasks have focused verify commands or shared gate dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all required infrastructure
- [x] No watch-mode flags
- [ ] Feedback latency < 90s in actual execution
- [ ] `nyquist_compliant: true` set in frontmatter after execution validation

**Approval:** pending
