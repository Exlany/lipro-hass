# Phase 92: Control/entity thin-boundary and redaction convergence - Research

**Researched:** 2026-03-28
**Confidence:** High

## Summary

- 当前仓库存在三套 redaction/detection truth：
  1. `custom_components/lipro/control/redaction.py` —— diagnostics-facing generic redaction
  2. `custom_components/lipro/core/anonymous_share/sanitize.py` —— structure-preserving share sanitizer
  3. `custom_components/lipro/core/telemetry/json_payloads.py` —— telemetry blocked-key/reference-alias policy
- 三者在 sensitive key registry、unknown secret-like key 处理、string-pattern rule、placeholder style 上存在重叠但不完全一致，已经构成 Phase 92 路标中点名的 contract drift。
- 现有 `custom_components/lipro/core/utils/redaction.py` 只有 `redact_identifier()`，但命名与位置都符合 shared cross-plane redaction truth home，最适合扩展为统一 policy root。

## Findings

### 1) Shared key registry drift
- `control/redaction.py` 同时维护 `TO_REDACT`、`OPTIONS_TO_REDACT`、`PROPERTY_KEYS_TO_REDACT`。
- `anonymous_share/sanitize.py` 维护独立的 `REDACT_KEYS` 与 `_SENSITIVE_KEY_RULES`。
- `telemetry/json_payloads.py` 又维护 `_BLOCKED_KEYS` 与 `_REFERENCE_ALIASES`。
- 这些列表都覆盖 `token/password/secret/deviceId/serial/phone/userId` 等 family，但 spelling、normalization 和扩展点不统一。

### 2) Unknown secret-like keys do not fail closed consistently
- diagnostics 主要依赖显式 key set + regex-based string cleanup；未知 `*_token` / `secretValue` / `apiSecret` 这类 key 名没有统一 fail-closed heuristics。
- anonymous share 已经有较强 string sanitizer，但 key-level detection 仍主要围绕显式名单。
- telemetry 只靠 blocked-key 集合，不具备 shared secret-like key heuristics。

### 3) Sink semantics can stay different while sharing policy truth
- diagnostics 适合继续输出 `**REDACTED**` 以兼容 HA diagnostics 习惯。
- anonymous share 现有测试明确依赖 `[TOKEN] / [IP] / [MAC] / [DEVICE_ID]` 这类 typed marker，适合保留。
- telemetry/exporter 则更适合继续采用 “drop or reference alias” 的策略。
- 因此应该统一 detection/policy truth，而不是强制所有 sinks 统一成同一 placeholder。

### 4) Test topology hotspots are already naturally splittable
- `tests/core/api/test_api_command_surface_responses.py` 已天然分成 3 个类：error handling / success codes / iot request。
- `tests/platforms/test_light_entity_behavior.py` 已天然分成 3 个类：commands / properties / additional coverage。
- `tests/services/test_services_diagnostics.py` 已天然分成 developer report、developer feedback、optional capabilities / payload builders 等主题簇。
- `tests/core/api/test_api_status_service.py` 则可按 fallback recursion / metrics-wrapper / endpoint wrapper 切成 sibling suites。

## Recommended Execution Shape

### Plan 92-01
- 扩展 `custom_components/lipro/core/utils/redaction.py`，引入 shared key normalization、explicit sensitive keys、secret-like key heuristics、reference alias map、string redaction helper。
- 让 `control/redaction.py`、`anonymous_share/sanitize.py`、`telemetry/json_payloads.py` 都从 shared policy 派生自己的 outward constants/defaults。

### Plan 92-02
- 收敛 diagnostics / exporter / developer feedback consumers 到共享 redaction truth。
- 新增 focused tests 覆盖 unknown secret-like key fail-closed、telemetry alias continuity、developer report/output shape stability。

### Plan 92-03
- 按主题切分四个 mega suites，保留 thin shell 根文件。
- 同步 `FILE_MATRIX.md`、`.planning/codebase/TESTING.md`、public-surface/testing guards 与 phase closeout docs。

## Minimum Verification

- `uv run pytest -q tests/core/test_diagnostics_redaction.py tests/core/anonymous_share/test_sanitize.py tests/core/telemetry/test_exporter.py tests/services/test_services_diagnostics.py`
- `uv run pytest -q tests/core/api/test_api_status_service.py tests/core/api/test_api_command_surface_responses.py tests/platforms/test_light_entity_behavior.py`
- `uv run pytest -q tests/meta`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check .`
- `uv run mypy`
