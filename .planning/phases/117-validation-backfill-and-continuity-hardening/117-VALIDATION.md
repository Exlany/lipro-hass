---
phase: 117
slug: validation-backfill-and-continuity-hardening
nyquist_compliant: true
wave_0_complete: true
updated: 2026-04-01
---

# Phase 117 Validation Contract

## Wave Order

1. `117-01` backfill archived validation bundles and v1.31 evidence chain
2. `117-02` repair active-route continuity drift and tighten stale hotspot guards
3. `117-03` close phase117 with verification assets and freeze next-step routing

## Completion Expectations

- `117-01/02/03-SUMMARY.md`、`117-SUMMARY.md`、`117-VERIFICATION.md` 与 `117-VALIDATION.md` 共同冻结 `TST-39 / GOV-73` 的完成状态。
- `v1.31` archived evidence chain 显式接纳 `112 -> 114` validation bundles，active-route selector truth 回到 `Phase 117 complete; closeout-ready (2026-03-31)`。
- 本 phase 的 validated scope 只覆盖 archived validation backfill、continuity drift repair 与 closeout-ready route freeze；`Phase 118` 的 execution-ready/closeout-ready 切换不属于 `117` 自身已完成事实。

## GSD Route Evidence

- `117-SUMMARY.md` 已记录 validation backfill、selector continuity repair 与 tightened hotspot budgets 的完成事实。
- `117-VERIFICATION.md` 已保存 focused governance / archive / version / gsd-tools proof，并明确 `$gsd-next` 自然落到 milestone closeout。
- `Phase 118` 只是在当前 milestone 内继续承接后续内部债务，不回写 `117` 的 handoff verdict。

## Validation Commands

- `uv run pytest -q tests/meta/governance_milestone_archives_assets.py tests/meta/test_governance_promoted_phase_assets.py`
- `uv run pytest -q tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py`
- `uv run pytest -q tests/meta/test_phase113_hotspot_assurance_guards.py tests/meta/test_governance_release_continuity.py tests/meta/test_governance_release_docs.py tests/meta/test_version_sync.py`
- `uv run ruff check .planning/phases/112-formal-home-discoverability-and-governance-anchor-normalization/112-VALIDATION.md .planning/phases/113-hotspot-burn-down-and-changed-surface-assurance-hardening/113-VALIDATION.md .planning/phases/114-open-source-reachability-honesty-and-security-surface-normalization/114-VALIDATION.md tests/meta/governance_milestone_archives_assets.py tests/meta/governance_current_truth.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase113_hotspot_assurance_guards.py`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 117`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 117`

## Archive Truth Guardrail

- `Phase 117` 的 validation backfill 只修复 archived `112 -> 114` 证据链与 current-route continuity，不新增新的 product scope。
- validation contract 不得把 `Phase 118` 的 execution-ready route sync、hotspot decomposition 或后续 milestone closeout 反写成 `117` 自身已经完成的历史。
