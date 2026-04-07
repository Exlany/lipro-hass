---
phase: 10-api-drift-isolation-core-boundary-prep
plan: "03"
status: completed
completed: 2026-03-14
requirements:
  - ISO-03
  - ISO-04
---

# Summary 10-03

## Outcome

- `custom_components/lipro/core/__init__.py` 已不再导出 `Coordinator`，改为只保留 host-neutral core exports，并新增 `AuthSessionSnapshot` export。
- `custom_components/lipro/control/runtime_access.py` 已继续收口为 control-plane runtime-home locator；`custom_components/lipro/control/telemetry_surface.py` 通过该 helper 惰性解析 runtime root，避免循环导入与散落 backdoor。
- meta guards 已补强：`tests/meta/test_modularization_surfaces.py` 与 `tests/meta/test_public_surface_guards.py` 继续阻断 `core` 重新长回 HA runtime root 叙事。

## Verification

- `uv run pytest -q -x tests/meta/test_modularization_surfaces.py tests/meta/test_public_surface_guards.py tests/test_coordinator_public.py tests/core/test_diagnostics.py tests/core/test_system_health.py`
- Result: `48 passed`

## Governance Notes

- `Coordinator` 的正式 home 继续固定在 `custom_components/lipro/coordinator_entry.py`；本计划收窄的是 narrative / public surface，不是更换 runtime root。
- `control/telemetry_surface.py` 继续保持 observer-only bridge 角色，不被允许重新成长成 runtime home。
