# Phase 56 Verification

status: passed

## Goal

- 验证 `Phase 56: Shared backoff neutralization and cross-plane retry hygiene` 是否完成 `RES-13 / ARC-09 / GOV-40`：generic exponential backoff primitive 已迁到 neutral helper home，非 API callers 不再从 `request_policy.py` 获取它，而 governance truth 也已明确关闭 residual。

## Evidence

- `custom_components/lipro/core/utils/backoff.py` 现承接 pure exponential backoff math；它没有扩张成 retry manager、strategy root 或 package-level public surface。
- `custom_components/lipro/core/api/request_policy.py` 不再导出 `compute_exponential_retry_wait_time()`；`RequestPolicy` 继续保留 `compute_rate_limit_wait_time()`、busy retry 与 CHANGE_STATE pacing formal truth。
- `custom_components/lipro/core/command/result_policy.py`、runtime `RetryStrategy` 与 `custom_components/lipro/core/mqtt/setup_backoff.py` 已切到 neutral helper import，plane-local semantics 保持稳定。
- `.planning/reviews/RESIDUAL_LEDGER.md` 已把 `Generic backoff helper leak` 从 active family 转入 closed family；`.planning/baseline/{PUBLIC_SURFACES,DEPENDENCY_MATRIX,VERIFICATION_MATRIX}.md` 与 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 也已同步记录 `Phase 56` current truth。

## Verification Commands

- `uv run pytest -q tests/core/api/test_api_request_policy.py tests/core/mqtt/test_mqtt_backoff.py tests/core/test_command_result.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance_followup_route.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_guards.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check custom_components/lipro/core/utils/backoff.py custom_components/lipro/core/api/request_policy.py custom_components/lipro/core/api/request_policy_support.py custom_components/lipro/core/command/result_policy.py custom_components/lipro/core/coordinator/runtime/command/retry.py custom_components/lipro/core/mqtt/setup_backoff.py tests/core/api/test_api_request_policy.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance_followup_route.py tests/meta/test_governance_phase_history.py scripts/check_file_matrix.py`

## Result

- Focused production / governance tests pass with `161 passed`.
- File-governance inventory remains synchronized and now includes `core/utils/backoff.py`.
- Residual closeout is reflected in both current-story docs and machine guards.

## Verdict

- `RES-13` satisfied: generic backoff primitive no longer leaks from `request_policy.py` across planes.
- `ARC-09` satisfied: command/runtime/MQTT callers share only a neutral primitive while keeping local retry semantics.
- `GOV-40` satisfied: baselines, ledgers, promoted assets, and current milestone truth all record the residual closure.
