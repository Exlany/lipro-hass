# 31-03 Summary

## Outcome

- `custom_components/lipro/select.py`、`custom_components/lipro/sensor.py` 与 `custom_components/lipro/helpers/platform.py` 现通过更窄的 runtime protocol / shadow base 维持 HA 适配面 typing，不再让 runtime_data、基类影子或 HA 签名噪声回流成 typed debt。
- `custom_components/lipro/services/maintenance.py` 的 reload failure contract 已保持显式 degraded semantics；service/platform/entity 尾部未借机回抬成第二控制面。
- `tests/services/test_services_diagnostics.py`、`tests/services/test_maintenance.py`、`tests/platforms/test_update.py`、`tests/platforms/test_select.py`、`tests/platforms/test_sensor.py` 与 `tests/core/test_diagnostics.py` 已锁定这些尾部收口语义。

## Key Files

- `custom_components/lipro/helpers/platform.py`
- `custom_components/lipro/select.py`
- `custom_components/lipro/sensor.py`
- `custom_components/lipro/services/maintenance.py`
- `tests/services/test_services_diagnostics.py`
- `tests/services/test_maintenance.py`
- `tests/platforms/test_update.py`
- `tests/platforms/test_select.py`
- `tests/platforms/test_sensor.py`
- `tests/core/test_diagnostics.py`

## Validation

- `uv run pytest -q tests/services/test_services_diagnostics.py tests/services/test_maintenance.py tests/platforms/test_update.py tests/platforms/test_select.py tests/platforms/test_sensor.py tests/core/test_diagnostics.py`

## Notes

- HA 平台适配层依旧是 thin adapter shell，不得因为 typing surgery 再长回业务根。