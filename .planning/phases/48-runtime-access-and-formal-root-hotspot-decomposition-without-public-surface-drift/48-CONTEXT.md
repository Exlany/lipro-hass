# Phase 48: Runtime-access and formal-root hotspot decomposition without public-surface drift - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning
**Source:** `Phase 46` audit + `Phase 47` closeout + focused hotspot re-read

<domain>
## Phase Boundary

本 phase 只处理 `Phase 46` 已正式路由的两类高杠杆结构债：

1. `custom_components/lipro/control/runtime_access.py` 已是正确的 control/runtime read-model formal home，但当前同时承载 entry traversal、device lookup、telemetry exporter、system-health snapshot coercion 与 diagnostics projection，已接近 projection megafile；
2. `custom_components/lipro/core/coordinator/coordinator.py`、`custom_components/lipro/__init__.py` 与 `custom_components/lipro/control/entry_lifecycle_controller.py` 虽然方向正确，但 decision density 仍偏高：`Coordinator` 仍保留多组 update-cycle / MQTT lifecycle / entity bookkeeping ballast，根模块仍携带较多 patch seam + lazy builder glue，entry lifecycle controller 仍独占 setup/unload/reload orchestration 的多段流程。

本 phase 的目标不是改变 public surface、不是重开第二 orchestration root，也不是把 `RuntimeAccess` 的正式地位削弱掉；目标是沿现有正式 seams 把热点继续 inward/topicize，同时让 dependency/public-surface/lazy-wiring 守卫与基线文档讲同一条当前故事线。

本 phase 不处理 mega-test topicization、failure-localization overhaul、REST typed-surface reduction 与 command/result ownership convergence；这些分别属于 `Phase 49` 与 `Phase 50`。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `custom_components/lipro/control/runtime_access.py` 继续是 control/services 读取 runtime entry、device lookup、snapshot projection 的唯一正式 read-model home；任何 topicization 都只能是 internal decomposition，不得创造第二条 control/runtime bridge。
- `Coordinator` 继续是唯一 runtime orchestration root；向 `orchestrator.py`、`lifecycle.py`、runtime/service collaborators 的 inward 下沉必须保持 import home 和 public attributes 稳定，不得恢复 pure forwarder cluster、compat folklore 或 package-level export。
- `custom_components/lipro/__init__.py` 必须保持按调用时现取依赖的 lazy composition；`async_setup_entry()` / `async_unload_entry()` / `async_reload_entry()` 不得回退为 eager binding、模块级单例或预绑定 controller。
- `EntryLifecycleController` 继续是 setup/unload/reload formal owner；若拆 helper，只能在现有 control/runtime homes 内做 localized decomposition，不得把 ownership 推回 services 或 runtime-infra side stories。
- dependency/public-surface/governance 守卫必须同步收口：一旦 runtime_access / coordinator / init wiring 的 formal story变化，baseline 与 meta tests 必须同轮更新。

### Claude's Discretion
- `RuntimeAccess` 的 topicization 采用 localized helper module、内部 dataclass 还是更窄的 focused functions，只要 public import home 不变即可；
- `Coordinator` ballast 优先往 `orchestrator.py`、`lifecycle.py` 还是已有 runtime/service collaborators 下沉，可按当前最小风险 seams 裁定；
- `__init__.py` 与 `EntryLifecycleController` 的 slim-down 先收 builder glue，还是先收 activate/unload/reload helper，可按测试耦合最低的路径执行；
- `48-01` 与 `48-02` 可以并行，但若实现中发现 shared seam 冲突，执行时应退回串行，不牺牲正确性。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / current truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 单主链、边界、禁止项
- `AGENTS.md` — formal root / runtime access / lazy wiring / governance sync 约束
- `.planning/PROJECT.md` — `v1.7` 当前默认入口与 milestone truth
- `.planning/ROADMAP.md` — `Phase 48` goal、criteria 与 plan titles
- `.planning/REQUIREMENTS.md` — `RUN-08` / `ARC-06` requirement truth
- `.planning/STATE.md` — next-action / shipped-baseline truth

