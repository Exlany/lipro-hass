# Authority Matrix

**Purpose:** 定义文档、fixtures、generated、implementation 的权威来源与同步方向，避免多口径漂移。
**Status:** Formal baseline asset (`BASE-01` authority truth source)
**Updated:** 2026-03-12

## Formal Role

- 本文件是 docs / fixtures / generated / implementation 同步方向的正式 baseline 真源。
- 本阶段只锁定“谁定义、向哪里同步、谁不能反向改写”，不在这里提前展开 `Phase 2.6` 的外部边界 family inventory。
- 后续 phase 只能扩展 authority families 或补充验证证据，不能绕开本文件另造平行真相。

## Authority Sources

| Artifact Family | Authority Source | Sync Direction | Notes |
|-----------------|------------------|----------------|-------|
| 终态架构原则 | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` | north-star -> planning/docs/code review | 终态判断真源 |
| 基准资产 | `.planning/baseline/*.md` | baseline -> phase design / review / verification | downstream phase docs 只能解释或扩展，不能反向改写 |
| 项目目标与阶段路线 | `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` | planning -> phase execution | GSD 执行真源 |
| 当前工程落地说明 | `docs/developer_architecture.md` | codebase/planning -> developer docs | 当前态解释真源，不凌驾于 baseline 之上 |
| 文件治理状态 | `.planning/reviews/FILE_MATRIX.md` | execution -> governance review | 最终需提升到 file-level |
| 残留状态 | `.planning/reviews/RESIDUAL_LEDGER.md` | execution -> cleanup / audit | compat/residual 真源 |
| 删除裁决 | `.planning/reviews/KILL_LIST.md` | execution -> cleanup / audit | kill decision 真源 |
| 协议样例 / fixtures | `tests/fixtures/api_contracts/` | baseline/contracts -> fixtures -> contract tests | 必须脱敏，禁止真实敏感数据 |
| generated artifacts | owning baseline doc + fixture/snapshot contract + normalization rule | baseline/contracts/fixtures -> generated expectation -> docs/implementation review | 先锁同步方向；具体 external-boundary family 在后续 phase 展开 |
| 测试期望 | `tests/**` | requirements/baseline -> implementation | 测试需跟随正式结构迁移 |
| 实现代码 | `custom_components/lipro/**` | north-star + planning -> code | 不是架构真源，只是实现载体 |

## Conflict Resolution

若出现口径冲突，优先级如下：

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/baseline/*.md`
3. `.planning/PROJECT.md` / `.planning/ROADMAP.md` / `.planning/STATE.md`
4. `docs/developer_architecture.md`
5. tests / fixtures / implementation comments

## Synchronization Rule

按 artifact family 的正式同步方向执行：

- **docs**：`north-star -> baseline -> phase docs / developer docs`，实现与测试只能触发回写需求，不能静默改写文档真相。
- **fixtures**：`baseline/contracts -> fixture family -> owning tests`，fixture 漂移必须伴随 baseline 或 summary 解释。
- **generated**：`baseline/contracts + normalization rule + fixture/snapshot evidence -> generated artifact expectation`，禁止由实现临时输出反向定义真相。
- **implementation**：`north-star + baseline + tests -> code`，实现是载体，不是 authority source。

出现以下任一情况时，必须同步检查 authority matrix：

- 新增或删除正式 public surface
- phase 引入新的 fixture / generated artifact / shadow doc
- 旧 compat shell 被降级或删除
- 文档与实现出现双口径风险

---
*Used by: external boundary formalization, docs hygiene, and audit arbitration*
