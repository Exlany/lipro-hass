# 29-03 Summary

## Outcome

- capability regressions 继续 anchored 在 dedicated REST suites：`tests/core/api/test_api_diagnostics_service.py`、`tests/core/api/test_api_schedule_service.py`、`tests/core/api/test_api_schedule_endpoints.py`；`test_api.py` 不再承担全部 capability 叙事。
- `tests/meta/test_public_surface_guards.py`、`tests/meta/test_modularization_surfaces.py` 与 `scripts/check_file_matrix.py` 现在共同锁定 slimmer REST modularization story，避免 `Phase 29` 的结构真相再漂移。
- `FILE_MATRIX` 已补入 `tests/core/api/test_api_request_policy.py` 与 `tests/meta/test_phase31_runtime_budget_guards.py`，并把 `services/execution.py` row 校正回 closed-seam canonical truth。

## Key Files

- `tests/core/api/test_api_diagnostics_service.py`
- `tests/core/api/test_api_schedule_service.py`
- `tests/core/api/test_api_schedule_endpoints.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_modularization_surfaces.py`
- `tests/meta/test_governance_closeout_guards.py`
- `.planning/reviews/FILE_MATRIX.md`
- `scripts/check_file_matrix.py`

## Validation

- `uv run pytest -q tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_api.py tests/meta/test_public_surface_guards.py tests/meta/test_modularization_surfaces.py tests/meta/test_governance_closeout_guards.py`
- `uv run python scripts/check_file_matrix.py --check`

## Notes

- `Phase 29` 到此只完成 REST modularization / topicization / truth sync；typed-contract 与 distributed exception budget 继续由 `Phase 30/31` 负责。
