---
phase: 95-schedule-runtime-and-boundary-hotspot-inward-decomposition
plan: "01"
status: completed
completed: 2026-03-28
---

# Summary 95-01

**schedule candidate query/mutation flow 已被 inward split 到 codec / request-shape / endpoint adapter collaborators；`ScheduleEndpoints` 继续保留唯一正式 schedule endpoint story。**

## Outcome

- `custom_components/lipro/core/api/schedule_service.py` 现在把 batch query / mutation orchestration 拆成更小的 candidate helpers，GET / ADD / DELETE 不再把 timeout、batch cleanup、refresh re-read 与 error summarization 混成一团。
- `custom_components/lipro/core/api/schedule_codec.py` 新增 next-id selection helper；mesh schedule id 选择不再滞留在 service hotspot 内部。
- `custom_components/lipro/core/api/schedule_endpoint.py` 现在明确承载 `times/evt` 长度校验 helper，`custom_components/lipro/core/api/endpoints/schedule.py` 也删掉了重复的 private/public codec wrappers 与重复 `_typed_iot_request` 闭包。
- schedule focused tests 现同时覆盖 mesh 与 non-mesh 的 get/add/delete 路径，让 endpoint/service 边界能被测试直接解释。

## Verification

- `uv run pytest -q tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_schedule_codec.py tests/core/api/test_api_schedule_candidate_queries.py tests/core/api/test_api_schedule_candidate_mutations.py` → `43 passed`
- `uv run ruff check custom_components/lipro/core/api/schedule_service.py custom_components/lipro/core/api/schedule_codec.py custom_components/lipro/core/api/schedule_endpoint.py custom_components/lipro/core/api/endpoints/schedule.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_schedule_codec.py` → `passed`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- `custom_components/lipro/core/api/endpoints/schedule.py` 一并被收口，因为 endpoint adapter 内部还留有重复 wrapper / nested closure 残留；这属于 Phase 95 的正式 hotspot inward split，而不是新增 public root。

## Next Readiness

- 95-02 可以沿同一条 retained-formal-home story 继续 inward split runtime/auth hotspots，而无需再回头处理 schedule ownership 漂移。
