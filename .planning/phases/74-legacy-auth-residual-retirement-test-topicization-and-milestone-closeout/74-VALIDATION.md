# Phase 74 Validation Contract

## Wave Order

1. `74-01` auth residual / compat shell truthful retirement
2. `74-02` public docs fast-path cleanup / retired script wording alignment
3. `74-03` `ShareWorkerClient` + `CommandRuntime` topicized suite split and duplicate-collection guard
4. `74-04` governance closeout truth projection and reproducible validation evidence

## Per-Plan Focused Gates

- `74-01`
  - `uv run pytest -q tests/services/test_services_registry.py tests/core/test_init_runtime_unload_reload.py tests/meta/test_dependency_guards.py tests/meta/test_phase74_cleanup_closeout_guards.py`
  - Result: `41 passed`
- `74-02`
  - `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_phase74_cleanup_closeout_guards.py tests/meta/governance_followup_route_current_milestones.py`
  - Result: route/docs/public-fast-path focused gates passed
- `74-03`
  - `uv run pytest -q tests/core/test_share_client.py tests/core/coordinator/runtime/test_command_runtime.py tests/meta/test_version_sync.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_governance_release_contract.py tests/meta/test_phase74_cleanup_closeout_guards.py tests/meta/governance_followup_route_current_milestones.py`
  - Result: `109 passed`
- `74-04`
  - `uv run pytest -q tests/meta/governance_followup_route_closeouts.py::test_phase_40_closeout_truth_is_consistent tests/meta/test_governance_guards.py::test_phase_60_tooling_closeout_is_frozen_in_current_story_truth tests/meta/test_governance_milestone_archives.py::test_governance_truth_registers_v1_19_latest_archive_pointer tests/meta/test_phase31_runtime_budget_guards.py::test_repo_wide_tests_any_non_meta_bucket_is_explicit tests/meta/test_phase71_hotspot_route_guards.py::test_phase72_context_exists_for_planning_route tests/meta/test_phase72_runtime_bootstrap_route_guards.py::test_phase72_current_route_truth_replaces_stale_route_story tests/meta/test_public_surface_guards.py::test_phase_55_topicized_test_matrix_tracks_thin_shells_and_named_suites tests/meta/test_toolchain_truth.py::test_testing_map_counts_and_script_boundary_notes_match_repo_facts -q`
  - Result: `8 passed`

## Final Gate

- `uv run ruff check .` → `All checks passed!`
- `uv run mypy --follow-imports=silent .` → `Success: no issues found in 636 source files`
- `uv run python scripts/check_architecture_policy.py --check` → passed
- `uv run python scripts/check_file_matrix.py --check` → passed
- `uv run pytest -q` → `2592 passed in 62.98s`

## Sign-off Checklist

- [x] `custom_components/lipro/services/registrations.py` compat shell 已物理退场，相关导入、policy、guards 与 review ledger 同步收口。
- [x] `docs/README.md` 只保留 public docs map 身份，不再泄露 current-route / latest-archive pointer / maintainer next-command 内情。
- [x] `tests/core/test_share_client.py` 与 `tests/core/coordinator/runtime/test_command_runtime.py` 已 topicize 为 thin shell；full collection 与 mixed explicit collection 都不再重复收集。
- [x] active governance truth、baseline/review docs 与 route guards 已共同承认 `v1.20 active route / Phase 74 complete / latest archived baseline = v1.19`。
- [x] Phase 74 closeout 已留下 focused + repo-wide validation ledger；下一步只剩 `$gsd-complete-milestone v1.20`。
