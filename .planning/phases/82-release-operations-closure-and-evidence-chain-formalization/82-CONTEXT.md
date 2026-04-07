# Phase 82: Release operations closure and evidence-chain formalization - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Source:** v1.22 milestone continuation after Phase 81 closeout

<domain>
## Phase Boundary

本 phase 只处理 maintainer-facing release route 与 archived evidence pull-chain 的单一路由：

- 收口 `docs/MAINTAINER_RELEASE_RUNBOOK.md`、`CHANGELOG.md`、`docs/README.md`、version-sync truth 与 archived evidence pointer 的 maintainer-facing release story
- 清理 `.planning/reviews/V1_21_EVIDENCE_INDEX.md`、`.planning/v1.21-MILESTONE-AUDIT.md`、`.planning/baseline/AUTHORITY_MATRIX.md` 中把历史档案误写成 current governance truth 的残留叙事
- 冻结 `Phase 82 complete` 的 planning route contract、baseline/review truth 与 focused release/governance guards
- 不重开 production runtime / protocol surgery，不扩张 issue / PR / security intake 模板字段，也不把 `.planning/*` 重新包装成 public first hop

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- 本 phase 对应 `ROADMAP.md` 中 `Phase 82`，必须只覆盖 `GOV-60` 与 `ARC-21`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 是唯一 maintainer-facing release flow home；`CHANGELOG.md` 只负责 release notes / release posture 摘要，不再讲第二套 runbook
- `pyproject.toml`、`custom_components/lipro/manifest.json`、`custom_components/lipro/const/base.py` 继续是 package semver canonical sources；不得把 milestone version 写成 package version
- `.planning/reviews/V1_21_EVIDENCE_INDEX.md` 与 `.planning/v1.21-MILESTONE-AUDIT.md` 必须保持 archive / historical identity，不再承载 current route / default next truth
- current active-route / default-next-command / latest archived pointer 的 machine-readable formal home 仍然只在 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 的 `governance-route` blocks 与 `tests/meta/governance_current_truth.py`
- `docs/README.md` 可以提供 maintainer appendix reachability，但不得让 archived evidence pointer 回流为 public first hop
- workflow YAML 只有在发现真实 drift 时才改；若现有 `ci.yml` / `release.yml` 已正确，就优先通过 docs + tests + planning truth 收口
- 不为“完美对称”去修改 root README；release/evidence maintainer appendix 只在真正需要的 maintainer-facing docs 中显式出现

### The Agent's Discretion
- runbook 中预检命令可以选择显式展开，或改写为“以 `ci.yml` governance lane 为准”的单一路径，但必须避免再次漂移
- `CHANGELOG.md` 的 Unreleased 小节可以按 Added / Changed / Fixed 组织，只要能诚实覆盖当前 release operations hardening
- focused guards 的切片方式可自由设计，但必须优先验证 single release route、archive-only evidence identity、version sync、GSD fast-path truth 与 latest archived pointer 的一致性

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Governance / route truth
- `AGENTS.md` — 仓库级执行契约、release/docs/governance hygiene 约束
- `.planning/PROJECT.md` — `v1.22` 当前 milestone 目标与当前 active route
- `.planning/ROADMAP.md` — `Phase 82` goal / success criteria / plan skeleton
- `.planning/REQUIREMENTS.md` — `GOV-60`、`ARC-21` 的正式 wording
- `.planning/STATE.md` — 当前 milestone mode / next-step / execution status
- `.planning/MILESTONES.md` — archived vs active milestone continuity truth
- `.planning/baseline/AUTHORITY_MATRIX.md` — authority chain 与 archive-evidence identity
- `.planning/baseline/VERIFICATION_MATRIX.md` — required proof / promoted-evidence / release-contract verification baseline
- `.planning/reviews/FILE_MATRIX.md` — file ownership / release-guard homes
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` — promoted phase evidence allowlist

### Release route homes
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` — maintainer release / rehearsal / custody truth home
- `CHANGELOG.md` — release-facing notes / unreleased release posture summary
- `docs/README.md` — docs navigation + maintainer appendix reachability
- `.github/workflows/ci.yml` — governance/test/preview workflow anchor
- `.github/workflows/release.yml` — tagged release gate / asset publish workflow anchor
- `pyproject.toml`, `custom_components/lipro/manifest.json`, `custom_components/lipro/const/base.py` — canonical version-sync triad

### Archived evidence pull chain
- `.planning/reviews/V1_21_EVIDENCE_INDEX.md` — latest archived evidence index
- `.planning/v1.21-MILESTONE-AUDIT.md` — archived verdict home
- `.planning/milestones/v1.21-ROADMAP.md` / `.planning/milestones/v1.21-REQUIREMENTS.md` — archived planning snapshots

### Focused guards
- `tests/meta/governance_current_truth.py` — machine-readable current-route contract
- `tests/meta/test_governance_release_contract.py` — release workflow / runbook / governance anchor suite
- `tests/meta/test_governance_release_docs.py` — release/docs/private-access/maintainer appendix guard suite
- `tests/meta/test_governance_route_handoff_smoke.py` — current route / next-phase / GSD fast-path smoke guard
- `tests/meta/governance_followup_route_current_milestones.py` — active milestone + archived pointer follow-up truth
- `tests/meta/test_version_sync.py` — version-sync contract

</canonical_refs>

<specifics>
## Specific Ideas

- maintainer-facing release route 应该是一条线：`docs/README.md` maintainer appendix → `docs/MAINTAINER_RELEASE_RUNBOOK.md` → version-sync triad + release workflows + latest archived evidence pointer
- `CHANGELOG.md` 需要补上 release route 已存在但尚未记账的硬化项：CI reuse、tagged `CodeQL` gate、`pip-audit` gate、`SBOM` / attestation / `cosign` / release identity manifest、verify-only / non-publish rehearsal、compatibility preview advisory lane
- archived evidence index 与 milestone audit 仍然要保留“当时 closeout 的 route truth”，但必须转成历史语态，不能继续说“当前治理状态”或“唯一下一步”
- planning truth 在本 phase 完成后应前推到 `Phase 82 complete`，默认下一步应为 `$gsd-discuss-phase 83`

</specifics>

<deferred>
## Deferred Ideas

- issue / PR / security intake 表单补采 evidence fields 与 maintainer stewardship wording 归 `Phase 83`
- 更广义的 open-source/community-health template freeze 与 full guard-coverage burn-down 归 `Phase 84`
- 任何生产代码层面的 runtime / protocol / control surgery 不属于本 phase
- archive evidence 之外的更老 milestone prose cleanup 若不影响 current release route，可继续保持历史原貌

</deferred>
