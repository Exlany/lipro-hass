# 14 Validation

status: passed

- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py`
- `uv run pytest -q`
