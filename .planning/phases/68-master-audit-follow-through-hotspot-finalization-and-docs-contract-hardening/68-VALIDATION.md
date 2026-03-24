---
phase: 68
slug: master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening
status: passed
nyquist_compliant: true
review_gate_required: true
created: 2026-03-24
validated_at: 2026-03-24
---

# Phase 68 — Validation Strategy

## Review Gate First

Phase 68 的 locked decision 已明确要求单一路由：

1. `$gsd-plan-phase 68`
2. `$gsd-review 68`
3. `$gsd-plan-phase 68 --reviews`
4. `$gsd-execute-phase 68`

执行前必须先生成 `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-REVIEWS.md`，并完成等效的 `$gsd-plan-phase 68 --reviews` 回灌。`68-REVIEWS.md` 的 accepted **consensus / HIGH severity** concerns 必须进入以下闭环；执行前还必须修正 `.planning/ROADMAP.md` 与 `.planning/STATE.md` 的 Phase 68 plan-count truth。

| Review finding family | Routed plan | Closure mode |
|---|---|---|
| hotspot split still too thick / helper leakage risk | `68-01`, `68-02`, `68-03`, `68-05` | adjust split boundaries + add/strengthen `test_phase68_hotspot_budget_guards.py` |
| docs/version/release-example drift | `68-04`, `68-05` | update public surfaces + encode drift assertions in `test_governance_release_contract.py` / `test_version_sync.py` |
| dependency or public-surface backslide | `68-03`, `68-05`, `68-06` | tighten `test_dependency_guards.py` / `test_public_surface_guards.py` and governance matrices |
| review suggestion conflicts with north-star or deferred ideas | `68-05` | record explicit rejection in validation/summary with rationale; do not silently ignore |

## Wave Structure

## Accepted Review Concerns

- `HIGH`: `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py` is the only canonical MQTT topic/payload decode authority; `custom_components/lipro/core/mqtt/topics.py` may only remain a localized helper / boundary-backed adapter.
- `HIGH`: `68-06` must explicitly own `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-VERIFICATION.md`, `.planning/reviews/PROMOTED_PHASE_ASSETS.md`, and `.planning/baseline/AUTHORITY_MATRIX.md`.
- `MEDIUM`: execute may not start while `.planning/ROADMAP.md` / `.planning/STATE.md` still report `0/0` or `0` plans for Phase 68.
- `MEDIUM`: localized residuals for this phase must be enumerated, not left as category labels.
- `LOW`: every accepted review concern must map to a guard, plan, or ledger update.

## Localized Residual Closure Ledger

| Residual family | Closure owner | Closure mode |
|---|---|---|
| MQTT authority ambiguity (`topics.py` vs `mqtt_decoder.py`) | `68-01`, `68-05`, `68-06` | keep `protocol.boundary` as sole authority, add focused guard, confirm in `AUTHORITY_MATRIX.md` |
| planning truth drift (`ROADMAP.md`, `STATE.md`) | pre-execute sync, `68-06` | correct plan counts to `6`, then keep executed truth aligned |
| duplicate troubleshooting / release navigation story | `68-04`, `68-05`, `68-06` | collapse first-hop docs path, strengthen docs/meta guards, record final public routing |
| beta-vs-stable metadata / example drift | `68-04`, `68-05`, `68-06` | align `manifest.json` / `pyproject.toml` / README / issue templates and encode regression tests |
| localized helper residue after hotspot split | `68-01`, `68-02`, `68-03`, `68-06` | keep helpers inward-only, register in file/dependency/public-surface ledgers |

- **Wave 1:** `68-01`, `68-02`, `68-03`, `68-04`
- **Wave 2:** `68-05`
- **Wave 3:** `68-06`

## Per-Plan Verification Map

