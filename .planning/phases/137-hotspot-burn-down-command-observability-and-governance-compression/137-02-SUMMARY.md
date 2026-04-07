# Plan 137-02 Summary

- 已新增 `custom_components/lipro/core/auth/manager_support.py`，把 credential seed、token lease bookkeeping 与 auth-result parsing 拆回 support helper。
- 已把 `custom_components/lipro/core/auth/manager.py` 收回 orchestration shell，修复 mock/session readback 漂移，并保留 cold-start refresh dedupe。
- 已把 `custom_components/lipro/core/protocol/rest_port.py` 从纯 `cast` 绑定改为显式 concern-local adapter family，补齐 focused protocol/auth regressions。
