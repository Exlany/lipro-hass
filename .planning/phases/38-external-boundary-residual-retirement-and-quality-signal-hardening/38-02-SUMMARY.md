# 38-02 Summary

## Outcome

- `coverage_diff.py`、CI、`CONTRIBUTING.md` 与 `.planning/codebase/TESTING.md` 现显式区分 coverage floor 与 optional baseline diff。
- benchmark posture 保持 advisory，但 story 已收口为 advisory-with-artifact；toolchain guards 会阻止 dead quality-signal wording 回流。

## Validation

- `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py`
