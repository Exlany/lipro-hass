---
phase: 127
slug: runtime-access-de-reflection-typed-runtime-entry-contracts-and-hotspot-continuation
nyquist_compliant: true
wave_1_complete: true
updated: 2026-04-01
---

# Phase 127 Validation Contract

## Wave Order

1. `127-01` converge runtime-access on the typed system-health telemetry contract
2. `127-02` replace reflective runtime-entry narrowing with explicit support ports
3. `127-03` freeze focused runtime-access proof and sync governance projections

## Completion Expectations

- `127-01/02/03-SUMMARY.md`、`127-SUMMARY.md`、`127-VERIFICATION.md` 与 `127-VALIDATION.md` 共同证明 `ARC-39 / HOT-58 / TST-49` 已在同一 active route 下闭环。
- `runtime_access.py` 继续保持 protected thin runtime read-model home；`runtime_access_support_views.py` 只保留 explicit member/helper narrowing，不再回流 reflective seam。
- `Phase 127` 完成后，current route 必须诚实前推到 `active / phase 127 complete; phase 128 planning-ready (2026-04-01)` 与 `$gsd-plan-phase 128`。

## GSD Route Evidence

- `127-01-SUMMARY.md` 已记录 typed system-health telemetry seam 与 control failure-summary single-source truth。
- `127-02-SUMMARY.md` 已记录 runtime entry / coordinator narrowing 从 reflective probing 回切到显式 support-port story。
- `127-03-SUMMARY.md` 已记录 focused runtime/meta proof、治理投影同步与 Phase 128 handoff truth。

## Validation Commands

- `uv run pytest -q tests/core/test_runtime_access.py tests/core/test_control_plane.py tests/core/test_system_health.py tests/meta/test_phase111_runtime_boundary_guards.py tests/meta/test_runtime_contract_truth.py tests/meta/test_governance_phase_history_runtime.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_release_contract.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check .`
- `uv run pytest -q`
- `tmpdir=$(mktemp -d) && ln -s "$PWD" "$tmpdir/repo" && node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" --cwd="$tmpdir/repo" state json && printf "
---GSD_SPLIT---
" && node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" --cwd="$tmpdir/repo" init progress && printf "
---GSD_SPLIT---
" && node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" --cwd="$tmpdir/repo" phase-plan-index 127 && rm -rf "$tmpdir"`

## Archive Truth Guardrail

- `Phase 127` 可以关闭 runtime-access typed telemetry / de-reflection hotspot，但不得把 repo-external maintainer continuity 或 benchmark gate honesty 伪装成已在仓内完成；这些 concern 明确留给 `Phase 128`。
