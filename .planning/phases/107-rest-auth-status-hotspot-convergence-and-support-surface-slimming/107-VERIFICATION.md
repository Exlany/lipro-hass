# Phase 107 Verification

## Requirement Coverage

| Requirement | Verdict | Evidence |
| --- | --- | --- |
| `HOT-46` | passed | `custom_components/lipro/core/api/rest_facade.py`, `custom_components/lipro/core/api/status_fallback_support.py`, `custom_components/lipro/core/api/request_policy_support.py`, `107-01-SUMMARY.md`, `107-02-SUMMARY.md` |
| `ARC-27` | passed | `custom_components/lipro/core/api/rest_facade.py`, `custom_components/lipro/core/api/status_fallback_support.py`, `custom_components/lipro/core/api/request_policy_support.py`, `tests/meta/test_phase107_rest_status_hotspot_guards.py` |
| `TST-37` | passed | `tests/core/api/test_api.py`, `tests/core/api/test_api_status_service_fallback.py`, `tests/core/api/test_api_request_policy.py`, `tests/meta/test_phase107_rest_status_hotspot_guards.py`, `107-03-SUMMARY.md` |
| `QLT-45` | passed | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/codebase/TESTING.md`, `.planning/reviews/{RESIDUAL_LEDGER,KILL_LIST,FILE_MATRIX}.md`, `docs/developer_architecture.md`, `107-03-SUMMARY.md` |

## Focused Gates

- `uv run pytest -q tests/core/api/test_api_status_service_fallback.py tests/core/api/test_api_request_policy.py tests/core/api/test_api.py`
- `uv run pytest -q tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase105_governance_freeze_guards.py tests/meta/test_phase107_rest_status_hotspot_guards.py`
- `uv run python scripts/check_file_matrix.py --write`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check custom_components/lipro/core/api/rest_facade.py custom_components/lipro/core/api/status_fallback_support.py custom_components/lipro/core/api/request_policy_support.py tests/core/api/test_api.py tests/core/api/test_api_status_service_fallback.py tests/core/api/test_api_request_policy.py tests/meta/governance_current_truth.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase105_governance_freeze_guards.py tests/meta/test_phase107_rest_status_hotspot_guards.py scripts/check_file_matrix_registry_classifiers.py`
- `uv run mypy custom_components/lipro/core/api/rest_facade.py custom_components/lipro/core/api/status_fallback_support.py custom_components/lipro/core/api/request_policy_support.py`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 107`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 107`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 107`

## Repo-wide Gates

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_markdown_links.py`
