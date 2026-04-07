---
phase: 74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout
plan: "04"
subsystem: assurance
tags: [governance, docs, cleanup, topicization, validation]
requires:
  - phase: 74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout
    provides: auth residual retirement and topicized suite convergence
provides:
  - Phase 74 closeout-ready governance truth
  - public-docs fast-path cleanup without route leakage
  - `74-VALIDATION.md` reproducible validation ledger
affects: [milestone-closeout, governance-current-truth, public-docs-boundary]
tech-stack:
  added: []
  patterns: [focused guard repair, topicized thin-shell suite, validation ledger]
key-files:
  created:
    - .planning/phases/74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout/74-04-SUMMARY.md
    - .planning/phases/74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout/74-VALIDATION.md
    - tests/meta/test_phase74_cleanup_closeout_guards.py
  modified:
    - .planning/PROJECT.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/STATE.md
    - .planning/baseline/AUTHORITY_MATRIX.md
    - .planning/baseline/VERIFICATION_MATRIX.md
    - .planning/codebase/TESTING.md
    - .planning/reviews/FILE_MATRIX.md
    - .planning/reviews/RESIDUAL_LEDGER.md
    - docs/README.md
    - tests/conftest.py
    - tests/meta/governance_current_truth.py
    - tests/meta/test_governance_milestone_archives.py
    - tests/meta/test_phase72_runtime_bootstrap_route_guards.py
key-decisions:
  - "Keep `docs/README.md` as public docs map only; current-route and archive pointers stay in planning/runbook truth sources."
  - "Retire `services/registrations.py` physically instead of preserving a dead compat shell as a pseudo-public surface."
  - "Keep topicized thin shells directly runnable while preventing duplicate collection through `tests/conftest.py` guards."
requirements-completed: [GOV-56, HOT-34, TST-22, QLT-30]
completed: 2026-03-25
---

# Phase 74 Plan 04 Summary

**Phase 74 已把 legacy auth / compat 残留、public docs 边界、topicized mega-suite 与 closeout 路由真相一并收口到可归档状态。**

## Accomplishments
- 退役 `custom_components/lipro/services/registrations.py`，并同步修复相关测试、file-matrix/policy truth 与 cleanup guards，避免“代码已死、治理仍承认”的双重故事。
- 把 `tests/core/test_share_client.py` 与 `tests/core/coordinator/runtime/test_command_runtime.py` 收窄为 thin shell，新增 topicized suites 与重复收集防护，降低 failure radius 而不牺牲直接运行入口。
- 清理 `docs/README.md` 的内部治理泄露，让 latest archive pointer / current-route / next command 只留在 `PROJECT/STATE/RUNBOOK` 等 maintainer 真源。
- 修复 `REQUIREMENTS.md` 中多处 archived coverage 算术漂移，并同步 baseline/review 文档与 meta guards 到 `Phase 74 complete` / `$gsd-complete-milestone v1.20`。
- 补齐 `74-VALIDATION.md`，记录 focused gates 与全仓 gates，全量验证达到 `2592 passed`。

## Notes
- 本轮不引入任何新的 outward root，也不把 phase workspace 过程文档抬升为新的长期 authority chain。
- `$gsd-next` 的合理落点现应等价于 milestone closeout：`$gsd-complete-milestone v1.20`。
