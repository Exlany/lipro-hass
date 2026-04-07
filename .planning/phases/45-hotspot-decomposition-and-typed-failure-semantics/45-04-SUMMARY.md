# 45-04 Summary

- Completed on `2026-03-20`.
- Upgraded benchmark evidence from advisory artifact wording to a governed baseline / threshold / no-regression contract across CI, contributor docs, baseline matrices, and review ledgers.
- Added `tests/benchmarks/benchmark_baselines.json` plus `scripts/check_benchmark_baseline.py` as the machine-readable benchmark authority, and grouped benchmark tests so manifest comparison stays stable across hotspots.
- Kept the benchmark lane maintainer-facing and `schedule` / `workflow_dispatch` scoped while making `threshold warning` versus blocking regression semantics explicit.
- Verified with `uv run python scripts/check_benchmark_baseline.py .benchmarks/_all_shape.json --manifest tests/benchmarks/benchmark_baselines.json` (`Benchmark contract: ok`).
- Verified with `uv run pytest tests/benchmarks/test_command_benchmark.py tests/benchmarks/test_mqtt_benchmark.py tests/benchmarks/test_device_refresh_benchmark.py tests/benchmarks/test_coordinator_performance.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_closeout_guards.py -q` (`59 passed`).
