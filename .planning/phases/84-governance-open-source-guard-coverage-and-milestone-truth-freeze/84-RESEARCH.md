# Phase 84 Research — Governance/open-source guard coverage and milestone truth freeze

## Summary

`Phase 81`~`83` 已把 public entry、release operations、community-health intake 与 maintainer stewardship contract 收口成一条更诚实的外部协作路线；现在剩下的真正缺口不是再写一轮 prose，而是补齐 focused guard coverage 并把 `v1.22` 的 current-route / closeout-ready truth 冻结为 machine-checkable bundle。最佳策略是复用现有 governance/open-source suites 与 shared helpers，避免新增 giant guard 文件，同时把 touched ledgers 明确同步到 `Phase 84` closeout truth。

## What the current repo already gets right

- `tests/meta/test_governance_bootstrap_smoke.py` 与 `tests/meta/test_governance_route_handoff_smoke.py` 已能覆盖 active-route / default-next / latest archived pointer 的基础 smoke。
- `tests/meta/test_governance_release_docs.py`、`tests/meta/test_governance_release_continuity.py` 与 `tests/meta/test_version_sync.py` 已覆盖 docs-first routing、continuity wording、registry-backed community-health metadata 与 template field IDs。
- `.planning/baseline/GOVERNANCE_REGISTRY.json` 已成为 intake / continuity / docs-route 的 machine-readable governance metadata home，没有越权承载 milestone route truth。
- `Phase 83` 已把 issue / PR / security / support / stewardship story 收口到 `.github/*`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`docs/README.md` 与 `.github/CODEOWNERS`，当前不需要再起第二套 open-source docs tree。

## Concrete gaps found

### 1. Active-route smoke still proves only the route, not the public-entry / template contract surrounding it

`test_governance_bootstrap_smoke.py` 现在只断言：
- planning docs / state / verification matrix 的 current route 仍是 `Phase 83 complete`
- public docs 没有暴露 internal bootstrap story

它没有继续验证：
- `docs/README.md` 作为 canonical docs map 是否仍把 community-health contract 与 docs-first route 维持为 formal first hop
- `.github/ISSUE_TEMPLATE/config.yml` 的 Documentation link 是否仍与 `docs/README.md` / access-mode honesty 同步
- template evidence freeze 是否仍与 registry-backed metadata 对齐

这会让 route truth 与 public-entry truth 之间仍然存在小范围 drift 空间。

### 2. Registry-backed template checks exist, but docs-entry / contact-link drift is still split across suites

`test_version_sync.py` 已校验：
- `community_health` required field IDs / PR headings / security evidence tokens
- docs index route 与 documentation URL projection

但还没形成一条更 focused 的“docs-entry + issue contact link + template evidence contract”组合 guard；当前需要在现有 suites 中补几处桥接断言，让失败更快指向真实 drift family。

### 3. Verification / review ledgers still stop at Phase 83 current story

`VERIFICATION_MATRIX.md` 当前最新 `v1.22` active-route writeback 仍停在 `Phase 83 Intake / Stewardship Contract`。`RESIDUAL_LEDGER.md` 与 `KILL_LIST.md` 也只记录到 `Phase 83` residual/status delta。即便当前 repo 已准备进入 `Phase 84`，这些 ledgers 仍缺少：
- `Phase 84` focused guard coverage 的正式 artifact / runnable-proof 说明
- final phase closeout 应回到 milestone closeout 的 next-step honesty
- “无新增 residual / kill target”的显式记账

### 4. Final-phase route freeze has no closeout-ready package yet

`v1.22` 目前仍是 `Phase 83 complete`。如果直接停在这里，`$gsd-next` 之前仍需人工记忆“还差一个 focused governance/open-source freeze phase”。需要把 `Phase 84` 的 closeout bundle 做成和 `Phase 80` 类似的最终收口包：
- `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / governance_current_truth.py` 同步到 `Phase 84 complete`
- `PROMOTED_PHASE_ASSETS.md` 收录 `84-*SUMMARY/VERIFICATION/VALIDATION`
- `governance_followup_route_current_milestones.py`、`bootstrap_smoke`、`route_handoff_smoke`、`closeout_guards`、`promoted_phase_assets` 共同承认下一步是 `$gsd-complete-milestone v1.22`

## File-level implementation advice

### 84-01 focused guards
- 优先扩展 `tests/meta/governance_contract_helpers.py`，把 docs-entry / public-doc-hidden-bootstrap / template-evidence helper 统一到 shared home，减少新 literal 扩散。
- 在 `tests/meta/test_governance_bootstrap_smoke.py` 增补 active-route + docs-entry / Documentation link / public-first-hop smoke。
- 在 `tests/meta/test_governance_release_docs.py` 与 `tests/meta/test_version_sync.py` 收紧 community-health contract、template evidence fields、registry projection 与 docs-entry contact link 的组合证明。
- 仅在现有 concern home 明显容纳不下时新增测试文件；当前更优方案是就地拆成小断言。

### 84-02 verification / review writeback
- `VERIFICATION_MATRIX.md` 新增 `Phase 84` 段落，明确 required artifacts、required governance proof、required runnable proof 与 unblock effect。
- `FILE_MATRIX.md` 只为新 helper/test home 或 closeout assets 增补行项，不做大范围重排。
- `RESIDUAL_LEDGER.md` / `KILL_LIST.md` 明确写出 “无新增 active residual / kill target”，并把 future work 严格限制为 milestone closeout，而不是再开 phase。

### 84-03 closeout truth freeze
- 把 live route 前推到 `v1.22 active route / Phase 84 complete / latest archived baseline = v1.21`。
- `default_next_command` 改为 `$gsd-complete-milestone v1.22`；`gsd-tools init progress` 应表现为 `current_phase = null` / `next_phase = null` / all phases complete。
- 生成 `84-01/02/03-SUMMARY.md`、`84-SUMMARY.md`、`84-VERIFICATION.md`、`84-VALIDATION.md`，并同步 `PROMOTED_PHASE_ASSETS.md`。

## Recommended validation bundle

- `uv run ruff check tests/meta/governance_contract_helpers.py tests/meta/governance_current_truth.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_version_sync.py`
- `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_version_sync.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run python scripts/check_architecture_policy.py --check`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
