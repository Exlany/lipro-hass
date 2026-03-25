---
phase: 75-access-mode-truth-closure-evidence-promotion-formalization-and-thin-adapter-typing-hardening
plan: "03"
subsystem: thin-adapters
tags: [typing, diagnostics, system-health, options-flow]
requirements-completed: [ARC-19, TYP-21, QLT-30]
completed: 2026-03-25
---

# Phase 75 Plan 03 Summary

**diagnostics / system-health / options-flow 薄适配层继续变薄，并以更诚实的类型契约承接 formal homes。**

## Accomplishments
- `custom_components/lipro/diagnostics.py` 继续只做 thin adapter，明确委托 control-plane diagnostics surface 与 redaction contract。
- `custom_components/lipro/system_health.py` 保持根模块自己的 `system_health_info` 注册身份，同时继续委托 control surface。
- `custom_components/lipro/flow/options_flow.py` 收紧 persisted options typing、default resolution 与 schema helper，使 options-flow 不再依赖宽口 `Any`。

## Proof
- `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_diagnostics_config_entry.py tests/core/test_diagnostics_device.py tests/core/test_diagnostics_redaction.py tests/core/test_system_health.py tests/flows/test_options_flow.py tests/flows/test_options_flow_utils.py` → `63 passed`
