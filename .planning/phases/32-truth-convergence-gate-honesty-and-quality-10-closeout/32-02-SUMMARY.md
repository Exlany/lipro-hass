# 32-02 Summary

## Outcome

- repo-wide `ruff` / `mypy` / CI / contributor docs 的 gate story 已统一到真实 blocking contract，不再靠“默认大家都知道”维持。
- `.planning/baseline/VERIFICATION_MATRIX.md`、`CONTRIBUTING.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md` 与 `tests/meta/test_toolchain_truth.py` 已把 gate honesty 写成 machine-checkable truth。
- 本 wave 没有弱化 `.github/workflows/ci.yml`；相反，是在 `ruff` 与 `mypy` 真绿后，把文档与守卫对齐到现状。

## Key Files

- `.planning/baseline/VERIFICATION_MATRIX.md`
- `CONTRIBUTING.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `tests/meta/test_toolchain_truth.py`

## Validation

- `uv run ruff check .`
- `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py tests/meta/test_governance_guards.py -k "toolchain or release or runbook or support or security or codebase or contributing"`

## Notes

- `gate honesty` 的原则是：真实门禁更重要，不允许用文案美化未被执行的绿色故事。
