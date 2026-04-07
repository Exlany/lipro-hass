# 30-03 Summary

## Outcome

- `custom_components/lipro/control/entry_lifecycle_controller.py` 已把 setup/unload/reload 的 broad-catch 改成 named failure contracts，并保留 `CancelledError` passthrough；control lifecycle 不再依赖 generic swallow。
- `custom_components/lipro/control/system_health_surface.py` 仍只同步 shared `failure_summary` 最小载荷，没有被误扩成 diagnostics payload cleanup home。
- `tests/core/test_init.py`、`tests/core/test_init_edge_cases.py`、`tests/core/test_control_plane.py`、`tests/core/test_system_health.py` 与 `tests/meta/test_governance_guards.py` / `tests/meta/test_public_surface_guards.py` 已冻结 touched-zone truth。

## Key Files

- `custom_components/lipro/control/entry_lifecycle_controller.py`
- `custom_components/lipro/control/system_health_surface.py`
- `tests/core/test_init.py`
- `tests/core/test_init_edge_cases.py`
- `tests/core/test_control_plane.py`
- `tests/core/test_system_health.py`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_public_surface_guards.py`

## Validation

- `uv run pytest -q tests/core/test_init.py tests/core/test_init_edge_cases.py tests/core/test_control_plane.py tests/core/test_system_health.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_closeout_guards.py`

## Notes

- `Phase 31` 只承接 runtime/service/platform typed budget 与 broad-catch closeout；不得回退或重做此处已冻结的 control lifecycle / system health truth。