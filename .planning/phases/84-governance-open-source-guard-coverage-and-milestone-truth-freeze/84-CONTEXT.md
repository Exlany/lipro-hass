# Phase 84: Governance/open-source guard coverage and milestone truth freeze - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Source:** v1.22 milestone continuation after Phase 83 closeout

<domain>
## Phase Boundary

本 phase 只处理 focused governance / open-source assurance 收口：

- 为 active-route、docs-entry、community-health template evidence、release / version links、latest archived pointer 补齐 focused guards，确保 `Phase 81`~`83` 新形成的协作契约可持续防漂移。
- 把上述 focused proof 回写到 `VERIFICATION_MATRIX.md` 与 review ledgers，形成一条 machine-checkable 的 `v1.22` milestone truth freeze。
- 收口 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / governance_current_truth.py` 的 live route truth，让本里程碑在完成后诚实落到 `Phase 84 complete / closeout-ready`。
- 不重写 `Phase 81`~`83` 已完成的 docs / template narrative，除非 guard 明确暴露真实 drift；不把历史 archive assets 重新抬升成 live route source；不重开生产代码架构 surgery。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- 本 phase 对应 `ROADMAP.md` 中 `Phase 84`，必须只覆盖 `TST-26` 与 `QLT-34`。
- focused guards 优先复用现有 concern homes：`test_governance_bootstrap_smoke.py`、`test_governance_route_handoff_smoke.py`、`test_governance_release_docs.py`、`test_governance_release_continuity.py`、`test_version_sync.py` 与 shared governance helpers；只有在 concern home 明显缺失时才新增文件。
- active-route / default-next / latest archived pointer 的唯一 formal machine truth 继续是 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 的 shared `governance-route` contract + `tests/meta/governance_current_truth.py`；不得复制第二套 live route literal。
- `docs/README.md` 继续是 canonical docs map / public docs first hop；`.github/ISSUE_TEMPLATE/config.yml` 的 Documentation link、`README(.md/.zh)`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md` 与 PR / issue templates 只能投影 docs-first / access-mode honesty，不能泄露 internal route folklore。
- `.planning/baseline/GOVERNANCE_REGISTRY.json` 可继续承载 community-health / continuity / docs-route metadata，但不能越权承载 milestone route truth。
- `latest archived evidence index` 与 `archived milestone audit` 继续只保留 historical / pull-only 身份；guards 可以验证 pointer honesty，但 public docs 不得把真实 `.planning/...` internal path 暴露为 first hop。
- 因为 `Phase 84` 是 `v1.22` 的最后一个 active phase，完成后 live route 必须前推到 `v1.22 active route / Phase 84 complete / latest archived baseline = v1.21`，且默认下一步回到 `$gsd-complete-milestone v1.22`。

### The Agent's Discretion
- 若新增 helper 能明显减少 governance literal duplication，可局部提炼到 `tests/meta/governance_contract_helpers.py`；否则优先保持断言就近可读。
- docs-entry / template-evidence drift 的 focused guards 可以分散在 2~4 个现有 suites 中，只要 concern boundary 清晰、失败定位更好。
- review ledgers 若没有新增 residual / kill target，必须显式写“无新增”，而不是留空白暗示待清理。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Active route / planning truth
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `tests/meta/governance_current_truth.py`
- `tests/meta/governance_followup_route_current_milestones.py`

### Focused governance / open-source proof surfaces
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `tests/meta/governance_contract_helpers.py`
- `tests/meta/test_governance_bootstrap_smoke.py`
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_governance_promoted_phase_assets.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/test_governance_release_contract.py`
- `tests/meta/test_governance_release_docs.py`
- `tests/meta/test_governance_release_continuity.py`
- `tests/meta/test_version_sync.py`

### Docs / templates / contributor-facing entry surfaces
- `README.md`
- `README_zh.md`
- `docs/README.md`
- `CONTRIBUTING.md`
- `SUPPORT.md`
- `SECURITY.md`
- `.github/CODEOWNERS`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`

</canonical_refs>

<specifics>
## Specific Ideas

- 把 active-route smoke、docs-entry honesty、template evidence-field freeze 与 latest archived pointer honesty 做成更明确的 focused contract，而不是继续依赖跨 3~4 个文件的人肉串联判断。
- 让 `VERIFICATION_MATRIX.md` 与 review ledgers 明确承认 `Phase 84` 只是在 `Phase 81`~`83` 已成形协作契约上补 guard / freeze truth，而不是又造一条第二路线。
- closeout bundle 需要明确记录：`Phase 84` 完成后下一步是 milestone closeout，而不是继续停留在 `$gsd-discuss-phase` / `$gsd-plan-phase`。

</specifics>

<deferred>
## Deferred Ideas

- `v1.22` 的 milestone archive promotion / evidence index promotion 属于 milestone closeout，而不是本 phase。
- 若 public docs / templates 未暴露真实 drift，不为了“看起来更完整”重写现有 prose。
- 任何 protocol / runtime / control production code 重构、命名整理或 residual surgery 都不属于本 phase。

</deferred>
