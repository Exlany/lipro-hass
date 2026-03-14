# 09-04 Summary — API Mega-Test Convergence

## Outcome

- `tests/core/api/test_api.py` 已收窄：response-safety、status endpoint predicates、request-policy helper、schedule codec / candidate helper 等 formal helper 断言迁回各自分层 test home。
- 新增 focused tests：`tests/core/api/test_response_safety.py`、`tests/core/api/test_api_status_endpoints.py`、`tests/core/api/test_api_status_service_regressions.py`。
- `tests/core/api/test_helper_modules.py`、`tests/core/api/test_api_status_service.py`、`tests/core/api/test_schedule_codec.py`、`tests/core/api/test_api_schedule_service.py`、`tests/core/api/test_api_schedule_candidate_queries.py`、`tests/core/api/test_api_schedule_candidate_mutations.py`、`tests/core/api/test_api_schedule_endpoints.py` 已补足对应 formal truth coverage。

## Verification

- `uv run ruff check tests/core/api/test_api.py tests/core/api/test_response_safety.py tests/core/api/test_api_status_endpoints.py tests/core/api/test_api_status_service.py tests/core/api/test_api_status_service_regressions.py tests/core/api/test_helper_modules.py tests/core/api/test_schedule_codec.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_candidate_queries.py tests/core/api/test_api_schedule_candidate_mutations.py tests/core/api/test_api_schedule_endpoints.py`
- `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_response_safety.py tests/core/api/test_api_status_endpoints.py tests/core/api/test_api_status_service.py tests/core/api/test_api_status_service_regressions.py tests/core/api/test_helper_modules.py tests/core/api/test_schedule_codec.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_candidate_queries.py tests/core/api/test_api_schedule_candidate_mutations.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_api_command_service.py tests/core/api/test_request_codec.py`
- Result: `282 passed`
