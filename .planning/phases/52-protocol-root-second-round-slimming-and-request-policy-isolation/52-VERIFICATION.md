# Phase 52 Verification

status: passed

## Goal

- 验证 `Phase 52: Protocol-root second-round slimming and request-policy isolation` 是否完成 `ARC-08`：`LiproProtocolFacade` 继续保持单一 formal protocol root 身份，request-policy truth 已从 helper/executor/gateway 漂移中收回，baseline/review truth 与 meta guards 也已同步锁定新的 ownership story。

## Evidence

- `custom_components/lipro/core/protocol/facade.py` 仍只暴露 `LiproProtocolFacade` 这一 formal protocol root；`custom_components/lipro/core/protocol/rest_port.py` 已切成 concern-local `ProtocolRestPortFamily`，新增 `custom_components/lipro/core/protocol/protocol_facade_rest_methods.py` 也只承接 support-only child-facing bound methods，而非第二 public surface。
- `custom_components/lipro/core/api/request_policy.py` 现在直接持有 `handle_rate_limit()`、busy retry、CHANGE_STATE pacing 与 adaptive interval；`custom_components/lipro/core/api/transport_retry.py` 只剩 replay loop，所有 `429` 决策都通过 injected policy callback 回到 `RequestPolicy`。
- `custom_components/lipro/core/api/request_gateway.py` 已固定为 mapping/auth-aware retry-context orchestration home；`custom_components/lipro/core/api/transport_executor.py` 只保留 signed transport execution / response normalization。`tests/core/api/test_api_transport_and_schedule.py` 与 `tests/core/api/test_api_command_surface.py` 现直接守卫这一 gateway-vs-executor 切线。
- `.planning/baseline/PUBLIC_SURFACES.md`、`.planning/baseline/DEPENDENCY_MATRIX.md` 与 `.planning/baseline/VERIFICATION_MATRIX.md` 已新增 Phase 52 current truth；`.planning/reviews/FILE_MATRIX.md` 同步纳入 `protocol_facade_rest_methods.py`，`.planning/reviews/RESIDUAL_LEDGER.md` 与 `.planning/reviews/KILL_LIST.md` 也已把 `Generic backoff helper leak` 记为 deferred residual / non-kill-target story。
- `tests/meta/test_public_surface_guards.py` 与 `tests/meta/test_dependency_guards.py` 已新增 Phase 52 guards：禁止 `RequestPolicy` / `RestRequestGateway` / `RestTransportExecutor` 漂成 top-level package bindings，禁止 localized/support seams 被回讲成 second root / public contract。
- `.planning/ROADMAP.md`、`.planning/PROJECT.md`、`.planning/STATE.md`、`.planning/REQUIREMENTS.md` 与 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 已把 `Phase 52` 从 routed/execution status 提升为 complete/promoted evidence，并把默认下一步切到 `$gsd-plan-phase 53`。

## Validation

- `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_transport_and_schedule.py tests/core/api/test_api_request_policy.py tests/core/api/test_api_transport_executor.py tests/core/api/test_api_command_service.py tests/core/api/test_api_command_surface.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py -q` → `211 passed`
- `uv run python scripts/check_file_matrix.py --check` → `passed`
- `uv run pytest tests/meta/test_governance_followup_route.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_promoted_phase_assets.py -q` → `10 passed`

## Notes

- `Phase 52` 没有新增 second protocol root、second request owner、compat shell 或 package-level shortcut import；所有变化都沿既有 formal homes inward slimming。
- `Generic backoff helper leak` 是本 phase 唯一新增 deferred residual；它被显式记账，但当前不构成 file-level kill target。
- `52-SUMMARY.md` / `52-VERIFICATION.md` 已提升进 `PROMOTED_PHASE_ASSETS.md`；`52-CONTEXT.md`、`52-RESEARCH.md`、`52-VALIDATION.md` 与各 wave summary/plan 仍保持 execution-trace 身份。
