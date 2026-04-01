---
phase: 119-mqtt-boundary-runtime-contract-and-release-governance-hardening
plan: "01"
subsystem: protocol-boundary
tags: [mqtt, boundary, protocol, governance, guards]
completed: 2026-04-01
---

# Plan 119-01 Summary

## What changed
- `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py` 收回 MQTT payload-size / biz-id normalization / topic decode support truth。
- `custom_components/lipro/core/mqtt/{payload.py,topics.py,message_processor.py}` 改为直接单向复用 boundary-owned helpers，不再依赖 `import_module(...)` lazy-import folklore。
- 新增 `tests/meta/test_phase119_mqtt_boundary_guards.py`，并同步 `PUBLIC_SURFACES.md` / `DEPENDENCY_MATRIX.md` 的 one-way authority 叙事。

## Outcome
- MQTT boundary authority 已恢复 `protocol.boundary -> mqtt` 单向主链。
- malformed topic/payload 行为与既有 runtime usage 未回归。
