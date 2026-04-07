# Phase 110: Runtime snapshot surface reduction and milestone closeout - Research

**Researched:** 2026-03-30
**Domain:** runtime snapshot seam decomposition + v1.30 closeout convergence
**Confidence:** HIGH

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RUN-11 | `snapshot.py` must split sourcing / formatting / arbitration seams to reduce hotspot density. | `SnapshotBuilder` already exposes fetch/assemble/enrich inflection points; mechanical helpers can be moved to inward support without API drift. |
| GOV-70 | planning/baseline/review/docs/tests truth must converge for v1.30 closeout. | Existing phase guard pattern (107-109) can be extended to 110, with 109 demoted to predecessor visibility. |
| TST-37 | focused regressions must freeze new seams and prevent behavior drift. | `tests/core/test_device_refresh_snapshot.py` and `tests/core/coordinator/runtime/test_device_runtime.py` already cover core behavior; add focused support-level tests. |
| QLT-45 | touched scope must pass quality gates and GSD fast-path honesty. | Existing quality chain (`check_file_matrix`, `ruff`, `mypy`, `pytest`, `gsd-tools`) is sufficient for closeout proof. |
</phase_requirements>

## Summary

`custom_components/lipro/core/coordinator/runtime/device/snapshot.py` currently centralizes:

1. page-total coercion and pagination boundary logic;
2. row canonicalization and device-ref derivation;
3. snapshot assembly bookkeeping and identity-alias mapping;
4. orchestration over fetch → parse → enrich → index replace.

The orchestration root is valid, but seam mechanics remain co-located in one file. Phase 110 should perform inward decomposition:

- keep `SnapshotBuilder` as the outward runtime snapshot orchestration home;
- move page/row/assembly mechanics into localized support helper(s);
- keep refresh rejection semantics and runtime index update behavior identical;
- add focused tests for new support seam and preserve runtime snapshot regressions.

On governance side, Phase 110 should become active-route owner, and the route should move to:
`v1.30 active route / Phase 110 complete / latest archived baseline = v1.29`,
with default next command shifting to milestone closeout.

## Recommended Plan

### Plan 110-01（代码 inward split）
- Extract snapshot sourcing/formatting mechanics into `snapshot_support.py`.
- Wire `snapshot.py` to consume support helpers while keeping `SnapshotBuilder` outward API unchanged.
- Ensure no second runtime root and no new public export path.

### Plan 110-02（focused regressions）
- Add focused tests for snapshot support helpers.
- Run snapshot/runtime focused suites to verify no behavioral regressions.

### Plan 110-03（governance closeout projection）
- Add `test_phase110_runtime_snapshot_closeout_guards.py` as active-route guard.
- Demote phase109 guard to predecessor visibility wording.
- Sync planning/baseline/reviews/docs/meta constants and GSD route contract to phase110 complete + closeout next step.

## Risks & Controls

| Risk | Description | Control |
|------|-------------|---------|
| Alias/index drift | helper extraction could alter identity alias mapping or index replacement semantics | focused support tests + existing runtime snapshot tests |
| Pagination semantics drift | total coercion or has-more logic changes | explicit helper tests for bool/float/string/invalid totals |
| Route contract mismatch | docs/constants/tests disagree after phase advance | phase110 meta guard + route-handoff smoke + check_file_matrix regeneration |
| Closeout command drift | `$gsd-next` does not point to milestone closeout | verify via `init progress` + route constants + smoke tests |

## Validation Architecture

### Focused Gates
- `uv run pytest -q tests/core/test_device_refresh_snapshot.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/coordinator/runtime/test_snapshot_support.py`
- `uv run pytest -q tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase109_anonymous_share_manager_inward_decomposition_guards.py tests/meta/test_phase110_runtime_snapshot_closeout_guards.py`
- `uv run python scripts/check_file_matrix.py --write`
- `uv run python scripts/check_file_matrix.py --check`

### Quality Gates
- `uv run ruff check .`
- `uv run mypy`
- `uv run pytest -q`

### GSD Route Gates
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 110`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 110`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 110`
