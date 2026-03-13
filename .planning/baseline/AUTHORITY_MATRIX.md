# Authority Matrix

**Purpose:** 定义文档、fixtures、generated、implementation 的权威来源与同步方向，避免多口径漂移。
**Status:** Formal baseline asset (`BASE-01` authority truth source)
**Updated:** 2026-03-13

## Formal Role

- 本文件是 docs / fixtures / generated / implementation 同步方向的正式 baseline 真源。
- `Phase 2.6` 起，external boundary family 不能再只靠 implementation 口头约定；必须声明 authority source、fixture family 与 drift guard。
- `Phase 7.2` 起，architecture enforcement 也必须遵守同一 authority order：north-star / baseline 先裁决，再由 helper / script / tests / CI 执行。
- 后续 phase 只能扩展 authority families 或补充验证证据，不能绕开本文件另造平行真相。

## Authority Sources

| Artifact Family | Authority Source | Sync Direction | Notes |
|-----------------|------------------|----------------|-------|
| 终态架构原则 | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` | north-star -> planning/docs/code review | 终态判断真源 |
| 基准资产 | `.planning/baseline/*.md` | baseline -> phase design / review / verification | downstream phase docs 只能解释或扩展，不能反向改写 |
| architecture enforcement policy | `.planning/baseline/ARCHITECTURE_POLICY.md` | baseline -> helpers / scripts / meta guards / CI | `Phase 7.2` 起的执行型 policy truth，不得被 tests/scripts 倒逼改写 |
| 项目目标与阶段路线 | `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` | planning -> phase execution | GSD 执行真源 |
| 当前工程落地说明 | `docs/developer_architecture.md` | codebase/planning -> developer docs | 当前态解释真源，不凌驾于 baseline 之上 |
| 文件治理状态 | `.planning/reviews/FILE_MATRIX.md` | execution -> governance review | 最终需提升到 file-level |
| 残留状态 | `.planning/reviews/RESIDUAL_LEDGER.md` | execution -> cleanup / audit | compat/residual 真源 |
| 删除裁决 | `.planning/reviews/KILL_LIST.md` | execution -> cleanup / audit | kill decision 真源 |
| 协议样例 / fixtures | `tests/fixtures/api_contracts/` | baseline/contracts -> fixtures -> contract tests | 必须脱敏，禁止真实敏感数据 |
| protocol boundary decoder families | `.planning/phases/07.1-protocol-boundary-schema-decoder/07.1-01-BOUNDARY-INVENTORY.md`, `custom_components/lipro/core/protocol/boundary/`, `tests/fixtures/protocol_boundary/`, `tests/fixtures/api_contracts/` | boundary inventory -> schema registry -> decoder families -> replay-ready fixtures -> protocol tests / telemetry / replay assets | `Phase 7.1` 开始，REST/MQTT decode authority 必须登记到单一 boundary family home；已存在 authority 的 REST family 复用 `api_contracts`，不得复制第二真源 |
| runtime telemetry exporter family | `custom_components/lipro/core/telemetry/`, `custom_components/lipro/control/telemetry_surface.py`, `.planning/phases/07.3-runtime-telemetry-exporter/07.3-VALIDATION.md`, `07.3-01/02-SUMMARY.md` | runtime/protocol signals -> exporter contracts/views -> diagnostics/system-health/developer/replay/evidence consumers | exporter 只拥有 observer-only telemetry truth；允许真实时间戳，但敏感字段、伪匿名引用与 cardinality 仍必须继承 `07.3` 正式裁决 |
| replay manifest + run summary families | `tests/fixtures/protocol_replay/`, `tests/fixtures/api_contracts/`, `tests/fixtures/protocol_boundary/`, `tests/harness/protocol/`, `tests/integration/test_protocol_replay_harness.py`, `07.4-01/02/03-SUMMARY.md` | authority fixtures -> replay manifests -> deterministic driver -> replay assertions / run summary | replay manifests 只能索引 authority payload；run summary 只能 pull `07.3` exporter truth 与正式 boundary truth，不得复制第二份 payload 或 telemetry truth |
| v1.1 closeout evidence index | `.planning/baseline/AUTHORITY_MATRIX.md`, `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/RESIDUAL_LEDGER.md`, `.planning/reviews/KILL_LIST.md`, `.planning/phases/07.3-runtime-telemetry-exporter/`, `.planning/phases/07.4-protocol-replay-simulator-harness/` | governance truth + phase evidence -> `V1_1_EVIDENCE_INDEX.md` -> Phase 8 pull-only packaging inputs | evidence index 只是稳定指针，不得反向定义 boundary / telemetry / replay / governance 新真相 |
| generated artifacts | fixture families + canonical normalization rules | baseline/contracts -> fixture/snapshot truth -> generated expectation -> implementation review | 具体 family 由 `Phase 2.6` 明确登记 |
| share/support payload families | `tests/fixtures/external_boundaries/share_worker/`, `tests/fixtures/external_boundaries/support_payload/` | authority docs -> fixture families -> payload builders/services -> owning tests | `generated_at` / `timestamp` 等动态字段必须先 canonicalize |
| firmware advisory families | `custom_components/lipro/firmware_support_manifest.json`, `tests/fixtures/external_boundaries/firmware/` | local trust root -> advisory remote -> adapters/tests | remote advisory 不能单独放宽 `certified` |
| diagnostics external endpoints | `tests/fixtures/api_contracts/` for `get_city/query_user_cloud`; `tests/fixtures/external_boundaries/diagnostics_capabilities/` for other endpoint families | protocol truth -> external-boundary fixtures -> diagnostics services/tests | `get_city/query_user_cloud` 不得复制第二套真源 |
| 测试期望 | `tests/**` | requirements/baseline -> implementation | 测试需跟随正式结构迁移 |
| 实现代码 | `custom_components/lipro/**` | north-star + planning -> code | 不是架构真源，只是实现载体 |

## Conflict Resolution

若出现口径冲突，优先级如下：

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/baseline/*.md`
3. `.planning/PROJECT.md` / `.planning/ROADMAP.md` / `.planning/STATE.md`
4. phase execution summaries / validation docs
5. tests / fixtures / implementation comments

## Synchronization Rule

按 artifact family 的正式同步方向执行：

- **docs**：`north-star -> baseline -> phase docs / developer docs`，实现与测试只能触发回写需求，不能静默改写文档真相。
- **fixtures**：`baseline/contracts -> fixture family -> owning tests`，fixture 漂移必须伴随 baseline、summary 或 validation 解释。
- **generated**：`fixture families + canonical normalization rules -> generated expectation -> implementation review`，禁止由实现临时输出反向定义真相。
- **implementation**：`north-star + baseline + tests -> code`，实现是载体，不是 authority source。
- **enforcement**：`baseline -> policy doc -> helpers/scripts/tests/CI`，脚本、测试与工作流只能执行规则，不能成为规则真源。

出现以下任一情况时，必须同步检查 authority matrix：

- 新增或删除正式 public surface
- phase 引入新的 fixture / generated artifact / shadow doc
- 旧 compat shell 被降级或删除
- 文档与实现出现双口径风险
- external-boundary truth 从“实现 folklore”升级为“formal contract”
- protocol-boundary decoder family 新增/升级/删除 family、version 或 authority source
- architecture policy 新增 rule family、例外、extension hook 或 CI gate

---
*Used by: external boundary formalization, architecture policy enforcement, docs hygiene, and audit arbitration*
