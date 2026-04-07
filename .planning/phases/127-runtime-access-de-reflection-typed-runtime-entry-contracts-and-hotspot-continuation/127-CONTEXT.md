# Phase 127 Context

## Goal

显式推进 `runtime_access` seam：让 typed telemetry contract 成为唯一正式 truth，并把 runtime entry / coordinator narrowing 从反射式 probe 收紧到显式 port / adapter。

## Source Findings

- `custom_components/lipro/control/runtime_access.py` 仍会把 typed telemetry 擦回 dict 再用字符串 key 回捞。
- `custom_components/lipro/control/runtime_access_support_views.py` 仍保留 `type(...).__getattribute__` 主导的窄化方式。

## Planned Outcome

- `build_entry_system_health_view()` / `build_runtime_snapshot()` 直接消费 typed telemetry view。
- runtime entry / coordinator narrowing 有明确 typed contract 或 adapter helper。
