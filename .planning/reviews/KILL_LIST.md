# Kill List

## Candidate Removals (Initial)

- `_Client*Mixin` 聚合结构（Phase 2 替换后删除）
- 隐式散落的 compat wrappers（按调用方迁移结果逐一删除）
- 后续识别出的影子模块 / 测试专用生产残留（待各 phase 填充）

## Deletion Gate

删除前必须满足：
1. 下游消费者已迁移
2. contract / regression tests 通过
3. residual ledger 已关闭对应条目

## Phase 01 Closeout Review

- 已检查 kill list 与 Phase 01 baseline 产物的关系，本次**无新增删除项**。
- `_Client*Mixin` 与 compat wrappers 仍是后续 Phase 2 的主要清理对象；Phase 01 只补足它们必须遵守的 contract baseline。
- canonical snapshots、immutable constraints 与 phase summaries 属于治理资产，不进入删除候选。
