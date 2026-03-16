# 23-08 Summary

## Outcome

- 对齐 README、README_zh、troubleshooting、support、contributing 与 bug template：developer report / one-click feedback 降级为升级排障路径，不再作为公开 bug 的硬门槛；默认 installer 主入口继续保持 `ARCHIVE_TAG=latest`。
- 让 maintainer-facing release narrative 与 closeout evidence 讲同一条故事：当前已落地的是 pinned actions、CI reuse、tagged checkout、version match 与 `SHA256SUMS`；`provenance`、`SBOM`、`signing`、`code scanning` hard gate 与 richer firmware metadata 显式 defer。
- 如实表达单维护者支持/安全审查现实，并把 `.planning/*` 定位收紧为 maintainer-facing 治理真源，而不是普通用户排障入口。

## Key Files

- `README.md`
- `README_zh.md`
- `CONTRIBUTING.md`
- `SUPPORT.md`
- `SECURITY.md`
- `docs/TROUBLESHOOTING.md`
- `docs/README.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/pull_request_template.md`
- `.planning/reviews/V1_2_EVIDENCE_INDEX.md`
- `tests/meta/test_version_sync.py`
- `tests/meta/test_evidence_pack_authority.py`
- `tests/meta/test_governance_guards.py`

## Validation

- `uv run pytest tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py tests/meta/test_evidence_pack_authority.py tests/meta/test_public_surface_guards.py -q` → `79 passed`
- `uv run python scripts/check_architecture_policy.py --check` → passed
- `uv run ruff check .` → passed

## Notes

- 本 plan 没有伪造尚未落地的供应链增强项；未落地部分继续以显式 defer 方式保留。
- firmware certified truth 仍以本地 `firmware_support_manifest.json` 为 trust root，metadata 扩展必须在未来新 phase 明确登记。
