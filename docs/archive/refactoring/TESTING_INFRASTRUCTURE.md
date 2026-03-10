# Testing Infrastructure

## 已落地资产

- 快照测试目录：`tests/snapshots/`
- 快照基线：`tests/snapshots/snapshots/*.ambr`（当前 `4` 份）
- 基准测试目录：`tests/benchmarks/`（当前 `3` 个 benchmark 用例）
- 单一 benchmark 基线：`.benchmarks/Linux-CPython-3.13-64bit/0001_baseline.json`
- CI 基准产物单独输出到 `.benchmarks/benchmark.json`，不依赖 baseline 文件名
- 类型专项测试：`tests/type_checking/`（当前 `2` 个专项测试文件）
- 覆盖率差异工具：`scripts/coverage_diff.py`
- 重构工具：`scripts/refactor_tools.py`

## CI 覆盖范围

当前 `.github/workflows/ci.yml` 已覆盖：

- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy`
- `uv run pytest tests/type_checking/ -v`
- `uv run mypy tests/type_checking/ --strict`
- `uv run pytest tests/ --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95`
- `uv run pytest tests/snapshots/ -v`
- `uv run python scripts/coverage_diff.py coverage.json --minimum 95`
- `uv run python scripts/refactor_tools.py --coverage-json coverage.json --minimum-coverage 95`
- 定时/手动触发 benchmark job，并将结果输出到 `.benchmarks/benchmark.json`

## 建议执行顺序

```bash
uv run pytest tests/type_checking/ -v
uv run pytest tests/snapshots/ -v
uv run pytest tests/ --ignore=tests/benchmarks -q
uv run pytest tests/ --ignore=tests/benchmarks --cov=custom_components/lipro --cov-report=json -q
uv run python scripts/coverage_diff.py coverage.json --minimum 95
uv run pytest tests/benchmarks/ -v --benchmark-only --benchmark-save=baseline
```

## 本地重建基线

- 先备份或清空 `.benchmarks/Linux-CPython-3.13-64bit/`
- 再执行：`uv run pytest tests/benchmarks/ -v --benchmark-only --benchmark-save=baseline`
- 目标状态为仅保留单份 `.benchmarks/Linux-CPython-3.13-64bit/0001_baseline.json`

## 结论

测试基础设施任务已完成：静态检查、类型专项、快照、benchmark、覆盖率差异与重构工具均已进入仓库，并接入 CI。
