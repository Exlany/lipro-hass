---
phase: 132-current-story-compression-and-archive-boundary-cleanup
plan: "03"
summary: true
---

# Plan 132-03 Summary

## Completed

- 将 `tests/meta/test_governance_route_handoff_smoke.py` 收窄到 docs/ledger sync 与 GSD fast-path smoke，不再兼任 recent promoted-asset family 覆盖。
- 将 `Phase 76/77/81/82/102/105` 的 promoted asset coverage 回流到 `tests/meta/test_governance_promoted_phase_assets.py`。
- 将 `tests/meta/governance_followup_route_current_milestones.py` 改为数据化的 requirement trace / coverage snapshot 断言，支持 `v1.38` current route。

## Outcome

- handoff smoke 回到真正 smoke 责任，promoted asset coverage 不再横跨两套治理测试重复展开。
- 当前 follow-up route guards 现在能稳定承认 `v1.38` 的 requirements / coverage truth。
