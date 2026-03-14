---
phase: 09
status: partial
updated: 2026-03-14
---

# Phase 09 Verification

## Scope

原验证结果覆盖已执行的 `09-01` ~ `09-03`：protocol root 显式化、compat export 收窄、runtime device access 只读化、outlet-power primitive 正式化，以及治理/守卫回写。

**2026-03-14 planning addendum:** `09-04` / `09-05` 已新增，用于把 legacy tests 收敛到相同正式架构；因此本文件当前表示“production closure 已验证，phase addendum 待再次统一验证”。

## Commands

- `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_public_surface_guards.py tests/core/test_outlet_power.py tests/test_coordinator_public.py tests/platforms/test_sensor.py tests/core/test_diagnostics.py tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q`

## Result

- `09-01` ~ `09-03` 的 targeted regressions 与 fixture/governance hardening 回归已通过；本轮最小充分集合为 `150 passed`。
- `09-04` / `09-05` 仍未执行；legacy test architecture convergence 完成后需重跑本文件中的 full verification。
- governance guards 已通过：`uv run pytest -q tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py` → `23 passed`。
- architecture/file-matrix checks 已通过：`uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`。
- full suite 已通过：`uv run pytest -q` → `2133 passed`。
- `09-UAT.md` 已登记 automated UAT 结论；remaining compat seams 均已在 `RESIDUAL_LEDGER.md` / `KILL_LIST.md` 继续计数。

## Requirement Mapping

- `RSC-01`：`LiproProtocolFacade` / `LiproMqttFacade` 已改为显式 surface；`tests/meta/test_public_surface_guards.py` 覆盖。
- `RSC-02`：root/core/config-flow/MQTT package compat exports 已收窄；`raw_client` 仅剩显式 seam；governance docs 已同步。
- `RSC-03`：`Coordinator.devices` 为 read-only mapping；`tests/test_coordinator_public.py` 与 `tests/core/test_coordinator.py` 覆盖。
- `RSC-04`：`LiproDevice.outlet_power_info` 成为正式 primitive；`tests/core/test_outlet_power.py`、`tests/platforms/test_sensor.py`、`tests/core/test_diagnostics.py` 覆盖。
