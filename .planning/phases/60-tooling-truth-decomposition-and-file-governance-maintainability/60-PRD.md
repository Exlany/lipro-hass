# Phase 60 PRD — Tooling Truth Decomposition & File-Governance Maintainability

## Goal

把 `scripts/check_file_matrix.py` 与 `tests/meta/test_toolchain_truth.py` 按稳定 truth family / ownership boundary inward decomposition 成更窄的 internal homes 与 focused suites，同时保持 CLI、import contract、authority chain 与 daily runnable roots 稳定。

## In Scope

- `scripts/check_file_matrix.py`
- `tests/meta/test_toolchain_truth.py`
- 直接 import `scripts.check_file_matrix` public contract 的 meta guards
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/codebase/TESTING.md`
- 与上述 tooling topology 直接相关的 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`

## Requirements

- `HOT-14`
- `TST-12`
- `GOV-44`

## Success Criteria

1. `scripts/check_file_matrix.py` 退成 thin CLI / compatibility root，inventory / classifier / validator / render / override truth 按 internal families 收口；现有 import / CLI surface 保持稳定；
2. `tests/meta/test_toolchain_truth.py` topicize 成更小、更诚实的 focused suites 或 thin runnable roots，toolchain / release / docs / governance 断言不再混成 giant bucket；
3. `.planning/reviews/FILE_MATRIX.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/codebase/TESTING.md` 与 current-story docs 准确记录新的 tooling truth topology 与 no-growth story。

## Non-Goals

- 不重开 `Coordinator` / `__init__.py` / `config_flow.py` 级别的 runtime-root surgery
- 不借 tooling decomposition 反向创造第二条 governance story 或新 public helper root
- 不在本 phase 中提前执行 `Phase 61 / 62` 的 production hotspot slimming 或 naming/docs 全局清洗
