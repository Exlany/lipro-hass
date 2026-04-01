# Plan 125-02 Summary

## What changed

- `custom_components/lipro/runtime_types.py` 新增 `ScheduleMeshDeviceLike` formal contract，并继续保留 `CommandProperties` / `DeviceRefreshServiceLike` outward home。
- `custom_components/lipro/core/coordinator/services/protocol_service.py`、`custom_components/lipro/core/coordinator/services/schedule_service.py`、`custom_components/lipro/services/maintenance.py` 与 `custom_components/lipro/core/coordinator/runtime/command_runtime_support.py` 不再 shadow duplicate contracts。
- runtime/service-facing contract truth 继续停留在 sanctioned outward home，没有新开第二 formal root。

## Outcome

- `ARC-37` / `HOT-56` 的第一层 residual 已关闭：shared contract truth 不再跨平面重复定义。
- runtime hotspot 风险已从 truth duplication 收缩为 breadth / complexity。
