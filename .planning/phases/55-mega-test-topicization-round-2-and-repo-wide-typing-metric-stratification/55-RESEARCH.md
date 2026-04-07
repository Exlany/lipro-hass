# Phase 55 Research — Mega-test topicization + typing stratification

**Date:** 2026-03-21
**Requirement focus:** `TST-10`, `TYP-13`

## Hotspot Inventory

### 1. API mega test
- `tests/core/api/test_api_command_surface.py` ~1269 lines.
- Natural clusters already present: command payload/deviceType, error handling, success/auth code normalization, 429/backoff, extended command properties, IoT request path, biz_id/retry cap, and catch-all branch coverage.
- Best first split: the final “additional branch coverage” cluster, then regroup the rest into named concern files.

### 2. MQTT mega test
- `tests/core/mqtt/test_transport_runtime.py` ~1081 lines.
- Natural clusters: transport lifecycle/message entry, properties, subscription sync, connect+decode, connection loop.
- Good candidate for four topic files with stable shared fixtures.

### 3. Platform mega tests
- `tests/platforms/test_light.py` ~851 lines; hotspots in entity commands/properties.
- `tests/platforms/test_fan.py` ~717 lines; hotspots in entity behavior.
- `tests/platforms/test_select.py` ~696 lines; hotspots in entity behavior / setup.
- `tests/platforms/test_switch.py` ~499 lines; hotspots in feature/panel switch behavior.
- Existing classes already reveal natural topic families.

### 4. Typing metric guard
- `tests/meta/test_phase31_runtime_budget_guards.py` currently enforces touched-zone `Any` / broad-catch / `type: ignore` budgets.
- Strength: small and honest. Gap: repo-wide grep cannot distinguish production debt from test/meta literal debt.
- Recommended new buckets: `production_any`, `production_type_ignore`, `tests_any_non_meta`, `meta_guard_any_literals`, `tests_type_ignore`.

## Recommended Wave Plan

### Wave 1 — API topicization
- Split `test_api_command_surface` by command payloads, auth/response normalization, rate-limit/retry, and misc branches.
- Preserve coverage and fixture continuity.

### Wave 2 — MQTT topicization
- Split `test_transport_runtime` by lifecycle, message ingress/decode, subscription sync, connection loop.
- Prefer named files over total-line magic numbers.

### Wave 3 — Platform A
- Split `test_light.py` and `test_fan.py` by model/conversion, entity commands, setup/behavior topics.

### Wave 4 — Platform B
- Split `test_select.py` and `test_switch.py` by entity behavior / feature families.

### Wave 5 — Typing stratification + truth freeze
- Extend typing guard(s) to bucket production vs tests/meta debt.
- Keep production no-growth hard fail; keep tests/meta budgets explicit rather than ignored.
- Update file matrix / testing docs / related meta truth.

## Non-Goals
- No production architecture changes.
- No repo-wide formatting or unrelated test rewrites.
- No regression to one monolithic meta-guard.
