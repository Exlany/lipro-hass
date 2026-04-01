# Phase 118 Research

**Phase:** `118-final-hotspot-decomposition-and-validation-closure`
**Date:** `2026-04-01`
**Requirements:** `未新增 requirement ID；本 phase 处理 HOT-48 / HOT-49 / TST-39 / GOV-73 的 repo-internal follow-up debt`

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** `Phase 118` 的第一优先级是真相校准：既然 current milestone 已扩展到 `118`，route contract、default next command、phase range、progress 与 focused governance tests 都必须同步；不能让 `ROADMAP/STATE` 继续声称“下一步只剩 closeout”。
- **D-02:** 热点 slimming 只在既有正式 home 内进行：允许继续拆 helper / evaluator / builder / result vocabulary，但不允许通过新 compat shell、alias export 或 package-level folklore 假装“文件变小”。
- **D-03:** `status_fallback_support.py` 是当前最明显的 giant formal home，优先沿“query context / split executor / aggregate accounting / error mapping”继续切薄。
- **D-04:** `rest_decoder.py` / `rest_decoder_support.py` 的问题不是功能错误，而是 decoder family registry、canonical fingerprint 与 endpoint authority 聚在一起；应继续按 family / registry / utility 职责收窄，而不是复制第二套 decoder 入口。
- **D-05:** `firmware_update.py` 与 `anonymous_share/manager.py` 已较前序更干净，但仍是 orchestration-heavy formal homes；本轮只做 bounded split，保证实体 outward contract 与 aggregate/scoped manager 语义不变。
- **D-06:** `115/116/117-VALIDATION.md` 需要和各自 phase scope 严格一致：补齐 validation contract，而非改写历史 requirement fulfillment。
- **D-07:** 外部 continuity / open-source blocker 继续保持 honest-by-default，最多在审查报告中记录，不伪造成“本轮已通过代码解决”。

### Claude's Discretion

