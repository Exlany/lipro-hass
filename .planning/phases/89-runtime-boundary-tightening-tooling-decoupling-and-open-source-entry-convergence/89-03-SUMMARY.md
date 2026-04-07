---
phase: 89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence
plan: "03"
subsystem: tooling
tags: [tooling, governance, scripts, tests, decoupling]
requires: []
provides:
  - script-owned helper home for architecture/file-matrix governance tooling
  - thin tests helper shims
  - focused tooling-decoupling guards
affects: [scripts/check_architecture_policy.py, scripts/check_file_matrix.py, scripts/lib, tests/helpers, tests/meta]
tech-stack:
  added: []
  patterns:
    - script-owned helper kernels with test-side thin re-exports
key-files:
  created:
    - scripts/lib/__init__.py
    - scripts/lib/architecture_policy.py
    - scripts/lib/ast_guard_utils.py
    - tests/meta/test_phase89_tooling_decoupling_guards.py
  modified:
    - scripts/check_architecture_policy.py
    - scripts/check_file_matrix.py
    - tests/helpers/architecture_policy.py
    - tests/helpers/ast_guard_utils.py
    - tests/meta/public_surface_architecture_policy.py
    - tests/meta/test_governance_release_contract.py
key-decisions:
  - "Keep `scripts/check_architecture_policy.py` and `scripts/check_file_matrix.py` runnable both as package modules and as direct scripts, but only against script-owned helpers or sibling modules."
  - "Retain `tests.helpers.*` as compatibility consumers, not as the implementation authority."
patterns-established:
  - "Governance checkers may depend on `scripts.lib.*`; tests may re-export that same implementation, but must not own it."
requirements-completed:
  - GOV-64
  - HOT-39
  - TST-28
  - QLT-36
duration: session-carried
completed: 2026-03-27
---

# Summary 89-03

**Architecture/file-matrix governance tooling now relies on script-owned helpers or sibling modules, while tests consume the same implementation through thin shims instead of acting as the CLI source of truth.**

## Outcome

- `scripts/check_architecture_policy.py` and `scripts/check_file_matrix.py` no longer rely on `tests.helpers.*` or `sys.path.insert(...)` hacks.
- `scripts/lib/architecture_policy.py` and `scripts/lib/ast_guard_utils.py` now hold the real policy/AST helper implementation.
- `tests/helpers/architecture_policy.py` and `tests/helpers/ast_guard_utils.py` were demoted to thin re-export shims.
- Governance/public-surface tests were updated to assert the new ownership model across architecture/file-matrix checker roots.
- `tests/meta/test_phase89_tooling_decoupling_guards.py` now blocks script → tests helper backflow, `sys.path` reinjection, and file-matrix checker regressions.

## Verification

- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/public_surface_architecture_policy.py tests/meta/test_governance_release_contract.py tests/meta/test_dependency_guards.py tests/meta/toolchain_truth_testing_governance.py tests/meta/test_phase89_tooling_decoupling_guards.py`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- The helper home landed under `scripts/lib/*` instead of flat `scripts/*`; this is intentional and keeps script-owned kernels explicitly namespaced without reintroducing tests-owned ownership.

## Next Readiness

- `89-04` can now document script-owned tooling truth and reference focused guards instead of ad-hoc helper locality.
