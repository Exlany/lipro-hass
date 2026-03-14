# Phase 06 CI Gates

**Status:** Active
**Updated:** 2026-03-13

## Gate Layers

### 1. Lint gate
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy`

### 2. Governance gate
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py -q`

### 3. Functional / coverage gate
- `uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing`
- `uv run pytest tests/snapshots/ -v`
- `uv run python scripts/coverage_diff.py coverage.json --minimum 95`
- `uv run python scripts/refactor_tools.py --coverage-json coverage.json --minimum-coverage 95`

### 4. Validation gate
- HACS / Hassfest validation

## Pre-push Minimum

- `uv run mypy`
- diagnostics smoke gate
- governance / architecture gate
