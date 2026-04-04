# Phase 142 Context

## Goal

把 `.planning` selector family、promoted assets、derived collaboration maps、latest archived evidence pointer 与 maintainer-facing docs first-hop 压回单一 authority story，并为后续 toolchain / hotspot 工作建立 machine-checkable 的 planning foundation。

## Why Now

`v1.43` 已完成 archived closeout，但契约者要的不是“停在归档后自我满足”，而是继续做顶级架构师视角的彻底收敛。新一轮必须显式开启，而不是复活 `Phase 141`。

## Scope

- selector family / latest archived pointer / promoted asset allowlist 的 current truth 盘点
- `.planning/codebase` freshness / authority / snapshot 边界梳理
- maintainer-facing docs first-hop 与 route hardcode 盘点
- 把后续 Phase 143 -> 145 的 hotspot charter 压成可执行 plan

## Non-Goals

- 不在本 phase 直接重构 `runtime_types.py`、`dispatch.py`、`auth/manager.py`、`firmware_update.py`
- 不把 docs / derived views / gsd-tools fallback 提升为 authority

## Planned Requirement IDs

`AUD-10`, `GOV-99`, `GOV-100`, `DOC-25`, `TST-62`
