# Phase 53: Runtime and entry-root second-round throttling - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning
**Source:** `v1.8` roadmap route + `Phase 48/52` closeout evidence + targeted runtime/entry-root reread

<domain>
## Phase Boundary

本 phase 只处理 `HOT-12`：沿现有正式 seams 继续给 `custom_components/lipro/__init__.py`、`custom_components/lipro/control/entry_lifecycle_controller.py` 与 `custom_components/lipro/core/coordinator/coordinator.py` 限流，降低 root-level orchestration density，同时保持以下真相完全不漂移：

1. `custom_components/lipro/__init__.py` 仍只是 Home Assistant root adapter，且继续通过 lazy composition 按调用时现取依赖；
2. `EntryLifecycleController` 仍是 setup / unload / reload 的唯一 control-plane owner；
3. `Coordinator` 仍是唯一 runtime orchestration root；
4. `runtime_infra.py`、`core/coordinator/lifecycle.py` 与新增 support-only seams 只能承接局部机械细节，不得被提升为第二 root / 第二 runtime story / 第二 control story；
5. public behavior、dependency direction、tests wording 与 governance docs 必须继续讲同一条 single-root / single-owner / lazy-wiring 故事线。

本 phase 的重点不是创建新的 manager hierarchy、不是把 orchestration 再分叉到 services/runtime_infra side stories，也不是重新打开 `Phase 48` 已收口的 runtime-access 争议；重点是对仍然集中在 root body 的 wiring、activation / unload 流程与 runtime bootstrapping ballast 做第二轮 inward decomposition。

本 phase 不处理 `anonymous_share` / diagnostics helper hotspot（`Phase 54`），也不处理 mega-test topicization round 2 与 typing metric stratification（`Phase 55`）。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `custom_components/lipro/__init__.py` 只允许继续变薄，不得恢复 eager binding、模块级 controller singleton、预绑定 `EntryLifecycleController` 或新的 root-level state。
- `EntryLifecycleController` 可以引入 localized support module / dataclass / helper family，但 formal owner 身份必须保留在 controller；setup preparation、activation cleanup、unload service sync 与 reload logging 只能 inward 下沉，不能回流 `services/*` 或 `runtime_infra.py` 变成第二条 lifecycle mainline。
- `Coordinator` 必须继续保留唯一 runtime orchestration root 身份；runtime context、service-layer bootstrapping、update-cycle assembly、entity bookkeeping 若继续下沉，只能进入 `core/coordinator/*` internal/support home，不能新增 package export、runtime facade、orchestrator root 或 control-facing helper。
- `runtime_infra.py` 与 `core/coordinator/lifecycle.py` 继续只是 support/home-collaborator；不得因第二轮瘦身而被文档、tests 或 imports 偷渡成 public surface。
- 若本 phase 引入新的 support-only files，必须同步更新 baseline / review truth 与 meta guards，显式说明它们不是新 formal root。

### Claude's Discretion
- `__init__.py` 的瘦身优先落在 controller kwargs assembly、entry-auth wrapper glue，还是 service-registry / runtime-infra binding；只要 lazy wiring 更清晰且 patch seam 不上浮即可。
- `EntryLifecycleController` 的 support seam 采用 focused helper functions、support dataclass 还是更窄的 lifecycle operations module；只要 owner story 不漂移即可。
- `Coordinator` 的 ballast 优先落在 runtime bootstrapping、service-layer initialization 还是 entity registration bookkeeping；只要 `Coordinator` 仍保持唯一 import/public home 即可。
- verification 可优先使用 focused init/control/coordinator tests + meta guards；只要能 machine-check single-owner / lazy-wiring truth 即可。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / current truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

### Prior phase anchors
- `.planning/phases/48-runtime-access-and-formal-root-hotspot-decomposition-without-public-surface-drift/48-SUMMARY.md`
- `.planning/phases/48-runtime-access-and-formal-root-hotspot-decomposition-without-public-surface-drift/48-VERIFICATION.md`
- `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-SUMMARY.md`
- `.planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-VERIFICATION.md`

### Runtime / entry-root hotspots
- `custom_components/lipro/__init__.py`
- `custom_components/lipro/control/entry_lifecycle_controller.py`
- `custom_components/lipro/runtime_infra.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/core/coordinator/lifecycle.py`
- `custom_components/lipro/core/coordinator/orchestrator.py`
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/runtime_types.py`

### Focused verify anchors
- `tests/core/test_control_plane.py`
- `tests/core/test_coordinator.py`
- `tests/core/coordinator/test_runtime_root.py`
- `tests/core/coordinator/test_runtime_polling.py`
- `tests/core/test_init_runtime_behavior.py`
- `tests/core/test_init_runtime_setup_entry.py`
- `tests/core/test_init_runtime_unload_reload.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`

</canonical_refs>

<specifics>
## Specific Ideas

- `custom_components/lipro/__init__.py` 当前最明显的密度集中在：entry-auth wrapper aliases、`_build_service_registry()` 与 `_build_entry_lifecycle_controller_kwargs()`；这些适合继续向 control-plane support-only wiring seam 下沉。
- `EntryLifecycleController` 当前已具备清晰 owner 身份，但 prepare / complete / activate / abort / unload-sync 仍集中在一处；适合抽成 support-only lifecycle operations，而不是让 controller 持续兼任 full flow script。
- `Coordinator` 当前可继续 inward decomposition 的 concern clusters 包括：runtime context assembly、service-layer initialization、update-cycle build、entity bookkeeping；这些都可进入 `core/coordinator/*` internal home，但 `Coordinator` 仍保留唯一 runtime public home。
- `runtime_infra.py` 与 `core/coordinator/lifecycle.py` 已是正确 helper homes，本 phase 只应增强它们作为 internal/support seam 的清晰度，而不是把 ownership 从 root 挪走。
- meta guards 与 baseline docs 应明确说明 support-only seam 的边界，防止 `runtime_infra`、lifecycle collaborator 或 controller support module 被误叙述为新的 public surface。

</specifics>

<deferred>
## Deferred Ideas

- `Phase 54`: anonymous-share / diagnostics helper family slimming 与 privacy-sensitive helper formalization。
- `Phase 55`: API/MQTT/platform mega-test topicization round 2 与 repo-wide typing metric stratification。
- broad naming/style cleanup、runtime-access 第三轮 sweeping、或任何不直接服务 `HOT-12` 的 repo-wide governance rewrite。
- 新 façade、new manager hierarchy、package export、或 control/runtime 双主链并存的“便利性”设计。

</deferred>

---

*Phase: 53-runtime-and-entry-root-second-round-throttling*
*Context gathered: 2026-03-21 from v1.8 route + Phase 48/52 evidence + runtime/entry-root reread*