### Prior phase anchors
- `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-SUMMARY.md` — `runtime_access` formal-home truth
- `.planning/phases/43-control-services-boundary-decoupling-and-typed-runtime-access/43-SUMMARY.md` — typed `RuntimeAccess` / runtime-infra demotion 已完成状态
- `.planning/phases/43-control-services-boundary-decoupling-and-typed-runtime-access/43-01-PLAN.md` — `RuntimeAccess` typed-contract 的前序计划边界
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-AUDIT.md` — formal-root hotspots / open-source audit verdict
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-SCORE-MATRIX.md` — architecture score 与 phase routing rationale
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md` — `Phase 48` primary outcomes / verify anchors

### Formal-root hotspot files
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/telemetry_surface.py`
- `custom_components/lipro/control/system_health_surface.py`
- `custom_components/lipro/control/diagnostics_surface.py`
- `custom_components/lipro/control/entry_lifecycle_controller.py`
- `custom_components/lipro/__init__.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/core/coordinator/orchestrator.py`
- `custom_components/lipro/core/coordinator/lifecycle.py`
- `custom_components/lipro/runtime_infra.py`
- `custom_components/lipro/runtime_types.py`

### Baseline / guard truth
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_public_surface_guards.py`

### Focused verify anchors
- `tests/core/test_control_plane.py`
- `tests/core/test_diagnostics.py`
- `tests/core/test_system_health.py`
- `tests/core/test_coordinator.py`
- `tests/core/test_coordinator_integration.py`
- `tests/test_coordinator_public.py`
- `tests/test_coordinator_runtime.py`
- `tests/core/test_init.py`
- `tests/core/test_init_runtime_setup_entry.py`
- `tests/core/test_init_runtime_unload_reload.py`
- `tests/core/test_init_runtime_behavior.py`
- `tests/core/test_init_service_handlers.py`

</canonical_refs>

<specifics>
## Specific Ideas

- `runtime_access.py` 可按 concern 切成「entry traversal / device lookup」、「snapshot + diagnostics projection」、「telemetry exporter / system-health view」三个簇，但 `runtime_access.py` 仍保持唯一 import home；
- `telemetry_surface.py` / `system_health_surface.py` 目前已经很薄，适合作为被下沉逻辑的消费端，而不是继续把更多投影逻辑堆回 `runtime_access.py`；
- `Coordinator` 已有 `orchestrator.py`、`lifecycle.py`、runtime/service collaborators，可优先把 update-cycle / MQTT lifecycle / pure helper ballast 继续 inward 到这些现有 seams；
- 根模块当前的 lazy pattern 是对的，但 `_entry_auth_module()`、public patch seams、service-registry builder 与 controller builder 仍占据较多视觉密度，适合进一步压缩成更小的 local factories；
- `EntryLifecycleController` 当前最值得收的是 prepare / complete / activate / unload / reload 辅助簇，而不是改变 ownership；
- guard 层应明确禁止 control consumers 重新直读 `entry.runtime_data` / coordinator internals，并持续锁住 `__init__.py` 的 lazy composition contract。

</specifics>

<deferred>
## Deferred Ideas

- 不在本 phase 内进行 `tests/meta/test_governance_closeout_guards.py` 的 mega-test topicization；那属于 `Phase 49`；
- 不在本 phase 内进行 REST child façade `Any` 减债、command/result ownership convergence、diagnostics auth-error duplication closure；那属于 `Phase 50`；
- 不在本 phase 内改变 package exports、对外 docs index、release/support/security continuity story；这些已在前序 phase 收口；
- 不为 hotspot slim-down 引入新的 manager hierarchy、locator story、compat shell 或 public adapter root。

</deferred>

---

*Phase: 48-runtime-access-and-formal-root-hotspot-decomposition-without-public-surface-drift*
*Context gathered: 2026-03-21 after Phase 47 closeout*
