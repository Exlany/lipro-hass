---
phase: 10-api-drift-isolation-core-boundary-prep
plan: "02"
status: completed
completed: 2026-03-14
requirements:
  - ISO-02
  - ISO-04
---

# Summary 10-02

## Outcome

- `custom_components/lipro/core/auth/manager.py` 已新增 `AuthSessionSnapshot`，并把 `login()`、`refresh_token()`、`get_auth_session()` 固定为 formal auth/session contract。
- `custom_components/lipro/config_flow.py` 已切到 `LiproAuthManager.login()` 返回的 session snapshot，再映射回现有 flow result。
- `custom_components/lipro/entry_auth.py` 已优先消费 `get_auth_session()`；`get_auth_data()` fallback 仅保留给 legacy mocks / older callers。
- `build_entry_auth_context()` 已同步传递 `biz_id`，避免 token persistence 与 future-host contract 继续分叉。

## Verification

- `uv run pytest -q -x tests/core/test_auth.py tests/core/test_init.py tests/flows/test_config_flow.py`
- Result: `225 passed`

## Governance Notes

- `AuthSessionSnapshot` 现在是 host-neutral auth/session truth；raw login/result dict 不再被视作 formal public contract。
- 本计划没有引入第二条 auth root；HA adapters 仍只是 `LiproAuthManager` / protocol formal contract 的薄层消费者。
