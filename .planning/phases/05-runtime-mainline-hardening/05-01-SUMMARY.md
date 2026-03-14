---
phase: 05-runtime-mainline-hardening
plan: "01"
status: completed
completed: 2026-03-13
requirements:
  - ARCH-02
  - RUN-01
  - RUN-02
  - RUN-03
---

# Summary 05-01

## Outcome
- `RuntimeContext` 的 runtime signal ports 已从 coordinator 私有回调升级为 formal service-object ports。
- `CoordinatorSignalService` 已成为 MQTT runtime wiring 的唯一 signal owner：connect-state 只进 telemetry，group reconciliation 只经 refresh service。
- `Coordinator` 不再把 `_record_connect_state()` / `_request_group_reconciliation()` 当作 wiring contract，对 runtime mainline 的 private-callback 依赖已收口。
- Phase 5 文档已按真实代码 rebase，不再把 `connect-status` shadow chain 误写为 runtime 主链。

## Verification
- `uv run ruff check custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/core/coordinator/runtime_context.py custom_components/lipro/core/coordinator/services/__init__.py custom_components/lipro/core/coordinator/services/telemetry_service.py tests/core/test_coordinator.py`
- `uv run pytest tests/core/test_coordinator.py tests/core/coordinator/services/test_telemetry_service.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/integration/test_mqtt_coordinator_integration.py -q` → `69 passed`

## Governance Notes
- Phase 5 planning package 已从“Ready for execution + connect-status old story”切回“Execution-aligned + single runtime mainline truth”。
- `custom_components/lipro/services/execution.py` 的 private auth seam 关闭动作在 `05-03` closeout 中统一落表。
