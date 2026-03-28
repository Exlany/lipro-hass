# Phase 100: MQTT runtime and schedule service support extraction freeze - Context

**Gathered:** 2026-03-28
**Status:** Ready for execution

<domain>
## Phase Boundary

`Phase 100` 承接 `Phase 99` 之后的终审残留：继续不重开新功能，只把 runtime / api 面仍然偏厚但具备低风险 support seam 的两个正式 home —— `mqtt_runtime.py` 与 `schedule_service.py` —— 再做一轮 inward support extraction，并同步把治理、focused guards、phase 资产与 GSD parser truth 推进到 `v1.27 active route / Phase 100 complete / latest archived baseline = v1.26`。
</domain>

<decisions>
## Implementation Decisions
- **D-01:** `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` 继续保留 `MqttRuntime` 作为唯一正式 runtime MQTT orchestration home；只允许把 transport/notification/background-task support 逻辑 inward split 到 local support collaborator，不得新增第二条 runtime root。
- **D-02:** `custom_components/lipro/core/api/schedule_service.py` 继续保留 explicit REST schedule helper home 身份；candidate batching / timeout / request orchestration helpers 可以 inward split 到 local support collaborator，但 public functions、typed aliases 与 endpoint-facing contract 不得漂移。
- **D-03:** `Phase 99` 现在是 `v1.27` 里的 completed predecessor evidence；其 closeout bundle 继续保留，但 current-route truth 必须前推到 `Phase 100 complete`。
- **D-04:** `Phase 100` 只做 inward support extraction、治理同步与 proof chain freeze，不重开业务能力，也不反向改写 `v1.26` archived baseline truth。
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / governance
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 唯一终态架构裁决
- `.planning/PROJECT.md` — 当前里程碑目标与 active-route 真源
- `.planning/ROADMAP.md` — phase 编排与 closeout route
- `.planning/REQUIREMENTS.md` — requirement basket 与 traceability
- `.planning/STATE.md` — parser-facing live state truth
- `.planning/baseline/VERIFICATION_MATRIX.md` — focused/repo-wide proof chain 真源
- `.planning/reviews/FILE_MATRIX.md` — 文件归属与 hotspot note 真源

### Runtime hotspot target
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` — 待收口的正式 runtime MQTT home
- `tests/core/coordinator/runtime/test_mqtt_runtime.py` — MQTT runtime 主题化 suite shell
- `tests/core/coordinator/runtime/test_mqtt_runtime_connection.py` — 连接面回归
- `tests/core/coordinator/runtime/test_mqtt_runtime_messages.py` — message handling 回归
- `tests/core/coordinator/runtime/test_mqtt_runtime_notifications.py` — disconnect notification / issue flow 回归
- `tests/core/coordinator/runtime/test_mqtt_runtime_support.py` — MQTT runtime fixtures / support seam coverage

### Schedule hotspot target
- `custom_components/lipro/core/api/schedule_service.py` — 待收口的 explicit schedule helper home
- `tests/core/api/test_api_schedule_service.py` — schedule helper public behavior 回归
- `tests/core/api/test_api_schedule_candidate_queries.py` — candidate query helper 回归
- `tests/core/api/test_api_schedule_candidate_mutations.py` — add/delete mutation helper 回归
- `tests/core/api/test_api_transport_and_schedule_schedules.py` — schedule endpoint integration slice

</canonical_refs>

<specifics>
## Specific Ideas
- `mqtt_runtime.py` 当前仍承载 transport guard、disconnect notification、background task tracking 与 telemetry summary 组装，适合继续 inward split。
- `schedule_service.py` 当前 helper 函数簇边界清晰：candidate request / timeout / task drain / batch orchestration 可整体外提到 support 模块。
- focused current-route guard 应新增 `tests/meta/test_phase100_runtime_schedule_support_guards.py`，并把 `Phase 99` guard 退回 predecessor truth。
</specifics>

<deferred>
## Deferred Ideas
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`

以上仍是非阻塞热点，但本 phase 不同时推进，避免把 `v1.27` closeout 再次扩散成多热点并发重构。
</deferred>

---

*Phase: 100-mqtt-runtime-and-schedule-service-support-extraction-freeze*
*Context gathered: 2026-03-28*
