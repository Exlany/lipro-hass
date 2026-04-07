---
phase: 74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout
plan: "02"
subsystem: tests
tags: [topicization, thin-shell, share-client, command-runtime, no-dup-collection]
requires:
  - phase: 74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout
    provides: retired compat shell and cleanup baseline
provides:
  - topicized `ShareWorkerClient` suites behind a thin shell
  - topicized `CommandRuntime` suites behind a thin shell
  - duplicate-collection protection for full and mixed pytest selection
affects: [phase-74-03, testing-map, focused-runtime-tests]
tech-stack:
  added: []
  patterns: [thin runnable shell, topicized concern-local suites, duplicate-collection guard]
key-files:
  created:
    - .planning/phases/74-legacy-auth-residual-retirement-test-topicization-and-milestone-closeout/74-02-SUMMARY.md
    - tests/core/test_share_client_support.py
    - tests/core/test_share_client_primitives.py
    - tests/core/test_share_client_refresh.py
    - tests/core/test_share_client_submit.py
    - tests/core/test_share_client_boundary.py
    - tests/core/coordinator/runtime/test_command_runtime_support.py
    - tests/core/coordinator/runtime/test_command_runtime_builder_retry.py
    - tests/core/coordinator/runtime/test_command_runtime_sender.py
    - tests/core/coordinator/runtime/test_command_runtime_confirmation.py
    - tests/core/coordinator/runtime/test_command_runtime_orchestration.py
  modified:
    - tests/conftest.py
    - tests/core/test_share_client.py
    - tests/core/coordinator/runtime/test_command_runtime.py
    - scripts/check_file_matrix_registry.py
    - .planning/reviews/FILE_MATRIX.md
key-decisions:
  - "Keep thin shells directly runnable so contributors retain a single outward entry point per concern."
  - "Fix duplicate collection in `tests/conftest.py` instead of accepting noisy mixed-explicit pytest behavior."
requirements-completed: [TST-22, QLT-30]
completed: 2026-03-25
---

# Phase 74 Plan 02 Summary

**`ShareWorkerClient` 与 `CommandRuntime` 大型套件已 topicize 为 thin shell + concern-local suites，并且不再重复收集。**

## Accomplishments
- 把两组 remaining large suites 收窄为 thin shell roots，同时新增按主题切分的 support/primitives/refresh/submit/boundary 与 builder/retry/sender/confirmation/orchestration suites。
- 在 `tests/conftest.py` 加入 duplicate-collection 防护，让 full collection 与 mixed explicit selection 都保持干净。
- testing/file-matrix truth 已同步刷新，topicized topology 获得正式 discoverability。

## Proof
- `uv run pytest -q tests/core/test_share_client.py tests/core/coordinator/runtime/test_command_runtime.py tests/meta/test_version_sync.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_governance_release_contract.py tests/meta/test_phase74_cleanup_closeout_guards.py tests/meta/governance_followup_route_current_milestones.py` → `109 passed`.
