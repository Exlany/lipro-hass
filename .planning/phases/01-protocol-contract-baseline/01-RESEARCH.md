# Phase 01 Research: Protocol Contract Baseline

**Updated:** 2026-03-12
**Research mode:** closeout / boundary-baseline refinement
**Decision stance:** 不受历史成本约束，以“先冻结协议真相，再允许后续重构”为唯一判断标准

## Research Framing

Phase 01 的问题不是“要不要多测一点”，而是：

- 在进入 `LiproRestFacade` / `LiproProtocolFacade` 重构前，哪些协议边界必须先冻结？
- contract baseline 应该锁什么，不应该锁什么？
- Phase 01 的收尾产物除了 tests，还必须留下哪些治理资产，才能支撑后续 phase？

结论先行：

- **只锁 3 个高漂移入口是正确的，不应扩 scope**
- **contract baseline 必须锁 canonical output，而不是锁当前 `LiproClient` 结构**
- **Phase 01 的真正收尾不是“测试绿了”，而是“tests + immutable constraints + governance outputs + handoff” 全部成立**

## Why These Three Endpoints

### 1. `get_mqtt_config`

它最有代表性，因为同时具备：
- 多形态输入（`direct` / `wrapped`）
- 必须归一为单一 canonical output
- 会直接影响 Phase 2 / 2.5 的协议平面重构

因此它应继续作为 **Phase 01 的主样本**。

### 2. `get_city`

它代表 helper-level canonical mapping contract：
- 输入简单
- 输出清晰
- 适合作为“辅助协议 helper 不应泄漏 vendor noise”的样本

### 3. `query_user_cloud`

它代表 raw mapping helper contract：
- 与 diagnostics/support 面相关
- 对未来 external boundary formalization 有前置价值

## What Contract Baseline Should Lock

### Must lock

- 接受哪些输入形态
- 最终 canonical output 是什么
- 这些边界约束不依赖当前 `LiproClient` 继承结构
- fixtures 必须脱敏且可长期复用

### Must NOT lock

- 当前 `LiproClient` / mixin 的内部组织
- 临时 helper 装配顺序
- vendor payload 的全部噪音字段
- 任何敏感字面量、真实密钥、真实算法细节

## Immutable Constraints Handling

Phase 01 必须承认存在以下不可变约束：
- 固定密钥类别
- 固定算法类别
- 固定字段/包裹形态
- 固定 path/topic 约定

但此阶段的正确做法不是扩散细节，而是：
- 记录“约束类型 + 为什么不可变 + 后续归属到 protocol plane”
- 确保 fixtures / snapshots / summaries 全部脱敏
- 为 Phase 2 / 2.5 提供“要集中收口的清单”，而不是提前在全仓复制实现

## Snapshot Strategy

`snapshot` 在 Phase 01 的角色应从“API 示例集合”升级为：
- 与 contract baseline 对齐的结构观察面
- 用于判断 canonical output 是否漂移
- 不复制 vendor payload 原文

因此 `01-02` 的 snapshot 扩展应该：
- 直接包含 contract baseline 视角
- 保持样本少而精
- 继续服务于后续 façade 重构，而不是变成 payload 仓库

## Governance Closeout Requirement

Phase 01 收尾最容易被漏掉的不是测试，而是治理回写。最低应处理：

- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/phases/01-protocol-contract-baseline/01-IMMUTABLE-CONSTRAINTS.md`
- `.planning/phases/01-protocol-contract-baseline/01-01-SUMMARY.md`
- `.planning/phases/01-protocol-contract-baseline/01-02-SUMMARY.md`

注意：
- 某些治理产物即使“无新增变化”，也必须被明确检查并写明结果
- 否则 Phase 01 无法形成可交接 handoff

## Recommended Verification Matrix

### Minimum execution proof

```bash
uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/snapshots/test_api_snapshots.py -q
```

### Stronger closeout proof

```bash
uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_helper_modules.py tests/core/api/test_api_diagnostics_service.py tests/snapshots/test_api_snapshots.py -q
```

### Manual review proof

- `01-IMMUTABLE-CONSTRAINTS.md` 已说明约束类型且未泄漏敏感细节
- `VERIFICATION_MATRIX.md` 已确认 Phase 1 exit contract
- `FILE_MATRIX / RESIDUAL_LEDGER / KILL_LIST` 已检查并回写状态
- `01-01-SUMMARY.md` 与 `01-02-SUMMARY.md` 已明确 Phase 1 完成物与 Phase 2 / 1.5 handoff

## Recommendation

1. 保持 Phase 01 两计划结构，不新增 roadmap 级第三计划
2. `01-01` 继续代表“冻结边界真相”
3. `01-02` 明确升级为“snapshot + immutable constraints + governance closeout + handoff”
4. 在 `01-02` 中补齐 `PROT-02`，因为该计划负责把 baseline 从“测试资产”推进到“集中化台账 + 可交接阶段输出”

## Confidence

- **High**: 只锁 3 个入口仍是当前最优边界
- **High**: canonical output 优先于 vendor noise / current inheritance shape
- **High**: Phase 01 若缺治理收尾，后续 Phase 2 会建立在不完整基线上
- **Medium**: snapshot 的具体组织形式（专用 contract snapshot 还是并入现有 API snapshot）可在执行时由实现者裁决

## Sources

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/01-protocol-contract-baseline/01-CONTEXT.md`
- `.planning/phases/01-protocol-contract-baseline/01-01-PLAN.md`
- `.planning/phases/01-protocol-contract-baseline/01-02-PLAN.md`
- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/fixtures/api_contracts/README.md`
- `tests/snapshots/test_api_snapshots.py`
- `.planning/baseline/VERIFICATION_MATRIX.md`

