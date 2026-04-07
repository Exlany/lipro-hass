---
phase: 128
slug: open-source-readiness-benchmark-coverage-gates-and-maintainer-continuity-hardening
nyquist_compliant: true
wave_1_complete: true
wave_2_complete: true
updated: 2026-04-01
---

# Phase 128 Validation Contract

status: passed

## Wave Order

1. `128-01` unify readiness honesty / continuity truth / minimum-version source / selector projection
2. `128-02` formalize baseline-aware coverage diff / artifact upload / local lint mirror
3. `128-03` add benchmark smoke / strict markers / final governance freeze

## Completion Expectations

- `128-01/02/03-SUMMARY.md`、`128-SUMMARY.md`、`128-VERIFICATION.md` 与 `128-VALIDATION.md` 共同证明 `OSS-17 / GOV-86 / QLT-51` 已在同一 active route 下闭环。
- readiness honesty 与 operational limits 必须被诚实 codify；它们可以被 machine-check docs/tests 守护，但不能被伪装成 repo-external reality 已自动解决。
- coverage baseline compare、benchmark smoke、strict markers、review ledgers 与 selector docs 必须共享单一 current-route truth，不得分叉出第二条 governance story。

## GSD Route Evidence

- `128-01-SUMMARY.md` 记录 readiness honesty / continuity / canonical version source 的单一合同。
- `128-02-SUMMARY.md` 记录 baseline-aware coverage diff / artifact upload / local mirror 的 quality contract。
- `128-03-SUMMARY.md` 记录 benchmark smoke / strict markers / review-ledger freeze 与 final evidence chain。

## Validation Commands

- `uv run ruff check .`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_governance_release_continuity.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_version_sync.py tests/meta/toolchain_truth_ci_contract.py tests/meta/test_governance_release_contract.py tests/meta/toolchain_truth_testing_governance.py tests/meta/test_governance_route_handoff_smoke.py`
- `uv run pytest -q tests/benchmarks/test_command_benchmark.py tests/benchmarks/test_mqtt_benchmark.py tests/benchmarks/test_device_refresh_benchmark.py --benchmark-only --benchmark-json=.benchmarks/benchmark-smoke.json`
- `uv run python scripts/check_benchmark_baseline.py .benchmarks/benchmark-smoke.json --manifest tests/benchmarks/benchmark_baselines.json --benchmark-set smoke`
- `uv run pytest -q`
- `tmpdir=$(mktemp -d) && ln -s "$PWD" "$tmpdir/repo" && node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" --cwd="$tmpdir/repo" state json && printf "
---GSD_SPLIT---
" && node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" --cwd="$tmpdir/repo" init progress && printf "
---GSD_SPLIT---
" && node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" --cwd="$tmpdir/repo" phase-plan-index 128 && rm -rf "$tmpdir"`

## Archive Truth Guardrail

- `Phase 128` 可以关闭 repo-local governance / quality contract gap，但不得把 repo-external stewardship reality 伪装成“已经具备 hidden delegate / guaranteed fallback”。
- 后续若继续处理更深层 architecture debt，必须在新 milestone 中显式登记，而不是回写本 phase 的 closeout-ready 结论。
