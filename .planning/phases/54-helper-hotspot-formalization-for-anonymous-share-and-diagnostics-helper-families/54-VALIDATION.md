---
phase: 54
slug: helper-hotspot-formalization-for-anonymous-share-and-diagnostics-helper-families
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-21
---

# Phase 54 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + helper hotspot regressions + meta guards |
| **Config file** | `pyproject.toml` |
| **Smoke command** | `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/test_share_client.py -k "record or submit or outcome"` |
| **Quick run command** | `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/core/anonymous_share/test_observability.py tests/core/test_anonymous_share_storage.py tests/core/test_share_client.py tests/services/test_services_diagnostics.py tests/services/test_services_share.py tests/core/test_init_service_handlers_share_reports.py tests/core/api/test_api_request_policy.py` |
| **Phase gate command** | `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/core/anonymous_share/test_observability.py tests/core/test_anonymous_share_storage.py tests/core/test_share_client.py tests/services/test_services_diagnostics.py tests/services/test_services_share.py tests/core/test_init_service_handlers_share_reports.py tests/core/api/test_api_request_policy.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_phase50_rest_typed_budget_guards.py && uv run python scripts/check_file_matrix.py --check` |
| **Estimated runtime** | `~60-120s` |

## Wave Structure

- **Wave 1:** `54-01` anonymous-share manager slimming
- **Wave 2:** `54-02` share client transport/outcome split
- **Wave 3:** `54-03` diagnostics helper family topicization
- **Wave 4:** `54-04` request-policy companion closure + governance freeze

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 54-01-01 | 01 | 1 | HOT-13 | manager / storage / observability | `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/core/anonymous_share/test_observability.py tests/core/test_anonymous_share_storage.py` | ✅ passed |
| 54-02-01 | 02 | 2 | HOT-13 | share client transport / outcomes | `uv run pytest -q tests/core/test_share_client.py tests/core/anonymous_share/test_manager_submission.py -k "share or submit or outcome"` | ✅ passed |
| 54-03-01 | 03 | 3 | HOT-13 | diagnostics helper flows | `uv run pytest -q tests/services/test_services_diagnostics.py tests/services/test_services_share.py tests/core/test_init_service_handlers_share_reports.py` | ✅ passed |
| 54-04-01 | 04 | 4 | HOT-13 | request-policy closure / docs / guards | `uv run pytest -q tests/core/api/test_api_request_policy.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_phase50_rest_typed_budget_guards.py && uv run python scripts/check_file_matrix.py --check` | ✅ passed |

## Wave Commands

### Wave 1 Gate
- `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/core/anonymous_share/test_observability.py tests/core/test_anonymous_share_storage.py`

### Wave 2 Gate
- `uv run pytest -q tests/core/test_share_client.py tests/core/anonymous_share/test_manager_submission.py`

### Wave 3 Gate
- `uv run pytest -q tests/services/test_services_diagnostics.py tests/services/test_services_share.py tests/core/test_init_service_handlers_share_reports.py`

### Wave 4 Gate
- `uv run pytest -q tests/core/api/test_api_request_policy.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_phase50_rest_typed_budget_guards.py`
- `uv run python scripts/check_file_matrix.py --check`

## Manual-Only Verifications

- 确认 `AnonymousShareManager` 仍是 aggregate/scoped public story 的 formal home，而 support seam 没有变成第二 manager。
- 确认 `ShareWorkerClient` surface、worker payload contract 与 typed outcome story 没有漂移。
- 确认 `services/diagnostics/helpers.py` 继续只是 control helper；`control/service_router.py` 仍是 public handler home。
- 确认 `RequestPolicy` 仍是 `429` / busy / pacing truth；generic backoff residual 的 disposition 被显式登记和验证。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `manager -> share client -> diagnostics helper -> request-policy closure`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded.

**Approval:** execution completed and verified.
