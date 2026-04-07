---
phase: 96-redaction-telemetry-and-anonymous-share-sanitizer-burndown
plan: "01"
status: completed
completed: 2026-03-28
---

# Summary 96-01

**control-plane diagnostics redaction hotspot 已被 inward split 成更薄的 recursion / JSON-string / fail-closed helpers；`diagnostics.py` 继续保持 thin adapter。**

## Outcome

- `custom_components/lipro/control/redaction.py` 现在把 nested-key fail-closed gate、mapping/sequence traversal、JSON-string round-trip 与 scalar-string masking 分拆成命名私有 helper，`redact_property_value()` 不再承担整条递归分支树。
- `custom_components/lipro/diagnostics.py` 继续只承接 control-plane wiring；对非 mapping device properties 的处理保持防御性，同时不再回流内部 redaction helper。
- diagnostics focused tests 改为显式通过 typed payload helper 读取嵌套结果，避免隐式 `Any`-like 假设，让 entry/device/config-entry diagnostics 的 redaction contract 更直接可读。

## Verification

- `uv run pytest -q tests/core/test_diagnostics_redaction.py tests/core/test_diagnostics.py tests/core/test_diagnostics_config_entry.py tests/core/test_diagnostics_device.py` → `37 passed`
- `uv run ruff check custom_components/lipro/control/redaction.py custom_components/lipro/diagnostics.py tests/core/test_diagnostics_redaction.py tests/core/test_diagnostics.py tests/core/test_diagnostics_config_entry.py tests/core/test_diagnostics_device.py` → `passed`

## Task Commits

- None — per user instruction, this workspace keeps the phase uncommitted.

## Deviations from Plan

- 没有新增 outward diagnostics redaction surface；本轮只做 inward split 与测试显式化，刻意把治理/route freeze 留在 `Phase 97`。

## Next Readiness

- `96-03` 现在可以沿同一条 shared redaction truth 继续收薄 anonymous-share manager，而无需再担心 diagnostics sink 仍持有厚重 sanitizer 分支。
