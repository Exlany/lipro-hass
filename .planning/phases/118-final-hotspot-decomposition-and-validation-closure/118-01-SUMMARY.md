---
phase: 118-final-hotspot-decomposition-and-validation-closure
plan: "01"
subsystem: governance
tags: [governance, route-truth, phase-118, gsd, focused-tests]
requires:
  - phase: 117-validation-backfill-and-continuity-hardening
    provides: closeout-ready selector truth, v1.32 active-route baseline, and continuity guard foundations
provides:
  - Phase 118 active selector truth across PROJECT/ROADMAP/REQUIREMENTS/STATE/MILESTONES
  - GOV-75 completion with Phase 118 requirement basket expansion and traceability
  - Focused governance route guards aligned with the current in-progress counters
affects: [118-02 hotspot cleanup, 118-03 validation closure, v1.32 milestone closeout]
tech-stack:
  added: []
  patterns: [machine-readable governance-route contract sync, focused pytest route guards, selector-family truth alignment]
key-files:
  created: [.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-01-SUMMARY.md]
  modified:
    - .planning/PROJECT.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/STATE.md
    - .planning/MILESTONES.md
    - tests/meta/governance_current_truth.py
    - tests/meta/governance_followup_route_current_milestones.py
    - tests/meta/test_governance_route_handoff_smoke.py
key-decisions:
  - "Mark GOV-75 complete in requirements while keeping HOT-50/HOT-51/TST-40 pending under Phase 118."
  - "Keep selector wording at 'phase 118 execution-ready' while aligning GSD fast-path counters to the on-disk 118-01 and 118-02 summaries."
patterns-established:
  - "Current-route truth stays in the selector family; MILESTONES remains chronology-only context."
  - "Focused governance tests assert both document wording and gsd-tools progress counters."
requirements-completed: [GOV-75]
duration: 15min
completed: 2026-04-01
---

# Phase 118 Plan 01: Activate route truth and governance sync Summary

**Phase 118 selector truth now points at the live execution route, with GOV-75 complete, `118-01/118-02` acknowledged on disk, and only `118-03` remaining**

## Performance

- **Duration:** 15 min
- **Started:** 2026-04-01T00:35:00Z
- **Completed:** 2026-04-01T00:51:40Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments
- 把 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 收敛到单一 `Phase 118 execution-ready` 叙事，并把默认下一步固定到 `$gsd-execute-phase 118`。
- 完成 `GOV-75`：expanded requirement basket 已显式纳入 `HOT-50`、`HOT-51`、`TST-40`、`GOV-75`，并把完成态/待办态分别映射到 `Phase 118`。
- 对齐 focused governance suites 与 shared route constants，使 selector truth 与 `gsd-tools` 快速路径共同承认 `118` 当前为唯一正式 follow-up，且当前进度已是 `2/3 plans / 9/10 total plans / 90%`。

## Task Commits

1. **Task 1: relocate Phase 118 into the v1.32 roadmap and activate execution-ready route truth** - `6fd2667` (`feat`)
2. **Task 2: sync governance ledgers, developer guidance, and focused route guards** - `6d48127` (`test`)
3. **Corrective fix: revert out-of-scope governance/doc/test edits to honor the plan file boundary** - `67bbf39` (`fix`)
4. **Corrective fix: resync plan-owned docs/tests to the on-disk `118-02` evidence and current fast-path counters** - `0d998bb` (`fix`)

