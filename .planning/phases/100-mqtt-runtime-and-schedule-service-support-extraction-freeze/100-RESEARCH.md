# Phase 100 Research

## Scope

对 `mqtt_runtime.py` 与 `schedule_service.py` 做“正式 home 保留 + support collaborator inward split”式终审收口，并把治理真相前推到 `Phase 100 complete`。

## Findings

### 1. `mqtt_runtime.py` 适合继续 support extraction
- 当前文件 `463` 行，但已经具备良好的组合式分层：`connection/dedup/reconnect/message_handler` 都已外置，剩余厚度主要集中在 transport operation guard、disconnect notification、background task tracking 与 telemetry summarization。
- 这些逻辑是明显的 local support seam：不改变 `MqttRuntime` public methods 即可 inward split，回归风险相对低。
- 覆盖面充足：`tests/core/coordinator/runtime/test_mqtt_runtime_{init,connection,messages,notifications}.py` 与 `test_mqtt_runtime_support.py` 已提供良好护栏。

### 2. `schedule_service.py` 更像“显式 helper home + candidate support cluster”
- 当前文件 `413` 行，且 helper 函数簇边界非常清楚：`_run_timed_get_candidate_request`、`_create_get_candidate_tasks`、`_drain_candidate_tasks`、`_collect_schedule_rows_from_batch`、`_add_mesh_schedule_for_candidate`、`_delete_mesh_schedule_batch` 等都可整体下沉到 support。
- public home 应继续保留 `execute_mesh_schedule_candidate_request()`、`get_mesh_schedules_by_candidates()`、`add_mesh_schedule_by_candidates()`、`delete_mesh_schedules_by_candidates()` outward import story，防止 endpoint / tests / callers 漂移。
- 覆盖面同样充足：`test_api_schedule_service.py`、`test_api_schedule_candidate_queries.py`、`test_api_schedule_candidate_mutations.py`、`test_api_transport_and_schedule_schedules.py`。

### 3. 治理同步成本可控
- 本仓库已有 `Phase 98 -> 99` 前推模板；复制到 `Phase 100` 的主要工作是 current-route truth、focused guard、route-handoff smoke、verification/file matrix 与 phase closeout bundle。
- 风险在于：`Phase 99` guard 需要从 current-route 改成 predecessor truth，否则会与新 `Phase 100` current-route guard 冲突。

## Recommended Phase Shape

### Plan 100-01
把 `mqtt_runtime.py` 收口成 orchestration home，同时新增 `mqtt_runtime_support.py` 承载 transport/notification/background-task support。

### Plan 100-02
把 `schedule_service.py` 收口成 explicit helper home，同时新增 `schedule_service_support.py` 承载 candidate batching / timeout / request-orchestration helpers。

### Plan 100-03
把 `.planning/*`、developer guide、maps/ledgers、focused guards 与 GSD parser truth 推进到 `Phase 100 complete`，并通过 focused + repo-wide proof chain 重新冻结 `$gsd-next -> $gsd-complete-milestone v1.27`。

## Why This Is Optimal
- 两个目标都具备清晰 support seam、稳定 public home、充分测试面。
- 它们分别覆盖 runtime plane 与 api helper plane，是当前 closeout-ready 之前最值得再做的一轮“薄化 formal homes”动作。
- 同时避免把 `anonymous_share/manager.py` 与 `rest_decoder.py` 一起纳入，防止本轮 scope 过大。
