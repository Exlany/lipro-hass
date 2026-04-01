# Phase 124 Research

**Status:** ready

## Research Verdict

- `config_flow.py` 的正式 home 叙事已基本正确，但 persisted auth seed 语义与 schedule direct-call contract 仍未完全 single-source；本 phase 应把这两组 carry-forward 一次收口为 control-plane 的最终 closeout。

## Recommended Scope

- 让 `entry_auth` family 成为 `CONF_PASSWORD_HASH` / `CONF_REMEMBER_PASSWORD_HASH` / `CONF_BIZ_ID` 的唯一 persisted auth-seed 解释与回写真源。
- 把 `config_flow.py` 的 user / reauth / reconfigure branching 下沉到 `flow/` 下的 localized step handlers，根层仅保留 HA adapter glue。
- 在 `services/contracts.py` 中补齐 schedule direct-call normalization 与 named result types，并让 `services/schedule.py` inward 消费这些 contracts。
- 用 focused regressions 冻结 stale `biz_id` 清空、malformed reconfigure parity、schedule direct-call bad payload validation 与 typed result shape。
- 同步 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 以及 FILE_MATRIX / RESIDUAL_LEDGER / KILL_LIST / codebase docs / TESTING truth，使 `Phase 124` 成为 v1.35 的诚实最终 carry-forward。

## Risks and Guardrails

- 不改 config-entry key names，不重写 `AuthBootstrapSeed` / `HeadlessBootContext` public semantics。
- 不引入第二套 flow root；新 helper 只能留在既有 `flow/` 或 `entry_auth` 正式 home 下。
- `schedule` 只闭合 boundary contract，不动 coordinator/protocol 主链与 service router outward registration。
- 测试必须覆盖 direct-call path，而不是只依赖 service registry schema 间接兜底。
- 治理文档只能讲 single mainline，不得把新 helper 叙述成新的 compat shell 或第二 story。

## Suggested Plan Split

### Plan 124-01
- 目标：冻结 v1.35 execution-ready route truth，并把 Phase 124 assets 压实为五计划 inventory。
- 依赖：无。
- 验证：`node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 124`、`node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 124`、focused governance route smoke。

### Plan 124-02
- 目标：收口 config-entry auth seed semantics，并把 `config_flow.py` 压回 thin adapter；补 flow/token persistence focused regressions。
- 依赖：124-01。
- 验证：flow suites + token persistence suites。

### Plan 124-03
- 目标：闭合 schedule direct-call formal contract，补 typed result / normalization / focused runtime/service guards。
- 依赖：124-01, 124-02。
- 验证：schedule suites + runtime contract guard。

### Plan 124-04
- 目标：把 planning roots、review ledgers、baseline/developer projections 翻转到 `Phase 124 complete; closeout-ready`，且不让单计划文件面失控。
- 依赖：124-02, 124-03。
- 验证：governance route smoke + release contract + file-matrix/public-surface guards。

### Plan 124-05
- 目标：冻结 codebase/testing projections、focused meta guard 与 phase summary / verification evidence chain，为 v1.35 milestone closeout 提供 repo-local proof。
- 依赖：124-04。
- 验证：focused meta guard + runtime contract truth + phase summary / verification chain。
