---
phase: 52
status: passed
plans_completed:
  - 52-01
  - 52-02
  - 52-03
verification: .planning/phases/52-protocol-root-second-round-slimming-and-request-policy-isolation/52-VERIFICATION.md
---

# Phase 52 Summary

## Outcome

- `custom_components/lipro/core/protocol/facade.py` 继续保持 `LiproProtocolFacade` 作为唯一 formal protocol root；`custom_components/lipro/core/protocol/rest_port.py` 已进一步收窄成 concern-local `ProtocolRestPortFamily`，而新增的 `custom_components/lipro/core/protocol/protocol_facade_rest_methods.py` 只承担 support-only REST child-facing bound-method seam，没有引入第二 façade / wrapper / root story。
- `custom_components/lipro/core/api/request_policy.py` 现成为 `429` / Retry-After / busy / pacing / adaptive interval 的 formal truth；`custom_components/lipro/core/api/request_gateway.py` 与 `custom_components/lipro/core/api/transport_executor.py` 的 boundary 已被重新裁清：gateway 只持有 mapping/auth-aware retry-context orchestration，executor 只保留 signed transport execution / response normalization。
- `.planning/baseline/PUBLIC_SURFACES.md`、`.planning/baseline/DEPENDENCY_MATRIX.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md` 与 `.planning/reviews/KILL_LIST.md` 已同步 Phase 52 current truth；`Generic backoff helper leak` 也被显式登记为 deferred residual，不再 silent defer。
- `tests/core/api/test_protocol_contract_matrix.py`、`tests/core/api/test_api_transport_and_schedule.py`、`tests/core/api/test_api_command_surface.py`、`tests/meta/test_public_surface_guards.py` 与 `tests/meta/test_dependency_guards.py` 已把 single protocol-root truth、request-policy ownership、gateway/executor boundary 与 top-level export hygiene 冻结为 machine-checkable guards。
- `Phase 52` 完成后，`v1.8` 从“仅完成 continuity closeout”推进到“formal-root sustainment 第一轮 closeout complete”；下一条 routed follow-up 正式切换到 `Phase 53`，而不是继续停留在 protocol/request-policy freeze 收尾。

## Changed Surfaces

- Protocol-root slimming / child-facing seams: `custom_components/lipro/core/protocol/{facade.py,rest_port.py,mqtt_facade.py,protocol_facade_rest_methods.py}`
- Request-policy / request ownership isolation: `custom_components/lipro/core/api/{request_policy.py,request_gateway.py,transport_executor.py,transport_retry.py,rest_facade.py,rest_facade_request_methods.py,command_api_service.py}`
- Focused regressions / meta guards: `tests/core/api/{test_protocol_contract_matrix.py,test_api_transport_and_schedule.py,test_api_request_policy.py,test_api_transport_executor.py,test_api_command_service.py,test_api_command_surface.py}`, `tests/meta/{test_public_surface_guards.py,test_dependency_guards.py,test_governance_followup_route.py,test_governance_phase_history.py,test_governance_promoted_phase_assets.py}`
- Governance closeout truth: `.planning/{ROADMAP.md,PROJECT.md,STATE.md,REQUIREMENTS.md}`, `.planning/reviews/{PROMOTED_PHASE_ASSETS.md,FILE_MATRIX.md,RESIDUAL_LEDGER.md,KILL_LIST.md}`

## Verification Snapshot

- `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_transport_and_schedule.py tests/core/api/test_api_request_policy.py tests/core/api/test_api_transport_executor.py tests/core/api/test_api_command_service.py tests/core/api/test_api_command_surface.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py -q` → `211 passed`
- `uv run python scripts/check_file_matrix.py --check` → `passed`
- `uv run pytest tests/meta/test_governance_followup_route.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_promoted_phase_assets.py -q` → `10 passed`

## Deferred to Later Work

- `Phase 53` 继续承接 `HOT-12`：runtime / entry-root second-round throttling。
- `Phase 54` 继续承接 `HOT-13`，并收走 `Generic backoff helper leak`：把 `compute_exponential_retry_wait_time()` 迁往 neutral shared backoff home，或改为各 plane 自持 wrapper。
- `Phase 55` 继续承接 `TST-10 / TYP-13`：mega-test topicization round 2 与 repo-wide typing-metric stratification。

## Promotion

- `52-SUMMARY.md` 与 `52-VERIFICATION.md` 已登记到 `.planning/reviews/PROMOTED_PHASE_ASSETS.md`，作为 `Phase 52` 的长期 closeout evidence。
- `52-CONTEXT.md`、`52-RESEARCH.md`、`52-VALIDATION.md`、`52-01~52-03-SUMMARY.md` 与 `52-0x-PLAN.md` 继续保持 execution-trace 身份，不自动升级为长期治理真源。
