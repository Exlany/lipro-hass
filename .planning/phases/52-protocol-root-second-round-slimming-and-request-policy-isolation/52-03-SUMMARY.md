# 52-03 Summary

## Outcome

- `tests/core/api/test_protocol_contract_matrix.py`、`tests/core/api/test_api_transport_and_schedule.py` 与 `tests/core/api/test_api_command_surface.py` 已补上 Wave 3 ownership regressions：`LiproProtocolFacade` 继续锁定为唯一 protocol root，public transport wrapper 继续归于 executor boundary，public request wrapper 的 retry-context 继续归于 `RestRequestGateway`。
- `tests/meta/test_public_surface_guards.py` 与 `tests/meta/test_dependency_guards.py` 已新增 Phase 52 guard：冻结 single protocol-root story、禁止 `RequestPolicy` / `RestRequestGateway` / `RestTransportExecutor` 漂成 top-level public bindings，并要求 dependency/public-surface 文档显式记录新的 ownership truth。
- `.planning/baseline/PUBLIC_SURFACES.md`、`.planning/baseline/DEPENDENCY_MATRIX.md` 与 `.planning/baseline/VERIFICATION_MATRIX.md` 已回写 Phase 52 current truth：`protocol_facade_rest_methods.py` 是 support-only seam，`RequestPolicy` 是 `429` / busy / pacing truth，`RestRequestGateway` / `RestTransportExecutor` 各自只保留单一职责。
- `.planning/reviews/FILE_MATRIX.md` 已补齐 Wave 1 新文件 `custom_components/lipro/core/protocol/protocol_facade_rest_methods.py`，并把 touched protocol/API/tests/meta files 的 Phase 52 owner wording 收口到 single-root / localized-collaborator story。
- `.planning/reviews/RESIDUAL_LEDGER.md` 与 `.planning/reviews/KILL_LIST.md` 已显式登记 `Generic backoff helper leak`：`compute_exponential_retry_wait_time()` 的跨 plane 复用不再 silent defer，但当前也不被误写成 delete campaign。

## Validation

- `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_transport_and_schedule.py tests/core/api/test_api_request_policy.py tests/core/api/test_api_transport_executor.py tests/core/api/test_api_command_service.py tests/core/api/test_api_command_surface.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py -q`
- `uv run python scripts/check_file_matrix.py --check`

## Notes

- Phase 52 已完成 three-wave current-truth freeze；本轮没有引入第二 protocol root、第二 request owner、或新的 package export story。
- `Generic backoff helper leak` 目前是唯一新增 deferred residual；后续若继续清理，只能迁往更诚实的 shared backoff home，不能把 `request_policy.py` 重新包装成跨平面 utility root。
