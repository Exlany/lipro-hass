---
phase: 132-current-story-compression-and-archive-boundary-cleanup
plan: "02"
summary: true
---

# Plan 132-02 Summary

## Completed

- 新增 `tests/meta/governance_archive_history.py`，把历史 closeout / archive-transition literals 与 stale forbidden prose 从 `governance_current_truth.py` 中拆出，并保持兼容 re-export。
- 在 `tests/meta/governance_contract_helpers.py` 中新增共享 `assert_current_route_markers()` helper。
- 将 `Phase 101/102/103/104/105/107/108/109/110/123` predecessor guards 的重复 current-route marker loop 收敛为 shared helper 调用。

## Outcome

- current truth helper 继续聚焦 registry-backed live selector，而 archive-history literals 被压回更窄 home。
- predecessor guards 现在复用单一断言入口，减少 route/default-next 文案复制点。
