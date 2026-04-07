# Phase 108 Verification

## Requirement Coverage

| Requirement | Verdict | Evidence |
| --- | --- | --- |
| `RUN-10` | passed | `custom_components/lipro/core/mqtt/{transport.py,transport_runtime.py}`, `108-01-SUMMARY.md` |
| `ARC-27` | passed | `custom_components/lipro/core/mqtt/{transport.py,transport_runtime.py}`, `tests/meta/test_phase108_mqtt_transport_de_friendization_guards.py`, `108-03-SUMMARY.md` |
| `TST-37` | passed | `tests/core/mqtt/test_transport_refactored.py`, `tests/core/mqtt/test_transport_runtime_lifecycle.py`, `tests/core/mqtt/test_transport_runtime_connection_loop.py`, `tests/core/mqtt/test_transport_runtime_ingress.py`, `tests/core/mqtt/test_transport_runtime_subscriptions.py`, `108-02-SUMMARY.md` |
| `QLT-45` | passed | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/codebase/TESTING.md`, `.planning/reviews/{RESIDUAL_LEDGER,KILL_LIST,FILE_MATRIX}.md`, `docs/developer_architecture.md`, `108-03-SUMMARY.md` |

## Focused Gates

- `uv run pytest -q tests/core/mqtt/test_transport_refactored.py tests/core/mqtt/test_transport_runtime_lifecycle.py tests/core/mqtt/test_transport_runtime_connection_loop.py tests/core/mqtt/test_transport_runtime_ingress.py tests/core/mqtt/test_transport_runtime_subscriptions.py tests/core/mqtt/test_connection_manager.py`
- `uv run pytest -q tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase105_governance_freeze_guards.py tests/meta/test_phase107_rest_status_hotspot_guards.py tests/meta/test_phase108_mqtt_transport_de_friendization_guards.py`
- `uv run python scripts/check_file_matrix.py --write`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check custom_components/lipro/core/mqtt/transport.py custom_components/lipro/core/mqtt/transport_runtime.py tests/core/mqtt/test_transport_refactored.py tests/core/mqtt/test_transport_runtime_lifecycle.py tests/core/mqtt/test_transport_runtime_connection_loop.py tests/core/mqtt/test_transport_runtime_ingress.py tests/core/mqtt/test_transport_runtime_subscriptions.py tests/core/mqtt/test_connection_manager.py tests/meta/governance_current_truth.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase105_governance_freeze_guards.py tests/meta/test_phase107_rest_status_hotspot_guards.py tests/meta/test_phase108_mqtt_transport_de_friendization_guards.py scripts/check_file_matrix_registry_classifiers.py`
- `uv run mypy custom_components/lipro/core/mqtt/transport.py custom_components/lipro/core/mqtt/transport_runtime.py`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 108`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 108`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 108`

## Repo-wide Gates

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_markdown_links.py`
