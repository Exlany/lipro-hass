# Phase 133: Governance recovery, runtime consistency, and public contract correction - Research

**Researched:** 2026-04-02
**Domain:** governance route recovery, runtime consistency convergence, public contract correction, closeout resync
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- `v1.39` 必须恢复为唯一 active milestone route，`Phase 133` 是唯一 active phase。
- 变更只能落在既有正式 home，不得新增 compat root、第二控制面故事或 runtime backdoor。
- public/docs wording 必须服从真实实现；文档、测试、治理台账必须讲同一条故事。
- phase closeout 要同时交付计划、摘要、verification 与 governance projections，同步给出 `$gsd-next` 等价结论。

### Deferred Ideas (OUT OF SCOPE)
- 更深层 sanctioned hotspot 的后续 burn-down
- 新 milestone 规划与下一轮 repo-wide audit
- 把 phase working assets 整体提升为长期治理真源
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GOV-89 | 恢复 `v1.39` active route / phase truth 与 governance projections 一致性 | 使用单 phase 四计划结构，同时同步 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、registry、review ledgers |
| ARC-42 | runtime consistency debt 收口到 formal home | 只在 `firmware_manifest.py`、`runtime_access.py`、developer router / platform adapters 内 inward convergence |
| HOT-61 | sanctioned hotspot 进入同一执行 story，而非漂浮 debt | 通过 runtime lane 与 public-contract lane 明确列入 `Phase 133`，避免 docs-only carry-forward |
| DOC-18 | developer/public/runbook wording 回到 current truth | README、README_zh、troubleshooting、services/quality-scale 与 platform contract 同步修正 |
| QLT-55 | file-matrix / promoted assets / testing-map / continuity truth 同步 | 用 governance closeout lane 集中 resync，并补历史 appendix 锚点 |
| TST-53 | focused governance red-tests 先收敛后闭环 | 先修 docs/phase assets，再跑 runtime/public-contract 与 governance/meta 两组 focused validation |
</phase_requirements>

## Summary

审阅结果表明，`v1.39` 的真实问题不是“需要一轮新的大重构”，而是 **current governance truth、runtime consistency、public contract 与 closeout projections 同时失配**。最优解不是继续分散修补，而是把所有现存漂移压回一条单 phase 主线：

- 先恢复 `v1.39` route truth，使当前 active milestone 与 latest archived baseline `v1.38` 的关系重新诚实可验证；
- 再只在正式 home 内修 runtime/public contract 漂移，避免 helper folklore 回流；
- 最后把 testing map、promoted assets、historical chronology 与 requirement traceability 一次性回写，形成 closeout-ready handoff。

**Primary recommendation:** 保持 `Phase 133` 的四计划结构不变，把 execution 结果锁定为 `closeout-ready`，并通过 `CONTEXT / RESEARCH / PLAN / SUMMARY / VERIFICATION` + governance projections 证明 `$gsd-plan-phase 133`、`$gsd-execute-phase 133` 已有完整资产，`$gsd-next` 的等价结论为 `$gsd-complete-milestone v1.39`。

## Direct Answers

1. **为什么不重开更大范围重构？**
   - 因为当前失败点集中在 active truth 漂移与 formal-home contract mismatch；扩大范围会重新引入第二条故事线。
2. **runtime 修补的最优策略是什么？**
   - 只在既有正式 home inward convergence，防止 control/runtime/platform 间重新长出 bypass。
3. **public contract 修补的最优策略是什么？**
   - 让 climate/fan/service/docs wording 与 tests 同步收敛，确保 outward contract 只有一份 truth。
4. **governance closeout 的关键是什么？**
   - 不是补 prose，而是把 registry、file matrix、phase assets、testing-map、requirements traceability 同时校正。

## Recommended Outputs

- `133-CONTEXT.md`：补齐 phase context，恢复 `gsd-tools init plan-phase` 的 context truth
- `133-RESEARCH.md`：补齐研究资产，恢复 `has_research` truth
- `.planning/REQUIREMENTS.md`：补历史 `Phase 60` appendix，满足 archived continuity guards
- `133-VERIFICATION.md`：记录 focused validation 的真实通过结果

## Risks To Avoid

- 用 appendix 掩盖 active milestone 真相，而不是把它明确标注为 archived traceability
- 为了“彻底”而引入新的 formal home、compat shell 或第二治理根
- 只修 docs 不修 tests，或只修 tests 不修 governance projections
- 把 `$gsd-next` 结论错误地回退为重新 plan / execute 当前 phase

## Validation Architecture

### Focused runtime/public-contract lane
- `uv run pytest -q tests/core/ota/test_firmware_manifest.py tests/core/test_runtime_access.py tests/core/test_control_plane.py tests/services/test_services_diagnostics_feedback.py tests/platforms/test_climate.py tests/platforms/test_fan_entity_behavior.py`

### Governance/meta lane
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/toolchain_truth_testing_governance.py tests/meta/test_governance_release_continuity.py tests/meta/governance_milestone_archives_truth.py tests/meta/test_governance_closeout_guards.py tests/meta/test_phase90_hotspot_map_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_governance_release_docs.py tests/meta/test_service_translation_sync.py tests/meta/test_version_sync.py`

## Final Arbitration

`Phase 133` 的最佳落点不是“再做一次 execute-phase”，而是证明当前 phase 的 planning/execution 资产已经完整、治理主链已经收敛、下一步只剩 milestone closeout。只要 `CONTEXT / RESEARCH / appendix / verification` 补齐，`$gsd-plan-phase 133` 与 `$gsd-execute-phase 133` 的资产链就完整闭环，`$gsd-next` 也自然收敛到 `$gsd-complete-milestone v1.39`。
