# Phase 106 Research

## Comparative Lens

本轮参考了仓库既有的 `Phase 41` 与 `Phase 46` 大审计模式：

- 先做全仓 inventory 与 hotspot ranking
- 把问题分为 `fix now / route later / organization-only`
- 只对当前最容易持续放大维护成本、且不改变 outward contract 的问题动刀

## Architectural Decision

### Fix Now

1. **Endpoint auth collaborator de-privatization**
   - 根因：endpoint adapter 依赖 facade 私有字段 `_auth_api`
   - 风险：未来 facade 内部调整会破坏 endpoint adapter；也会让 private-field leak 被视作合理模式
   - 最优改法：给 `LiproRestFacade` 暴露显式 `auth_api` surface，让 endpoint adapter 通过 sanctioned property 读取 collaborator

2. **Status batching orchestration slimming**
   - 根因：`query_device_status()` 同时承担 batch 组装、task 构造、并发执行、结果扁平化
   - 风险：热点继续扩张时，行为虽稳定但理解成本上涨，修改更容易漏掉并发/批量契约
   - 最优改法：抽出 `_build_status_batch_tasks()`、`_query_status_batches()`、`_merge_status_batch_rows()`

3. **Options flow schema composition helpers**
   - 根因：init/advanced schema 都重复循环式装配 option fields
   - 风险：配置项增加时逻辑会继续长胖，并让验证路径变得不透明
   - 最优改法：抽出 `_add_int_option_fields()`、`_add_bool_option_fields()`、`_add_device_filter_option_fields()`，再把 spec 提升为 module-level tuples

4. **ADR terminology alignment**
   - 根因：ADR-0001 仍用 `Client` 叙述层次
   - 风险：和 ADR-0005 / current architecture docs 的 `facade` 语义不完全一致，降低 onboarding 清晰度
   - 最优改法：改成 `Protocol façade / transport collaborators` 语义

### Route Later

- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/api/status_fallback_support.py`
- `custom_components/lipro/core/api/rest_facade.py`
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`

这些模块仍是高价值热点，但涉及面更广，最好放在正式新 milestone 中按 phase 化推进，而不是在 archived-only route 上临时拉长战线。
