# Phase 50: REST typed-surface reduction and command/result ownership convergence - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning
**Source:** `Phase 46` remediation route + `Phase 47 -> 49` closeout + targeted REST/command/diagnostics reread

<domain>
## Phase Boundary

本 phase 只处理 `Phase 46` 已正式路由到 `Phase 50` 的两类收口工作：

1. `custom_components/lipro/core/api/endpoint_surface.py`、`request_gateway.py`、`rest_facade.py` 及其 request/endpoint method thin wrappers 中仍残留的宽口 `Any`、诚实度不足的 helper 签名，以及未接入现有 typed alias/TypedDict 的 REST child façade family 类型债；
2. `core/command/result.py` / `result_policy.py` 与 diagnostics auth-error 流中的 ownership drift：同一类 polling/retry policy 与 auth-error handling 仍散落在 `core/command/*`、`services/execution.py`、`services/diagnostics/helpers.py`、`services/diagnostics/handlers.py` 之间。

本 phase 的目标是继续压缩 typed debt 与 conceptual ownership drift，而不是重设计 REST public API、引入第二条正式主链、或让 localized collaborator 反向变成新 root。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `LiproRestFacade` 继续保持唯一 canonical REST child façade；`request_gateway.py`、`endpoint_surface.py`、`rest_facade_request_methods.py`、`rest_facade_endpoint_methods.py` 只能是 localized collaborator / thin wrapper，不得提升为第二 public root。
- REST typed truth 必须优先回接到 `custom_components/lipro/core/api/types.py` 或同一 API family 内的正式 typed alias home；不能靠新增大量 `cast(...)`、`assert isinstance(...)` 或局部 helper 私有 folklore 假装“类型更严”。
- `endpoint_surface.py` / `request_gateway.py` 中保留的宽口 `Any` 必须区分 `sanctioned_any` 与 `backlog_any`，并被 machine-checkable typed-budget guard 约束；不能仅在 summary prose 里宣称“后续再清理”。
- `custom_components/lipro/core/command/result_policy.py` 应作为 command-result polling/retry/delayed-refresh policy 的 formal implementation home；`custom_components/lipro/core/command/result.py` 应继续承担 stable export / failure payload composition，而不是复制第二套 policy 实现。
- `custom_components/lipro/services/execution.py` 继续保持 formal shared service execution facade 身份；diagnostics auth-error handling 必须向这里回收或显式复用这里，不能在 `helpers.py` / `handlers.py` 中继续长出独立 auth chain。
- REST public surface、command/query contract、control/runtime dependency direction 与 north-star formal root 叙事必须保持稳定；Phase 50 不得恢复 compat shell、legacy package export、second root、或 raw vendor payload 穿透 boundary。

### Claude's Discretion
- 可新增少量 API family 内部 typed alias / Protocol / TypedDict，只要 formal home 明确、命名贴近现有 `types.py` 风格，且不扩大 public surface。
- typed-budget guard 可选择扩展现有 `tests/meta/test_phase45_hotspot_budget_guards.py`，或新增一个仅覆盖 Phase 50 touched zone 的 meta guard；前提是 touched-zone machine truth 清晰、no-growth / net-reduction 可验证。
- diagnostics auth-error convergence 可通过抽取 execution-level helper、增加 small wrapper、或重用 `async_execute_coordinator_call()` 完成；只要最终 formal home 收敛到 `services/execution.py`，且 multi-coordinator optional capability degrade 语义不丢失即可。
- 若某些 REST payload 仍无法在本 phase 完全 TypedDict 化，必须在 guard 中显式登记为 sanctioned boundary debt，并压缩到最小、最诚实的边界。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / governance truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 单主链、边界归一化与 north-star 裁决
- `AGENTS.md` — formal home、truth order、phase asset 身份与 required sync 规则
- `.planning/PROJECT.md` — 当前 `v1.7` follow-up route 与 execution truth
- `.planning/ROADMAP.md` — `Phase 50` 的正式 goal / plans / success criteria
- `.planning/REQUIREMENTS.md` — `TYP-12` / `ARC-07` traceability truth
- `.planning/STATE.md` — 当前 next action 与 phase continuity

