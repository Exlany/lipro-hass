# Phase 97: Governance, open-source contract sync, and assurance freeze - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

`Phase 97` 承接前面三段实现收敛，把 v1.26 active route、baseline / review / codebase docs、route smoke tests、meta guards 与 open-source entry docs 最终冻结到同一条 current story 上，同时保持 v1.25 archived bundle 的 pull-only 身份不漂移。
</domain>

<decisions>
## Implementation Decisions
- **D-01:** 当前故事线必须显式区分 active milestone truth 与 archived evidence truth。
- **D-02:** assurance suites 继续 topicize / localize；不能让 governance tests 再长回 mega root。
- **D-03:** verification matrix、file matrix、dependency matrix、public surfaces、developer architecture 与 route smoke 必须统一更新。
</decisions>
