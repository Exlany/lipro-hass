# Plan 125-03 Summary

## What changed

- `custom_components/lipro/flow/step_handlers.py` 的 protocol 现直接绑定 `config_flow.py` private helper seam。
- `custom_components/lipro/config_flow.py` 删除了 user / reauth / reconfigure 的 public pass-through wrapper 壳层。
- `custom_components/lipro/entry_auth.py` 删除了单次中转 helper，persisted auth-seed formal home 保持不变。

## Outcome

- `config_flow.py` 更接近真正的 thin adapter。
- `entry_auth.py` 继续保持单一正式 auth/bootstrap truth，而不是第二 control root。
