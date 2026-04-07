# Phase 98 Research

**Phase:** `98-carry-forward-eradication-route-reactivation-and-closeout-proof`
**Date:** `2026-03-28`
**Requirements:** `RES-15`, `GOV-65`, `TST-31`, `QLT-39`

## Objective

把 `v1.26` closeout 后仓库真实已有的 carry-forward eradication 与 governance truth reactivation 收口成 machine-check current route：既要承认 `outlet_power` legacy side-car fallback 已退出 live path，也要让 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、developer guide、verification/testing maps 与 focused guards 共同承认 `v1.27 active route / Phase 98 complete / latest archived baseline = v1.26`。

## Inputs Reviewed

- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/codebase/TESTING.md`
- `docs/developer_architecture.md`
- `custom_components/lipro/core/device/device.py`
- `custom_components/lipro/core/coordinator/runtime/command_runtime.py`
- `tests/platforms/test_sensor.py`
- `tests/meta/public_surface_runtime_contracts.py`
- `tests/meta/governance_current_truth.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_phase97_governance_assurance_freeze_guards.py`
- `tests/meta/test_phase90_hotspot_map_guards.py`

## Findings

1. code path truth 与 planning/governance truth 分叉：`outlet_power` legacy fallback 已删，但 `.planning/*` 和 current-route guards 仍停留在 `no active milestone route / latest archived baseline = v1.26`。
2. `v1.27` 还不存在 active route contract，也没有 `Phase 98` 的 context / research / plan / summary / verification / validation bundle，导致 `$gsd-plan-phase` / `$gsd-execute-phase` 无法被诚实重演。
3. `FILE_MATRIX` / `TESTING.md` / `VERIFICATION_MATRIX.md` 仍只冻结到 `Phase 97`，无法描述新的 current-route reactivation focused guard footprint。
4. `CommandRuntime` 仍保留重复 failure-state clear helper；这是一个低风险、可证明的本轮顺手收口点。

## Execution Shape

- `98-01`: 冻结 carry-forward eradication truth，并顺手移除 `CommandRuntime` 的重复 failure-state clear helper。
- `98-02`: 把 current-route docs、developer architecture、ledgers/testing/verification maps 与 governance tests 统一切到 `v1.27 active route / Phase 98 complete / latest archived baseline = v1.26`。
- `98-03`: 跑完整 proof chain，写 `Phase 98` verification / validation，并确认 `$gsd-next` 现在应前推到 `$gsd-complete-milestone v1.27`。

## Risks

- 如果只改 prose 不改 machine-readable route contract / `STATE.md` frontmatter，`gsd-tools` parser truth 会继续和 human-readable truth 分叉。
- 如果新增 focused guard 却不刷新 `FILE_MATRIX` / `TESTING.md` / `VERIFICATION_MATRIX.md`，当前 route 会再次落回“代码对了、治理投影没跟上”。
- 如果把 `v1.26` archived assets 写成 live current story，会破坏 archived bundle 的 pull-only 身份。
