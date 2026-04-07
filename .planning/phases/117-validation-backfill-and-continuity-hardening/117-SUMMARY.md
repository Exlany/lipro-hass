# Phase 117 Summary

## What changed
- 回补 `Phase 112 -> 114` 的 validation bundles，并把它们正式纳入 `v1.31` latest archived evidence chain。
- 修复 planning selector family、developer/runbook guidance、meta guards 与 gsd fast-path 之间的 continuity drift，把 current route 前推到 `active / phase 117 complete; closeout-ready (2026-03-31)`。
- 收紧 `status_fallback_support.py` / `rest_facade.py` / `anonymous_share/manager.py` 的 no-growth budgets 到 `655 / 360 / 359`，并为 `Phase 115 -> 117` 追加 verification matrix 合同。

## Why it changed
- `Phase 117` 的使命不是再开新功能，而是把已完成的 `v1.31` archived baseline 与 `v1.32` active route 之间的验证链、文档链、工具链与 handoff 链补成单一真相。
- 只有把 archived validation backfill 与 closeout-ready route truth 一次打通，`$gsd-next` 才会自然落到 milestone closeout，而不会反复回到 stale phase continuation。

## Verification
- `uv run pytest -q tests/meta/governance_milestone_archives_assets.py tests/meta/test_governance_promoted_phase_assets.py`
- `uv run pytest -q tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py`
- `uv run pytest -q tests/meta/test_phase113_hotspot_assurance_guards.py tests/meta/test_governance_release_continuity.py tests/meta/test_governance_release_docs.py tests/meta/test_version_sync.py`
- `uv run ruff check .planning/phases/112-formal-home-discoverability-and-governance-anchor-normalization/112-VALIDATION.md .planning/phases/113-hotspot-burn-down-and-changed-surface-assurance-hardening/113-VALIDATION.md .planning/phases/114-open-source-reachability-honesty-and-security-surface-normalization/114-VALIDATION.md tests/meta/governance_milestone_archives_assets.py tests/meta/governance_current_truth.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase113_hotspot_assurance_guards.py`

## Outcome
- `TST-39` / `GOV-73` 已完成；`v1.32` 当前只剩 `$gsd-complete-milestone v1.32` 这一条正式下一步。
