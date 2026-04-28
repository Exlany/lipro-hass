## CI Contract
- [ ] `lint`: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run python scripts/check_translations.py`
- [ ] `governance`: `uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q -x tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`
- [ ] `test`: `uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing`、`uv run python scripts/coverage_diff.py coverage.json --minimum 95 --changed-files .coverage-changed-files --changed-minimum 95`、`uv run python scripts/refactor_tools.py --coverage-json coverage.json --minimum-coverage 95`（snapshot coverage 已包含在 `tests/` 主 lane 中；若本地想镜像 CI 的 baseline-aware compare，请设置 `COVERAGE_BASELINE_JSON=/path/to/baseline.json` 后运行 `./scripts/lint --full`）
- [ ] `benchmark`: PR / push / `workflow_call` 默认使用 smoke subset：`uv run pytest -q tests/benchmarks/test_command_benchmark.py tests/benchmarks/test_mqtt_benchmark.py tests/benchmarks/test_device_refresh_benchmark.py --benchmark-only --benchmark-json=.benchmarks/benchmark-smoke.json` 与 `uv run python scripts/check_benchmark_baseline.py .benchmarks/benchmark-smoke.json --manifest tests/benchmarks/benchmark_baselines.json --benchmark-set smoke`；完整 benchmark 仍仅在 `schedule` / `workflow_dispatch` 对齐：`uv run pytest tests/benchmarks/ -v --benchmark-only --benchmark-json=.benchmarks/benchmark.json` 与 `uv run python scripts/check_benchmark_baseline.py .benchmarks/benchmark.json --manifest tests/benchmarks/benchmark_baselines.json`；threshold warning 仅作 maintainer signal，failure threshold 才是 no-regression gate
- [ ] `security`: 若涉及依赖、安全边界或发布链路，已确认 `pip-audit` / `security` job 结果；否则在 Summary 中注明依赖面未变
- [ ] `shellcheck`: 若修改 `install.sh` / `scripts/*` shell 脚本，已运行 `shellcheck install.sh scripts/develop scripts/lint scripts/setup`
- [ ] `docs/navigation`: 若修改 `README.md` / `README_zh.md` / `CONTRIBUTING.md` / `SUPPORT.md` / `SECURITY.md` / `.github/*` / release workflow / maintainer docs，已同步 `docs/README.md`、`docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`、`docs/TROUBLESHOOTING.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md` 与相关导航入口；若改动触及 protocol / runtime / control / external-boundary / governance 边界，已确认 PR 描述与文档入口都指向 `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`；Issue UI 的 Documentation 链接仍应指向 `docs/README.md`；若 maintainer continuity / custody 叙事发生变化，已同步 `.github/CODEOWNERS` 并明确记录 contract change；若涉及 maintainer-only `break-glass verify-only` / `non-publish rehearsal`，已在 Summary 中显式说明；若涉及 release 叙事，已说明 `provenance` / `SBOM` / `signing` / `code scanning` / firmware metadata 是否变化
- [ ] No sensitive data in logs, diagnostics, or test fixtures

## Summary
<!-- What changed and why? -->

> If this PR touches protocol / runtime / control / external-boundary / governance boundaries, link the relevant decisions or call out how this change follows `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`.
> 若本 PR 涉及 protocol / runtime / control / external-boundary / governance 边界，请说明它遵循了 `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md` 的哪一段决策或约束。

## Affected boundary / scope
<!-- Route this PR to the closest boundary family and name the concrete surfaces changed. / 请把本 PR 路由到最接近的边界家族，并写清具体受影响 surface。 -->
- Boundary family / 边界家族:
- Affected surfaces or files / 受影响 surface 或文件:
- Install / source / release path changes / 安装、来源或发布路径变化:

## Risk / impact
<!-- Describe user impact, maintainer impact, regressions, migrations, or release/security implications. -->
- User or maintainer impact / 对用户或维护者的影响:
- Risk, regressions, or rollback notes / 风险、回归面或回滚说明:
- Security-sensitive follow-up / 安全敏感后续:
  - [ ] Not security-sensitive / 不涉及安全敏感细节
  - [ ] Security-sensitive details stay out of this PR and are handled through `SECURITY.md` / 安全敏感细节不写进此 PR，改按 `SECURITY.md` 私密处理

## Validation commands
<!-- List the exact commands or equivalent evidence used to validate this change. / 请列出精确验证命令或等价证据。 -->
- `uv run ...`

## Testing
<!-- Paste relevant output, summarize coverage, or explain why a command could not run. / 粘贴关键输出、总结覆盖，或说明未执行某命令的原因。 -->
