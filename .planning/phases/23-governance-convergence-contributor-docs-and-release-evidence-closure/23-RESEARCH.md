# Phase 23 Research

**Status:** `draft research complete`
**Date:** `2026-03-16`

## Key Findings

- 当前 `v1.2` 已完成 `Phase 18-20`，因此 `Governance convergence, contributor docs and release evidence closure` 不再需要为 remaining boundary family formalization 背锅，而应消费 `Phase 20` 结果继续前进。
- 本 phase 的 requirement set 为 `GOV-16, GOV-17`；执行时必须保持与 `.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 三处一致。
- 本 phase 应拆成 3 个 plans，按照 wave 顺序推进：先落核心 truth，再做 surface/gate/gov closeout。

## Recommended Breakdown

- **Plan 23-01**：sync governance truth and authority ledgers；主要文件域：.planning/baseline/, .planning/reviews/, .planning/ROADMAP.md, .planning/REQUIREMENTS.md
- **Plan 23-02**：align contributor docs templates and support surfaces；主要文件域：CONTRIBUTING.md, .github/ISSUE_TEMPLATE/, .github/pull_request_template.md, README.md
- **Plan 23-03**：close release evidence and workflow gate alignment；主要文件域：.github/workflows/, tests/meta/test_governance_guards.py, tests/meta/test_version_sync.py

## Risks To Watch

- 不要把跨 phase 工作揉成一个 megaphase；每一相只交付自身 must-have。
- 所有 docs/governance 变更都必须跟实现真相同轮更新，禁止“先写 README，后补实现/guard”。
- 若执行中发现新 requirement，必须先仲裁是否属于 `v1.2` 还是应 defer 到 `v1.3`。
