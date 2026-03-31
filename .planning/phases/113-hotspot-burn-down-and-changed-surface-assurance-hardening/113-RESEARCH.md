# Phase 113: Hotspot burn-down and changed-surface assurance hardening - Research

**Researched:** 2026-03-31
**Domain:** production hotspot burn-down / changed-surface assurance / bounded no-regrowth budgets
**Confidence:** HIGH

<user_constraints>
## User Constraints

### Locked Decisions
- 本轮必须以顶级架构师视角做全仓审视，并把结论沉淀为正式计划与执行资产，而不是停留在口头建议。
- 必须沿 `$gsd-plan-phase -> $gsd-execute-phase -> $gsd-next` 的工作流推进。
- 允许彻底重构，但禁止 second root、compat shell 回流、临时修补式妥协。
- 最终需要给出终极审查报告：问题、不足、对应修改、剩余建议与后续计划。

### the agent's Discretion
- 可以用 repo-wide metrics、focused guards、file-matrix / baseline / planning truth 作为“全量审视”的证据，而不是逐文件人工复述全部 745 个 Python 文件内容。
- 可优先处理收益最高且 blast radius 最可控的 hotspots，再把更高层治理/开源问题显式登记到 final report / deferred plan。

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| QLT-46 | 当前 top-priority implementation hotspots 必须继续 inward split 或由 focused no-regrowth guards 固化，而不是被默许为 permanent large-file exception。 | `## Repo-wide hotspot inventory`、`## Recommended target selection`、`## Recommended Plan Decomposition` |

</phase_requirements>

## Summary

本仓库当前共有 `745` 个 Python 文件；其中 production `314` 个、tests `410` 个、scripts `21` 个。production 侧 `0` 个文件超过 `700` 行，但仍有 `11` 个文件超过 `400` 行，说明仓库已经不再有 giant unbounded carrier，却仍存在一批 **large-but-sanctioned hotspots**。结合历史 predecessor guards、public-surface authority 与当前 `v1.31 / Phase 113` 目标，最优策略不是粗暴“大拆所有热点”，而是：

1. **优先继续 inward split 两个高收益、低治理爆炸半径的 carriers：**
   - `custom_components/lipro/core/anonymous_share/share_client_submit.py`（`455` 行）
   - `custom_components/lipro/core/command/result.py`（`469` 行）
2. **对 remaining hotspots 建立 explicit bounded allowance：**
   - `status_fallback_support.py` (`652`)
   - `rest_facade.py` (`431`)
   - `manager.py` (`430`)
   - `rest_decoder.py` (`425`)
   - `firmware_update.py` (`418`)
   - `result_policy.py` (`417`)
   - `rest_decoder_support.py` (`417`)
   - `dispatch.py` (`412`)
   - `auth/manager.py` (`407`)
3. **把 changed-surface assurance 下沉到 maintainer 日常默认门禁**，避免只有 `--full` 模式才看见 hotspot regressions。

这一路径同时满足了 `QLT-46` 的三条成功标准：
- 至少两处 top-priority hotspots 继续 inward split；
- changed surfaces 拥有 focused assurance run，而不是只靠 repo-wide coverage；
- remaining hotspot allowance 变成显式 budget / locality truth，而不是“默许长期存在”。

## Repo-wide hotspot inventory

### Production size/complexity snapshot

- Production files: `314`
- Production total lines: `47,270`
- Production classes: `446`
- Production functions: `2,571`
- Production files `> 400` lines: `11`

### Largest production carriers

| Lines | File | Notes |
|------:|------|-------|
| 652 | `custom_components/lipro/core/api/status_fallback_support.py` | support-only, predecessor guard heavy, not ideal for this phase's lowest-risk cut |
| 469 | `custom_components/lipro/core/command/result.py` | stable export home with helper ballast |
| 455 | `custom_components/lipro/core/anonymous_share/share_client_submit.py` | support-only submit flow carrier with natural internal grouping |
| 431 | `custom_components/lipro/core/api/rest_facade.py` | formal REST child façade; many small wrappers, lower immediate payoff |
| 430 | `custom_components/lipro/core/anonymous_share/manager.py` | formal aggregate manager home; many small methods, less obvious seam |
| 425 | `custom_components/lipro/core/protocol/boundary/rest_decoder.py` | predecessor-sensitive boundary carrier |
| 418 | `custom_components/lipro/entities/firmware_update.py` | protected thin shell with OTA projection obligations |

### Long-function snapshot (selected)

| Length | Function | File |
|-------:|----------|------|
| 52 | `apply_command_result_rejected` | `custom_components/lipro/core/command/result.py` |
| 50 | `_resolve_submit_attempt_outcome` | `custom_components/lipro/core/anonymous_share/share_client_submit.py` |
| 49 | `query_with_fallback_impl` | `custom_components/lipro/core/api/status_fallback_support.py` |
| 44 | `_query_with_batch_fallback` | `custom_components/lipro/core/api/status_fallback_support.py` |

## Recommended target selection

### Target 1: `share_client_submit.py`

**Why it is a phase-113 target**
- 已是 support-only submit flow home，不承载 public root 语义；
- 内部存在清晰自然边界：`preflight/refresh`、`HTTP outcome builders`、`variant/token attempt resolution`；
- production importer story 简单：`share_client.py -> share_client_flows.py -> share_client_submit.py`；
- 现有 `tests/core/test_share_client_submit.py` 覆盖成熟，适合做 focused changed-surface assurance。

