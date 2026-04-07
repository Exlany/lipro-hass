# 17-02 Summary

## Outcome

- Deleted the `get_auth_data()` fallback path from token persistence so `AuthSessionSnapshot` is now the only formal token-persistence contract.
- Tightened outlet-power typing to `OutletPowerInfoRow | list[OutletPowerInfoRow]` and removed the synthetic `{"data": rows}` helper envelope from the formal runtime/protocol path.
- Updated focused auth/init/runtime tests to consume the explicit typed contract instead of legacy dict projections.

## Key Files

- `custom_components/lipro/entry_auth.py`
- `custom_components/lipro/core/auth/manager.py`
- `custom_components/lipro/core/api/power_service.py`
- `custom_components/lipro/core/protocol/contracts.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/coordinator/runtime/outlet_power_runtime.py`
- `tests/core/test_init.py`
- `tests/core/test_auth.py`
- `tests/core/test_outlet_power_runtime.py`

## Validation

- `uv run pytest -q tests/core/test_init.py tests/core/test_auth.py tests/core/api/test_api.py tests/core/api/test_helper_modules.py tests/core/test_outlet_power_runtime.py`
- `uv run mypy custom_components/lipro/entry_auth.py custom_components/lipro/core/auth/manager.py custom_components/lipro/core/api/power_service.py custom_components/lipro/core/protocol custom_components/lipro/core/coordinator/runtime/outlet_power_runtime.py`
- `uv run ruff check custom_components/lipro/core/auth custom_components/lipro/core/api custom_components/lipro/core/protocol custom_components/lipro/core/coordinator/runtime tests/core`