- 继续在 formal homes 内 inward split 剩余热点，降低 giant-home 密度；
- 回补 `115/116/117-VALIDATION.md`，让 `v1.32` 自身达到 verification + validation 双闭环；
- 把 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / baseline / review ledgers / meta guards` 同步到 `Phase 118` 的真实 route，不再维持 stale closeout-ready wording。

### Deferred Ideas (OUT OF SCOPE)

- 伪造 non-GitHub private fallback、public mirror、HACS path、delegate maintainer 等仓外事实；
- 新增 outward root、compat shell、second mainline；
- 把 repo-wide 所有 medium-size 文件都强行打散，只收敛当前明确已被审计点名且与 formal-home 清晰度直接相关的热点。
</user_constraints>

## Project Constraints (from CLAUDE.md)

- 读取顺序必须以 `AGENTS.md` → `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` → `.planning/*` 主链为准。
- 若 `CLAUDE.md` 与 `AGENTS.md` 冲突，以 `AGENTS.md` 为准。
- `CLAUDE.md` 不定义第二套 truth source，只是 Claude Code 兼容入口。
- 不创建也不依赖 `agent.md`。
- 当前 milestone / phase / recommended next step 以 `.planning/STATE.md` 为准。

## Objective

`Phase 118` 不是“顺手补几个文件”的收尾杂项，也不是假装 `Phase 117` 已经零债务后的重复 closeout。当前仓库的真实状态是：`v1.32` 曾被推进到 `Phase 117 complete / closeout-ready`，但审计与上下文已经明确把 `Phase 118` 拉回 active route，用来处理三类仍然留在仓内、且仍可由代码 / 测试 / planning truth 直接修复的问题：`route truth` 重新对齐、formal-home hotspot 的 bounded inward split、以及 `115 -> 117` phase-local validation 闭环。

这意味着本 phase 的首要目标不是继续写热点代码，而是先让 `Phase 118` 重新成为 parser-visible、machine-checkable、docs-first 的 current route。只有 route truth 激活之后，后续 hotspot slimming 与 validation closure 才不会落在已经过期的 `117 -> closeout` 叙事上。

## Inputs Reviewed

- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-CONTEXT.md`
- `.planning/v1.32-MILESTONE-AUDIT.md`
- `custom_components/lipro/core/api/status_fallback_support.py`
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py`
- `custom_components/lipro/entities/firmware_update.py`
- `custom_components/lipro/core/anonymous_share/manager.py`
- `tests/meta/governance_current_truth.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `.planning/phases/117-validation-backfill-and-continuity-hardening/117-RESEARCH.md`
- `.planning/phases/116-anonymous-share-and-rest-fa-ade-hotspot-slimming/116-RESEARCH.md`
- `.planning/phases/115-status-fallback-query-flow-normalization/115-SUMMARY.md`
- `.planning/phases/116-anonymous-share-and-rest-fa-ade-hotspot-slimming/116-SUMMARY.md`
- `.planning/phases/117-validation-backfill-and-continuity-hardening/117-SUMMARY.md`
- `.planning/phases/112-formal-home-discoverability-and-governance-anchor-normalization/112-VALIDATION.md`
- `.planning/phases/114-open-source-reachability-honesty-and-security-surface-normalization/114-VALIDATION.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `tests/meta/test_phase113_hotspot_assurance_guards.py`

## Findings

1. **[HIGH] `Phase 118` 现在还不是真正“活着”的 current route。**
   - `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap get-phase 118` 当前返回 `found = false`，说明 parser 还看不到这个 phase。
   - `.planning/ROADMAP.md` 的 `### Phase 118` 被错误追加到文件尾，而不是挂在 `v1.32` 的 phase detail / progress 主链里。
   - `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 与 `tests/meta/{governance_current_truth.py,test_governance_route_handoff_smoke.py,governance_followup_route_current_milestones.py}` 仍冻结在 `active / phase 117 complete; closeout-ready (2026-03-31)` 与 `$gsd-complete-milestone v1.32`。
   - **结论：** `118-01` 必须先修 parser-visible route truth；否则 planner、gsd fast-path 与 focused meta guards 都不会承认 `Phase 118`。

2. **[HIGH] 最合理的 plan 拆分仍是 3 个，而且顺序不能颠倒。**
   - **118-01 Route truth activation and governance resync**
     - 把 `Phase 118` 插回 `v1.32` 正式 active route；
     - 修复 `ROADMAP` phase placement / contract blocks / progress math / default next command；
     - 同步 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / VERIFICATION_MATRIX` 与三份 route truth tests。
   - **118-02 Hotspot decomposition round two**
     - 先处理 `status_fallback_support.py` 与 `rest_decoder` family；
     - 再视预算决定是否对 `firmware_update.py` 与 `anonymous_share/manager.py` 做 bounded split；
     - 任何 split 都必须保持 formal home 不变、无 compat shell、无 second root。
   - **118-03 Validation closure and final proof chain**
     - 回补 `115/116/117-VALIDATION.md`；
     - 同步 allowlist / audit / verification truth；
     - 收口 targeted + route + repo-wide verification，重新得到真实 closeout-ready story。

3. **[HIGH] `status_fallback_support.py` 的最安全 inward split 是“算法内聚化”，不是再造入口。**
   - 现状：655 行，同一 formal home 同时背着 query setup、binary split recursion、accumulator/result vocabulary、error-code mapping、logging/summary 与 fallback-depth bookkeeping。
   - 最安全做法：保留 `status_fallback_support.py` 作为唯一 outward import home 和 `__all__` 所在地，只把内部职责继续 topicize 成本地 support-only collaborators。
   - 推荐刀口：
     - `query context / options / result vocabulary` 一组；
     - `recursive split executor` 一组；
     - `fallback logging / empty-summary reporting` 一组。
   - 安全边界：
     - 不新增 `status_fallback.py` 或其他 alias root；
     - 不在 `core/api/__init__` 或 package export 暴露新 helper；
     - 保持 `query_with_fallback_impl()` 与 `query_items_by_binary_split_impl()` 的 outward contract 不变。

4. **[MEDIUM-HIGH] `rest_decoder.py` / `rest_decoder_support.py` 的最安全 inward split 是“family/topic split”，不是 registry 分叉。**
   - 现状：`rest_decoder.py=425`、`rest_decoder_support.py=417`；一边承载 decoder classes + endpoint authority，一边承载 fingerprint / normalization / list/status/group canonical builders。
   - 最安全做法：保留 `rest_decoder.py` 作为 decoder family 的唯一入口与 current registry home；继续把纯 generic normalization 与 family-specific canonical builder 向内切薄。
   - 推荐刀口：
     - `RestDecodeContext / decoder family metadata / registry helpers` 保持在 `rest_decoder.py`；
     - `payload fingerprint / pagination / scalar normalization` 可向 family-neutral helper 下沉；
     - `device-list / device-status / mesh-group-status` canonical builders 可独立为 family-local collaborator。
   - 安全边界：
     - 不创建第二套 `rest_decoders/` 包或 package-level export；
     - 不复制第二个 registry / entrypoint；
     - 任何新增 helper 只允许被 `rest_decoder.py` / `rest_decoder_support.py` 本地消费。
   - 补充：`tests/meta/test_phase101_anonymous_share_rest_boundary_guards.py` 与 `tests/meta/test_phase113_hotspot_assurance_guards.py` 目前冻结了该 family 的文件名 / 预算 / helper 证据；若发生 split，guard 需要在同一 plan 中同步。

5. **[MEDIUM] `firmware_update.py` 的最安全 inward split 是“实体保留、任务/状态下沉”。**
   - 现状：`LiproFirmwareUpdateEntity` 既承担 HA outward entity contract，又承担 OTA refresh scheduling、background task cleanup、install preparation、translated error build 与 extra-state projection。
   - 最安全做法：
     - 保留 `LiproFirmwareUpdateEntity` 作为唯一 outward entity home；
     - 纯 OTA 选择/判定继续复用现有 `core/ota/*`；
     - 仅把 HA-specific refresh-task lifecycle、install-preparation glue 或 state-attribute builder 向 entity-local support seam 下沉。
   - 安全边界：
     - 不把 entity orchestration 搬到新的 runtime/service root；
     - 不把 HA-specific translated error / `async_write_ha_state()` 之类逻辑塞进 protocol/runtime formal root；
     - 这项应排在 `status_fallback_support.py` 与 `rest_decoder` 之后。

6. **[HIGH] `anonymous_share/manager.py` 的最安全 inward split 是“沿现有 `manager_*` family 继续 topicize”，且优先级应低于前三者。**
   - 现状：359 行；`manager_support.py`、`manager_submission.py`、`manager_scope.py` 已经建立了正确的 inward split 方向。
   - 最安全做法：继续在同一 family 内下沉 report/persistence glue、aggregate/scoped facade boilerplate 或 submit-state accessor grouping，而不是重写 outward API。
   - 安全边界：
     - 保持 `AnonymousShareManager` 身份、`core.__init__` export、registry/factory truth 与 aggregate/scoped contract 不变；
     - 不引入新的 `share_manager` / `submission_manager` outward root；
     - 若预算不足，这个热点可以只记录为 residual continuation，而不强行大拆。

7. **[HIGH] Route truth sync 的最小完备工件集合必须覆盖 parser 真源、shared truth helper 与 focused route smoke。**
   - **严格最小集合：**
     - `.planning/PROJECT.md`
     - `.planning/ROADMAP.md`
     - `.planning/REQUIREMENTS.md`
     - `.planning/STATE.md`
     - `.planning/MILESTONES.md`
     - `.planning/baseline/VERIFICATION_MATRIX.md`
     - `tests/meta/governance_current_truth.py`
     - `tests/meta/test_governance_route_handoff_smoke.py`
     - `tests/meta/governance_followup_route_current_milestones.py`
   - **条件项：**
     - `.planning/reviews/FILE_MATRIX.md` —— 只有在新增 `tests/meta/test_phase118_*` 专用 guard 时才是必改；若只是复用既有 route guards，则可以不动。
   - **关键说明：**
     - `ROADMAP` 把 `Phase 118` 放回 `v1.32` 段内、让 `roadmap get-phase 118` 从 `found=false` 变成 `found=true`，不是“附带优化”，而是最小集合中的硬要求。

8. **[HIGH] `115/116/117` VALIDATION backfill 的最小完备工件集合必须覆盖 phase-local contract、allowlist / audit truth，以及至少一个 machine-checkable 资产守卫。**
   - **严格最小集合：**
     - `.planning/phases/115-status-fallback-query-flow-normalization/115-VALIDATION.md`
     - `.planning/phases/116-anonymous-share-and-rest-fa-ade-hotspot-slimming/116-VALIDATION.md`
     - `.planning/phases/117-validation-backfill-and-continuity-hardening/117-VALIDATION.md`
     - `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
     - `.planning/v1.32-MILESTONE-AUDIT.md`
     - `.planning/baseline/VERIFICATION_MATRIX.md`
   - **同 bundle 但通常无需重写内容的相邻工件：**
     - `115/116/117` 既有 `*-SUMMARY.md` 与 `*-VERIFICATION.md` 继续作为 phase-local proof chain 的邻接资产，validation 只应 cross-reference，不应重写历史完成结论。
   - **测试侧最低要求：**
     - 至少有一个现有 meta suite 对 `115/116/117` 的 validation bundles 做 machine-checkable 断言；最佳 home 是扩展既有 promoted-assets / governance suite，而不是再造第二套 truth 文件。
   - **额外耦合：**
     - 若 `118-02` 让 line budget 发生变化，`tests/meta/test_phase113_hotspot_assurance_guards.py` 也必须在同一 change set 里更新，否则 validation backfill 之后依旧会留下 stale proof。

9. **[HIGH] 真正的仓外 blocker 仍然只能如实记录，不能塞进 `Phase 118` 伪装成“已解决事项”。**
   - guaranteed non-GitHub private disclosure fallback；
   - public mirror / HACS-grade distribution path；
   - delegate / backup maintainer identity；
   - 任何需要 maintainer 现实授权、外部基础设施或 public hosting 才能成立的 continuity 承诺。
   - **结论：** 这些内容可以出现在 `118` 的审查 / audit / summary 中作为 honest blocker，但不能成为 repo-internal closeout 的伪完成项。

## Execution Shape

建议继续采用 **3 plans / 单主链顺序执行** 的形态，不建议把 `118-01` 与其余两项并行：

- **118-01 Route truth activation and governance resync**
  - 先修 `Phase 118` 的 parser 可见性与 selector truth；
  - 默认下一步应从 `$gsd-complete-milestone v1.32` 改回 `118` 当前真实阶段（研究完成后应先到 `$gsd-plan-phase 118`，计划完毕后再到 `$gsd-execute-phase 118`）；
  - 只有这一步完成后，剩余 work 才拥有合法 current story。

- **118-02 Hotspot decomposition round two**
  - 优先顺序：`status_fallback_support.py` → `rest_decoder` family → `firmware_update.py` → `anonymous_share/manager.py`；
  - 前两者是 audit 与 context 都反复点名的主热点；后两者应以 bounded split / residual burn-down 为目标，而不是大范围重构。

- **118-03 Validation closure and final proof chain**
  - 回补 `115/116/117-VALIDATION.md`；
  - 同步 `PROMOTED_PHASE_ASSETS` / `v1.32-MILESTONE-AUDIT` / `VERIFICATION_MATRIX`；
  - 收口 route truth、budget truth 与 validation truth 的最终证明，让 closeout-ready 再次成立且不带伪债务遮蔽。

## Risks

- 若先做热点代码、后修 route truth，整个 phase 会持续建立在错误的 `117 -> closeout` selector 上，`gsd-tools` 与 meta guards 仍会把 `118` 当成不存在或无效延长。
- 若把 inward split 误做成 package export / alias file / compat shell，文件也许变小了，但 north-star single-mainline / formal-home truth 会立即被破坏。
- 若只写 `115/116/117-VALIDATION.md` 而不同时提升 allowlist / audit / verification truth，validation debt 只是从“缺文件”变成“文件存在但机器不承认”。
- 若试图借 `Phase 118` 顺手“解决” public mirror / delegate maintainer / non-GitHub fallback 等仓外问题，只会制造新的虚假 repo truth。
- `firmware_update.py` 在本次已读输入里没有与 `status_fallback` / `route truth` 同等级的 phase-local focused guard；若计划触碰该文件，执行时应先确认现有 entity/platform coverage 是否足够，否则把它降级为次优先 residual 更安全。

## Validation Notes

- route truth focused smoke：`uv run pytest -q tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py`
- hotspot no-growth / helper-locality：`uv run pytest -q tests/meta/test_phase113_hotspot_assurance_guards.py`
- promoted assets / archive truth：`uv run pytest -q tests/meta/governance_milestone_archives_assets.py tests/meta/test_governance_promoted_phase_assets.py`
- status-fallback / anonymous-share touched-scope 回归：沿用 `115` / `116` 已冻结的 focused suites；若 `rest_decoder` 或 `firmware_update` 发生 split，再补相邻 family 的 focused tests。
- 最终门禁：`uv run pytest -q`、`uv run ruff check .`、`uv run python scripts/check_file_matrix.py --check`
