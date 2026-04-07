---
phase: 95-schedule-runtime-and-boundary-hotspot-inward-decomposition
plan: "02"
status: completed
completed: 2026-03-28
---

# Summary 95-02

**`CommandRuntime`、`MqttRuntime` 与 REST auth-recovery hotspot interiors 已被 inward split 成更小的 trace / failure / reconnect / refresh helpers，同时 formal homes 保持不变。**

## Outcome

- `custom_components/lipro/core/coordinator/runtime/command_runtime.py` 现在把 command trace 构建、command-result failure classification 与 reauth reason resolution 明确抽成 helper，formal runtime root 仍只在 `CommandRuntime`。
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` 现在显式集中 transport requirement、connect-attempt finalization、disconnect-notification threshold 计算与 background-task exception consumption，不再把这些边角决策散落在 connect/disconnect/notifier 方法里。
- `custom_components/lipro/core/api/auth_recovery.py` 现在把 result message 解析、refresh reuse bookkeeping、refresh failure bookkeeping 与 replay-allowed retry decision inward split 成局部 helper；它继续只是 localized REST collaborator，而不是新 orchestration owner。
- focused runtime/auth tests 新增 no-regression coverage：auth mapping retry path、transport never-confirms connect path、already-notified disconnect path。

## Verification

- `uv run pytest -q tests/core/api/test_auth_recovery_telemetry.py tests/core/coordinator/runtime/test_command_runtime.py tests/core/coordinator/runtime/test_command_runtime_orchestration.py tests/core/coordinator/runtime/test_mqtt_runtime_connection.py tests/core/coordinator/runtime/test_mqtt_runtime_notifications.py` → `48 passed`
- `uv run ruff check custom_components/lipro/core/api/auth_recovery.py custom_components/lipro/core/coordinator/runtime/command_runtime.py custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py tests/core/api/test_auth_recovery_telemetry.py tests/core/coordinator/runtime/test_mqtt_runtime_connection.py tests/core/coordinator/runtime/test_mqtt_runtime_notifications.py` → `passed`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- `CommandRuntime` 本轮只抽出 high-signal helper，而没有再人为拆出第二个 runtime module；这是刻意保持 formal home 不变，避免为了“看起来更碎”而制造第二条运行面故事线。

## Next Readiness

- 95-03 可以把这批 hotspot inward split 结果冻结到 guard / matrix / route truth，而不必再担心 runtime/auth hotspot 仍处于厚类高分支状态。
