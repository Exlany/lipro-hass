# Phase 129: rest fallback explicit-surface convergence and api hotspot slimming - Context

**Gathered:** 2026-04-01
**Status:** Ready for planning
**Source:** v1.37 milestone bootstrap + repo-wide audit intake

<domain>
## Phase Boundary

本阶段只处理 `custom_components/lipro/core/api/rest_facade.py` 与 `custom_components/lipro/core/api/status_fallback_support.py` 的首波 hotspot 收口，并同步补强 focused regressions / planning truth。目标是让 REST façade 的正式 surface 更显式、binary-split fallback support 更易审阅与验证，而不是扩展功能或引入第二条 API/query 故事线。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- 不新增第二个 REST root；`LiproRestFacade` 仍是唯一正式 REST child façade。
- 不改变 outward behavior；所有 refactor 必须以 focused/full tests 证明语义不变。
- `status_fallback_support.py` 只能 inward 收口职责，不能把 fallback truth 再散落回 wrapper 或 endpoint callers。
- phase 只覆盖 REST hotspot；`command_runtime.py` / `firmware_update.py` 留给后续 `Phase 130`。
- external continuity / private fallback 不在本 phase 伪装为已解决，它们属于后续 governance closeout 议题。

### the agent's Discretion
- 是否通过显式 wrapper/property 替代部分 generic helper。
- 是否将 fallback setup/context 的内部结构收口为更直观的 internal helper，只要不新增 public surface。
- 新增或调整 focused tests 的具体粒度与命名。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Governance & Architecture
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 北极星裁决标准
- `.planning/PROJECT.md` — 当前里程碑与 route truth
- `.planning/ROADMAP.md` — v1.37 阶段目标与成功标准
- `.planning/REQUIREMENTS.md` — v1.37 requirement mapping
- `.planning/codebase/CONCERNS.md` — 当前热点排名与技术债描述
- `AGENTS.md` — 仓级约束、formal home 与文档同步规则

### REST Hotspots
- `custom_components/lipro/core/api/rest_facade.py` — REST child façade 正式 home
- `custom_components/lipro/core/api/rest_facade_request_methods.py` — request-facing wrapper methods
- `custom_components/lipro/core/api/rest_facade_endpoint_methods.py` — endpoint wrapper methods
- `custom_components/lipro/core/api/status_fallback.py` — outward fallback wrapper
- `custom_components/lipro/core/api/status_fallback_support.py` — binary-split fallback support hotspot
- `custom_components/lipro/core/api/status_fallback_split_executor.py` — fallback split executor collaborator

### Guard Rails
- `tests/core/api/test_protocol_contract_facade_runtime.py` — façade topology / explicit-surface guards
- `tests/core/api/test_api_status_service_fallback.py` — fallback behavior / regression coverage
- `tests/core/api/test_api_status_service_regressions.py` — fallback logging / regression anchor

</canonical_refs>

<specifics>
## Specific Ideas

- 优先减少 `rest_facade.py` 中 generic property/method factory 对正式 surface 的遮蔽。
- 优先收口 `status_fallback_support.py` 中 primary-query / fallback-setup 重复与阅读负担。
- 如需新增 focused tests，优先围绕 façade explicitness 与 fallback invariants，而不是增加 brittle wording assertions。

</specifics>

<deferred>
## Deferred Ideas

- `command_runtime.py` / `firmware_update.py` 的 deeper decomposition
- repo-wide terminal audit final report 与 governance continuity closeout
- external delegate / private disclosure fallback 现实本身的外部补位

</deferred>

---

*Phase: 129-rest-fallback-explicit-surface-convergence-and-api-hotspot-slimming*
*Context gathered: 2026-04-01 via milestone bootstrap*
