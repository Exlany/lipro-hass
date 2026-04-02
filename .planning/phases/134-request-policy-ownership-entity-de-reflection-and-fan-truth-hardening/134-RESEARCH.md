# Phase 134 Research

## Primary Findings

1. `custom_components/lipro/core/api/request_policy.py` 在本轮开始前同时保留 module-level mutating pacing helpers 与 `RequestPolicy` 实例代理，mutable pacing state 的 owner story 不够单一。
2. `custom_components/lipro/core/api/request_policy_support.py` 已具备 `_CommandPacingCaches`，但 public helper 仍搬运多组并行 dict 参数，support surface 参数密度偏高。
3. `custom_components/lipro/entities/descriptors.py` 与 `custom_components/lipro/binary_sensor.py` 仍依赖 dotted-path/getattr 反射，违背 explicit projection / domain truth 优先原则。
4. `custom_components/lipro/fan.py` 对 unknown `fanMode` fallback 为 `cycle`，会把 preset truth 与 supported_features truth 扭成矛盾投影。

## Repo-Wide Audit Snapshot

- production Python files: `322`
- production files > 500 lines: `0`
- production functions > 50 lines: `13`
- production functions complexity > 10: `12`
- 重点 formal hotspots 仍包括：`core/command/dispatch.py`, `core/auth/manager.py`, `control/runtime_access_support_telemetry.py`, `core/device/group_status.py`

## Immediate Phase Thesis

本 phase 选择了“高价值、低歧义、可验证”的三类残留：single owner、explicit projection、truthful fan preset。它们都能在既有 formal homes 内 inward convergence，不需要引入新 root 或新依赖。
