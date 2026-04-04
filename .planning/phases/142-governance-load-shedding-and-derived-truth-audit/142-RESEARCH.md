# Phase 142 Research

## Thesis

`v1.43` closeout 已证明 archived-only selector story 可以稳定落盘，但 remaining maintenance tax 主要还集中在两类：

1. **治理减负 / derived truth 压缩**
   - `.planning/codebase` 是协作图谱，不应承担 live truth。
   - selector family、promoted assets、latest archived pointer 与 docs first-hop 仍有继续 topicize / harden 的空间。
   - nested worktree 下 `gsd-tools` root detection 继续不能被误当 authority。 

2. **sanctioned hotspot breadth**
   - `runtime_types.py`
   - request-policy family
   - `core/command/dispatch.py` / `result.py` / `result_policy.py`
   - `core/auth/manager.py` / `core/api/auth_recovery.py`
   - `entities/firmware_update.py` / `core/ota/manifest.py` / `core/anonymous_share/manager.py`

## Decision

`Phase 142` 只处理第一类：
- inventory & selector-boundary audit
- toolchain / freshness proof hardening
- docs / baseline / guard sync

热点收窄本身后移到 `Phase 144` / `145`，避免把治理减负与大规模 code refactor 混成同一执行波次。

## Guardrails

- 不把 formal homes 误判为 kill targets
- 不让 `.planning/codebase`、docs 或 fallback tooling 反向升级为 authority
- 不复活 `v1.43` archived-only route
