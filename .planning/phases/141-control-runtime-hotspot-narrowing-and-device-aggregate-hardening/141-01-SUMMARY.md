# Plan 141-01 Summary

- `custom_components/lipro/control/service_router.py` 现只暴露 formal `async_handle_*` callbacks；router root 不再 outward 泄漏 `_get_device_and_coordinator`、`_summarize_service_properties`、share manager 或 client-session collaborator。
- sanctioned patch seam 已收回 `custom_components/lipro/control/service_router_support.py`：anonymous-share 与 developer-feedback 相关测试现统一 patch support-owned helper，而不是 patch router root 上的 accidental export。
- `tests/meta/test_phase123_service_router_reconvergence_guards.py` 与 `tests/services/test_services_registry.py` 已补 predecessor/focused guard，能直接阻止 second control-root story 与 router-root collaborator leakage 回流。
