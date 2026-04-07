# Phase 118: Final hotspot decomposition and validation closure - Context

**Gathered:** 2026-04-01
**Status:** Draft planning workspace

<domain>
## Phase Boundary

本 phase 是对 `v1.32` 的显式延长，而不是伪装成“117 已经完全无债务”。当前仓库已经达到 `Phase 117 complete / closeout-ready` 的机械态，但终极审阅与里程碑审计仍诚实留下三类 repo-internal 余量：

1. formal home 热点仍偏厚：
   - `custom_components/lipro/core/api/status_fallback_support.py`
   - `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
   - `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py`
   - `custom_components/lipro/entities/firmware_update.py`
   - `custom_components/lipro/core/anonymous_share/manager.py`
2. `Phase 115 -> 117` 缺少 phase-local `VALIDATION.md`，Nyquist 证据闭环仍不完整；
3. live governance route truth 仍停留在“`117 complete -> closeout`”故事，而 `Phase 118` 已被显式加到当前 milestone 中，说明 selector truth 需要再次同步。

因此本 phase 只处理**仓内还能被代码 / 测试 / planning truth 直接修复的剩余问题**：
- 继续在 formal homes 内 inward split 剩余热点，降低 giant-home 密度；
- 回补 `115/116/117-VALIDATION.md`，让 v1.32 自身达到 verification + validation 双闭环；
- 把 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / baseline / review ledgers / meta guards` 同步到 `Phase 118` 的真实 route，不再维持 stale closeout-ready wording。

本 phase **不处理**：
- 伪造 non-GitHub private fallback、public mirror、HACS path、delegate maintainer 等仓外事实；
- 新增 outward root、compat shell、second mainline；
- 把 repo-wide 所有 medium-size 文件都强行打散，只收敛当前明确已被审计点名且与 formal-home 清晰度直接相关的热点。
</domain>

<decisions>
## Implementation Decisions

- **D-01:** `Phase 118` 的第一优先级是真相校准：既然 current milestone 已扩展到 `118`，route contract、default next command、phase range、progress 与 focused governance tests 都必须同步；不能让 `ROADMAP/STATE` 继续声称“下一步只剩 closeout”。
- **D-02:** 热点 slimming 只在既有正式 home 内进行：允许继续拆 helper / evaluator / builder / result vocabulary，但不允许通过新 compat shell、alias export 或 package-level folklore 假装“文件变小”。
- **D-03:** `status_fallback_support.py` 是当前最明显的 giant formal home，优先沿“query context / split executor / aggregate accounting / error mapping”继续切薄。
- **D-04:** `rest_decoder.py` / `rest_decoder_support.py` 的问题不是功能错误，而是 decoder family registry、canonical fingerprint 与 endpoint authority 聚在一起；应继续按 family / registry / utility 职责收窄，而不是复制第二套 decoder 入口。
- **D-05:** `firmware_update.py` 与 `anonymous_share/manager.py` 已较前序更干净，但仍是 orchestration-heavy formal homes；本轮只做 bounded split，保证实体 outward contract 与 aggregate/scoped manager 语义不变。
- **D-06:** `115/116/117-VALIDATION.md` 需要和各自 phase scope 严格一致：补齐 validation contract，而非改写历史 requirement fulfillment。
- **D-07:** 外部 continuity / open-source blocker 继续保持 honest-by-default，最多在审查报告中记录，不伪造成“本轮已通过代码解决”。
</decisions>

<canonical_refs>
## Canonical References

- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/v1.32-MILESTONE-AUDIT.md`
- `.planning/phases/115-status-fallback-query-flow-normalization/{115-CONTEXT.md,115-SUMMARY.md,115-VERIFICATION.md}`
- `.planning/phases/116-anonymous-share-and-rest-fa-ade-hotspot-slimming/{116-CONTEXT.md,116-RESEARCH.md,116-SUMMARY.md,116-VERIFICATION.md}`
- `.planning/phases/117-validation-backfill-and-continuity-hardening/{117-CONTEXT.md,117-RESEARCH.md,117-SUMMARY.md,117-VERIFICATION.md}`
- `custom_components/lipro/core/api/status_fallback_support.py`
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py`
- `custom_components/lipro/entities/firmware_update.py`
- `custom_components/lipro/core/anonymous_share/manager.py`
- `tests/meta/governance_current_truth.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_phase112_formal_home_governance_guards.py`
</canonical_refs>

<specifics>
## Specific Ideas

- `gsd-tools phase add` 已创建 `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/`，但把 `### Phase 118` 错误追加到 `ROADMAP.md` 文件尾，而不是 `v1.32` 段内；这必须在执行中修复。
- 当前 live docs / tests 仍冻结 `active / phase 117 complete; closeout-ready (2026-03-31)` 与 `$gsd-complete-milestone v1.32`；它们现在已变成 stale truth，必须回到 `Phase 118` 真实 route。
- 五个热点文件当前总计 `2274` 行，其中 `status_fallback_support.py=655`、`rest_decoder.py=425`、`rest_decoder_support.py=417`、`firmware_update.py=418`、`anonymous_share/manager.py=359`；Phase 118 不要求把它们全部压到任意阈值以下，但至少要继续降低单文件职责密度、命名歧义与 orchestration 粘连。
- `115/116/117` 当前都有 `VERIFICATION.md`，但没有 phase-local `VALIDATION.md`；这一点已经被 `v1.32` audit 诚实标为 validation debt。
- phase planning 应至少拆成三类工作：`route/governance sync`、`hotspot decomposition`、`validation closure + verification`，避免把所有问题塞入一个 giant plan。
</specifics>
