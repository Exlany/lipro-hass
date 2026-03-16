# Phase 23 Research

**Status:** `research complete`
**Date:** `2026-03-16`
**Mode:** `deep refinement after Phase 22 planning`
**Requirements:** `GOV-16`, `GOV-17`

## Executive Judgment

`Phase 23` 不是“再做一点文档修补”，而是**把 `Phase 21-22` 的技术真相同步成可协作、可发版、可审计的单一治理故事**。

最优拆分是 `3 plans / 3 waves`：

1. `23-01`：先同步 baseline / reviews / roadmap-state / phase lifecycle 真源。
2. `23-02`：再同步 contributor-facing docs / templates / troubleshooting / support/security/version entry points。
3. `23-03`：最后收 release evidence index、workflow gate 与 maintainer release narrative。

## Governance Reality Audit

### 1. 当前治理守卫已经很强，但仍缺少 v1.2-specific closeout 资产

现有仓库已具备：

- `.github/workflows/ci.yml` 与 `.github/workflows/release.yml` 的 gate reuse
- `tests/meta/test_governance_guards.py` 对 README / SUPPORT / SECURITY / TROUBLESHOOTING / RUNBOOK / workflow reuse 的结构化守卫
- `CONTRIBUTING.md` / `SUPPORT.md` / `SECURITY.md` / `README*.md` 的导航互链

**缺口：**

- 当前还没有 `v1.2` 专用 release evidence index，可让 maintainer / release gate / milestone closeout 共享同一 pointer doc。
- `Phase 21-22` 的 observability/taxonomy closeout 真相还未沉淀到 baseline/reviews 与 public entry docs 的最终口径。
- `v1.2` 的 final milestone audit 也还不存在，但这是 `Phase 24` 的工作，不应在本 phase 里偷跑。

### 2. Phase 23 必须遵守“baseline/reviews first, public docs second”

目前 contributor-facing docs 已经广泛引用：

- `docs/TROUBLESHOOTING.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `SUPPORT.md`
- `SECURITY.md`
- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/pull_request_template.md`

**裁决：** 若 `Phase 23` 直接先改 README / bug template，而不先同步 baseline/reviews/roadmap-state，会再次制造“外部入口先于真源”的治理漂移。

### 3. Release workflow 已复用 CI，但 release evidence narrative 仍需要显式 v1.2 收口

当前 `release.yml` 已复用 `ci.yml`，这是正确方向；但 `GOV-17` 还要求：

- maintainer-facing release narrative 与 v1.2 governance truth 同步
- release evidence 有单一 pointer/index
- workflow gate / docs / tests 对这个 pointer/index 讲同一条故事

**结论：** `Phase 23-03` 最佳产出不是“再改一个 workflow 条件”，而是补齐 `V1_2_EVIDENCE_INDEX.md` 与其配套 guards/runbook references。

## Recommended Plan Structure

### Plan 23-01 — sync long-term governance truth and ledgers

**建议文件域：**
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/PUBLIC_SURFACES.md`（若 `Phase 21-22` 变更了 formal contract exposure）
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

**必须达成：**
- `Phase 21-22` 的 truth 成为长期治理真源，而不是只留在 phase 目录里。
- 若 `Phase 21-22` 引入新的 contract home / verification slice / residual rationale，必须被 baseline/reviews 明确记录。
- contributor-facing docs 仍暂不动。

### Plan 23-02 — align contributor docs, templates and public entry points

**建议文件域：**
- `README.md`
- `README_zh.md`
- `CONTRIBUTING.md`
- `SUPPORT.md`
- `SECURITY.md`
- `docs/TROUBLESHOOTING.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/ISSUE_TEMPLATE/config.yml`（若需要）

**必须达成：**
- 所有 public entry points 对 v1.2 最终 support/security/troubleshooting/release navigation 讲同一条故事。
- 若 `Phase 22` 改变了 developer report / observability expectations，这些入口必须同步更新。
- 不修改 workflow gates 本体；那是 `23-03`。

### Plan 23-03 — close release evidence index and workflow gate alignment

**建议文件域：**
- `.planning/reviews/V1_2_EVIDENCE_INDEX.md`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_version_sync.py`

**必须达成：**
- v1.2 有明确的 evidence index / release pointer doc。
- maintainer runbook 与 workflow tests 都引用同一 evidence / gate truth。
- Phase 24 只需要消费这些 release-ready assets 做 final audit/archive/handoff，而不用再次补 release narrative。

## Risks And Boundaries

### Risk 1 — 把 production refactor 偷跑进治理 phase

**控制：** 23 只能回写真源、docs、templates、workflow evidence；不再改核心实现。

### Risk 2 — public docs 先于 baseline/reviews

**控制：** 23-01 先行；23-02/03 只能消费 23-01 落地的真源。

### Risk 3 — release workflow 看似不变，于是漏掉 evidence index

**控制：** 23-03 必须显式交付 `V1_2_EVIDENCE_INDEX.md` 或等价单一 pointer asset。

### Risk 4 — 把 final milestone audit 偷跑到 23

**控制：** 23 只做 release-ready governance/doc closure；`v1.2` 最终 audit/archive/handoff 留给 24。
