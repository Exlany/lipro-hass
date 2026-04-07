# 71-02 Summary

## Outcome

OTA diagnostics 与 firmware-install orchestration 已继续 inward split，entity surface 与 outward behavior 保持稳定。

## Highlights

- `diagnostics_api_ota.py` 新增 payload / primary-failure / controller-merge helper，降低主入口 orchestration 密度。
- `firmware_update.py` 把 install command preparation、translated error raising 与 command execution 拆成更窄步骤。
- OTA / firmware touched tests 保持绿色，没有引入新的 outward root 或 archive-truth 回流。

## Proof

- `uv run pytest -q tests/core/api/test_api_diagnostics_service.py tests/platforms/test_update.py tests/platforms/test_update_entity_refresh.py tests/platforms/test_update_install_flow.py tests/meta/test_phase71_hotspot_route_guards.py` → `37 passed`.
