# Plan 121-03 Summary

## What changed

- `scripts/lint` 的 default changed-surface assurance 不再依赖 `Phase 113`-named guard file，统一切到新的 `tests/meta/test_changed_surface_assurance_guards.py`。
- `tests/meta/test_phase113_hotspot_assurance_guards.py` 保留历史 hotspot budget / helper-locality 断言，但退出 live changed-surface route ownership。
- `.planning/codebase/TESTING.md` 与 `.planning/reviews/FILE_MATRIX.md` 已同步声明：`Phase 113` guard 是历史证据；live default-lint route 的正式 home 现在是 phase-agnostic guard。
- `Phase 121` 的 `ROADMAP` 已从 placeholder 变为完整计划/执行事实，live route 不再停在 `Phase 120 closeout-ready` 的分叉状态。

## Outcome

- `GOV-80`：default changed-surface assurance 已退相位化，不再把历史 phase 名称保留在 live route owner 上。
- `DOC-11`：toolchain / testing / file-matrix wording 已和当前 active route 对齐。
- `TST-43`：toolchain slice 有 dedicated meta guard 冻结。

