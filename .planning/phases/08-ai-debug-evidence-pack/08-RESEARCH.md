# Phase 8 Research

**Phase:** `8 AI Debug Evidence Pack`
**Source milestone research:** `.planning/research/SUMMARY.md`
**Date:** 2026-03-13

## Findings

### 1. `Phase 8` 的正确定位是 assurance/tooling exporter，而不是 production feature

`08` 的目标不是给 Home Assistant 用户新增运行时能力，而是把 `07.3 telemetry`、`07.4 replay`、`07.5 governance closeout` 的正式产物统一打包成一份 **可给 AI 调试/分析** 的证据包。

因此最佳形态是：
- tool-only exporter；
- pull-only collector；
- 稳定 schema + JSON 输出 + markdown index；
- 不进入 runtime orchestration 主链。

### 2. 最佳 truth chain

`08` 只能从以下正式真源 pull：
- `07.3`：exporter snapshots / views / telemetry surface；
- `07.4`：replay run summaries / authority-indexed replay manifests；
- `07.5`：`V1_1_EVIDENCE_INDEX.md`、governance matrices、residual / delete gates；
- boundary inventory / authority docs：用于字段 authority trace。

最优 evidence pack chain：

`formal sources -> evidence source adapters -> pseudo-id/redaction policy -> evidence pack schema -> JSON pack + index`

### 3. evidence pack 最优落点不在 `custom_components/`

由于 `08` 是 assurance/tooling only，最佳 home 是：
- `scripts/export_ai_debug_evidence_pack.py`：导出入口；
- `tests/harness/evidence_pack/`：schema / collector / source adapters / redaction rules；
- `tests/integration/` 与 `tests/meta/`：包结构、authority、脱敏与来源守卫。

不推荐把 evidence pack exporter 落到 `custom_components/lipro/core/`：
- 会模糊 production 与 tooling 边界；
- 容易演变为第二 diagnostics / observability 实现；
- 与北极星的 assurance-plane 定位冲突。

### 4. 脱敏与关联策略已经足够明确，不需要在 `08` 再造一套

契约者已锁定：
- 凭证等价物永不出现：`password_hash`、token、secret、refresh/access key 等；
- 允许真实时间戳；
- 允许 `entry_ref` / `device_ref` 这类报告内稳定、跨报告不可关联的伪匿名引用。

因此 `08` 最优做法不是新造 redaction truth，而是：
- 明确消费 `07.3` / control redaction contract；
- 在 evidence pack 层做最后一层 source-level denylist / schema-level validation；
- 让每个 evidence field 能追溯其 authority/source。

### 5. “最好的” schema/backend 选择：当前不引入新重型依赖

对 `08` 而言，最优立即解不是引入 `msgspec` 或 `pydantic v2`，而是：
- 用现有 typed contracts + stdlib JSON 先锁定 schema；
- 让导出器保持 backend-swappable；
- 只有当 evidence pack 的 schema validation / encoding 成本被证明成为瓶颈时，再单独裁决编码后端。

理由：
- `08` 是 assurance/tooling only，当前核心价值在于“单一真源、可追溯、脱敏正确”，不是编码性能；
- 过早引入新依赖会扩大治理面；
- 这比把 `msgspec / pydantic v2` 绑定进当前 phase 更符合北极星的克制原则。

### 6. 与 `07.5` 的 handoff 必须是“索引到打包”的关系

- `07.5` 提供 `V1_1_EVIDENCE_INDEX.md`、矩阵对齐、residual/delete gates；
- `08` 根据该 index 和正式真源生成 evidence pack；
- `08` 不应回头重做 closeout 仲裁；
- `07.5` 也不应提前实现 evidence pack exporter。

## Recommended Outputs

### 1. Tooling structure

建议新增：
- `scripts/export_ai_debug_evidence_pack.py`
- `tests/harness/evidence_pack/__init__.py`
- `tests/harness/evidence_pack/schema.py`
- `tests/harness/evidence_pack/sources.py`
- `tests/harness/evidence_pack/collector.py`
- `tests/harness/evidence_pack/redaction.py`
- `tests/fixtures/evidence_pack/README.md`

### 2. Tests

建议新增：
- `tests/integration/test_ai_debug_evidence_pack.py`
- `tests/meta/test_evidence_pack_authority.py`
- 如有需要，补一个 golden / snapshot-style pack schema regression test

### 3. Governance hooks

至少需要同步：
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`

## Risks To Avoid

- evidence pack exporter 变成新的 runtime root 或 diagnostics implementation；
- 重新扫描仓库临时拼接第二套事实，而不是 pull 正式真源；
- 在 `08` 重新定义 redaction / pseudo-id 规则，导致与 `07.3` / `07.5` 分裂；
- 过早为 tooling-only phase 引入重型依赖与复杂 stack。

## Validation Architecture

`08` 的验证必须同时证明：
1. evidence pack 只 pull 正式真源；
2. evidence schema 稳定、版本化、默认 JSON 输出；
3. 凭证等价物不会进入 pack，真实时间戳与伪匿名引用策略正确；
4. 每个 evidence section 都能追溯 authority/source，并与 `07.5` evidence index 对齐。

### 推荐 quick run

- `uv run pytest -q -x tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py`

### 推荐 full suite

- `uv run ruff check scripts/export_ai_debug_evidence_pack.py tests/harness/evidence_pack tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py`
- `uv run pytest -q -x tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_evidence_pack_authority.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py`

## Final Arbitration

`08` 的最优实现不是“做一个更大的 diagnostics”，而是：
- 以 assurance/tooling 方式 pull 正式真源；
- 把 telemetry / replay / boundary / governance 输出统一为 AI 可消费的结构化证据包；
- 在不扩散主链复杂度的前提下，显著提升 AI 调试、人工诊断与后续演进建议的质量。
