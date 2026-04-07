# Plan 121-02 Summary

## What changed

- `custom_components/lipro/flow/login.py` 的 `ConfigEntryLoginProjection` 现在显式要求非空 `access_token`、`refresh_token` 与正整数 `user_id`，不再对 malformed auth session 做 silent default projection。
- `custom_components/lipro/config_flow.py` 把 user / reauth / reconfigure 的 auth-session projection failure 统一映射回 `invalid_response`，并保留现有 outward flow semantics。
- `custom_components/lipro/flow/submission.py` 抽出 `_validate_existing_entry_submission()`，把 reauth / reconfigure 共用的 entry-bound invariant chain 收敛成一条内部路径，仅保留 phone error placement 的策略差异。
- flow regressions 已同步到 `tests/flows/test_config_flow_user.py`、`tests/flows/test_config_flow_reauth.py` 与 `tests/flows/test_flow_submission.py`。

## Outcome

- `HOT-53`：existing-entry validator duplication 已收口为单一内部链路。
- `QLT-48`：malformed auth-session projection 现在 fail closed 为 `invalid_response`。
- `TST-43`：flow slice 的 focused regressions 已补齐并通过。

