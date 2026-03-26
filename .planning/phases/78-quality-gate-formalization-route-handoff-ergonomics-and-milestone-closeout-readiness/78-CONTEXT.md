# Phase 78: Quality gate formalization, route-handoff ergonomics, and milestone-closeout readiness - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning
**Source:** `$gsd-plan-phase 78` + repo-local governance / GSD fast-path audit

<domain>
## Phase Boundary

本 phase 是一次 **planning/governance closeout formalization**，不是新的 production-plane 大重构。

必须只处理与 `v1.21 current route -> milestone closeout-ready -> later archive promotion` 直接相关的 live truth：

1. 把 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / tests/meta` 的 current-route story 从 `Phase 76 execution-ready` 前推到 `Phase 78 complete`，并把默认下一步切换到 `$gsd-complete-milestone v1.21`；
2. 让 `gsd-tools` 的本地 fast path（`init progress`、`state json`、`phase-plan-index 78`）与 repo live docs 讲同一条 closeout-ready 故事，而不是只在 prose 中“看起来完成”；
3. 把 verification / file-matrix / promoted-assets / residual / kill truth 同步到新的 route-handoff contract，确保后续 archive promotion 不再需要一次性补 current story；
4. 为 `Phase 76 / 77 / 78` 冻结一套低维护、可审计、可机器消费的 governance evidence bundle；
5. 不得借机修改外部 GSD 源码、发明第二条治理故事线，或把 archive promotion 提前偷跑成当前 phase 的隐式副作用。

本 phase 不处理：

- Home Assistant 生产代码热点；
- `.planning/milestones/v1.20-*` 等已归档快照重写；
- 外部 `get-shit-done` 工具仓库改动；
- 仅为“更整齐”而进行的无收益拆分。

</domain>

<decisions>
## Locked Decisions

- `tests/meta/governance_current_truth.py` 继续是 machine-readable route contract 的唯一正式 helper home；`PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 的 contract block 必须与其逐字同构。
- current route 必须从 `v1.21 active route / Phase 76 execution-ready / latest archived baseline = v1.20` 前推到 `v1.21 active route / Phase 78 complete / latest archived baseline = v1.20`；closeout readiness 由 `status` 与 default next command 共同表达，而不是重新发明第二套 prose-only state。
- `Phase 78` 需要一个新的 focused meta smoke home，专门负责 route-handoff / GSD fast-path：覆盖 `init progress`、`state json`、`phase-plan-index 78`、default next command、closeout-ready status 与 promoted evidence pointers。
- `tests/meta/test_governance_bootstrap_smoke.py` 继续负责 bootstrap/current-route 最小充分 smoke；`tests/meta/test_governance_closeout_guards.py` 继续负责 file-matrix / promoted-assets / verification alignment；新的 route-handoff smoke 不应把这些 concern 重新混回去。
- `.planning/baseline/VERIFICATION_MATRIX.md` 必须新增 `Phase 78 Exit Contract`，明确 required artifacts / governance proof / runnable proof / unblock effect。
- `.planning/reviews/FILE_MATRIX.md` 与 `scripts/check_file_matrix_registry.py` 必须共同承认新的 route-handoff smoke home；不能只改测试文件、不改治理登记。
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 应冻结 `Phase 76 / 77 / 78` 的 closeout evidence allowlist；`.planning/reviews/RESIDUAL_LEDGER.md` 与 `.planning/reviews/KILL_LIST.md` 需显式声明本轮无新增 active residual / kill target。
- 本 phase 只把里程碑推进到 **closeout-ready**；真正 archive promotion 仍由后续 `$gsd-complete-milestone v1.21` 完成。

### Claude's Discretion

- 可以新增一个 focused route-handoff smoke suite，只要它的职责与 bootstrap smoke / closeout guards 清晰分离。
- 可以把与 `Phase 76 execution-ready` 绑定的 stale literals 加入 forbidden prose guard，只要不篡改历史 phase execution traces。
- 可以为后续 archive promotion 预先提升 `76 / 77 / 78` 的 closeout bundle 到 promoted allowlist，只要不把 `PLAN / CONTEXT / RESEARCH` 误提升为长期证据。
- 可以扩展 `STATE.md` 的推荐命令与连续性提示，让 resume path 与 closeout-ready 真相保持一致。

</decisions>

<canonical_refs>
## Canonical References

- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/phases/76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation/76-CONTEXT.md`
- `.planning/phases/76-governance-bootstrap-truth-hardening-archive-seed-determinism-and-active-route-activation/76-VERIFICATION.md`
- `.planning/phases/77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction/77-CONTEXT.md`
- `.planning/phases/77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction/77-VERIFICATION.md`
- `tests/meta/governance_current_truth.py`
- `tests/meta/governance_contract_helpers.py`
- `tests/meta/governance_promoted_assets.py`
- `tests/meta/test_governance_bootstrap_smoke.py`
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_governance_milestone_archives.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_phase75_governance_closeout_guards.py`
- `tests/meta/toolchain_truth_checker_paths.py`
- `scripts/check_file_matrix_registry.py`
- `scripts/check_file_matrix.py`

## Hotspot Observations

- live docs 仍把 `v1.21` current route 锚定在 `Phase 76 execution-ready`，这对 `Phase 77` 已完成、`Phase 78` 将完成的事实是不诚实的；后续若直接 `$gsd-next`，closeout routing 仍会依赖一次性人工判断。
- `Phase 76` 已证明 bootstrap contract 可以 machine-readably 暴露给 `gsd-tools`；但目前还没有 focused smoke 直接守卫“当前 milestone 已 closeout-ready、下一步只能 `$gsd-complete-milestone v1.21`”这一条 fast path。
- `tests/meta/test_governance_bootstrap_smoke.py` 与 `tests/meta/test_governance_closeout_guards.py` 目前主要守 active-route activation 和 file-matrix/promoted-assets manifest；Phase 78 需要的是一条更贴近 `route-handoff` 的 focused suite，而不是继续在旧文件上堆更多断言。
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 目前还没有 `76 / 77 / 78` closeout bundle；如果不在本轮冻结，后续 archive promotion 仍要回头补 allowlist 与 proof story。
- `.planning/reviews/RESIDUAL_LEDGER.md` / `KILL_LIST.md` 目前停在 `Phase 71`；如果不显式声明 `76 -> 78` 无新增 active residual / kill target，后续 closeout-ready 叙事会缺一块治理证据。
- `state json` frontmatter 仍是 `0/3 phases`、`0/0 plans`，这会让 `gsd-tools` fast path 与实际 phase completion 事实脱钩。

</canonical_refs>

<execution_shape>
## Recommended Execution Shape

- `78-01`：先前推 machine-readable current-route contract 与 GSD fast path，把 live docs / state / current truth 改到 `Phase 78 complete` + `$gsd-complete-milestone v1.21`，并新增 focused route-handoff smoke。
- `78-02`：再把 verification matrix、file matrix、registry 与 focused governance guards 同步到新的 closeout-ready contract，确保 quality gates 真正阻断 drift。
- `78-03`：最后冻结 promoted-assets / residual / kill / summary / verification / validation 等 closeout evidence，让后续 archive promotion 不再需要补 governance story。

## Minimum Validation Intent

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 78`
- `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase75_governance_closeout_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py tests/meta/test_governance_promoted_phase_assets.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check tests/meta`

## Migration Guardrails

- 允许新增 focused smoke，但不允许让旧 suite 失去明确 boundary。
- 允许提升 `76 / 77 / 78` closeout bundles，但不得提升 `PLAN / CONTEXT / RESEARCH`。
- 允许更新 `STATE.md` frontmatter 以匹配 phase completion；不得伪造未执行的 archive promotion。
- 历史 phase 执行痕迹（`.planning/phases/76/**`, `.planning/phases/77/**`）保持原样，除非作为 promoted evidence allowlist 被引用。
- 任何新字符串都应服务“更低维护成本的单一路由真相”，而不是制造第三套命名。

## Expected Outputs For Planning

- 一套前推到 `Phase 78 complete` / `$gsd-complete-milestone v1.21` 的 live route contract。
- 一个 focused route-handoff smoke suite，直接守卫 GSD fast path 与 closeout-ready wording。
- 一条 `Phase 78 Exit Contract`，将 route-handoff / fast-path / promoted evidence / governance ledgers 绑定成同一质量门。
- 一份冻结好的 `76 / 77 / 78` evidence allowlist 与无新增 residual/kill target 的治理结论。
- 一组 phase-level summary / verification / validation 资产，供后续 archive promotion 直接消费。

## Non-Goals Reminder

- 不在本 phase 内执行 `$gsd-complete-milestone v1.21`。
- 不修改外部 GSD CLI 源码。
- 不触碰与 route-handoff 无关的 production logic。

</execution_shape>
