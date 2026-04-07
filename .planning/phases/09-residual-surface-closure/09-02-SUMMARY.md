---
phase: 09-residual-surface-closure
plan: "02"
status: completed
completed: 2026-03-14
requirements:
  - RSC-03
  - RSC-04
---

# Summary 09-02

## Outcome

- `Coordinator.devices` 已收口为 read-only mapping，平台/helper/diagnostics 仍可遍历读取，但 public surface 不再泄露 live mutable dict。
- `LiproDevice.outlet_power_info` 已成为正式 outlet-power primitive；`apply_outlet_power_info()` 只写 formal primitive，不再把 `power_info` 旁写进 `extra_data`。
- `sensor.py` 与 `control/diagnostics_surface.py` 已统一读取 `device.outlet_power_info`；diagnostics 把 outlet power 作为独立正式字段输出。

## Verification

- `uv run pytest -q tests/core/test_outlet_power.py tests/test_coordinator_public.py tests/platforms/test_sensor.py tests/core/test_diagnostics.py tests/core/test_coordinator.py`

## Governance Notes

- `extra_data["power_info"]` 只保留 legacy read fallback；新的正式写路径已被 meta/public regression guards 锁定。
