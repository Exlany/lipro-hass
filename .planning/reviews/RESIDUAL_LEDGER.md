# Residual Ledger

## Active Residual Families

| Family | Current example | Owner phase | Exit condition |
|--------|------------------|-------------|----------------|
| API compat wrappers | `LiproClient` 中 legacy-style list payload wrappers | Phase 2 | façade / collaborators 稳定且调用方迁移完成 |
| API mixin inheritance | `_ClientTransportMixin`、`_ClientEndpointsMixin` | Phase 2 | 显式组合对象替代并回归通过 |
| Control-plane scatter | diagnostics / system_health / service wiring 分散 | Phase 3 | control plane public surface 收口 |
| Capability duplication | domain / entity / platform 多处表达 | Phase 4 | capability registry 成为单一真源 |

## Rules

- 新发现的残留必须登记，不能只在对话中提到
- 任何 residual 若进入第二个 phase 仍未收敛，必须解释原因

## Phase 01 Closeout Review

- 已复核当前 residual families 与 Phase 01 baseline 的关系：本阶段只锁定 protocol boundary truth，不试图提前消除 residual。
- 本次**无新增 residual family**；canonical snapshots 与 immutable constraints 没有引入新的桥接层或临时兼容结构。
- `API compat wrappers` 与 `API mixin inheritance` 继续由 Phase 2 负责清理；Phase 01 仅为其提供不可漂移的 contract 输入边界。
