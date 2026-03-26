---
phase: 76
slug: governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation
status: passed
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-26
---

# Phase 76 Validation Contract

## Wave Order

1. `76-01` bootstrap contract block activation
2. `76-02` historical prose demotion and archive-seed determinism
3. `76-03` verification/file-matrix/release guard projection

## Per-Plan Focused Gates

- `76-01`
  - `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init new-milestone`
  - `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
  - Result: bootstrap smoke resolves `current_milestone = v1.21` and keeps `latest_completed_milestone = v1.20`
- `76-02`
  - `uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/test_phase72_runtime_bootstrap_route_guards.py tests/meta/test_phase75_governance_closeout_guards.py`
  - Result: historical milestone / archived-route guards remain green
- `76-03`
  - `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py`
  - Result: current-route, release-contract, and version-sync guards remain green

## Final Gate

- `uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase75_governance_closeout_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` → `66 passed in 1.13s`
- `uv run python scripts/check_file_matrix.py --check` → exit `0`
- `76-VERIFICATION.md` 已记录 `9/9 must-haves verified`

## Sign-off Checklist

- [x] bootstrap contract block 已成为 active-route / latest-archive 的唯一 parser-visible selector
- [x] historical milestone prose 只保留 archive/audit 身份，不再参与 current-route 选择
- [x] verification / release / version / file-matrix guards 已共同承认 `Phase 76 execution-ready`
- [x] focused CLI smoke 与 pytest gate 已形成闭环，无需人工兜底
- [x] `nyquist_compliant: true` 已在 frontmatter 固化
