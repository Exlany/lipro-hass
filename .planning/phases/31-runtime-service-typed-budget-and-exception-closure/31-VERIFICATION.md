# Phase 31 Verification

status: passed

## Goal

- 核验 `Phase 31: runtime/service typed budget and exception closure` 是否完成 `TYP-07` / `ERR-05` / `GOV-23`：把 runtime/service/platform touched zones 的 typed backlog、broad-catch 语义与 no-growth guard 收口成持续 machine truth。
- 终审结论：**`TYP-07`、`ERR-05` 与 `GOV-23` 已完成；Phase 31 已把 continuation route 的 runtime/service/platform 余债转成可审计预算与持续守卫。**

## Reviewed Assets

- Phase 资产：`31-CONTEXT.md`、`31-RESEARCH.md`、`31-VALIDATION.md`
- 已生成 summaries：`31-01-SUMMARY.md`、`31-02-SUMMARY.md`、`31-03-SUMMARY.md`、`31-04-SUMMARY.md`
- synced truth：`custom_components/lipro/core/coordinator/{coordinator.py,mqtt_lifecycle.py}`、`custom_components/lipro/core/coordinator/runtime/{mqtt_runtime.py,device_runtime.py,state/updater.py,device/filter.py,device/snapshot.py}`、`custom_components/lipro/helpers/platform.py`、`custom_components/lipro/{select.py,sensor.py}`、`custom_components/lipro/services/maintenance.py`、`tests/core/{test_coordinator.py,test_coordinator_integration.py,test_device_refresh.py,test_device.py,test_diagnostics.py,test_system_health.py}`、`tests/core/coordinator/runtime/{test_mqtt_runtime.py,test_device_runtime.py}`、`tests/services/{test_services_diagnostics.py,test_maintenance.py}`、`tests/platforms/{test_update.py,test_select.py,test_sensor.py}`、`tests/meta/{test_governance_guards.py,test_governance_closeout_guards.py,test_public_surface_guards.py,test_toolchain_truth.py,test_phase31_runtime_budget_guards.py}`、`.planning/{ROADMAP.md,REQUIREMENTS.md,STATE.md,v1.3-HANDOFF.md}`

## Must-Haves

- **1. Runtime lifecycle and transport failures are classified — PASS**
  - coordinator / MQTT lifecycle broad-catch 已显式落到 fail-closed、degraded 或 best-effort teardown 语义。
  - runtime negative-path tests 现在验证的是 failure contract，而不是仅验证“不崩溃”。

- **2. Runtime/service/platform typing is budgeted instead of hand-waved — PASS**
  - touched production zones 已建立 `sanctioned_any`、`backlog_any` 与 `type: ignore` no-growth truth。
  - runtime device/state narrowing 没有为了数字好看而虚构第二套 payload wrapper。

- **3. No-growth governance is machine-checked — PASS**
  - `tests/meta/test_phase31_runtime_budget_guards.py` 已冻结 broad-catch allowlist、typed budget 与 touched-zone type-ignore contract。
  - planning docs、handoff truth 与 meta guards 对 `Phase 25 -> 31` continuation closeout 讲同一条正式故事。

## Evidence

- `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/test_coordinator_integration.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_device_refresh.py tests/core/test_device.py tests/services/test_services_diagnostics.py tests/services/test_maintenance.py tests/platforms/test_update.py tests/platforms/test_select.py tests/platforms/test_sensor.py tests/core/test_diagnostics.py tests/meta/test_phase31_runtime_budget_guards.py` → `368 passed`
- `uv run mypy custom_components/lipro/core/coordinator custom_components/lipro/services custom_components/lipro/entities custom_components/lipro/select.py custom_components/lipro/sensor.py` → `Success: no issues found in 76 source files`
- `uv run pytest -q tests/platforms/test_select.py tests/platforms/test_sensor.py tests/core/test_init.py tests/core/test_control_plane.py` → `202 passed`
- `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/test_coordinator_integration.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_device_refresh.py tests/core/test_device.py tests/services/test_services_diagnostics.py tests/services/test_maintenance.py tests/platforms/test_update.py tests/platforms/test_select.py tests/platforms/test_sensor.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_phase31_runtime_budget_guards.py && uv run mypy custom_components/lipro/core/coordinator custom_components/lipro/services custom_components/lipro/entities custom_components/lipro/select.py custom_components/lipro/sensor.py` → `445 passed` + `Success: no issues found in 76 source files`

## Risks / Notes

- `Phase 31` 明确只完成 continuation route touched zones 的 typed/exception closeout；它没有宣称 repo-wide zero debt。
- 后续若继续扩写 runtime/service/platform production files，必须同步更新 `tests/meta/test_phase31_runtime_budget_guards.py`、mypy proof 与 planning closeout truth。