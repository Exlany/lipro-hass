---
phase: 128-open-source-readiness-benchmark-coverage-gates-and-maintainer-continuity-hardening
plan: "03"
summary: true
---

# Plan 128-03 Summary

## Completed

- `.github/workflows/ci.yml` 已新增 `benchmark_smoke` lane：PR / push / `workflow_call` 默认运行 manifest-governed smoke subset，而 full benchmark 仍保留给 `schedule` / `workflow_dispatch`。
- `pyproject.toml` 已开启 `--strict-markers` 并显式登记 `benchmark` marker，防止 benchmark governance 静默漂移。
- `scripts/check_benchmark_baseline.py` 与 `tests/benchmarks/benchmark_baselines.json` 已支持 `--benchmark-set smoke` 与 `policy.smoke_benchmarks`，保证 smoke/full 共享同一 manifest truth。
- `.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER,KILL_LIST}.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/codebase/TESTING.md` 与本 phase 资产已同步冻结最终 closeout-ready 证据链。

## Outcome

- PR 路径现在拥有受治理的 benchmark smoke feedback，同时没有把 full benchmark 粗暴塞进 correctness lane。
- `Phase 128` 已形成可审计的最终证据链：benchmark smoke、strict markers、review ledgers 与 phase assets 共同支撑里程碑 closeout。
