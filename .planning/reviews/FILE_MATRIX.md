# File Matrix

**Python files total:** 378

## Phase Ownership by Cluster

| Cluster | Python files | Primary phase | Status |
|---------|--------------|---------------|--------|
| `custom_components/lipro/core/api` | 33 | Phase 2 | Planning |
| `tests/core/api` | 14 | Phase 2 | Planning |
| `tests/snapshots` | 5 | Phase 1 / 2 / 6 | Phase 01 baseline locked |
| `custom_components/lipro/core/coordinator` | 56 | Phase 5 | Pending |
| `custom_components/lipro/core/device` | 23 | Phase 4 | Pending |
| `custom_components/lipro/core/mqtt` | 12 | Phase 2 / 5 / 6 | Pending |
| `custom_components/lipro/services` | 11 | Phase 3 | Pending |
| `custom_components/lipro/flow` + entry files | 8 | Phase 3 | Pending |
| `custom_components/lipro/entities` + platform modules | 13 | Phase 4 | Pending |
| Remaining helpers / scripts / tests | remainder | Cross-cutting | Pending |

## Current Focus Slice

### Phase 2 Slice

- `custom_components/lipro/core/api/**/*.py`
- `tests/core/api/**/*.py`
- `tests/snapshots/test_api_snapshots.py`
- `tests/flows/test_config_flow.py`
- `tests/test_coordinator_runtime.py`
- `tests/platforms/test_update_task_callback.py`

## Classification Vocabulary

- `保留`：符合北极星终态，仅做轻微整理
- `重构`：保留职责，但必须按新架构重写内部实现
- `迁移适配`：阶段性桥接层，必须登记删除条件
- `删除`：不进入终态，待消费者清零后移除

## Phase 01 Closeout Review

- 已检查 `tests/fixtures/api_contracts/**`、`tests/core/api/test_protocol_contract_matrix.py` 与 `tests/snapshots/test_api_snapshots.py`，确认它们构成 Phase 01 的 baseline 资产面。
- 本次未调整文件归属：协议实现与大多数 API 测试仍归后续 Phase 2 收口；Phase 01 只负责锁定 contract baseline。
- `tests/snapshots` 状态更新为 `Phase 01 baseline locked`，表示已有 canonical contract 观察面，但后续 Phase 2 / 6 仍可在同一承载面继续扩展。
