# 51-03 Summary

## Outcome

- `.github/workflows/release.yml` 现支持 `workflow_dispatch` 下的 `publish_assets=false` verify-only / non-publish rehearsal，并只在 tag push 或显式 `publish_assets=true` 时发布资产。
- `CONTRIBUTING.md`、`SUPPORT.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 已给出 `docs-only` / `governance-only` / `release-only` 的最小充分验证路径，并明确 maintainer-only rehearsal 不会发布 public assets。

## Validation

- `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`

## Notes

- verify-only / non-publish rehearsal 复用同一条 release chain，不创建 shadow CI 或 softer publish path。
