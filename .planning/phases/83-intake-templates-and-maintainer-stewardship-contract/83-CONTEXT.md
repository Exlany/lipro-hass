# Phase 83: Intake templates and maintainer stewardship contract - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Source:** v1.22 milestone continuation after Phase 82 closeout

<domain>
## Phase Boundary

本 phase 只处理 community-health intake 与 maintainer stewardship contract：

- 把 `.github/ISSUE_TEMPLATE/{bug.yml,feature_request.yml,config.yml}`、`.github/pull_request_template.md` 与 `SECURITY.md` 收口为 evidence-first intake surfaces
- 把 `CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`docs/README.md` 与 `.github/CODEOWNERS` 收口为 contributor-facing maintainer ownership / triage / continuity contract
- 把上述 truth 投影到 governance-only ledger 与既有 focused proof surfaces（以 `.planning/baseline/GOVERNANCE_REGISTRY.json`、`tests/meta/test_governance_release_docs.py`、`tests/meta/test_governance_release_continuity.py`、`tests/meta/test_version_sync.py` 为主），避免继续依赖隐性口头知识
- 不重开 release route / changelog / archived evidence pointer；不更新 active-route / default-next / milestone completion truth；不补齐 focused guard coverage

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- 本 phase 对应 `ROADMAP.md` 中 `Phase 83`，必须只覆盖 `GOV-61` 与 `OSS-11`
- issue / PR / security intake 必须收集最小充分证据：复现步骤、影响边界家族、风险/影响面、验证命令或等价证明、以及正确 disclosure route
- docs-first/public-first-hop 仍以 `docs/README.md` → `docs/TROUBLESHOOTING.md` / `SUPPORT.md` / `SECURITY.md` 为正式首跳；GitHub issue/PR/security UI 只是当前 access mode 下可见时成立的条件性 intake surface
- security intake 的正式 home 仍是 `SECURITY.md` 与 `.github/ISSUE_TEMPLATE/config.yml` 的 contact links；不得编造新的 GitHub security advisory template 文件
- maintainer stewardship truth 必须继续诚实承认 single-maintainer / no-hidden-delegate / no documented delegate；`.github/CODEOWNERS` 仍是 owner / custody truth 的 formal source
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 继续保持 maintainer-only appendix；本 phase 只能让 contributor-facing docs 引到正确 stewardship surfaces，不能把 runbook 重新抬升为 public first hop
- `.planning/baseline/GOVERNANCE_REGISTRY.json` 可承载 machine-readable intake / stewardship facts，但 active route、default next 与 phase-complete freeze 仍属于 planning governance-route contract family 与 `Phase 84`
- 不新增依赖，不新增第二套 community-health docs tree，也不为“形式完整”而添加仓库中不存在的 policy/template 文件

### The Agent's Discretion
- evidence-first intake 字段可以使用显式字段或精简 checklist/callout，但必须保持最小、可读、可执行
- contributor-facing stewardship contract 的最终落点可以在 `CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`docs/README.md` 之间择优分工，但不得重复整份 maintainer appendix
- governance-only truth projection 以 `.planning/baseline/GOVERNANCE_REGISTRY.json` 与既有 focused suites 为主；若出现更广的 baseline narrative freeze 需求，统一留给 `Phase 84`

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Governance / route truth
- `AGENTS.md` — 仓库级执行契约、模板/docs 修改与验证命令约束
- `.planning/PROJECT.md` — `v1.22` 当前目标、开源协作边界与 why-now
- `.planning/ROADMAP.md` — `Phase 83` / `Phase 84` 分界、success criteria 与 requirement mapping
- `.planning/REQUIREMENTS.md` — `GOV-61` 与 `OSS-11` 的正式 requirement wording
- `.planning/STATE.md` — 当前 active route 与“下一步是 Phase 83”的 continuity context

### Intake surfaces
- `.github/ISSUE_TEMPLATE/bug.yml` — 现有 bug intake baseline
- `.github/ISSUE_TEMPLATE/feature_request.yml` — 现有 feature intake baseline
- `.github/ISSUE_TEMPLATE/config.yml` — issue UI contact / routing baseline
- `.github/pull_request_template.md` — PR intake / CI contract baseline
- `SECURITY.md` — private disclosure 与 security triage contract

### Stewardship / contributor docs
- `CONTRIBUTING.md` — contributor workflow 与 PR contract home
- `SUPPORT.md` — support boundary、triage ownership、best-effort posture
- `docs/README.md` — canonical docs map / maintainer appendix reachability
- `.github/CODEOWNERS` — maintainer owner / custody truth source
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` — maintainer-only continuity / custody appendix（仅作引用，不是本 phase 的 public home）

### Governance ledgers / guard baseline
- `.planning/baseline/GOVERNANCE_REGISTRY.json` — machine-readable governance facts projection home
- `tests/meta/test_governance_release_docs.py` — docs/template route-consistency baseline
- `tests/meta/test_governance_release_continuity.py` — continuity / custody wording baseline
- `tests/meta/test_version_sync.py` — registry/docs/template sync baseline

</canonical_refs>

<specifics>
## Specific Ideas

- `bug.yml` 已有 diagnostics-first、security reroute、复现步骤与 expected behavior，但尚未显式要求影响边界家族、风险/影响面与验证命令
- `feature_request.yml` 目前更像需求收集表，而非 maintainer-friendly evidence router；它缺少 boundary / impact / validation expectation
- `.github/pull_request_template.md` 已有 CI checklist，但 `Summary` / `Testing` 仍偏自由文本，尚未把 affected boundary family、risk / impact、docs / disclosure follow-up 结构化
- `SUPPORT.md`、`SECURITY.md` 与 `.github/CODEOWNERS` 已有 continuity truth，但 `CONTRIBUTING.md` / `docs/README.md` 还没有把 maintainer ownership、review expectations 与 handoff rules 收口成一份 contributor-facing stewardship contract
- governance registry 目前已记录 support/documentation route 与 continuity phrases，但尚未承载 intake evidence contract 与 stewardship projection 的更细粒度 machine-readable truth；既有 focused suites 也还没有把这组字段/措辞冻结成 targeted proof

</specifics>

<deferred>
## Deferred Ideas

- focused guards、`PROJECT/ROADMAP/REQUIREMENTS/STATE/MILESTONES` current-story freeze、以及 `governance_current_truth.py` 前推归 `Phase 84`
- `VERIFICATION_MATRIX.md` 的 route-freeze / guard-proof 对齐归 `Phase 84`
- release runbook、changelog、archive evidence pointer 与 version-sync 主线已在 `Phase 82` 收口，本 phase 不重开
- README / README_zh / contributor architecture map 的 broader public-entry restructuring 不属于本 phase，除非只是必要的最小交叉链接修正

</deferred>
