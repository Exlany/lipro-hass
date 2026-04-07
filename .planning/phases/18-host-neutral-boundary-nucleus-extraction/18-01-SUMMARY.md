# 18-01 Summary

## Outcome

- 抽出 `custom_components/lipro/core/auth/bootstrap.py` 作为 host-neutral auth/bootstrap helper home。
- `custom_components/lipro/config_flow.py` 改为通过 `AuthBootstrapSeed` + `async_login_with_password_hash()` 获取 `AuthSessionSnapshot`，再投影为 `ConfigEntryLoginProjection`。
- `custom_components/lipro/entry_auth.py` 内部统一复用 shared bootstrap wiring；对外 seam `build_entry_auth_context()` / `persist_entry_tokens_if_changed()` 保持稳定。
- `custom_components/lipro/flow/login.py` 将 `ConfigEntryLoginProjection` 明确为 HA config-entry projection home。

## Verification

- `uv run pytest -q tests/flows/test_config_flow.py tests/core/test_init.py tests/core/test_token_persistence.py`
