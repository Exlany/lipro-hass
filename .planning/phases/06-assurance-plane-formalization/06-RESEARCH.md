# Phase 06: Assurance Plane 正式化 - Research

**Updated:** 2026-03-13
**Status:** Execution-aligned

## What Already Landed

- `06-ASSURANCE-TAXONOMY.md` 与 `06-CI-GATES.md` 已形成 active assurance taxonomy / gate 分层说明；
- `scripts/check_file_matrix.py` + `tests/meta/test_governance_guards.py` 已把 file-matrix / authority drift 纳入正式 guard；
- `.github/workflows/ci.yml` 已拥有 governance job；
- `.pre-commit-config.yaml` 已修正 diagnostics gate，并新增 governance gate。

## What Is Still Missing

### 1. Assurance evidence 还需要 phase-level summary / validation 封口
- 执行产物已在仓库中；
- 但 planning package 仍缺 summary / validation，导致 `ROADMAP / STATE / REQUIREMENTS` 无法正式宣告完成。

### 2. 部分测试与文档仍保留旧叙事残影
- 需要继续把 key tests 聚焦到 formal telemetry / service surface / meta guards；
- 需要让 docs authority 彻底承认 `.planning/*` + `FILE_MATRIX` 才是 current truth。

## Recommended Truth Sources

最小正式 assurance 真源：
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`：终态裁决；
- `.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`：当前 phase/requirement/status；
- `.planning/baseline/DEPENDENCY_MATRIX.md`、`.planning/baseline/PUBLIC_SURFACES.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/baseline/AUTHORITY_MATRIX.md`：guard rules；
- `.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md`：repo governance truth；
- `CoordinatorTelemetryService`：runtime observability truth。

## Recommended Execution Shape

- `06-01`：冻结 assurance taxonomy / truth-source / validation template；
- `06-02`：冻结 governance checker 与 meta guards；
- `06-03`：对齐 snapshot/integration evidence 到正式 runtime 结构；
- `06-04`：以 CI / pre-commit / validation docs 完成 Assurance Plane 收口。
