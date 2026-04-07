# 38-01 Summary

## Outcome

- firmware external-boundary 术语已收口到 bundled local trust-root asset + remote advisory payload；历史文件名保留，但不再误导 authority truth。
- `AUTHORITY_MATRIX`、`RESIDUAL_LEDGER`、user-facing docs 与 OTA/fixture tests 现共同讲同一条 external-boundary 故事。

## Validation

- `uv run pytest -q tests/meta/test_external_boundary_authority.py tests/meta/test_external_boundary_fixtures.py tests/meta/test_firmware_support_manifest_repo_asset.py tests/core/ota/test_firmware_manifest.py`
