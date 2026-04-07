# 64-02 Summary — schedule formal contracts

## Outcome
- 将 schedule service 的主路径从本地 `tuple[Any, Any]` / `Mapping[str, Any]` / broad `getattr()` probing 收口到显式 typed contracts。
- 保持 `custom_components/lipro/services/schedule.py` 的 outward home、shared executor 调用链、以及 service 响应 shape 不变。
- 复用 `custom_components/lipro/core/api/types.py` 作为 schedule row 的正式 type home，没有新建第二套 schedule truth。

## Files Changed
- `custom_components/lipro/core/api/types.py`
  - 新增 `SchedulePayload`，并让 `ScheduleTimingRow.schedule` 指向该正式 payload contract。
- `custom_components/lipro/services/schedule.py`
  - 复用 `LiproDevice` / `LiproCoordinator` 作为 resolver contract。
  - 新增 `NormalizedScheduleRow`，使 service 归一化输出 keys 显式化。
  - 将 `_normalize_schedule_time_events()` 改为消费 `SchedulePayload`。
  - 将 `get_mesh_context()` 改为优先读取声明属性，仅保留显式 `ir_remote_gateway_device_id` fallback 分支。
- `tests/services/test_services_schedule.py`
  - 补充 blank mesh gateway 不被 IR fallback 覆盖的回归用例，锁定 None-only fallback 语义。

## Verification
- `uv run pytest tests/services/test_services_schedule.py tests/core/test_init_service_handlers_schedules.py -q`
  - 结果：✅ 通过（已纳入 Phase 64 汇总验证，合并输出 `35 passed`）。

## Notes
- 未修改 service outward behavior、shared executor usage、`serial + schedules` / add / delete 响应形状。
- 未新增新的 schedule helper root 或第二套 typed truth。
