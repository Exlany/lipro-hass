# Refactor Tools

## 提供内容

- `scripts/coverage_diff.py`：读取 `pytest-cov` 的 JSON 报告并校验最低覆盖率/基线差异
- `scripts/refactor_tools.py`：提供 `RefactorValidator`，统一输出覆盖率与 API 合同摘要
- `tests/test_refactor_tools.py`：校验脚本行为，避免工具自身漂移

## 常用命令

```bash
uv run python scripts/coverage_diff.py coverage.json --minimum 95
uv run python scripts/refactor_tools.py --coverage-json coverage.json --minimum-coverage 95
uv run pytest tests/test_refactor_tools.py -v
```

## 设计原则

- 只依赖仓内现有测试输出，不引入额外服务
- CLI 默认参数可直接用于本地与 CI
- 失败时返回非 0，方便接入 GitHub Actions
