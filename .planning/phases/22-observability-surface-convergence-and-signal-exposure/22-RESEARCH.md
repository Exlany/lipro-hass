# Phase 22 Research

**Status:** `draft research complete`
**Date:** `2026-03-16`

## Key Findings

- 当前 `v1.2` 已完成 `Phase 18-20`，因此 `Observability Surface Convergence & Signal Exposure` 不再需要为 remaining boundary family formalization 背锅，而应消费 `Phase 20` 结果继续前进。
- 本 phase 的 requirement set 为 `OBS-03`；执行时必须保持与 `.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 三处一致。
- 本 phase 应拆成 3 个 plans，按照 wave 顺序推进：先落核心 truth，再做 surface/gate/gov closeout。

## Recommended Breakdown

- **Plan 22-01**：expose classified failure signals to diagnostics and system health；主要文件域：custom_components/lipro/control/diagnostics_surface.py, custom_components/lipro/control/system_health_surface.py, tests/core/test_diagnostics.py, tests/core/test_system_health.py
- **Plan 22-02**：converge support and developer evidence consumers；主要文件域：custom_components/lipro/services/, tests/core/test_report_builder.py, tests/services/test_services_diagnostics.py, tests/services/test_services_share.py
- **Plan 22-03**：harden observability contracts and integration guards；主要文件域：tests/meta/test_governance_guards.py, tests/meta/test_public_surface_guards.py, tests/integration/

## Risks To Watch

- 不要把跨 phase 工作揉成一个 megaphase；每一相只交付自身 must-have。
- 所有 docs/governance 变更都必须跟实现真相同轮更新，禁止“先写 README，后补实现/guard”。
- 若执行中发现新 requirement，必须先仲裁是否属于 `v1.2` 还是应 defer 到 `v1.3`。
