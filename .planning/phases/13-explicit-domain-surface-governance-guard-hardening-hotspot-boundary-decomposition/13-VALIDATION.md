# 13 Validation

status: passed

- `uv run pytest -q tests/core/device/test_device.py tests/core/device/test_state.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_device_refresh.py tests/core/api/test_api_status_service.py tests/core/api/test_api_status_service_regressions.py`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py`
- `uv run ruff check .`
- `uv run mypy`
- `uv run pytest -q`