## Files Created/Modified
- `.planning/PROJECT.md` - 固化 `v1.32` 当前路线与 `Phase 118` follow-up 叙事
- `.planning/ROADMAP.md` - 让 `Phase 118` 正式嵌回当前 milestone，并登记当前 `2/3` plan 进度与 `118-03` remaining queue
- `.planning/REQUIREMENTS.md` - 标记 `GOV-75` 完成，保留 `HOT-50/HOT-51/TST-40` 为 pending
- `.planning/STATE.md` - 把当前状态收敛到 `Phase 118 / Plan 118-02 complete` 与 `9/10 plans, 90%`
- `.planning/MILESTONES.md` - 同步当前里程碑为 `3/4 phases, 9/10 plans`
- `tests/meta/governance_current_truth.py` - 刷新 machine-readable route truth 与 in-progress 计数常量
- `tests/meta/governance_followup_route_current_milestones.py` - 收紧当前 milestone 断言到 `GOV-75 complete + 9/10 plans`
- `tests/meta/test_governance_route_handoff_smoke.py` - 让 handoff smoke 只校验 plan-owned docs/tests，并覆盖 `2/3` 当前进度

## Decisions Made

- 先完成 `GOV-75`，不提前假装 `HOT-50/HOT-51/TST-40` 已闭环。
- 保留 `active / phase 118 execution-ready (2026-04-01)` 作为 selector wording，同时让 `gsd-tools init progress` 如实报告 `118 in_progress / 2 summaries`。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Reconciled route counters with the on-disk 118 summaries**
- **Found during:** Task 2 (sync governance ledgers, developer guidance, and focused route guards)
- **Issue:** focused suites had to honor the actual on-disk phase evidence. After scope cleanup, `gsd-tools init progress` still reported `118 in_progress / 2 summaries` because both `118-01-SUMMARY.md` and `118-02-SUMMARY.md` existed, while selector docs/tests still told a `1/3` / `8/10` story.
- **Fix:** updated `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/MILESTONES.md`, `tests/meta/governance_current_truth.py`, `tests/meta/governance_followup_route_current_milestones.py`, and `tests/meta/test_governance_route_handoff_smoke.py` to reflect `2/3 complete`, `9/10 plans`, `90%`, and a plan-owned verification boundary.
- **Files modified:** `.planning/ROADMAP.md`, `.planning/MILESTONES.md`, `.planning/STATE.md`, `tests/meta/governance_current_truth.py`, `tests/meta/governance_followup_route_current_milestones.py`
- **Verification:** `uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py`
- **Committed in:** `0d998bb`

**2. [Rule 1 - Scope correction] Reverted non-plan governance/doc/test edits**
- **Found during:** final scope audit before summary commit
- **Issue:** one task commit had also updated non-plan governance/docs/tests, conflicting with the user-level file-boundary constraint for `118-01`.
- **Fix:** restored `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/FILE_MATRIX.md`, `docs/developer_architecture.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, and `tests/meta/test_phase112_formal_home_governance_guards.py` to their pre-plan versions.
- **Files modified:** `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/FILE_MATRIX.md`, `docs/developer_architecture.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `tests/meta/test_phase112_formal_home_governance_guards.py`
- **Verification:** `uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py`
- **Committed in:** `67bbf39`

---

**Total deviations:** 2 auto-fixed (Rule 1)
**Impact on plan:** 一次范围纠偏 + 一次当前计数纠偏；最终交付既回到 plan 允许的文件边界，也与仓内现存 `118` 证据一致。

## Issues Encountered

- 接手时仓内已存在未跟踪的 `118` planning bundle 与旧版 `118-01-SUMMARY.md`；吾先读取其内容，再按实际 `gsd-tools` 输出回填 progress truth，避免编造 counters。

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 现在只剩 `118-03` 继续沿 `$gsd-execute-phase 118` 执行，不再建立在 `117 -> closeout-ready` 的 stale selector 上。
- maintainer continuity / public mirror / delegate identity 仍是仓外 blocker，未被本计划伪装为已解决。

## Self-Check: PASSED

- Summary exists: `.planning/phases/118-final-hotspot-decomposition-and-validation-closure/118-01-SUMMARY.md`
- Task commit found: `6fd2667`
- Task commit found: `6d48127`
- Corrective commit found: `67bbf39`
- Corrective commit found: `0d998bb`

---
*Phase: 118-final-hotspot-decomposition-and-validation-closure*
*Completed: 2026-04-01*
