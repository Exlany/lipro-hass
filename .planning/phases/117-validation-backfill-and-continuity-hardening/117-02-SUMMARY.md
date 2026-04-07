# Plan 117-02 Summary

## What changed
- 把 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 的 machine-readable route contract、selector prose、progress 表格与 default next command 统一前推到 `active / phase 117 complete; closeout-ready (2026-03-31)`。
- 更新 `docs/developer_architecture.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 的当前路线说明，移除 `Phase 117 execution-ready` / `$gsd-execute-phase 117` 的 stale handoff wording。
- 重写 `tests/meta/governance_followup_route_current_milestones.py`，并更新 `tests/meta/governance_current_truth.py`、`tests/meta/test_governance_route_handoff_smoke.py` 与 `tests/meta/test_phase113_hotspot_assurance_guards.py`，让 meta truth、gsd fast-path 与热点 no-growth guard 一次对齐到 closeout-ready 真相。
- 在 `.planning/baseline/VERIFICATION_MATRIX.md` 追加 `Phase 115 -> 117` 合同块，并把 `status_fallback_support.py` / `rest_facade.py` / `anonymous_share/manager.py` budgets 对齐到 `655 / 360 / 359`。

## Why it changed
- `Phase 117` 之前最大的缺口已不是代码实现，而是 planning docs、developer guidance、runbook note、meta guards 与 gsd tooling 对当前 handoff 的叙事互相漂移。
- 若不把 route truth、stale budgets 与 verification contract 一并收口，closeout-ready 只会变成新的 conversation-only 故事线。

## Verification
- `uv run pytest -q tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py`
- `uv run pytest -q tests/meta/test_phase113_hotspot_assurance_guards.py tests/meta/test_governance_release_continuity.py tests/meta/test_governance_release_docs.py tests/meta/test_version_sync.py`
- `uv run ruff check tests/meta/governance_current_truth.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase113_hotspot_assurance_guards.py`

## Outcome
- active-route continuity story、machine-readable selector、maintainer guidance 与 hotspot no-growth guard 现共同收口到 `Phase 117 closeout-ready`，不再残留 `execution-ready` / `discuss-ready` 漂移。
