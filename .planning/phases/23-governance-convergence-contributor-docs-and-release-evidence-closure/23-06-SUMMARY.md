# 23-06 Summary

## Outcome

- 将 developer-only 路由 helper 集中到 `developer_router_support.py`，让 `service_router.py` 更接近薄转发层。
- 拆清 diagnostics helper 的本地视图 / 上传投影职责，减少 report builder、service router 与 diagnostics helper 之间的热点缠绕。
- 在 residual ledger 中显式登记更深层 coordinator/api 拆分仍属 post-closeout follow-up，避免 silent debt。

## Key Files

- `custom_components/lipro/control/developer_router_support.py`
- `custom_components/lipro/control/service_router.py`
- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/core/utils/developer_report.py`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `tests/services/test_services_diagnostics.py`
- `tests/services/test_services_registry.py`
- `tests/core/test_developer_report.py`
- `tests/core/api/test_api.py`

## Validation

- `uv run pytest tests/services/test_services_diagnostics.py -q` → passed
- `uv run pytest tests/services/test_services_registry.py tests/core/test_developer_report.py tests/core/test_coordinator.py tests/core/api/test_api.py -q` → passed
- `uv run ruff check custom_components/lipro/control/developer_router_support.py custom_components/lipro/control/service_router.py custom_components/lipro/services/diagnostics/helpers.py custom_components/lipro/core/utils/developer_report.py tests/services/test_services_diagnostics.py` → passed

## Notes

- 本 plan 只把 developer-only helper home 更清晰化，没有重写 coordinator 主循环。
- developer report 仍区分“本地视图”与“上传投影”，为后续更深 decouple 预留边界。
