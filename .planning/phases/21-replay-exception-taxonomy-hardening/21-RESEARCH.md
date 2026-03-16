# Phase 21 Research

**Status:** `draft research complete`
**Date:** `2026-03-16`

## Key Findings

- 当前 `v1.2` 已完成 `Phase 18-20`，因此 `Replay Coverage & Exception Taxonomy Hardening` 不再需要为 remaining boundary family formalization 背锅，而应消费 `Phase 20` 结果继续前进。
- 本 phase 的 requirement set 为 `SIM-04, ERR-02`；执行时必须保持与 `.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 三处一致。
- 本 phase 应拆成 3 个 plans，按照 wave 顺序推进：先落核心 truth，再做 surface/gate/gov closeout。

## Recommended Breakdown

- **Plan 21-01**：expand replay and evidence across completed families；主要文件域：tests/harness/protocol/replay_driver.py, tests/harness/evidence_pack/, tests/integration/test_protocol_replay_harness.py, tests/integration/test_ai_debug_evidence_pack.py
- **Plan 21-02**：tighten broad-catch exception arbitration；主要文件域：custom_components/lipro/core/protocol/, custom_components/lipro/core/coordinator/, custom_components/lipro/control/, tests/core/
- **Plan 21-03**：formalize failure taxonomy contracts and guards；主要文件域：custom_components/lipro/control/diagnostics_surface.py, custom_components/lipro/control/system_health_surface.py, tests/meta/test_governance_guards.py, tests/meta/test_dependency_guards.py

## Risks To Watch

- 不要把跨 phase 工作揉成一个 megaphase；每一相只交付自身 must-have。
- 所有 docs/governance 变更都必须跟实现真相同轮更新，禁止“先写 README，后补实现/guard”。
- 若执行中发现新 requirement，必须先仲裁是否属于 `v1.2` 还是应 defer 到 `v1.3`。
