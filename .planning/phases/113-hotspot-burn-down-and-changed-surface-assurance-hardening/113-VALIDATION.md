---
phase: 113
slug: hotspot-burn-down-and-changed-surface-assurance-hardening
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-31
---

# Phase 113 Validation Contract

## Wave Order

1. `113-01` thin anonymous-share submit hotspot into local attempt and outcome helpers
2. `113-02` slim command-result stable export home without changing public contract
3. `113-03` freeze remaining hotspot budgets and wire phase113 focused assurance into default lint
4. `113-04` advance phase113 route truth and write final verification summary and audit assets

## Completion Expectations

- `113-01` 至 `113-04` 全部生成对应 `*-SUMMARY.md`，并在 `phase-plan-index 113` 中全部表现为 `has_summary = true`。
- `113-VERIFICATION.md` 对 `QLT-46` 给出 passed verdict；`113-AUDIT.md` 记录 hotspot assurance / changed-surface 结果。
- `tests/meta/test_phase113_hotspot_assurance_guards.py` 必须冻结 hotspot line budgets、helper import locality 与 default `scripts/lint` focused-assurance route。
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 需显式提升：
  - `113-01-SUMMARY.md`
  - `113-02-SUMMARY.md`
  - `113-03-SUMMARY.md`
  - `113-04-SUMMARY.md`
  - `113-SUMMARY.md`
  - `113-VERIFICATION.md`
  - `113-VALIDATION.md`
  - `113-AUDIT.md`

## GSD Route Evidence

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → expected `milestone = v1.31`, active route continues through Phase 113
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap get-phase 113` → expected requirement `QLT-46`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 113` → expected 4 plans, wave order `1 -> 1 -> 2 -> 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 113` → expected `plan_count = 4`
- historical next-step expectation after phase complete: 推进到 `Phase 114`

## Validation Commands

- `uv run pytest -q tests/core/test_share_client_submit.py tests/core/test_command_result.py`
- `uv run pytest -q tests/meta/test_phase113_hotspot_assurance_guards.py tests/meta/toolchain_truth_ci_contract.py`
- `uv run pytest -q tests/meta/test_governance_release_docs.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py`
- `uv run python scripts/check_file_matrix.py --check`

## Archive Truth Guardrail

- `Phase 113` tightened hotspots by inward split and guard freezing; it did not restore second roots or compat shells.
- active-route closeout truth remained `v1.31`-scoped while keeping `v1.30` as the latest archived baseline at execution time.
