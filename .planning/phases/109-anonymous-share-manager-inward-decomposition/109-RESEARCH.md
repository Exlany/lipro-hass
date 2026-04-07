# Phase 109: Anonymous-share manager inward decomposition - Research

**Researched:** 2026-03-30
**Domain:** anonymous-share manager scoped/aggregate orchestration
**Confidence:** HIGH

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HOT-47 | `manager.py` orchestration hotspot must continue inward decomposition while keeping manager as outward home. | Scope-view orchestration and report/finalize mechanics can be delegated to inward collaborators without changing manager outward API. |
| TST-37 | Preserve behavior using focused regressions and predecessor guards. | Existing scoped/aggregate/service tests cover behavior; add focused scope-view tests for new collaborator semantics. |
| QLT-45 | Keep quality gates and governance truth synchronized with current route. | Phase verification includes focused tests + meta + lint/type/full-suite gates and route-truth projection. |
</phase_requirements>

## Summary

`custom_components/lipro/core/anonymous_share/manager.py` 仍承载了三类“可机械下沉”的逻辑：

1. scoped/aggregate 视图遍历与 primary-scope 选择；
2. pending report 选择逻辑（aggregate/scoped 分支判断）；
3. successful submit 后的状态落盘机械流程（时间戳、reported keys、collector clear）。

`manager_scope.py` 和 `manager_support.py` 已具备承接能力，但当前 `manager.py` 尚未完全接线。Phase 109 的最小正确改造应是“只做 inward wiring，不改 outward contract”：

- `AnonymousShareManager` 继续是唯一 outward home；
- `manager_scope.py` 仅负责 scoped/aggregate 视图编排；
- `manager_support.py` 仅负责 pending/finalize 机械逻辑；
- `manager_submission.py` 的 typed outcome 语义与 aggregate collapse 逻辑保持不变。

## Recommended Plan

### Plan 109-01（核心代码接线）
- 将 `for_scope` / `iter_scope_states` / `primary_manager` / aggregate enabled/pending 路径切换到 `AnonymousShareScopeViews`。
- 将 `get_pending_report()` 切换到 `build_pending_report_payload(...)`。
- 将 `async_finalize_successful_submit()` 切换到 `finalize_successful_submit_state(...)`（保留 async thread offload）。
- 保持 `AnonymousShareManager` outward surface 不漂移，不新增 root/export。

### Plan 109-02（focused regressions）
- 运行匿名分享 focused tests（recording/submission/observability/service）。
- 新增 `manager_scope` focused tests，冻结 scope view collaborator 的缓存、primary 选择、aggregate 计数语义。

### Plan 109-03（governance projection）
- 新增 `tests/meta/test_phase109_anonymous_share_manager_inward_decomposition_guards.py`。
- 将 phase 109 完成态投射到 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`、baseline/reviews/docs、governance truth 常量。
- 将 phase108 guard 退化为 predecessor visibility，不再宣称 active-route owner。

## Risks & Controls

| Risk | Description | Control |
|------|-------------|---------|
| Scoped manager identity drift | `for_scope` 缓存策略变更可能影响 monkeypatch 测试路径 | 保持每个 manager 实例的 scoped cache 行为，与旧语义一致 |
| Aggregate primary mismatch | primary scope 选择不一致会影响 aggregate feedback/submit client 选择 | 用现有 aggregate submission tests + 新增 scope-view tests 冻结语义 |
| Report payload regression | pending report 入口切换后可能出现空 payload 或 aggregate/scoped 混淆 | 运行 recording/submission/service focused suite 覆盖 |
| Governance drift | code 完成但 route truth 未前推 | phase109 meta guard + route-handoff smoke + file-matrix check |

## Validation Architecture

### Focused Gates
- `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/core/anonymous_share/test_observability.py tests/services/test_services_share.py`
- `uv run pytest -q tests/core/anonymous_share/test_manager_scope_views.py`
- `uv run pytest -q tests/meta/test_phase109_anonymous_share_manager_inward_decomposition_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py`

### Quality Gates
- `uv run ruff check .`
- `uv run mypy`
- `uv run pytest -q`
- `uv run python scripts/check_file_matrix.py --write`
- `uv run python scripts/check_file_matrix.py --check`

### GSD Route Gates
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 109`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 109`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 109`

