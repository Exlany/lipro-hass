---
phase: 127-runtime-access-de-reflection-typed-runtime-entry-contracts-and-hotspot-continuation
plan: "01"
summary: true
---

# Plan 127-01 Summary

## Completed

- `custom_components/lipro/control/telemetry_surface.py` 已把 `build_entry_system_health_view()` / `build_entry_diagnostics_view()` 收窄到 typed telemetry return，不再把 observer bridge 伪装成宽泛 `dict[str, object]` 故事。
- `custom_components/lipro/control/runtime_access.py` 现在直接消费 typed `SystemHealthTelemetryView`，`build_runtime_snapshot()` 与 diagnostics projection 不再依赖 string-key 回捞 surrogate payload。
- `custom_components/lipro/control/models.py` 的 `FailureSummary` / `empty_failure_summary` 已回收到 `core.telemetry.models` 真源，control read-model 不再 shadow 第二份 failure contract。

## Outcome

- `ARC-39` 已在本计划范围内落地。
- control-plane telemetry seam 继续保持 observer-only posture，同时把 system-health projection 收敛为单一 typed formal truth。
