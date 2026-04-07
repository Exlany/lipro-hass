# Phase 89 Research

## Summary

本 phase 不需要重新做 vendor/domain research；主要输入来自 fresh repo-wide review 与当前代码真相。结论是：仓库总体已经是高质量、强治理、单主链的 Home Assistant 集成，但仍有 4 组值得在 fresh milestone 中继续收敛的 repo-internal debt。

## 1. Entity / Runtime Boundary Honesty

- `custom_components/lipro/entities/base.py` 仍通过 `coordinator.command_service` 和 `coordinator.get_device_lock(...)` 操作 runtime internals。
- `custom_components/lipro/entities/firmware_update.py` 仍直连 `coordinator.protocol_service.async_query_ota_info(...)`。
- `custom_components/lipro/runtime_types.py` 作为 entities 的 type contract，仍把 `command_service` / `protocol_service` / `get_device_lock` 暴露给 entity consumers。

**Research verdict:** 应把 entity-facing runtime surface 收口为 verbs（发送命令、应用 optimistic update、查询 OTA），而不是 service/lock handles。

## 2. Runtime Wiring Single-Root Story

- `Coordinator` 先 new `CoordinatorAuthService` / `CoordinatorProtocolService` / `CoordinatorSignalService`，再把它们传给 `RuntimeOrchestrator.build_bootstrap_artifact(...)`。
- `RuntimeOrchestrator` 已经承担 state/runtimes/service-layer bootstrap 的大部分装配故事。

**Research verdict:** 应继续往 orchestrator/factory 侧集中 runtime assembly，减少 `Coordinator` 的 parallel wiring role。

## 3. Tooling Kernel Ownership

- `scripts/check_architecture_policy.py` 仍通过 `sys.path` 注入导入 `tests.helpers.architecture_policy` 与 `tests.helpers.ast_guard_utils`。
- 这说明 script-side truth 仍借住 test-side helper home。

**Research verdict:** 把共享 helper 提升到 script-owned library，tests 与 scripts 共同消费它，比继续让 CLI 依赖 `tests.helpers` 更诚实。

## 4. Open-Source Entry Consistency

- README/docs/templates 对 private-access 的提醒出现频繁且分散。
- `manifest.json` 的 `documentation` / `issue_tracker` 分流仍可更清晰。

**Research verdict:** 把 distribution/support/issues 统一成 first-hop story，减少 mixed signal，比继续叠加解释文字更优。

## Recommended Execution Strategy

1. 先收窄 entity/runtime public surface，确保生产边界更诚实。
2. 再把 runtime wiring 继续往 single bootstrap story 收口。
3. 并行处理 tooling helper ownership 与 open-source entry/docs cleanup。
4. 最后同步 planning/codebase/current-story truth 并跑 focused verification。
