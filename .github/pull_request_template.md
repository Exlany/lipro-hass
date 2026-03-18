## CI Contract
- [ ] `lint`: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run python scripts/check_translations.py`
- [ ] `governance`: `uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q -x tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`
- [ ] `test`: `uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing`、`uv run python scripts/coverage_diff.py coverage.json --minimum 95`、`uv run python scripts/refactor_tools.py --coverage-json coverage.json --minimum-coverage 95`（snapshot coverage 已包含在 `tests/` 主 lane 中）
- [ ] `benchmark`: 仅在性能敏感改动或手动对齐 schedule/workflow_dispatch 时执行 `uv run pytest tests/benchmarks/ -v --benchmark-only --benchmark-json=.benchmarks/benchmark.json`，并保留 `.benchmarks/benchmark.json` 作为 advisory artifact / budget 对照
- [ ] `security`: 若涉及依赖、安全边界或发布链路，已确认 `pip-audit` / `security` job 结果；否则在 Summary 中注明依赖面未变
- [ ] `shellcheck`: 若修改 `install.sh` / `scripts/*` shell 脚本，已运行 `shellcheck install.sh scripts/develop scripts/lint scripts/setup`
- [ ] `docs/release`: 若修改 `README.md` / `README_zh.md` / `CONTRIBUTING.md` / `SUPPORT.md` / `SECURITY.md` / `.github/*` / release workflow / maintainer docs，已同步 `docs/TROUBLESHOOTING.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.planning/reviews/V1_2_EVIDENCE_INDEX.md` 与相关导航入口，并明确记录任何 contract change（禁止 silent carry-forward）；若涉及 release 叙事，还需说明 `provenance` / `SBOM` / `signing` / `code scanning` / firmware metadata 是否本次变更或保持对齐
- [ ] No sensitive data in logs, diagnostics, or test fixtures

## Summary
<!-- What changed and why? -->

## Testing
<!-- What tests were run? Paste relevant output or describe coverage. -->
