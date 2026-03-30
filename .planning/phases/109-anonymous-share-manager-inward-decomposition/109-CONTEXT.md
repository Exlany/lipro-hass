# Phase 109: Anonymous-share manager inward decomposition - Context

**Gathered:** 2026-03-30
**Status:** Ready for planning
**Source:** `v1.30` active route continuation from `.planning/MILESTONE-CONTEXT.md` + `Phase 108` closeout evidence

<domain>
## Phase Boundary

本 phase 只处理 `custom_components/lipro/core/anonymous_share/manager.py` 的热点继续内聚收口：

- 把 manager 中仍偏厚的 scope/aggregate orchestration、state-access 代理、report-projection 选择与 submit finalize 机械流程继续下沉到 focused local collaborators。
- 保持 `AnonymousShareManager` 为 anonymous-share aggregate/scoped 的唯一 outward home，不新增第二 root、不新增 public import 路径、不引入 compat shell。
- 保持 typed `OperationOutcome` 提交语义与 aggregate-child 失败优先裁决不回退。
- 用 focused regressions 冻结 scoped/aggregate 行为、服务层输出契约与 predecessor guards。

不在本 phase 重开 snapshot hotspot 或 milestone closeout；它们属于 `Phase 110`。
</domain>

<decisions>
## Locked Decisions

- `manager.py` 保持 outward coordination home；decomposition 只允许 inward split，禁止 outward ownership 迁移。
- `manager_submission.py` / `manager_support.py` 继续是 collaborator homes，不能被外部消费者直接当 public API。
- scoped/aggregate 提交流保持单轨 typed outcome；禁止 bool-only 主真相回流。
- aggregate primary-scope 选择、disabled scope 处理与 child-failure 折叠语义必须保持既有行为与测试预期。
- phase 完成后要同步 planning/baseline/reviews/docs/tests 的 current-route truth，确保 `Phase 109` 成为 active continuation 的新完成锚点。
</decisions>

<canonical_refs>
## Canonical References

- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/MILESTONE-CONTEXT.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `docs/developer_architecture.md`
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/anonymous_share/manager_submission.py`
- `custom_components/lipro/core/anonymous_share/manager_support.py`
- `custom_components/lipro/core/anonymous_share/report_builder.py`
- `custom_components/lipro/core/anonymous_share/share_client.py`
- `custom_components/lipro/services/share.py`
- `tests/core/anonymous_share/test_manager_recording.py`
- `tests/core/anonymous_share/test_manager_submission.py`
- `tests/core/anonymous_share/test_observability.py`
- `tests/services/test_services_share.py`
- `tests/meta/test_phase101_anonymous_share_rest_boundary_guards.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
</canonical_refs>
