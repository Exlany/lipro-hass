# Plan 61-04 Summary

- `custom_components/lipro/select.py` 继续保留唯一 HA select platform root；gear-preset extraction / projection logic 已 inward split 到 `custom_components/lipro/select_internal/gear.py`，而 `LiproLightGearSelect` outward class / constants / setup shell 保持稳定。
- `tests/platforms/test_select_behavior.py` 已收敛成 thin shell，gear / mapped / setup cases 已 topicize 到 `select_gear_behavior_cases.py`、`select_mapped_behavior_cases.py`、`select_setup_behavior_cases.py`；`tests/meta/test_phase61_formal_home_budget_guards.py` 与 `.planning/reviews/FILE_MATRIX.md` 已冻结新的 no-growth / one-root story。
- 验证命令 `uv run pytest -q tests/platforms/test_select_behavior.py tests/platforms/test_select_models.py tests/platforms/test_platform_entities_behavior.py tests/meta/test_phase61_formal_home_budget_guards.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py` 通过（`104 passed`）。
