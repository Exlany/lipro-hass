# Phase 78 Research

## Inputs

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
- `tests/meta/governance_current_truth.py`
- `tests/meta/test_governance_bootstrap_smoke.py`
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/toolchain_truth_checker_paths.py`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`

## Findings That Directly Drive Implementation

### 1. `Phase 76 execution-ready` 已成为 stale current story

`PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / governance_current_truth.py` 目前仍一致，但一致地停留在旧 truth：

- active route = `v1.21 active route / Phase 76 execution-ready / latest archived baseline = v1.20`
- default next command = `$gsd-execute-phase 76`
- milestone status = `execution-ready (2026-03-26)`

在 `Phase 76 / 77` 已完成、`Phase 78` 即将完成的前提下，这种 truth 会让：

- `gsd-tools` fast path 继续把 live route 理解成“准备执行 opening phase”；
- later closeout readiness 缺少 repo-local、machine-checkable 入口；
- `$gsd-next` 无法自然落到 `$gsd-complete-milestone v1.21`。

### 2. 需要一条专门的 route-handoff smoke，而不是继续向 bootstrap / closeout mega-suite 加压

现有分工已经相对清晰：

- `test_governance_bootstrap_smoke.py`：bootstrap/current-route 最小充分 smoke
- `test_governance_closeout_guards.py`：verification/file-matrix/promoted-assets anchor
- `governance_followup_route_current_milestones.py`：historical follow-up route consistency

Phase 78 最缺的是 `gsd-tools` fast path 与 closeout-ready wording 的 focused smoke。如果继续塞进 bootstrap smoke 或 closeout guards，会再次模糊 concern boundary。

### 3. `state json` / `init progress` / `phase-plan-index` 必须成为 Phase 78 的一等证据

用户这轮明确要求走 `$gsd-plan-phase -> $gsd-execute-phase -> $gsd-next`，因此最诚实的验证不只是文档字符串匹配，而是：

- `init progress` 能看见 `Phase 78` 已 complete / no incomplete plans；
- `state json` 能反映 frontmatter 的 `3 phases / 9 plans` completion；
- `phase-plan-index 78` 没有 incomplete plans。

这些命令不应只在命令行人工 spot-check 一次，而应进入 focused meta smoke。

### 4. closeout-ready 需要同步冻结 promoted assets 与 review ledgers

如果 live docs 前推到 `Phase 78 complete`，但 `PROMOTED_PHASE_ASSETS / RESIDUAL_LEDGER / KILL_LIST` 不更新，就会留下两类漂移：

- closeout-ready route 缺少长期 evidence allowlist；
- repo review ledgers 还停在 `Phase 71`，看不出 `v1.21` 没有新增 active residual / kill target。

为了让后续 archive promotion 低维护，Phase 78 需要直接补齐这些治理面。

### 5. 最优解是“前推 live route + 增加 fast-path smoke + 冻结 closeout evidence”，而不是“马上归档”

本轮的正确终态是：

- `v1.21` 仍是 active milestone；
- 当前 route 已是 `Phase 78 complete`；
- milestone status = `closeout-ready`；
- default next command = `$gsd-complete-milestone v1.21`。

这样既诚实反映已完成事实，也不偷跑 archive promotion。

## Rejected Alternatives

- **直接执行 `$gsd-complete-milestone v1.21`，不补 live route-handoff guards**：会让 closeout-ready 判定再次依赖对话残影，而不是 repo truth。
- **继续沿用 `Phase 76 execution-ready`，只在最终报告里说明 `78` 已完成**：这是典型的 prose-over-truth 漂移，无法满足 `GOV-57 / QLT-31`。
- **把 gsd fast path 断言塞进 `test_governance_bootstrap_smoke.py`**：会重新混合 bootstrap activation 与 closeout handoff concern。
- **不更新 `PROMOTED_PHASE_ASSETS / RESIDUAL_LEDGER / KILL_LIST`**：后续 archive promotion 仍需回头补治理资产，Phase 78 就不算“低维护 closeout-ready”。
