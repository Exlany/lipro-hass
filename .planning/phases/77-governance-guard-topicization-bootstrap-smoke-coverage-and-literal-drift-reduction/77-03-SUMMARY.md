---
phase: 77-governance-guard-topicization-bootstrap-smoke-coverage-and-literal-drift-reduction
plan: "03"
subsystem: governance-boundaries
tags: [governance, helpers, boundaries, file-matrix, verification]
requirements-completed: [DOC-04, TST-23]
completed: 2026-03-26
---

# Phase 77 Plan 03 Summary

**`test_governance_closeout_guards.py` 已不再兼任共享 helper 仓库；doc-facing / promoted-assets / bootstrap smoke 的边界均已冻结并登记。**

## Accomplishments
- 新增 `tests/meta/governance_promoted_assets.py`，把 promoted-phase-asset manifest helper 从测试文件中剥离到诚实的 helper home。
- 所有 `tests/meta/**` 对 `test_governance_closeout_guards.py` 的共享 helper 反向依赖已清零；import 拓扑已变为 `suite -> helper` 单向收敛。
- `.planning/reviews/FILE_MATRIX.md`、`.planning/baseline/VERIFICATION_MATRIX.md` 与 `scripts/check_file_matrix_registry.py` 已同步登记 `governance_contract_helpers.py`、`governance_promoted_assets.py` 与 `test_governance_bootstrap_smoke.py` 的新 topology。
- `tests/meta/test_governance_closeout_guards.py` 已收缩为 closeout + promoted-asset manifest smoke anchor，不再承担 helper API 身份。

## Proof
- `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase75_governance_closeout_guards.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_phase71_hotspot_route_guards.py tests/meta/test_phase72_runtime_bootstrap_route_guards.py tests/meta/test_phase74_cleanup_closeout_guards.py tests/meta/test_governance_phase_history_runtime.py tests/meta/toolchain_truth_docs_fast_path.py` → `108 passed`
- `uv run python scripts/check_file_matrix.py --check` → exit `0`
