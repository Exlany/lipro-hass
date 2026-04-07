# Phase 105 Verification

## Requirement Coverage

| Requirement | Verdict | Evidence |
| --- | --- | --- |
| `GOV-69` | passed | `tests/meta/governance_followup_route_specs.py`, `tests/meta/governance_followup_route_{current_milestones,closeouts,continuation}.py`, `scripts/check_file_matrix_registry_{shared,classifiers,overrides}.py`, `105-01-SUMMARY.md`, `105-02-SUMMARY.md` |
| `QLT-44` | passed | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/{PROMOTED_PHASE_ASSETS,RESIDUAL_LEDGER,KILL_LIST,FILE_MATRIX}.md`, `docs/developer_architecture.md`, `tests/meta/test_phase105_governance_freeze_guards.py`, `105-03-SUMMARY.md` |

## Focused Gates

- `uv run pytest -q tests/meta/governance_followup_route_current_milestones.py tests/meta/governance_followup_route_closeouts.py tests/meta/governance_followup_route_continuation.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_phase103_root_thinning_guards.py tests/meta/test_phase104_service_router_runtime_split_guards.py tests/meta/test_phase105_governance_freeze_guards.py`
- `uv run python scripts/check_file_matrix.py --write`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check tests/meta/governance_current_truth.py tests/meta/governance_followup_route_specs.py tests/meta/governance_followup_route_current_milestones.py tests/meta/governance_followup_route_closeouts.py tests/meta/governance_followup_route_continuation.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_phase104_service_router_runtime_split_guards.py tests/meta/test_phase105_governance_freeze_guards.py scripts/check_file_matrix_registry_shared.py scripts/check_file_matrix_registry_classifiers.py scripts/check_file_matrix_registry_overrides.py`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 105`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 105`

## Repo-wide Gates

- `uv run pytest -q tests/meta`
- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_markdown_links.py`
- `uv run pytest -q`
