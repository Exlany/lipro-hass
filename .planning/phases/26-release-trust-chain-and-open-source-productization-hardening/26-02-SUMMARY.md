# 26-02 Summary

## Outcome

- `.github/workflows/release.yml` 继续复用 `ci.yml`，但现在会一并发布 `install.sh`、SBOM 与 GitHub artifact provenance attestation，不再只停在 `zip + SHA256SUMS`。
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 已把 installer / SBOM / attestation 写成当前 release posture 与 post-release checks，而不是“以后再补”的 defer note。
- release workflow 守卫测试已同步到新权限、新 step 命名与新资产列表。

## Key Files

- `.github/workflows/release.yml`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_version_sync.py`
- `tests/meta/test_toolchain_truth.py`

## Validation

- `uv run pytest -q tests/meta/test_governance_guards.py -k "release or workflow" tests/meta/test_toolchain_truth.py`
- `uv run pytest -q tests/meta/test_version_sync.py tests/meta/test_governance_guards.py -k "runbook or supply_chain"`

## Notes

- 本 tranche 没有另立第二条发版故事线；仍是 `validate -> build -> publish` 单链，只是把 release identity evidence 做硬了。