| Plan | Wave | Primary scope | Automated command |
|------|------|---------------|-------------------|
| `68-01` | 1 | telemetry + MQTT hotspot split | `uv run pytest -q tests/core/telemetry/test_models.py tests/core/telemetry/test_sinks.py tests/integration/test_telemetry_exporter_integration.py && uv run pytest -q tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_mqtt_payload.py tests/integration/test_mqtt_coordinator_integration.py` |
| `68-02` | 1 | anonymous-share + OTA hotspot split | `uv run pytest -q tests/core/test_share_client.py tests/services/test_services_share.py tests/core/test_anonymous_share_storage.py tests/core/test_init_service_handlers_share_reports.py && uv run pytest -q tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_request_policy.py tests/services/test_services_diagnostics.py` |
| `68-03` | 1 | runtime infra/runtime access thinning | `uv run pytest -q tests/services/test_maintenance.py tests/core/test_init.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_unload_reload.py && uv run pytest -q tests/services/test_maintenance.py tests/meta/test_dependency_guards.py tests/core/test_diagnostics.py tests/core/test_system_health.py` |
| `68-04` | 1 | docs/metadata/current-story contract hardening | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` |
| `68-05` | 2 | focused guards + review-fed closure | `test -f .planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-REVIEWS.md && uv run pytest -q tests/meta/test_phase68_hotspot_budget_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py` |
| `68-06` | 3 | governance sync + repo-wide gate | `uv run ruff check . && uv run mypy --follow-imports=silent . && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/core/telemetry/test_models.py tests/core/telemetry/test_sinks.py tests/core/mqtt/test_message_processor.py tests/core/test_share_client.py tests/core/api/test_api_diagnostics_service.py tests/services/test_maintenance.py tests/meta/test_phase68_hotspot_budget_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py && uv run pytest -q` |

## Focused Guard Expectations

- 新增 `tests/meta/test_phase68_hotspot_budget_guards.py`，守住以下 families 的 regrowth：
  - `custom_components/lipro/core/telemetry/models.py`
  - `custom_components/lipro/core/mqtt/message_processor.py`
  - `custom_components/lipro/core/anonymous_share/share_client_flows.py`
  - `custom_components/lipro/core/api/diagnostics_api_ota.py`
  - `custom_components/lipro/runtime_infra.py`
- `tests/meta/test_governance_release_contract.py` / `tests/meta/test_version_sync.py` 必须覆盖：
  - docs first-hop 统一为 `README(.md/.zh) -> docs/README.md`
  - version signal / release-example truth 一致
  - continuity wording honest but non-fictional
- `tests/meta/test_dependency_guards.py` / `tests/meta/test_public_surface_guards.py` 必须继续阻止：
  - control/services 绕开 `runtime_access.py`
  - helper/support module 回流为 second root
  - docs/release metadata 重新开启第二条 current-story

## Full Phase Gate

```bash
uv run pytest -q tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py
uv run ruff check .
uv run mypy --follow-imports=silent .
uv run python scripts/check_architecture_policy.py --check
uv run python scripts/check_file_matrix.py --check
uv run pytest -q tests/core/telemetry/test_models.py tests/core/telemetry/test_sinks.py tests/core/mqtt/test_message_processor.py tests/core/mqtt/test_mqtt_payload.py tests/core/mqtt/test_topics.py tests/core/test_share_client.py tests/core/test_anonymous_share_storage.py tests/core/test_init_service_handlers_share_reports.py tests/services/test_services_share.py tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_request_policy.py tests/services/test_services_diagnostics.py tests/services/test_maintenance.py tests/core/test_init.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_unload_reload.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/meta/test_phase68_hotspot_budget_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py
uv run pytest -q
```

## Execution Outcome

- `68-REVIEWS.md` exists, review-fed replan closure was preserved, and accepted concerns were routed into guards, ledgers, and authority/public-surface documentation.
- `uv run pytest -q tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_phase45_hotspot_budget_guards.py` → `12 passed in 0.43s`
- `uv run ruff check .` → passed
- `uv run mypy --follow-imports=silent .` → `Success: no issues found in 605 source files`
- `uv run python scripts/check_architecture_policy.py --check` → passed
- `uv run python scripts/check_file_matrix.py --check` → `All checks passed!`
- Focused Phase 68 suite → `373 passed in 9.25s`
- Repo-wide gate `uv run pytest -q` → `2542 passed in 52.69s`

## Sign-Off Checklist

- [x] `68-REVIEWS.md` exists, review-fed replan is complete, and accepted concerns were either encoded into guards / ledgers or explicitly rejected with north-star rationale.
- [x] `.planning/ROADMAP.md` and `.planning/STATE.md` already report the true Phase 68 plan count before execute starts.
- [x] Wave 1 hotspot/docs plans completed before Wave 2 focused-guard freeze.
- [x] `68-VALIDATION.md` matches the final command bundle actually used.
- [x] Governance docs (`PROJECT / ROADMAP / REQUIREMENTS / STATE / baseline / reviews`) tell the same executed Phase 68 story.
- [x] No plan or review feedback reintroduced a second public root, compat shell, or helper-owned architecture narrative.

**Approval target:** passed — review-fed replan, execution, and repo-wide validation are complete.
