---
phase: 126
slug: service-router-developer-callback-home-convergence-and-diagnostics-helper-residual-slimming
nyquist_compliant: true
wave_0_complete: true
updated: 2026-04-01
---

# Phase 126 Validation Contract

## Wave Order

1. `126-01` collapse diagnostics helper duplicate mechanics into the canonical helper-support home and freeze route bootstrap proof

## Completion Expectations

- `126-01-SUMMARY.md`、`126-SUMMARY.md`、`126-VERIFICATION.md` 与 `126-VALIDATION.md` 共同证明 `ARC-38 / HOT-57 / GOV-85 / TST-48 / QLT-50 / DOC-15` 已在同一 active route 下闭环。
- `services/diagnostics/handlers.py` 继续直连 `helper_support.py` 的 canonical mechanics truth；`helpers.py` 只保留 outward-stable helper home 身份，不再作为第二实现真源。
- `developer_router_support.py` 继续复用统一 runtime iterator builder；route/bootstrap docs 与 registry 保持历史执行时的单一 truth：`active / phase 126 complete; phase 127 planning-ready (2026-04-01)`。
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 需显式提升 `126-VALIDATION.md`，使 `Phase 126` 的 archived evidence chain 不再保留 Nyquist 缺口。

## GSD Route Evidence

- `126-01-SUMMARY.md` 已记录 diagnostics helper shell thinning、canonical helper-support mechanics convergence 与 route bootstrap sync。
- `126-SUMMARY.md` 已记录 `Phase 126` closeout、`Phase 127` handoff 与 v1.36 carry-forward story。
- `126-VERIFICATION.md` 已记录 focused diagnostics proof、repo-wide proof，以及 isolated `gsd-tools state json` / `init progress` snapshots。

## Validation Commands

- `uv run pytest -q tests/services/test_services_diagnostics_capabilities.py tests/services/test_services_diagnostics_payloads.py`
- `uv run ruff check .`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase101_anonymous_share_rest_boundary_guards.py tests/meta/test_phase102_governance_portability_guards.py tests/meta/test_phase103_root_thinning_guards.py tests/meta/test_phase104_service_router_runtime_split_guards.py tests/meta/test_phase105_governance_freeze_guards.py tests/meta/test_phase107_rest_status_hotspot_guards.py tests/meta/test_phase108_mqtt_transport_de_friendization_guards.py tests/meta/test_phase109_anonymous_share_manager_inward_decomposition_guards.py tests/meta/test_phase110_runtime_snapshot_closeout_guards.py tests/meta/test_phase85_terminal_audit_route_guards.py`
- `uv run pytest -q`
- `tmpdir=$(mktemp -d) && ln -s "$PWD" "$tmpdir/repo" && node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" --cwd="$tmpdir/repo" state json && printf "
---GSD_SPLIT---
" && node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" --cwd="$tmpdir/repo" init progress && rm -rf "$tmpdir"`

## Wave 0 Requirements

- Existing infrastructure already covered the full `Phase 126` requirement basket.
- No new framework/bootstrap layer or extra phase split was required for this retroactive Nyquist backfill.

## Manual-Only Verifications

- All phase behaviors already have automated verification; this file only formalizes the Nyquist evidence contract that the phase had already satisfied in practice.

## Archive Truth Guardrail

- `Phase 126` 可以补齐 repo-internal Nyquist validation 资产，但不得把 repo-external continuity / delegate / private fallback reality 伪装成仓内已解决能力。
- live selector docs 现已回到 archived `v1.36`；本文件只补齐 historical execution proof，不改写 `Phase 126` 当时的 active-route 历史语义。
