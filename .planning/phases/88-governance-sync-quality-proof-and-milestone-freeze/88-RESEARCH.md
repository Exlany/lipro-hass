# Phase 88: Governance sync, quality proof, and milestone freeze - Research

**Date:** 2026-03-27
**Status:** Final
**Confidence:** HIGH
**Suggested shape:** 3 plans / 3 waves

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- `Phase 88` 只处理 `GOV-63` 与 `QLT-35`：目标是把 `v1.23` 的治理/证据/验证真相冻结成单一 closeout-ready story，而不是重开 production cleanup。
- live route truth 只能停留在 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 与 `tests/meta/governance_current_truth.py`；review docs / historical audit / archived evidence 只能 pull 当前真源。
- `FILE_MATRIX / RESIDUAL_LEDGER / KILL_LIST / PUBLIC_SURFACES / developer_architecture` 必须共同承认同一条 post-eradication topology、ownership 与 delete-gate truth；如果 active residual / kill target 为空，必须显式写空。
- 质量证明必须诚实覆盖 repo-wide freeze 所需的 lint / scripts / governance-meta / touched topical suites / broader proof；不得只跑局部 smoke。
- `Phase 88` 完成后下一步必须收口到 `$gsd-complete-milestone v1.23`，不能继续停留在 discuss/plan/execute 回路。

### Deferred / Out of Scope
- 不重开 `Phase 85`~`87` 已关闭的 production residual、assurance hotspot topicization 与 delete-gate争议。
- 不提前做 `v1.23` milestone archive promotion、evidence-index promotion 或 `v1.23-MILESTONE-AUDIT.md` 归档；那是 milestone closeout 工作。
- 不为了“看起来更干净”制造新的 file-delete campaign、虚假 residual 或无必要的大规模 prose 重写。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| `GOV-63` | `FILE_MATRIX / RESIDUAL_LEDGER / KILL_LIST / PUBLIC_SURFACES / developer_architecture` 必须共同冻结 post-eradication topology、ownership 与 delete-gate truth。 | 当前真实缺口集中在 evidence allowlist、historical audit 身份、zero-active posture 与 docs freshness，不在生产代码。 |
| `QLT-35` | touched scope 必须通过 repo-wide quality proof，并在 closeout 时实现 `zero orphan residuals`；若仍有 carry-forward，必须显式登记 owner、exit condition 与 evidence。 | `RESIDUAL_LEDGER` 已显示 active residual 为空，但 `KILL_LIST` 零态表达、`VERIFICATION_MATRIX` 的 `Phase 88` 合同与 focused guards 尚未补齐。 |

</phase_requirements>

## Summary

`Phase 85`~`87` 已经完成 repo-wide terminal audit、production residual closeout 与 assurance hotspot topicization。当前仓库最真实的缺口不再是生产代码，而是 **governance / evidence / verification 口径未完全冻结**：

1. `PROMOTED_PHASE_ASSETS.md` 仍落后于 `Phase 85`~`87` 已被其他文档当作长期证据消费的 closeout assets；
2. `VERIFICATION_MATRIX.md` 尚无 `Phase 88` closeout-ready contract，也没有 dedicated focused guard 冻结 `zero-active residual / zero-active kill target / default-next = complete-milestone`；
3. `V1_23_TERMINAL_AUDIT.md`、`PUBLIC_SURFACES.md`、`docs/developer_architecture.md` 与 live route docs 的 freshness / historical-role wording 仍有小范围漂移；
4. `KILL_LIST.md` 的 `Phase 85 Routed Delete Gates` 虽为空，但未显式表达 “none currently registered / historical-only”，距离 `zero orphan kill target` 还差最后一步 machine-checkable freeze。

**Primary recommendation:** 用 `3 个 sequential plans` 完成 `Phase 88`：
- Plan 1 收口 governance evidence / zero-active ledgers / docs freshness；
- Plan 2 建立 `Phase 88` focused guard 与 verification topology truth；
- Plan 3 跑 closeout proof、前推 live route 到 `Phase 88 complete`，并生成 phase-level verification / summary 资产。

## What the current repo already gets right

- `.planning/reviews/RESIDUAL_LEDGER.md` 已 truthfully 表示 active residual family 为空；`Phase 85` carry-forward 也已被 `Phase 87` closeout 关闭。
- `.planning/reviews/KILL_LIST.md` 已没有 `Phase 85+` active file-delete target；production residual 与 giant assurance carriers 都已被改写成 formal homes / topicized suites，而非 future file-kill campaign。
- `tests/meta/test_phase85_terminal_audit_route_guards.py`、`tests/meta/test_phase87_assurance_hotspot_guards.py` 与 route-handoff suites 已把审计历史与 current truth 分离出较成熟的 focused-guard 模式。
- `uv run python scripts/check_file_matrix.py --check`、`uv run python scripts/check_architecture_policy.py --check` 与当前关键 governance guards 均可通过，说明 `Phase 88` 更像“终局 freeze”而非“再做一次 repo rescue”。

## Concrete gaps found

### 1. Evidence identity conflict: `PROMOTED_PHASE_ASSETS.md` lags the already-consumed `Phase 85`~`87` closeout evidence

`ROADMAP.md`、`VERIFICATION_MATRIX.md`、`V1_23_TERMINAL_AUDIT.md` 与 `RESIDUAL_LEDGER.md` 已把 `Phase 85`~`87` summaries 当作长期 evidence / carry-forward consumption source；但 `PROMOTED_PHASE_ASSETS.md` 白名单仍停在 `Phase 84`。这会让“哪些 phase assets 算 governance evidence”出现双口径。

### 2. `Phase 88` has roadmap requirements but no machine-checkable verification contract yet

