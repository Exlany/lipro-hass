# Summary 114-02

## What changed
- 为 `pyproject.toml` 增加 `Access Mode` project URL，并在 `.planning/baseline/GOVERNANCE_REGISTRY.json` 新增 `open_source_surface` 机器真相区块，显式声明 `private-access`、docs-first、conditional GitHub surfaces、无 guaranteed non-GitHub private fallback、debug-mode developer services、partial redaction，以及 schema-limited metadata projections。
- 收紧 `.github/ISSUE_TEMPLATE/config.yml` 的 Security contact link 文案，明确当前没有已文档化、保证可达的非 GitHub 私密回报通道。
- 新增 `tests/meta/test_phase114_open_source_surface_honesty_guards.py`，并扩展 `tests/meta/test_governance_release_continuity.py`、`tests/meta/test_version_sync.py`、`tests/meta/toolchain_truth_docs_fast_path.py`，把 access-mode / fallback / metadata projection truth 冻结为仓库级守卫。
- 同步回写 `.planning/codebase/TESTING.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/reviews/FILE_MATRIX.md`，登记 Phase 114 proof chain，并更新派生 inventory 计数。

## Why it changed
- Wave 1 解决了人类可读文档的 honesty，但 machine-readable metadata / governance registry / issue contact links 仍不足以表达同一套真相。
- 如果 registry 与 meta guards 不把 schema-limited projection、fallback blocker 与 access-mode 条件化写死，后续很容易再次出现“文档诚实、metadata 漂移”的回退。

## Verification
- `uv run pytest -q tests/flows/test_flow_credentials.py tests/services/test_services_registry.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_version_sync.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_phase114_open_source_surface_honesty_guards.py`
- `83 passed in 1.31s`
- `bash -n scripts/lint`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check custom_components/lipro/flow/credentials.py tests/flows/test_flow_credentials.py tests/meta/test_phase114_open_source_surface_honesty_guards.py tests/meta/test_governance_release_continuity.py tests/meta/test_version_sync.py tests/meta/toolchain_truth_docs_fast_path.py`

## Outcome
- Wave 2 现在把“公开可达性 / docs-first / private fallback blocker / debug-only developer surfaces / metadata projection limit”收敛为单一机器可验证合同，不再只是会话共识。
