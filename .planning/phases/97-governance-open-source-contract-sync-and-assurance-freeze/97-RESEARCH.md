# Phase 97 Research

**Phase:** `97-governance-open-source-contract-sync-and-assurance-freeze`
**Date:** `2026-03-28`
**Requirements:** `ARC-25`, `TST-30`, `QLT-38`

## Objective

把 `v1.26` active route 的最后一段治理冻结做成 machine-check current truth：既要补齐 `Phase 96` closeout 证据，又要把 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`、baseline/review docs、developer architecture 与 focused meta guards 收口到同一条 `Phase 97 complete / closeout-ready` 故事线上，并让 `$gsd-next` 自然前推到 `$gsd-complete-milestone v1.26`。

## Inputs Reviewed

- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/codebase/TESTING.md`
- `docs/developer_architecture.md`
- `tests/meta/governance_current_truth.py`
- `tests/meta/test_governance_bootstrap_smoke.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_phase90_hotspot_map_guards.py`

## Findings

1. `Phase 96` 的代码与 summaries 已完成，但缺少 phase-level `VERIFICATION.md` / `VALIDATION.md` 与 focused guard，因此 route handoff 仍缺 final freeze 证据。
2. 当前治理真相仍停在 `Phase 96 planning-ready`，而 `init progress` 已识别 `Phase 96` complete、`Phase 97` pending，说明 parser truth 与 prose truth 分叉。
3. `FILE_MATRIX` 与 `TESTING.md` 已对 Phase 94/95 做同步，但还没有登记 `Phase 96` focused guard，也没有预留 `Phase 97` governance freeze focused guard。
4. `docs/developer_architecture.md` 仍停在 `Phase 95`；developer-facing current-topology guide 还没承认 sanitizer burn-down 与 governance closeout 完成态。

## Execution Shape

- `97-01`: 补 Phase 96 closeout bundle、focused guard、matrix/file/testing 同步，为 `Phase 97` 提供可信 handoff。
- `97-02`: 把 current-route docs、developer architecture 与 governance smoke guards 统一切到 `Phase 97 complete / closeout-ready`。
- `97-03`: 跑完整质量证明链，写 `Phase 97` verification/validation，并确认 `$gsd-next` 现在应前推到 `$gsd-complete-milestone v1.26`。

## Risks

- 如果只改 prose 不改 `STATE.md` frontmatter，`state json` 会继续输出旧进度，导致 guard 继续分叉。
- 如果新增 focused meta guards 却不更新 `FILE_MATRIX` / `TESTING.md` 计数，`check_file_matrix` 与 docs truth 会继续漂移。
- `v1.25` archived assets 必须保持 pull-only 历史语义，不能被追写成 `Phase 97` current truth。
