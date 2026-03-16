# 19-03 Summary

## Outcome

- Demoted platform `async_setup_entry()` functions to thin setup shells by routing all `entry.runtime_data -> async_add_entities` glue through `helpers/platform.add_entry_entities()`.
- Kept `helpers/platform.py` as the single HA platform projection home while preventing platform shells from growing a separate runtime locator or control story.
- Added focused helper coverage so the platform setup shell contract stays explicit and future drift is caught early.

## Key Files

- `custom_components/lipro/helpers/platform.py`
- `custom_components/lipro/light.py`
- `custom_components/lipro/cover.py`
- `custom_components/lipro/fan.py`
- `custom_components/lipro/select.py`
- `custom_components/lipro/switch.py`
- `custom_components/lipro/update.py`
- `tests/core/test_helpers.py`

## Validation

- `uv run ruff check custom_components/lipro/helpers/platform.py custom_components/lipro/light.py custom_components/lipro/cover.py custom_components/lipro/fan.py custom_components/lipro/select.py custom_components/lipro/switch.py custom_components/lipro/update.py tests/core/test_helpers.py`
- `uv run pytest -q tests/core/test_helpers.py tests/platforms/test_entity_behavior.py`
- `uv run pytest -q tests/core/test_control_plane.py -k runtime_access && uv run pytest -q tests/integration/test_headless_consumer_proof.py`
