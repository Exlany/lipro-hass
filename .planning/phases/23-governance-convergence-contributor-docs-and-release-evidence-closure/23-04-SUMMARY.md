# 23-04 Summary

## Outcome

- 修复 fan preset/options 漂移：补齐 `gentle_wind` 与 vent `off`，确保显示态、可选列表与回写路径一致。
- 去掉 `runtime_access.py` 通过修改 `__dict__` 注入 `entry_id/options` 的副作用做法，改为只读 projection，避免污染 foreign object / test doubles。
- 锁定默认安装入口仍然是 `ARCHIVE_TAG=latest`，并把该契约同步回 README、中文 README、troubleshooting 与治理守卫。

## Key Files

- `custom_components/lipro/fan.py`
- `custom_components/lipro/control/runtime_access.py`
- `README.md`
- `README_zh.md`
- `docs/TROUBLESHOOTING.md`
- `tests/platforms/test_fan.py`
- `tests/core/test_system_health.py`
- `tests/meta/test_governance_guards.py`

## Validation

- `uv run pytest tests/platforms/test_fan.py -q` → passed
- `uv run pytest tests/core/test_system_health.py tests/core/test_diagnostics.py -q` → passed
- `uv run pytest tests/meta/test_governance_guards.py -q` → passed

## Notes

- 默认安装主路径继续是 `latest`；pin tag / `main` / mirror 仅作高级与可复现场景，不得反转成主入口。
- 本 plan 只修复 surface mismatch 与 side-effect seam，不重写 fan/service 主链。
