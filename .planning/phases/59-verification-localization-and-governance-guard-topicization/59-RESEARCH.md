# Phase 59 Research

## Why This Phase Exists

`Phase 58` 已确认当前主风险更多是 **verification maintainability**，而不是 formal-root correctness。当前几份 megaguards / megasuites 虽然大体正确，但它们把多个 truth family 混在一起，导致：

- failure localization 成本偏高；
- follow-up refactor 很难做到最小验证集；
- current-story docs 难以诚实描述“应该跑哪组最小充分守卫”。

## Current High-Signal Observations

1. **Public-surface and governance route guards are semantically overloaded**
   - `test_public_surface_guards.py` 同时承载 public surface、naming、review ledger、phase-note truth。
   - `test_governance_phase_history.py` 与 `test_governance_followup_route.py` 同时承担历史证明、当前路线与下一步仲裁。

2. **`test_device_refresh.py` mixes three distinct concerns**
   - filter parsing / normalization
   - inclusion / exclusion semantics
   - runtime refresh / stale-device / reset behavior

3. **Best next move is topology honesty, not new architecture**
   - 先拆验证半径，后续 `Phase 60+` 的 tooling / production refinement 才更容易做最小验证。

## Recommended Plan Shape

- `59-01`：治理 / public-surface megaguards topicization
- `59-02`：`test_device_refresh.py` topicization
- `59-03`：docs / matrix / follow-up truth freeze

## Verification Philosophy

- 验证重点是：新 suite topology 可运行、coverage intent 未丢失、current-story docs 明确记录 focused commands。
- 不为 split 发明新的 business behavior tests；优先重组现有 truth 并保持语义稳定。
