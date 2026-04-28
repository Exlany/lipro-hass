# External Boundary Fixtures

这些样本用于 Phase 2.6 的 external-boundary contract / drift 检查。

- `share_worker/`：匿名分享上传 payload 与 lite fallback contract
- `support_payload/`：HA service / support-facing payload contract
- `firmware/`：bundled trust-root / remote advisory payload 样本
- `diagnostics_capabilities/`：外部 diagnostics endpoint payload 样本

占位符约定：
- `__INTEGRATION_VERSION__`：测试加载时替换为当前集成版本
- `<generated_at>`：运行时动态字段 canonical placeholder
- `<timestamp>`：运行时错误时间戳 canonical placeholder
