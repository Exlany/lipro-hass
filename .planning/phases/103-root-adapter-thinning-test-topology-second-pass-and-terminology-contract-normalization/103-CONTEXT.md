# Phase 103: Root adapter thinning, test topology second pass, and terminology contract normalization - Context

**Gathered:** 2026-03-28
**Status:** Complete / active-route continuation-ready

<domain>
## Phase Boundary

本 phase 只处理三类高 ROI 残留：
- HA 根入口 `custom_components/lipro/__init__.py` 仍承载过多 lazy-load / entry-auth / service-registry adapter 细节
- `tests/conftest.py` 仍集中维护 topicized collection hooks 与 `_CoordinatorDouble`
- `support / surface / wiring / handlers / facade` 术语在代码/文档层仍有认知重叠

它不直接进入 `service_router_handlers.py` / `command_runtime.py` 的更深拆分；这些被显式留给 `Phase 104`。
</domain>

<decisions>
## Locked Decisions

- 保持 `v1.28` 作为 latest archived baseline，不回写其 closeout 资产。
- `Phase 103` 只做 thin-adapter 收窄、test-topology second pass 与 terminology contract normalization。
- `Phase 104/105` 必须继续存在于 roadmap/requirements 中，防止未完成残留再次退化成 conversation-only TODO。
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
</canonical_refs>
