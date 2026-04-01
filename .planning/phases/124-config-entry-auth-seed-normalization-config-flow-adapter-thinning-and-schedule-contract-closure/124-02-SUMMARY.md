# Plan 124-02 Summary

## What changed

- `custom_components/lipro/entry_auth.py` 现在集中承接 persisted auth-seed（`password_hash` / `remember_password_hash` / `biz_id`）解释与回写。
- `custom_components/lipro/config_flow.py` 已压回 thin adapter；user / reauth / reconfigure orchestration 通过 `custom_components/lipro/flow/step_handlers.py` localized 下沉。
- focused regressions 已补齐 malformed reconfigure parity、explicit remembered-hash false 优先级与 stale `biz_id` 清理。

## Outcome

- `ARC-35` / `HOT-55` 已在 auth-flow 主链完成收敛。
- config-entry auth seed 不再在 flow projection 与 token callback 之间各自解释。
