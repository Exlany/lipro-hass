# Plan 122-03 Summary

## What changed

- `pyproject.toml` 与 `custom_components/lipro/manifest.json` 的 release-facing URL 已从 `blob/main` 收回到当前 semver tag `v1.0.0`，恢复 tagged-release traceability。
- `tests/meta/test_version_sync.py` 与 `tests/meta/test_phase75_access_mode_honesty_guards.py` 新增 tag-aware projection guards，明确拒绝 `/blob/main/` 回流。
- `tests/meta/toolchain_truth_docs_fast_path.py` 继续冻结 support/security appendix ordering，保证 metadata traceability 与 docs routing 不会再次漂移。

## Outcome

- `OSS-16`：release-facing metadata projection 现在可追溯到 package semver 对应 tag。
- `TST-44`：focused guards 已同时覆盖 metadata projection 与 appendix ordering 两类 regression。
