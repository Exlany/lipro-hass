# Phase 104 Research

## Repository-Wide Audit Inputs

- `custom_components/lipro/control/service_router_handlers.py` 目前 359 行，仍把 command / schedule / share / diagnostics / capability / maintenance 多族群收在同一 private handler home。
- `custom_components/lipro/core/coordinator/runtime/command_runtime.py` 目前 464 行，仍保留 success bookkeeping、API-error / reauth handling、command-result failure shaping 等 inward mechanics。
- `tests/core/test_init_service_handlers_*.py`、`tests/core/coordinator/runtime/test_command_runtime*.py` 已具备 topicized regression 基础，可以在不扩大 outward story 的前提下承接 second-pass inward split。
- `.planning/reviews/RESIDUAL_LEDGER.md` 已把 `service_router_handlers.py` family density 与 `command_runtime.py` second pass 明确登记为 live residual；本 phase 要把它们真正收口，而不是继续 conversation-only 跟踪。

## Selected Scope

本 phase 选择三段式推进：
1. 先把 `service_router_handlers.py` 切成 focused handler families，同时保留 `service_router.py` public callback surface 不变。
2. 再把 `CommandRuntime` 的 success / failure / reauth outcome mechanics 继续下沉到 localized runtime support（`command_runtime_support.py` + `command_runtime_outcome_support.py`），保留 orchestration root 在正式 runtime home。
3. 最后把 active-route 文档、focused guards、FILE_MATRIX / residual ledgers 一次性前推到 `Phase 104 complete`。

## Explicit Non-Goals

- 不把 `control/service_router.py` 改写成第二条 control root，也不让 `services/*` 回流拥有 callback truth。
- 不改变 `CommandRuntime.send_device_command()`、`ConfirmationManager`、`CommandSender` 的 outward contract。
- 不提前处理 `Phase 105` 的 governance rule datafication、脚本规则表驱动或 milestone freeze。
