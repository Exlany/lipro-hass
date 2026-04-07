# Phase 53 Research — Runtime and entry-root second-round throttling

**Date:** 2026-03-21
**Requirement focus:** `HOT-12`

## Hotspot Inventory

### 1. `custom_components/lipro/core/coordinator/coordinator.py`
- 现状：`Coordinator` 已比早期更瘦，但仍同时持有 runtime context assembly、service-layer initialization、update-cycle creation、entity bookkeeping、command failure mapping。
- 风险：runtime root 若继续承载重复簿记与 delegation ballast，会重新稀释 single-runtime-root 可读性。
- 推荐方向：优先把 runtime bootstrapping 和 entity bookkeeping ballast inward 到现有 `core/coordinator/*` internal home 或新的 support-only seam；`CoordinatorUpdateCycle` 继续只作为 internal collaborator。

### 2. `custom_components/lipro/control/entry_lifecycle_controller.py`
- 现状：formal owner 已正确，但一个类内仍集中着 bootstrap shared infra、entry auth build、coordinator construction、activation cleanup、rollback、unload service sync、reload contract logging。
- 风险：后续若继续堆特例，controller 会再次变成巨型流程脚本；若把流程散回 `runtime_infra.py` / `ServiceRegistry` / root adapter，又会稀释 owner truth。
- 推荐方向：第二波再把 prepare / activate / abort / unload mechanics 下沉为 controller-private lifecycle support operations；controller 本体只保留 owner methods、order contract、named failure arbitration。

### 3. `custom_components/lipro/__init__.py`
- 现状：HA root adapter 已保持 lazy module loading，但仍同时承载 entry-auth wrapper aliases、service-registry wiring、runtime-infra binding 与 controller kwargs assembly。
- 风险：如果过早动 root adapter，容易在 runtime/controller 仍未稳定时引入新的 wiring noise。
- 推荐方向：最后一波再压缩 root adapter wiring，把 controller kwargs/builder glue 压成更清晰的 support-only bundle，同时保持顶层 `async_setup*` / `async_unload*` / `async_reload*` 仍只做 thin delegate。

### 4. `runtime_infra.py` / `core/coordinator/lifecycle.py`
- 现状：二者都已经是正确 internal home；`runtime_infra.py` 负责 shared infra/listener，`lifecycle.py` 负责 update/shutdown cycle。
- 风险：第二轮瘦身若把更多 owner decisions 塞入这两个文件，会让 support seam 变相成为 second home。
- 推荐方向：只让它们承接更清晰的局部 mechanics；若新建 support-only files，必须通过 docs + tests 明确 non-root 身份。

## Concern Clusters

### Runtime cluster A — entity bookkeeping / state sync ballast
- current signals: `register_entity()`、`unregister_entity()`、`_replace_devices()` 与 `_state.entities` / `_state.entities_by_device` 重复簿记。
- recommended landing zone: `core/coordinator/runtime/*` 现有 state/internal helper 或新的 `core/coordinator/runtime_wiring.py` support seam。
- forbidden drift: 不得把 state runtime/internal helper 讲成 runtime root；entity/platform consumers 仍只通过 `Coordinator` public methods 访问。

### Runtime cluster B — runtime bootstrapping
- current signals: `_build_runtime_context()`、`_build_update_cycle()`、`_init_service_layer()`。
- recommended landing zone: `custom_components/lipro/core/coordinator/runtime_wiring.py` 或等价 internal home。
- forbidden drift: `Coordinator` 仍是唯一 runtime root；不能新增 `RuntimeRootBuilder` / façade / package export。

### Lifecycle cluster — setup preparation / activation / rollback / unload reconcile
- current signals: `_async_prepare_entry_setup()`、`_async_complete_setup()`、`_attach_entry_lifecycle_hooks()`、`_async_abort_setup()`、`_async_cleanup_unloaded_entry()`、`_async_sync_services_after_unload()`。
- recommended landing zone: `custom_components/lipro/control/entry_lifecycle_support.py` 或等价 controller-private support-only home。
- forbidden drift: `EntryLifecycleController` 仍必须拥有 public lifecycle methods 与 named failure contract logging；support file 不能成为新的 lifecycle owner。

### Entry-root cluster — lazy wiring / controller assembly
- current signals: `_entry_auth_module()` / `_service_registrations_module()` wrappers、`_build_service_registry()`、`_build_entry_lifecycle_controller_kwargs()`。
- recommended landing zone: `custom_components/lipro/control/entry_root_wiring.py` 或等价 support-only home。
- forbidden drift: 新 support file 不能成为 HA adapter public home；根模块方法仍只在 `custom_components/lipro/__init__.py` 暴露。

## Verification Strategy

### Focused tests
- `tests/core/test_coordinator.py`
- `tests/core/test_coordinator_entry.py`
- `tests/core/coordinator/test_runtime_root.py`
- `tests/core/coordinator/test_update_flow.py`
- `tests/core/test_init_runtime_setup_entry.py`
- `tests/core/test_init_runtime_setup_entry_failures.py`
- `tests/core/test_init_runtime_registry_refresh.py`
- `tests/core/test_init_runtime_unload_reload.py`
- `tests/core/test_control_plane.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_modularization_surfaces.py`

## Recommended Wave Plan

### Wave 1 — Runtime root throttling
- First shrink `Coordinator`: move entity bookkeeping and runtime bootstrapping ballast inward.
- Keep `Coordinator` as sole runtime public home.
- Verify with coordinator/runtime-focused suites.

### Wave 2 — Lifecycle owner decomposition
- Split controller-private setup/activation/rollback/unload mechanics.
- Keep `EntryLifecycleController` as sole control-plane lifecycle owner.
- Verify with init runtime setup/unload/failure suites.

### Wave 3 — HA root adapter compression + truth freeze
- Compress `__init__.py` controller-assembly glue behind a support-only seam.
- Keep lazy loading and thin delegate entrypoints intact.
- Freeze story via control-plane tests + public surface / dependency / modularization guards.

## Non-Goals
- No `anonymous_share` / diagnostics helper refactor.
- No mega-test or typing-metric work here.
- No new public exports or new runtime/control roots.