`ROADMAP.md`、`REQUIREMENTS.md` 已把 `GOV-63 / QLT-35` 挂到 `Phase 88`，但 `VERIFICATION_MATRIX.md` 最后只到 `Phase 87`。当前还没有 dedicated `Phase 88` guard 去冻结：
- zero-active residual / zero-active kill-target posture；
- `PUBLIC_SURFACES / developer_architecture / ledgers / verification bundle` 的同步完成态；
- final-phase next-step honesty（`$gsd-complete-milestone v1.23`）。

### 3. Historical audit / docs freshness still drift slightly from current route truth

`V1_23_TERMINAL_AUDIT.md` 仍写着 `Phase 87 execution-ready` 的 route string，而 live truth 已是 `Phase 87 complete`；`docs/developer_architecture.md` 仍自报 “Last aligned through Phase 85”。这些都属于 `Phase 88` 应收掉的 honesty/freshness 漂移。

### 4. Zero-active posture is real, but not fully frozen across all governance surfaces

`RESIDUAL_LEDGER.md` 已写 active residual 为空，但 `KILL_LIST.md` 只用空表表达 routed delete gates 为空，缺少显式文字冻结；`PUBLIC_SURFACES.md` 与 `docs/developer_architecture.md` 也尚未共同承认 `v1.23` closeout 后“不存在 active residual / active kill target regrowth story”。

### 5. Final-phase route freeze package is missing

`Phase 88` 是 `v1.23` 最后一个 active phase；完成后 live route 必须前推到 `Phase 88 complete`，requirements 应标记完成，default next 应切到 `$gsd-complete-milestone v1.23`，并需要 `88-VERIFICATION.md` / `88-SUMMARY.md` 与 promoted evidence allowlist 支撑。

## File-level implementation advice

### 88-01 governance evidence / zero-active ledger sync
- 更新 `.planning/reviews/PROMOTED_PHASE_ASSETS.md`，把 `Phase 85`~`87` 已被 current docs/verification 消费的 evidence assets 提升为 allowlisted governance evidence。
- 更新 `.planning/reviews/V1_23_TERMINAL_AUDIT.md`，明确它是 historical audit artifact，不再承担 live route truth；同时消除会误导维护者的 stale route wording。
- 更新 `.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md`、`.planning/baseline/PUBLIC_SURFACES.md`、`docs/developer_architecture.md`，显式冻结 `zero active residual / zero active kill target / docs aligned through Phase 88 freeze`。

### 88-02 focused guard + verification truth
- 新增 `tests/meta/test_phase88_governance_quality_freeze_guards.py`，直接守护：phase 85~87 evidence allowlist、zero-active ledgers、historical audit role、Phase 88 verification bundle / next-step honesty。
- 更新 `.planning/baseline/VERIFICATION_MATRIX.md`，为 `Phase 88` 添加 required artifacts / governance proof / runnable proof / unblock effect。
- 更新 `.planning/reviews/FILE_MATRIX.md` 与 `.planning/codebase/TESTING.md`，把新 guard 与 closeout proof entry 注册为 machine-checkable truth。

### 88-03 closeout-ready route advance
- 把 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`、`tests/meta/governance_current_truth.py`、`tests/meta/governance_followup_route_current_milestones.py`、`tests/meta/test_governance_route_handoff_smoke.py` 前推到 `Phase 88 complete / next = $gsd-complete-milestone v1.23`。
- 生成 `88-01/02/03-SUMMARY.md`、`88-SUMMARY.md`、`88-VERIFICATION.md`，并把 `88` phase-level evidence 加入 `PROMOTED_PHASE_ASSETS.md`。
- 验证通过后，`gsd-tools init progress` 与 `state json` 应体现 `v1.23` 全部 phases complete；`$gsd-next` 应自动路由到 `$gsd-complete-milestone v1.23`。

## Suggested Plan / Wave Shape

| Wave | Plan | Objective |
|------|------|-----------|
| 1 | `88-01` | freeze governance evidence identity, zero-active ledgers, and doc freshness |
| 2 | `88-02` | add focused Phase 88 guards and verification/file-governance truth |
| 3 | `88-03` | execute closeout proof, promote evidence, and advance live route to `Phase 88 complete` |

**Why this is optimal:** `88-01` 先把治理资产口径统一，避免后续 guard 建在漂移文档之上；`88-02` 再把这些事实 machine-checkable 化；`88-03` 最后统一写回 live route、requirements 与 verification assets，保持 final-phase honesty。

## Recommended validation bundle

- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run pytest -q tests/meta`
- `uv run pytest -q tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_diagnostics_service_*.py tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_contract_*.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/runtime/test_mqtt_runtime_*.py`
- 若时间/环境允许，追加：`uv run pytest -q tests/ --ignore=tests/benchmarks`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`

## Sources

### Primary (HIGH confidence)
- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/V1_23_TERMINAL_AUDIT.md`
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-RESEARCH.md`
- `.planning/phases/87-assurance-hotspot-decomposition-and-no-regrowth-guards/87-RESEARCH.md`
- `tests/meta/governance_current_truth.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/test_phase85_terminal_audit_route_guards.py`
- `tests/meta/test_phase87_assurance_hotspot_guards.py`
- `tests/meta/test_governance_closeout_guards.py`
- `scripts/check_file_matrix.py`
- `scripts/check_architecture_policy.py`

### Secondary (MEDIUM confidence)
- `.planning/codebase/TESTING.md`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_toolchain_truth.py`

## Metadata

- **Architecture / scope confidence:** HIGH
- **Evidence conflict diagnosis confidence:** HIGH
- **Final validation cost estimate:** MEDIUM-HIGH (broad meta + optional full-suite pass)
- **Research valid until:** 2026-03-28
