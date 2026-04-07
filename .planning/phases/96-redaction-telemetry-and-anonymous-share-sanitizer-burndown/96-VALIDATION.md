---
phase: 96
slug: redaction-telemetry-and-anonymous-share-sanitizer-burndown
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-28
---

# Phase 96 Validation Contract

## Wave Order

1. `96-01` diagnostics redaction helper split and thin adapter preservation
2. `96-02` telemetry exporter sanitize helper split and long-string proof
3. `96-03` anonymous-share manager/support/sanitize inward split and route handoff

## Focused Gates

- `96-01`
  - `uv run pytest -q tests/core/test_diagnostics_redaction.py tests/core/test_diagnostics.py tests/core/test_diagnostics_config_entry.py tests/core/test_diagnostics_device.py` → `passed`
  - `uv run ruff check custom_components/lipro/control/redaction.py custom_components/lipro/diagnostics.py tests/core/test_diagnostics_redaction.py tests/core/test_diagnostics.py tests/core/test_diagnostics_config_entry.py tests/core/test_diagnostics_device.py` → `passed`
- `96-02`
  - `uv run pytest -q tests/integration/test_telemetry_exporter_integration.py` → `passed`
  - `uv run ruff check custom_components/lipro/core/telemetry/exporter.py custom_components/lipro/core/telemetry/json_payloads.py tests/integration/test_telemetry_exporter_integration.py` → `passed`
- `96-03`
  - `uv run pytest -q tests/core/test_anonymous_share_cov_missing.py tests/core/anonymous_share/test_observability.py tests/core/anonymous_share/test_sanitize.py tests/core/anonymous_share/test_manager_submission.py` → `passed`
  - `uv run ruff check custom_components/lipro/core/anonymous_share/manager.py custom_components/lipro/core/anonymous_share/manager_support.py custom_components/lipro/core/anonymous_share/manager_submission.py custom_components/lipro/core/anonymous_share/sanitize.py tests/core/test_anonymous_share_cov_missing.py tests/core/anonymous_share/test_observability.py tests/core/anonymous_share/test_sanitize.py tests/core/anonymous_share/test_manager_submission.py` → `passed`
  - `uv run mypy custom_components/lipro/core/anonymous_share/manager.py custom_components/lipro/core/anonymous_share/manager_support.py custom_components/lipro/core/anonymous_share/manager_submission.py custom_components/lipro/core/anonymous_share/sanitize.py` → `passed`
  - `uv run pytest -q tests/meta/test_phase96_sanitizer_burndown_guards.py` → `passed`
  - `uv run python scripts/check_file_matrix.py --check` → `passed`
  - `uv run ruff check .` → `passed`
  - `uv run mypy` → `passed`

## GSD Route Evidence

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → `milestone = v1.26`, `current_phase = 97`, `status = active`, `completed_phases = 3`, `completed_plans = 9`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → `Phase 96 summary_count = 3`, `Phase 97 = planning-ready target`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 96` → `incomplete = []`

## Sign-off Checklist

- [x] diagnostics / telemetry / anonymous-share sanitizer hotspots 不再把 recursion / container-string / scope aggregation 挤在同一 outward shell
- [x] shared redaction truth 继续由 shared classifier 单点定义，未知 secret-like key 仍 fail-closed
- [x] focused guard、file/dependency truth 与 planning route 共同承认 `Phase 96` closeout
- [x] next step 已降到 `$gsd-plan-phase 97`
