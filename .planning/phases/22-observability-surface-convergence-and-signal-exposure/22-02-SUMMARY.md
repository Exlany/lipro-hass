# 22-02 Summary

## Outcome

- 让 developer / support / report / evidence consumer 复用同一 shared `failure_summary` vocabulary，不再把 service-local `last_error` 或 legacy report 语言当成 canonical truth。
- `collect_developer_reports()` 现在会把 exporter-backed `entry_ref` 与 `failure_summary` 合流进 legacy `build_developer_report()` 分支，兼容路径不再平行定义失败语义。
- diagnostics service 的 `last_error` payload 新增嵌套 `failure_summary`，把 API 失败也投影到统一的 category / origin / handling policy 语言上。

## Key Files

- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/services/diagnostics/handlers.py`
- `custom_components/lipro/services/diagnostics/types.py`
- `custom_components/lipro/core/telemetry/sinks.py`
- `tests/services/test_services_diagnostics.py`
- `tests/services/test_services_share.py`
- `tests/services/test_execution.py`
- `tests/core/test_report_builder.py`
- `tests/core/test_developer_report.py`
- `tests/integration/test_ai_debug_evidence_pack.py`

## Validation

- `uv run pytest -q tests/services/test_services_diagnostics.py tests/services/test_services_share.py tests/services/test_execution.py tests/core/test_report_builder.py tests/core/test_developer_report.py tests/integration/test_ai_debug_evidence_pack.py` → `45 passed`
- `uv run mypy` → `Success: no issues found in 446 source files`

## Notes

- 本 plan 没有进入 README / SUPPORT / SECURITY / release workflow 范围；它只收口 consumer payload contract。
- 为消除类型裂缝，本轮顺带收紧了 shared failure-summary 相关 TypedDict / helper 返回值，使静态真相与运行时 contract 对齐。
