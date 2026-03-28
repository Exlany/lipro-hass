# Phase 95: Schedule/runtime and boundary hotspot inward decomposition - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

`Phase 95` 只做 hotspot inward split，不重新打开 typed-boundary 路线：重点对象是 `custom_components/lipro/core/api/schedule_service.py`、相邻 runtime orchestration helpers 与 boundary decoder support。目标是继续缩小单文件 / 单函数复杂度，同时保持 formal home 与 single-root story 不漂移。
</domain>

<decisions>
## Implementation Decisions
- **D-01:** 只能沿 `v1.25` 已冻结的 formal-home map inward split；不得新建 outward root。
- **D-02:** 优先切出 pure helper / selector / executor，而不是复制 coordinator / protocol orchestration。
- **D-03:** 所有拆分都要同步 `FILE_MATRIX / DEPENDENCY_MATRIX / PUBLIC_SURFACES` 的 formal-home 叙事。
</decisions>
