# Phase 02 Validation: API Client De-Mixin

**Updated:** 2026-03-12
**Validation mode:** Executed + Nyquist audit
**Status:** Completed / validated

## Requirement Coverage

| Requirement | Covered by | Evidence Type | Current State |
|---|---|---|---|
| `ARCH-01` | `02-ARCHITECTURE.md`, `02-01/02/03/04-SUMMARY.md`, `.planning/reviews/FILE_MATRIX.md` | architecture + execution + governance proof | Complete |
| `PROT-03` | `custom_components/lipro/core/api/__init__.py`, `custom_components/lipro/core/api/client.py`, `02-02-SUMMARY.md` | formal REST root + collaborator graph | Complete |
| `PROT-04` | `custom_components/lipro/core/api/request_policy.py`, `custom_components/lipro/core/api/response_safety.py`, `02-03-SUMMARY.md`, `02-04-SUMMARY.md` | canonical normalization + compat demotion | Complete |
| `PROT-07` | `tests/core/api/test_protocol_contract_matrix.py`, `tests/snapshots/test_api_snapshots.py`, `02-04-SUMMARY.md` | contract regression + public-surface closeout | Complete |

## Automated Proof

- `uv run pytest tests/core/api/test_api.py tests/core/api/test_api_command_service.py tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_status_service.py tests/core/api/test_protocol_contract_matrix.py tests/snapshots/test_api_snapshots.py tests/flows/test_config_flow.py tests/test_coordinator_runtime.py tests/platforms/test_update_task_callback.py tests/meta/test_public_surface_guards.py -q`
- Result: `335 passed`, `2 snapshots passed`

## Residual / Manual-Only

- `LiproClient` 仍作为显式 compat shell 存在，但不再承担正式 REST root 语义。
- mixin spine 已退出正式生产主链，剩余 compat/patch seams 已登记到 `RESIDUAL_LEDGER.md` 与 `KILL_LIST.md`。

## Release Gate

- [x] `LiproRestFacade` 已成为 Phase 2 的正式 REST 子门面
- [x] contract tests / snapshots 持续证明 Phase 1 baseline 未被破坏
- [x] compat wrappers、legacy public names、mixin residual 已进入治理台账
- [x] `Phase 2.5` 可把 Phase 2 输出作为统一协议根的真实上游

## Validation Audit 2026-03-12

| Metric | Count |
|--------|-------|
| Gaps found | 3 |
| Resolved | 3 |
| Escalated | 0 |
