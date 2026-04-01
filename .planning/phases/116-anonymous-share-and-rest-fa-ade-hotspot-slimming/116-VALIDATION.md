---
phase: 116
slug: anonymous-share-and-rest-fa-ade-hotspot-slimming
nyquist_compliant: true
wave_0_complete: true
updated: 2026-04-01
---

# Phase 116 Validation Contract

## Wave Order

1. `116-01` slim REST façade state and collaborator wrapper density
2. `116-02` clarify anonymous-share scope-state and aggregate submit semantics
3. `116-03` close Phase 116 with route-sync and governance truth freeze

## Completion Expectations

- `116-01/02/03-SUMMARY.md`、`116-SUMMARY.md`、`116-VERIFICATION.md` 与 `116-VALIDATION.md` 全部存在，并讲述同一条 `HOT-49` 关闭链路。
- `LiproRestFacade` 继续保持 stable import / single formal composition-root truth；匿名分享 aggregate/scoped outcome contract 保持不变。
- 本 phase 的 validated closeout 只承认 `Phase 117 discuss-ready` handoff，不把 `Phase 118` 的后续热点收口倒灌成 `116` 当时已完成的历史事实。

## GSD Route Evidence

- `116-SUMMARY.md` 已记录 REST façade 与 anonymous-share manager 的 bounded inward split 完成，并把 route truth 推到 `Phase 117 discuss-ready`。
- `116-VERIFICATION.md` 已冻结 focused API / anonymous-share / governance commands 与 contract assertions。
- `Phase 118` 回补本 validation contract 时，仅提升 `116` 的 evidence completeness，不扩张 `HOT-49` 的原始 scope。

## Validation Commands

- `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_api_status_service_wrappers.py`
- `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/core/anonymous_share/test_manager_scope_views.py tests/core/anonymous_share/test_observability.py`
- `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase112_formal_home_governance_guards.py`
- `uv run ruff check custom_components/lipro/core/api/rest_facade.py custom_components/lipro/core/anonymous_share/manager.py custom_components/lipro/core/anonymous_share/manager_support.py tests/core/api/test_api.py tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/meta/governance_current_truth.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase112_formal_home_governance_guards.py`

## Archive Truth Guardrail

- `Phase 116` 只验证 REST façade / anonymous-share manager 的当轮 hotspot slimming 与 discuss-ready handoff。
- validation backfill 不得把 `Phase 118` 的 route truth sync、rest-decoder split、firmware update slimming 或 Nyquist closure 伪装成 `116` 已完成范围。
