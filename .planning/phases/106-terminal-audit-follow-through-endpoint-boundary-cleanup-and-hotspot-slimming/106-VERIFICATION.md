# Phase 106 Verification

## Focused Verification

- `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_api_status_service_wrappers.py tests/flows/test_options_flow.py tests/flows/test_options_flow_utils.py tests/meta/toolchain_truth_docs_fast_path.py`

## Repo-wide Verification

- `uv run ruff check .`
- `uv run mypy`
- `uv run pytest -q`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_markdown_links.py`
- `uv run python scripts/check_file_matrix.py --check`

## Expected Outcome

- focused behavior unchanged
- repo-wide quality gates all green
- `gsd-next` semantics remain archived-only: next legal route = `$gsd-new-milestone`
