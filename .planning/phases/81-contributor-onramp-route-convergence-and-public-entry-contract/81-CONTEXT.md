# Phase 81: Contributor onramp route convergence and public entry contract - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Source:** v1.22 milestone initialization + contract-driven follow-through

<domain>
## Phase Boundary

本 phase 只处理对外 first-hop 与 contributor-facing architecture guidance：

- 统一 `README.md`、`README_zh.md`、`docs/README.md`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md` 的入口叙事、交叉链接与角色分流
- 输出一份 contributor-facing 的架构变更地图，告诉外部贡献者“改哪里、不能碰哪里、改完要回写哪些证据”
- 保持 public docs 隐藏 internal bootstrap / archived-route 细节，不把 `.planning/` 当前治理真相直接暴露到 public entry
- 不在本 phase 重开 runtime / protocol production surgery；任何生产代码整治只允许以架构地图中的 evidence / boundary 约束形式出现

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- 本 phase 对应 `ROADMAP.md` 中 `Phase 81`，必须只覆盖 `OSS-10` 与 `DOC-08`
- 对外入口必须是一条单一路由：用户/贡献者先看 README 与 docs index，需要贡献时落到 `CONTRIBUTING.md`，需要支持时落到 `SUPPORT.md`，安全问题走 `SECURITY.md`
- 文档必须双语协同：`README.md` 与 `README_zh.md` 不能讲两套不同的 project/support/contribution story
- contributor-facing 架构地图必须显式说明 protocol / runtime / control / external-boundary / governance 这 5 类改动边界
- contributor-facing 架构地图必须告诉贡献者：改动 public surface / dependency / authority / file ownership / residual 时，要同步哪些 `.planning/` 基线与 ledger
- public docs 不能暴露 internal bootstrap folklore、active archived pointer、GSD 内部命令流或其它只属于维护者内部的 current-governance 细节
- 不为“看起来完整”而新增第二套 docs tree；优先复用现有 public docs homes
- 不为 docs phase 引入新依赖；只改现有 markdown / templates / guards / 必要的 focused tests

### The Agent's Discretion
- architecture change map 的最终文件名与落点，可在现有 docs 结构内择优决定，但必须可从 README / CONTRIBUTING / docs index 稳定抵达
- 各入口文档中的表格、callout、FAQ 或 checklist 形式可按可读性选择
- focused guards 的切片方式可自由设计，但必须定位精确且不把 Phase 81 真相写成第二套 current-governance story

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / governance truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 单一正式主链与五平面边界的最高裁决
- `AGENTS.md` — 仓库级执行契约、文档回写规则、测试命令与 architecture hygiene 约束
- `.planning/PROJECT.md` — `v1.22` 当前 milestone 目标、target features 与 key context
- `.planning/ROADMAP.md` — `Phase 81` goal / success criteria / plan skeleton
- `.planning/REQUIREMENTS.md` — `OSS-10`、`DOC-08` 的正式 requirement wording
- `.planning/STATE.md` — 当前 active route、default next command 与 continuity anchors

### Public entry surfaces
- `README.md` — 英文 first-hop 入口
- `README_zh.md` — 中文 first-hop 入口
- `docs/README.md` — docs index / navigation home
- `CONTRIBUTING.md` — contributor contract home
- `SUPPORT.md` — support boundary / triage entry
- `SECURITY.md` — security disclosure route

### Contributor / maintainer intake
- `.github/pull_request_template.md` — current PR intake contract
- `.github/ISSUE_TEMPLATE/bug.yml` — bug intake baseline
- `.github/ISSUE_TEMPLATE/feature_request.yml` — feature intake baseline
- `.github/ISSUE_TEMPLATE/config.yml` — issue-routing baseline

### Governance / evidence destinations
- `.planning/baseline/PUBLIC_SURFACES.md` — public surface truth
- `.planning/baseline/DEPENDENCY_MATRIX.md` — dependency truth
- `.planning/baseline/AUTHORITY_MATRIX.md` — authority / truth-source matrix
- `.planning/baseline/VERIFICATION_MATRIX.md` — required verification / artifact matrix
- `.planning/reviews/FILE_MATRIX.md` — file ownership / fate matrix
- `.planning/reviews/RESIDUAL_LEDGER.md` — active / closed residual registry
- `.planning/reviews/KILL_LIST.md` — delete-gate registry

</canonical_refs>

<specifics>
## Specific Ideas

- 建议把“如何贡献 / 需要去哪份文档”收口成统一入口矩阵，而不是让 README/CONTRIBUTING/SUPPORT/SECURITY 各自平行陈述
- 架构地图应面向外部贡献者，关注“允许改什么 / 不要直连什么 / 改完去哪里补证据”，而不是重复完整北极星文档
- phase 成功后，应能从 README 或 docs index 以不超过 2 跳到达 contributor onboarding 与 architecture change map
- focused guards 需要验证双语入口、security/support/contributing links、以及 architecture map 的可达性与 boundary wording

</specifics>

<deferred>
## Deferred Ideas

- release runbook、changelog、version sync、archive evidence-chain 的 maintainer 主线归 `Phase 82`
- issue / PR / security intake 表单的证据字段与 maintainer stewardship contract 归 `Phase 83`
- 更大范围的 open-source / governance focused guard freeze 归 `Phase 84`
- 任何 production runtime/protocol refactor 均不属于本 phase

</deferred>
