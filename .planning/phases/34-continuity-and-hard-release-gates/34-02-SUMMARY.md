# 34-02 Summary

## Outcome

- `.github/workflows/release.yml` 现新增 tagged `CodeQL` hard gate、keyless `cosign` signing bundles 与签名校验，release identity manifest 也已回写新的 hard-gate truth。
- `.github/workflows/codeql.yml` 已建立 push / PR / tag / manual dispatch 的代码扫描主线。
- README / README_zh / SUPPORT / SECURITY / CONTRIBUTING / runbook 已把 `SHA256SUMS`、`SBOM`、attestation/provenance、artifact signing 与 code-scanning hard gate 统一成单一可审计故事。

## Validation

- `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`