**Best move**
- 把 outcome builders 与 attempt-resolution 逻辑 inward split 到 sibling support modules；
- 保持 `submit_share_payload_with_outcome()` outward semantics 不变；
- 用 locality guard 保证新 helper 不被其他模块随意吸入。

### Target 2: `result.py`

**Why it is a phase-113 target**
- `result.py` 是 stable export / failure arbitration home，但文件仍携带一层 helper ballast；
- public users 只关心 outward functions，internal helper 抽走不会改变 stable export story；
- `tests/core/test_command_result.py` 是天然 focused assurance suite。

**Best move**
- inward split unconfirmed/failure helper builders 到 local support module；
- 保留 `apply_*` / `resolve_polled_command_result` / `build_command_api_error_failure` 等 public API 原地不变；
- 若可能，把文件压回 `< 400` lines，至少把 helper ballast 从 stable export home 中抽离。

### Why not pick `status_fallback_support.py` first

- 它确实是最大 remaining carrier，但 predecessor guards (`Phase 99` / `Phase 107`) 对其内部 token 与位置已经写得较深；
- 同一 phase 同时重构它、更新 predecessor guards、再做 route closeout，治理 blast radius 远高于本 phase 的最优解；
- 因此更适合作为 **explicit bounded allowance**：先 no-growth，再在未来专门 phase 拆。

## Governance / tooling audit findings

本轮全仓审视还发现了若干高价值但非全部属于 `QLT-46` 的问题：

### Critical / High findings
- 私有 `gsd-tools` 路径进入正式测试/closeout guards，影响 OSS 复现性。
- promoted assets allowlist 存在多处手写 phase->asset 清单，真源可能漂移。
- current-route truth 在 docs / tests / constants 多处硬编码，里程碑轮转成本偏高。
- `scripts/lint` 默认模式过轻，本地“全绿”不等于治理/changed-surface 全绿。
- governance smoke guards 对 phase 标题 / guard 名单过多 literal 断言，closeout 易脆断。

### Medium findings
- `.planning/codebase/*` freshness 漂移。
- planning 文档链接校验不完整。
- 架构文档重复度偏高；贡献者入口较重。
- maintainer continuity 仍是 single-point model。

**Research conclusion:** 这些问题必须进入最终审查报告与后续计划，但不宜全部塞进 `Phase 113`，否则会稀释 `QLT-46` 的实现型目标。

## Recommended Plan Decomposition

| Plan | Wave | Depends on | Scope | Output |
|------|------|------------|-------|--------|
| `113-01` anonymous-share submit hotspot inward split | Wave 1 | none | 拆 `share_client_submit.py` 为 thin orchestrator + local outcome/attempt helpers | thinner submit flow + unchanged outward contract |
| `113-02` command-result hotspot inward split | Wave 1 | none | 拆 `result.py` helper ballast，保留 stable export home | thinner `result.py` + unchanged outward contract |
| `113-03` hotspot assurance + bounded allowance freeze | Wave 2 | `113-01`, `113-02` | 新增 phase113 focused guard、冻结 remaining hotspots exact budgets、升级 `scripts/lint` 默认 changed-surface assurance、回写 testing/verification/file-matrix truth | no-growth hotspot contract + default focused assurance |
| `113-04` route closeout + final audit assets | Wave 3 | `113-01`, `113-02`, `113-03` | 前推 active route 到 `Phase 114 discussion-ready`，并写出 verification/summary/audit assets | phase113 closeout + route advances to 114 |

## Minimal Sufficient Validation Checklist

- `uv run pytest -q tests/core/test_share_client_submit.py tests/core/test_command_result.py`
- `uv run pytest -q tests/meta/test_phase113_hotspot_assurance_guards.py tests/meta/toolchain_truth_ci_contract.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py`
- `uv run pytest -q tests/meta/test_governance_release_docs.py tests/meta/toolchain_truth_docs_fast_path.py` when `CONTRIBUTING.md` or closeout docs text changes
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check custom_components/lipro/core/anonymous_share/share_client_submit.py custom_components/lipro/core/anonymous_share/share_client_submit_attempts.py custom_components/lipro/core/anonymous_share/share_client_submit_outcomes.py custom_components/lipro/core/command/result.py custom_components/lipro/core/command/result_support.py tests/core/test_share_client_submit.py tests/core/test_command_result.py tests/meta/test_phase113_hotspot_assurance_guards.py tests/meta/toolchain_truth_ci_contract.py scripts/lint tests/meta/governance_current_truth.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py`

## Sources

### Primary (HIGH confidence)
- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/codebase/CONVENTIONS.md`
- `custom_components/lipro/core/anonymous_share/share_client_submit.py`
- `custom_components/lipro/core/command/result.py`
- `custom_components/lipro/core/api/status_fallback_support.py`
- `custom_components/lipro/core/api/rest_facade.py`
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/entities/firmware_update.py`
- `tests/core/test_share_client_submit.py`
- `tests/core/test_command_result.py`
- `tests/meta/test_phase70_governance_hotspot_guards.py`
- `tests/meta/test_phase71_hotspot_route_guards.py`
- `tests/meta/test_phase95_hotspot_decomposition_guards.py`
- `tests/meta/test_phase99_runtime_hotspot_support_guards.py`
- `tests/meta/test_phase107_rest_status_hotspot_guards.py`
- `scripts/lint`

## Metadata

- Repo-wide scan basis: `745` Python files (`314` production / `410` tests / `21` scripts)
- Confidence: HIGH
- Valid until: `Phase 113` closeout or route switch
