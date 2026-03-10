# Developer Testing Guide

## 常规回归

```bash
uv run ruff check .
uv run mypy --hide-error-context --no-error-summary
uv run pytest tests/ --ignore=tests/benchmarks -q
```

## 重构专项

### 快照

```bash
uv run pytest tests/snapshots/ -v --snapshot-update
uv run pytest tests/snapshots/ -v
```

### 类型合同

```bash
uv run pytest tests/type_checking/ -v
uv run mypy tests/type_checking/ --strict
```

### 覆盖率差异

```bash
uv run pytest tests/ --ignore=tests/benchmarks --cov=custom_components/lipro --cov-report=json -q
uv run python scripts/coverage_diff.py coverage.json --minimum 95
uv run python scripts/refactor_tools.py --coverage-json coverage.json --minimum-coverage 95
```

### Benchmark

```bash
uv run pytest tests/benchmarks/ -v --benchmark-only --benchmark-save=baseline
```

基线默认保存在：`.benchmarks/Linux-CPython-3.13-64bit/0001_baseline.json`

## 建议流程

1. 先跑目标目录的最小测试
2. 再跑对应范围的 `ruff` / `mypy`
3. 涉及结构化输出时补快照
4. 涉及性能敏感路径时补 benchmark
5. 最后执行全量 `tests/ --ignore=tests/benchmarks`
