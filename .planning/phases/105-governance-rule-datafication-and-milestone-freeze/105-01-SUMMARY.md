---
requirements-completed: [GOV-69]
---

# 105-01 Summary

- 新增 `tests/meta/governance_followup_route_specs.py`，把 planning-doc snapshot、requirement trace row 与 coverage arithmetic 抽成共享 table-driven builder。
- `governance_followup_route_current_milestones.py`、`governance_followup_route_closeouts.py`、`governance_followup_route_continuation.py` 改为复用共享 spec builders，不再散落手写 `Current mapped/complete/pending` 与 requirement-row literals。
- `tests/meta/governance_current_truth.py` 把测试库存计数改为 derivation，并为 `Phase 105` focused guard / completed-phase progress 提供单一 current-route truth。
