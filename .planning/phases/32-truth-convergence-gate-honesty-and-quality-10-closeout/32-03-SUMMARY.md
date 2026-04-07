# 32-03 Summary

## Outcome

- `release identity`、`attestation/provenance`、`SBOM`、`signing defer`、`code_scanning defer` 与 single-maintainer continuity 现已在 workflow、runbook、README、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md` 中讲同一条故事。
- `.github/workflows/release.yml` 的 release identity manifest 已显式写入 `provenance=GitHub artifact attestation` 与 `code_scanning=deferred`，避免 release posture 再漂移。
- public docs 不再暗示不存在的 backup maintainer；maintainer continuity 改为显式 freeze / disclosure / best-effort boundary contract。

## Key Files

- `.github/workflows/release.yml`
- `README.md`
- `README_zh.md`
- `CONTRIBUTING.md`
- `SUPPORT.md`
- `SECURITY.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `tests/meta/test_toolchain_truth.py`

## Validation

- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py -k "release or runbook or support or security or template or owner"`

## Notes

- provenance / attestation 是当前 release identity evidence，不是 artifact signing；这一边界已被制度化写明。
