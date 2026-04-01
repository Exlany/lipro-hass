---
phase: 118
slug: final-hotspot-decomposition-and-validation-closure
nyquist_compliant: true
wave_0_complete: true
updated: 2026-04-01
---

# Phase 118 Validation Contract

## Wave Order

1. `118-01` resync route truth to the live phase118 execution path
2. `118-02` decompose the remaining formal-home hotspots without reopening governance sync
3. `118-03` close nyquist validation debt and refresh the v1.32 evidence chain

## Completion Expectations

- `118-01/02/03-SUMMARY.md`、`118-SUMMARY.md`、`118-VERIFICATION.md` 与 `118-VALIDATION.md` 共同证明 `HOT-50 / HOT-51 / TST-40 / GOV-75` 已在同一 active route 下闭环。
- `status_fallback` / `rest_decoder` / `firmware_update` 的 slimming 已保持 outward homes 稳定；`anonymous_share/manager.py` 虽未继续物理拆分，但已有显式 bounded watchlist 裁决与 focused guard 佐证。
- `115/116/117-VALIDATION.md` 已全部补齐并被提升进 v1.32 evidence chain；live route 现已从 `execution-ready` 回到 `active / phase 118 complete; closeout-ready (2026-04-01)` 与 `$gsd-complete-milestone v1.32`。

## GSD Route Evidence

- `118-01-SUMMARY.md` 已记录 selector family / route truth 从 premature closeout 回切到 `Phase 118 execution-ready`。
- `118-02-SUMMARY.md` 已记录 status-fallback 与 rest-decoder family 的 inward split，并保留 `firmware_update.py` / `anonymous_share/manager.py` 的 bounded follow-up posture。
- `118-03` 已把 validation backfill、promoted assets、v1.32 audit 与 live selector truth 一并收口，milestone closeout-ready 已恢复。

## Validation Commands

- `uv run pytest -q tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase112_formal_home_governance_guards.py tests/meta/test_version_sync.py`
- `uv run pytest -q tests/core/api/test_api_status_service_fallback.py tests/core/api/test_protocol_contract_boundary_decoders.py tests/platforms/test_firmware_update_entity_edges.py tests/platforms/test_update_background_tasks.py tests/platforms/test_update_task_callback.py tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/meta/test_phase101_anonymous_share_rest_boundary_guards.py tests/meta/test_phase107_rest_status_hotspot_guards.py tests/meta/test_phase109_anonymous_share_manager_inward_decomposition_guards.py tests/meta/test_phase113_hotspot_assurance_guards.py`
- `uv run pytest -q tests/meta/governance_milestone_archives_assets.py tests/meta/test_governance_promoted_phase_assets.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check .`
- `uv run pytest -q`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`

## Archive Truth Guardrail

- `Phase 118` 可以关闭 repo-internal hotspot / validation / continuity debt，但不得把 repo-external maintainer continuity blockers 伪装为已在仓内解决。
- `anonymous_share/manager.py` 经终局审计被保留为 bounded façade/watcher，而非继续拆分；validation 与 audit 已诚实记录这一裁决，没有宣称“所有 formal-home giant files 已被物理拆净”。
