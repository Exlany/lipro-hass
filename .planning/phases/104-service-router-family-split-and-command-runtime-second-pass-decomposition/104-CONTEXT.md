# Phase 104: Service-router family split and command-runtime second-pass decomposition - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

本 phase 只处理两类 active-route 热点，并补齐对应 focused regressions：
- `custom_components/lipro/control/service_router_handlers.py` 仍把 command / schedule / share / diagnostics / capability / maintenance 多族群揉在同一 handler home，family density 过高。
- `custom_components/lipro/core/coordinator/runtime/command_runtime.py` 仍把 orchestration、failure normalization、success bookkeeping 与 reauth handling 混在同一正式 runtime home。
- 补齐 `TST-36`：保证 family split 与 second-pass inward split 后，outward contract、focused guards、质量门与治理文档不回流。

本 phase 不改 `service_router.py` outward callback surface，不改变 `CommandRuntime` outward contract，也不提前消费 `Phase 105` 的 governance rule datafication。
</domain>

<decisions>
## Locked Decisions

- 保持 `v1.28` 作为 latest archived baseline，不回写其 closeout 资产。
- `service_router.py` 保持 outward service callback surface 稳定；允许其依赖更细粒度的 family handler homes，但不引入第二条 control story。
- `CommandRuntime` 保持正式 orchestration root 身份；只把 failure normalization、success bookkeeping 与 reauth error handling 下沉到 local runtime support collaborator。
- `Phase 104` 必须同步 focused guards、planning docs 与 file-governance 真源，不能留下 conversation-only verdict。
</decisions>

<canonical_refs>
## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `docs/developer_architecture.md`
- `docs/adr/0005-entry-surface-terminology-contract.md`
- `custom_components/lipro/control/service_router.py`
- `custom_components/lipro/control/service_router_handlers.py`
- `custom_components/lipro/core/coordinator/runtime/command_runtime.py`
- `custom_components/lipro/core/coordinator/runtime/command_runtime_support.py`
- `tests/core/test_init_service_handlers_commands.py`
- `tests/core/test_init_service_handlers_schedules.py`
- `tests/core/test_init_service_handlers_share_reports.py`
- `tests/core/test_init_service_handlers_debug_queries.py`
- `tests/core/test_init_runtime_registry_refresh.py`
- `tests/core/coordinator/runtime/test_command_runtime.py`
- `tests/meta/test_phase73_service_runtime_convergence_guards.py`
- `tests/meta/test_phase95_hotspot_decomposition_guards.py`
- `tests/meta/test_phase99_runtime_hotspot_support_guards.py`
</canonical_refs>
