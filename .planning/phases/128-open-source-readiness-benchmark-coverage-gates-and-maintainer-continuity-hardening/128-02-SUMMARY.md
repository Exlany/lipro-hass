---
phase: 128-open-source-readiness-benchmark-coverage-gates-and-maintainer-continuity-hardening
plan: "02"
summary: true
---

# Plan 128-02 Summary

## Completed

- `.github/workflows/ci.yml` 已新增 `Generate coverage baseline evidence` 与 `Upload coverage artifact`，把 coverage evidence 升级为与 benchmark 同等级的 CI 可审计资产。
- `scripts/coverage_diff.py` 已支持 `--fail-on-changed-regression`，在 baseline 文件存在时阻断 changed measured file 相对 baseline 的回退，而不只检查当前 run 的绝对 floor。
- `scripts/lint` 已支持本地 `COVERAGE_BASELINE_JSON`，使 `./scripts/lint --full` 可以镜像 CI 的 baseline-aware compare story。
- `.planning/baseline/VERIFICATION_MATRIX.md` 与 `.planning/codebase/TESTING.md` 已回写 coverage baseline compare、artifact upload 与 changed-surface regression guard 的治理真相。

## Outcome

- `QLT-51` 的 coverage 维度已从 review-note 提升为 machine-checkable contract。
- coverage truth 继续保持单一故事线：absolute floor、changed-surface floor 与 baseline regression guard 都复用 `scripts/coverage_diff.py`，没有创造第二套 coverage gate。
