# Plan 123-02 Summary

## What changed

- `custom_components/lipro/control/service_router_handlers.py` 已重收敛为 command / schedule / share / maintenance callbacks 的正式 control-local family home。
- `custom_components/lipro/control/service_router_command_handlers.py`、`custom_components/lipro/control/service_router_schedule_handlers.py`、`custom_components/lipro/control/service_router_share_handlers.py` 与 `custom_components/lipro/control/service_router_maintenance_handlers.py` 已删除。
- `tests/meta/test_phase69_support_budget_guards.py`、`tests/meta/test_phase104_service_router_runtime_split_guards.py` 与新增的 `tests/meta/test_phase123_service_router_reconvergence_guards.py` 已分别冻结 locality truth、predecessor visibility 与 current-topology reconvergence truth。
- `scripts/check_file_matrix_registry_classifiers.py`、`scripts/check_file_matrix_registry_overrides.py` 与 `.planning/reviews/FILE_MATRIX.md` 已同步投影新的 family ownership 与删除结果。

## Outcome

- `ARC-34` / `HOT-54`：control-plane 过薄 split 已被正式收口，不再存在四个 current-topology shell。
- `service_router_diagnostics_handlers.py` 继续保留独立身份，避免 developer / diagnostics 语义重新与 public callback family 混杂。
