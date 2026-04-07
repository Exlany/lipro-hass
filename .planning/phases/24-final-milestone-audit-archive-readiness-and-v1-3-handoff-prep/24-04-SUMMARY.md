# 24-04 Summary

## Outcome

- `find_runtime_entry_for_coordinator()` 恢复 bound-entry identity：当 coordinator 已绑定 live config entry 时，控制面现在返回原始 entry，而不是 `_RuntimeEntryProjection`。
- developer diagnostics 路由 seam 现通过显式设备投影与静态类型收窄保持类型真相，`uv run mypy` 之前的 11 个错误已清零，且未扩展到额外重构。
- `LiproEntity._async_dispatch_runtime_command()` 现在在正式 `command_service` 可用时优先走该 surface，同时保留对轻量测试夹具的 coordinator fallback；既消除了 `Any` 返回漂移，也没有打碎 init/service 回归切片。

## Key Files

- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/developer_router_support.py`
- `custom_components/lipro/entities/base.py`

## Validation

- `uv run mypy` ✅
- `uv run pytest -q tests/core/test_control_plane.py tests/services/test_services_diagnostics.py` ✅
- `uv run pytest tests/core/test_init.py -k "get_city or query_user_cloud or fetch_body_sensor_history or fetch_door_sensor_history" -q` ✅
- `uv run ruff check .` ✅

## Notes

- 本次仅修复 `24-04-PLAN.md` 已证实的 closeout blockers；`custom_components/lipro/control/service_router.py`、`custom_components/lipro/runtime_types.py`、`custom_components/lipro/services/diagnostics/types.py` 无需变更即可恢复 gate。
- Summary generated at `2026-03-17T00:41:29Z`.
