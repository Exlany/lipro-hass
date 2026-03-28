# Phase 99 Research

**Phase:** `99-runtime-hotspot-support-extraction-and-terminal-audit-freeze`
**Date:** `2026-03-28`
**Requirements:** `HOT-41`, `GOV-65`, `TST-31`, `QLT-39`

## Objective

把 terminal audit 仍指向的两处高收益热点继续 inward decomposition：`status_fallback.py` 保留 outward anchors、把 binary-split 递归 mechanics inward split；`command_runtime.py` 保留 `CommandRuntime` orchestration home、把请求/失败 support block 外提；随后把 planning/governance/docs/tests/current-route truth 同步推进到 `Phase 99 complete`。

## Inputs Reviewed

- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/codebase/{TESTING.md,CONCERNS.md}`
- `.planning/reviews/{FILE_MATRIX.md,RESIDUAL_LEDGER.md,KILL_LIST.md}`
- `docs/developer_architecture.md`
- `custom_components/lipro/core/api/{status_fallback.py,status_service.py}`
- `custom_components/lipro/core/coordinator/runtime/command_runtime.py`
- `tests/core/api/test_api_status_service_fallback.py`
- `tests/core/coordinator/runtime/test_command_runtime*.py`
- `tests/meta/governance_current_truth.py`
- `tests/meta/test_phase98_route_reactivation_guards.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_phase90_hotspot_map_guards.py`
- `tests/meta/test_phase97_governance_assurance_freeze_guards.py`

## Findings

1. `status_fallback.py` 的 outward anchors（typed aliases、`_build_query_payload`、`_resolve_device_status_batch_size`、`query_with_fallback`）已被 tests/meta 直接冻结，不能简单搬空；但其递归 mechanics 仍适合 inward split 到 support collaborator。
2. `CommandRuntime` 的核心风险不在 orchestration root 本身，而在顶部请求/失败 helper block 仍与 class 同居；这些 helper 是纯 support seam，可安全外提。
3. 现有 planning/governance truth 仍把 `Phase 98` 视为 current route；若不整体前推，`Phase 99` 即使落地代码也会再次形成“实现已变、route 未变”的双重现实。
4. `Phase 98` focused guard 必须降级为 predecessor guard；`Phase 99` 需要新的 current-route focused guard 来冻结 support extraction / governance freeze / testing-map projection。

## Execution Shape

- `99-01`: slim `status_fallback.py` into outward public home + local support collaborator while preserving monkeypatch/test anchors.
- `99-02`: slim `command_runtime.py` into orchestration home + request/failure support collaborator while preserving runtime import and service/test contracts.
- `99-03`: advance route truth, maps, docs, meta guards, phase assets, and full verification to `Phase 99 complete`.

## Risks

- 若把 `status_fallback.py` 的 constants 或 typed anchors 一并移走，`tests/core/api/test_api_status_service_fallback.py` 与 `tests/meta/test_phase94_typed_boundary_guards.py` 会直接失败。
- 若改变 `CommandRuntime` 的 constructor / public methods / failure-summary semantics，runtime services 与 topicized runtime tests 会同时失效。
- 若只更新 prose 不更新 shared route contract / `STATE.md` frontmatter / GSD assets，`$gsd-next` 与 human-readable truth 会再次分叉。