### Baseline / review truth that may need sync
- `.planning/baseline/PUBLIC_SURFACES.md` — `LiproRestFacade` canonical status、`services/execution.py` formal shared facade truth
- `.planning/baseline/DEPENDENCY_MATRIX.md` — REST child façade / localized collaborator / dependency direction truth
- `.planning/baseline/VERIFICATION_MATRIX.md` — protocol/API/control verification routing
- `.planning/reviews/FILE_MATRIX.md` — `endpoint_surface.py`、`request_gateway.py`、`services/execution.py`、diagnostics helper family 的 current wording
- `.planning/reviews/RESIDUAL_LEDGER.md` — residual/kill wording 与 execution facade non-residual truth
- `.planning/reviews/KILL_LIST.md` — 不得误把 `services/execution.py` 写回 kill target

### Prior audit / prior phase anchors
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-AUDIT.md` — repo-wide audit verdict
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-SCORE-MATRIX.md` — typing / architecture scoring 与 follow-up rationale
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md` — `Phase 50` 原始 remediation route
- `.planning/phases/48-runtime-access-and-formal-root-hotspot-decomposition-without-public-surface-drift/48-SUMMARY.md` — formal-root hotspot recent truth
- `.planning/phases/49-mega-test-topicization-and-failure-localization-hardening/49-SUMMARY.md` — most recent closeout / testing topology baseline
- `.planning/phases/49-mega-test-topicization-and-failure-localization-hardening/49-VERIFICATION.md` — current guard topology / regression anchors

### Implementation hotspots
- `custom_components/lipro/core/api/types.py`
- `custom_components/lipro/core/api/endpoint_surface.py`
- `custom_components/lipro/core/api/request_gateway.py`
- `custom_components/lipro/core/api/rest_facade.py`
- `custom_components/lipro/core/api/rest_facade_request_methods.py`
- `custom_components/lipro/core/api/rest_facade_endpoint_methods.py`
- `custom_components/lipro/core/command/result.py`
- `custom_components/lipro/core/command/result_policy.py`
- `custom_components/lipro/core/command/dispatch.py`
- `custom_components/lipro/services/execution.py`
- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/services/diagnostics/handlers.py`

### Verification / touched guards
- `tests/core/api/test_api_command_surface.py`
- `tests/core/api/test_api_status_service.py`
- `tests/core/test_command_result.py`
- `tests/meta/test_phase31_runtime_budget_guards.py`
- `tests/meta/test_phase45_hotspot_budget_guards.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_public_surface_guards.py`

</canonical_refs>

<specifics>
## Specific Ideas

- `core/api/types.py` 已具备 `JsonValue`、`MqttConfigResponse`、`CommandResultApiResponse`、`DiagnosticsApiResponse` 等 typed asset；Phase 50 应优先把 endpoint/request helper 返回值接回这些已存在的 truth，而不是继续让 `dict[str, Any]` 横贯 façade family。
- `tests/core/api/test_api_status_service.py` 已揭示 `on_batch_metric` 的实际 callback 形状；该 seam 适合在 `endpoint_surface.py` 变成正式 typed callback alias / protocol。
- `request_gateway.py` 是 raw mapping response 最自然的 localized home：可在此承接 `tuple[status, raw_payload, headers, request_token]` 一类 boundary alias，再向上层尽快收敛为 typed mapping / typed payload。
- `result.py` 与 `result_policy.py` 当前同时持有 polling/retry/delayed-refresh 语义；本 phase 应结束“实现双持、导出双重叙事”的状态。
- diagnostics optional capability 流已经部分复用 `async_execute_coordinator_call()`；剩余的 auth-error duplication 主要集中在 multi-coordinator fallback helper，应尽量在 `services/execution.py` 加强复用而不是新造 helper home。
- 若本 phase 调整 file-matrix / baseline wording，必须明确是“formal home unchanged, implementation convergence tightened”，避免把 localized collaborator 重新讲成 external contract。

</specifics>

<deferred>
## Deferred Ideas

- 不在本 phase 内做 REST public API redesign、protocol child façade 改名、package export 迁移或对外 breaking changes。
- 不在本 phase 内承诺全仓 `Any` 清零；只处理 `Phase 50` touched zone 的 targeted typed reduction 与 ownership convergence。
- 不在本 phase 内引入新的 service family / diagnostics execution subsystem / command-result package split；formal home 以现有 north-star home 为准。

</deferred>

---

*Phase: 50-rest-typed-surface-reduction-and-command-result-ownership-convergence*
*Context gathered: 2026-03-21 via Phase 46 route + targeted hotspot reread*
