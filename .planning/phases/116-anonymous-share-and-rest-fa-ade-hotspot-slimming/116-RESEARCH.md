# Phase 116 Research

**Phase:** `116-anonymous-share-and-rest-fa-ade-hotspot-slimming`
**Date:** `2026-03-31`
**Requirements:** `HOT-49`

## Objective

把 `custom_components/lipro/core/api/rest_facade.py` 与 `custom_components/lipro/core/anonymous_share/manager.py` 继续在既有 formal homes 内 inward split：前者主要收窄 session-state / transport / request wrapper density，后者主要收窄 scope-state / collector delegation / aggregate-view submit-memory 语义噪音，同时保持 `client.py` stable import shell、`AnonymousShareManager` outward identity、registry/factory contract 与 child-façade composition truth 全部不变。

## Inputs Reviewed

- `.planning/phases/116-anonymous-share-and-rest-fa-ade-hotspot-slimming/116-CONTEXT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/api/rest_facade.py`
- `custom_components/lipro/core/api/session_state.py`
- `custom_components/lipro/core/api/request_gateway.py`
- `custom_components/lipro/core/api/transport_executor.py`
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/anonymous_share/manager_scope.py`
- `custom_components/lipro/core/anonymous_share/manager_submission.py`
- `custom_components/lipro/core/anonymous_share/manager_support.py`
- `custom_components/lipro/core/anonymous_share/registry.py`
- `tests/core/api/test_api.py`
- `tests/core/api/test_api_status_service_wrappers.py`
- `tests/core/api/test_protocol_contract_facade_runtime.py`
- `tests/core/anonymous_share/test_manager_scope_views.py`
- `tests/core/anonymous_share/test_manager_submission.py`
- `tests/core/anonymous_share/test_manager_recording.py`
- `tests/core/anonymous_share/test_observability.py`
- `tests/core/test_anonymous_share_cov_missing.py`

## Findings

1. `rest_facade.py` 当前最厚的部分并不是 endpoint binding，而是两层样板：
   - `RestSessionState` 上的手写 getter/setter 成片堆叠；
   - `_transport_executor` / `_request_gateway` / `_auth_recovery` 的薄 wrapper 成片堆叠。
   其中第一层已有现成 inward 机制：`custom_components/lipro/core/api/session_state.py` 已提供 `session_state_property()`，但 `rest_facade.py` 仍未使用。**最优做法**是直接在 formal home 内采用 declarative state binding，而不是再造新 façade/support shell。

2. `manager.py` 已经部分走在正确方向上：
   - `manager_support.py` 已有 `_AggregateViewState` 与 `scope_state_property()`；
   - `manager.py` 已经把 `_collector` / `_last_upload_time` / `_installation_id` 等字段切到 declarative scope-state property；
   - aggregate view 也已通过共享 `_AggregateViewState` 避免 aggregate outcome 孤岛。
   因此本 phase 在匿名分享侧不该另起炉灶，而应继续沿同一 inward split 方向，把剩余的 discoverability 噪音与 collector delegation boilerplate 收窄。

3. 当前匿名分享剩余热点主要有两类：
   - 内部命名仍偏短而隐：`_state` / `_primary_state` 使“当前 scope state”与“聚合优先 state”不够一眼可辨；
   - `record_*` 系列仍有多段纯转发样板，虽然行为不复杂，但继续放大 manager 文件噪音。
   **最优做法**是把 `_state` 语义抬升为 `_scope_state`，并把重复 collector forwarding 收敛为内部 declarative delegation，而不是引入新的 outward helper family。

4. 不应新增 compat shell / second root，原因非常明确：
   - `client.py` 已被 meta / protocol contract tests 明确冻结为 stable import shell；
   - `AnonymousShareManager` + `registry.py` 已是现行 outward manager / factory truth；
   - 任何新增 façade/adapter shell 都会把“热点收口”重新变成“多入口并存”，直接违背仓库的 north-star single-mainline / formal-home 裁决。

5. 当前 focused tests 已经覆盖大部分行为面，但还缺两类更窄的 contract freeze：
   - REST façade 对 injected `RestSessionState` 的 declarative state binding contract；
   - aggregate views 之间共享 submit-outcome memory 的 contract。
   这两点正好是本 phase 重构后最值得冻结的 inward split 结果。

## Execution Shape

建议拆为 **2 个 plans**，分别收敛两处热点，避免把两类认知模型混在一个 plan 中：

- **116-01 REST façade declarative state/wrapper slimming**
  - 使用 `session_state_property()` 替换 `rest_facade.py` 中成片的手写 session/token/callback 属性代理；
  - 用局部 declarative collaborator delegation 收窄 `_transport_executor` / `_request_gateway` / `_auth_recovery` 的薄 wrapper 密度；
  - focused tests 冻结 stable import / injected session state / sync-session setter contract。

- **116-02 Anonymous-share scope-state naming and collector delegation slimming**
  - 将 `manager.py` 内部 `_state` / `_primary_state` 提升为更清晰的 `_scope_state` / `_primary_scope_state` 语义；
  - 把剩余 collector forwarding boilerplate inward 收口为 declarative delegation；
  - focused tests 冻结 aggregate view shared outcome state、scope manager contract 与既有 registry/observability 行为。

## Risks

- 若只把 `rest_facade.py` 的样板挪到一个新 helper 文件，但不复用现有 `session_state_property()`，会形成“换名不减重”的假瘦身。
- 若匿名分享侧改了内部命名却不补 focused tests，后续很容易再次把 aggregate/scoped submit memory 分叉回去。
- 若 phase 完成后只补 code，不同步 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md` 与 governance truth，`$gsd-next` 仍会停在 `116 discuss-ready` 而不是推进到 `117`。
