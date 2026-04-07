# Phase 58 — Architecture & Code Audit Refresh

## Audit Frame

- **Scope baseline:** `557` Python files, `24` Markdown docs, `48` config/data assets were included in the refreshed repository census.
- **Primary evidence families:** `custom_components/lipro/**`, `tests/**`, `scripts/**`, root docs/config, `.planning/**` governance truth.
- **Judgment rule:** use current code as truth; historical audits are baseline references, not override authority.

## Top Strengths

1. **Single formal mainline still holds**
   - `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` and the current implementation still agree on one protocol root, one runtime root, and thin HA adapters.
   - evidence: `custom_components/lipro/core/protocol/facade.py`, `custom_components/lipro/core/api/rest_facade.py`, `custom_components/lipro/control/service_router.py`, `custom_components/lipro/control/runtime_access.py`.

2. **Residual honesty is excellent**
   - `.planning/reviews/RESIDUAL_LEDGER.md` currently records no active residual families, and recent phases closed the two most explicit late debts (`Phase 56` backoff leak, `Phase 57` command-result string drift).
   - evidence: `.planning/reviews/RESIDUAL_LEDGER.md`, `custom_components/lipro/core/utils/backoff.py`, `custom_components/lipro/core/command/result_policy.py`, `custom_components/lipro/core/command/result.py`.

3. **Boundary and assurance discipline remain repo-level highlights**
   - protocol replay / external-boundary / authority-chain assets are unusually mature for a Home Assistant custom integration.
   - evidence: `tests/fixtures/protocol_replay/**`, `tests/fixtures/external_boundaries/**`, `.planning/baseline/AUTHORITY_MATRIX.md`, `.planning/baseline/VERIFICATION_MATRIX.md`.

4. **Typed contract convergence keeps improving**
   - recent work continued to replace weak literal / bool semantics with typed contract language, especially in runtime/command/diagnostics surfaces.
   - evidence: `custom_components/lipro/core/command/result_policy.py`, `custom_components/lipro/services/diagnostics/types.py`, `custom_components/lipro/core/telemetry/models.py`.

5. **Directory topology is mostly coherent and teachable**
   - production code, platform adapters, control plane, services, protocol/runtime families, fixtures, and governance assets all have recognizable homes.
   - evidence: `custom_components/lipro/{control,core,services,entities,const}/`, `tests/{core,services,platforms,meta,fixtures}/`, `.planning/{baseline,reviews,phases,milestones}/`.

## Highest-Risk Findings

1. **Failure localization cost is still too high in several megasuites / megaguards**
   - the biggest current maintainability drag is no longer wrong architecture, but large verification surfaces that make regressions slower to localize.
   - evidence: `tests/meta/test_public_surface_guards.py`, `tests/meta/test_governance_phase_history.py`, `tests/core/test_device_refresh.py`, `tests/core/api/test_api_device_surface.py`, `tests/core/coordinator/runtime/test_mqtt_runtime.py`.

2. **A handful of formal homes remain “correct but still thick”**
   - these modules are no longer architectural mistakes, but they still concentrate more decision density than ideal.
   - evidence: `custom_components/lipro/core/anonymous_share/manager.py`, `custom_components/lipro/core/anonymous_share/share_client.py`, `custom_components/lipro/core/api/diagnostics_api_service.py`, `custom_components/lipro/core/ota/candidate.py`, `custom_components/lipro/select.py`.

3. **Governance/tooling scale is strong but heavy**
   - the repo’s governance truth is unusually disciplined, yet `scripts/check_file_matrix.py` and several meta guards now form their own maintenance hotspot.
   - evidence: `scripts/check_file_matrix.py`, `tests/meta/test_public_surface_guards.py`, `tests/meta/test_dependency_guards.py`, `tests/meta/test_governance_followup_route.py`.

4. **Naming clarity is better than before, but support-only semantics still require attention**
   - `*_support`, `*_surface`, `*_service`, `helpers.py` / `helper_support.py` families are no longer chaotic, yet some names still encode implementation history more than current responsibility.
   - evidence: `custom_components/lipro/control/service_router_support.py`, `custom_components/lipro/control/developer_router_support.py`, `custom_components/lipro/services/diagnostics/helper_support.py`, `custom_components/lipro/core/anonymous_share/{manager_support.py,share_client_support.py}`.

5. **Historical audit guidance is now partially stale**
   - several `Phase 41` / `Phase 46` findings were valid then but have already been satisfied; future refactors must not blindly replay them.
   - evidence: `.planning/phases/41-full-spectrum-architecture-code-quality-and-open-source-audit/41-REMEDIATION-ROADMAP.md`, `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-02-ARCHITECTURE-CODE-AUDIT.md`, current line counts and current module roles.

## Hotspot Census

### Production hotspots (current)

| File | Current reading | Verdict |
|------|-----------------|---------|
| `custom_components/lipro/core/anonymous_share/manager.py` | aggregate formal home, many scope/report helpers | **Keep, split inward later** |
| `custom_components/lipro/core/anonymous_share/share_client.py` | transport/outcome/backoff worker home | **Keep, trim responsibility density later** |
| `custom_components/lipro/core/api/diagnostics_api_service.py` | many diagnostics endpoint shapes in one file | **Keep, candidate for later topicization** |
| `custom_components/lipro/core/ota/candidate.py` | certification/install arbitration remains dense | **Keep, later slimming candidate** |
| `custom_components/lipro/select.py` | platform home is functionally correct but broad | **Keep, platform-local slimming candidate** |
| `custom_components/lipro/core/command/result_policy.py` | now typed and formalized, still moderately dense | **Healthy after Phase 57; no urgent action** |

### Verification hotspots (current)

| File | Current reading | Verdict |
|------|-----------------|---------|
| `tests/meta/test_public_surface_guards.py` | wide cross-phase assertions, large failure radius | **High-priority topicization candidate** |
| `tests/meta/test_governance_phase_history.py` | history + promoted evidence + lifecycle truth packed together | **High-priority localization candidate** |
| `tests/core/test_device_refresh.py` | broad runtime/device refresh matrix | **Likely worth topicizing** |
| `tests/core/api/test_api_device_surface.py` | deep API surface coverage, broad domain span | **Selective split candidate** |
| `tests/core/coordinator/runtime/test_mqtt_runtime.py` | large but still topology-coherent | **Later split candidate** |

### Tooling hotspots (current)

| File | Current reading | Verdict |
|------|-----------------|---------|
| `scripts/check_file_matrix.py` | extremely valuable governance gate, but now large enough to deserve its own maintainability pass | **High-value tooling follow-up candidate** |
| `scripts/check_architecture_policy.py` | bounded and understandable | **Healthy** |
| `scripts/check_translations.py` | small and narrow | **Healthy** |

## Naming and Directory Verdict

### What is already strong
- top-level directory layout is now much clearer than a typical long-lived HA integration repo; control/core/services/entities/tests/planning are easy to locate.
- `const/`, `core/device/`, `core/telemetry/`, `core/command/`, `tests/fixtures/` show strong family grouping.

### What still creates cognitive drag
- `*_support` names often mean “support-only collaborator” but not always “small helper”; the suffix is accurate structurally, but semantically generic.
- `helpers.py` vs `helper_support.py` vs `services/*.py` still makes some boundaries feel historical rather than intention-revealing.
- some platform files remain thick enough that directory clarity does not fully solve reader load (`select.py`, `entities/firmware_update.py`).

### Verdict
- **Directory structure:** `8.9/10` — strong and maintainable, with only localized readability debt.
- **Naming clarity:** `8.3/10` — mostly converged, but support/helper/service vocabulary still has residual ambiguity.

## Historical Recommendation Arbitration

### Recommendations now satisfied / stale as active guidance
- `RuntimeAccess` as a giant reflective hotspot is no longer a top risk at current size; it remains important but not emergency-scale.
- `__init__.py` and `EntryLifecycleController` are still meaningful roots, yet their earlier P0/P1 “giant hotspot” framing is now too severe relative to current code size.
- `Phase 41` / `46` concerns about active residual families are largely stale; active residual ledger is now empty.
- `diagnostics_api_service.py` and `share_client.py` were valid Phase 45 hotspots and still matter, but they are now “large but legitimate” rather than “architecturally suspect”.

### Recommendations still valid
- topicize the biggest megaguards / megasuites to improve failure localization;
- keep tightening naming/directness around support-only collaborators;
- continue inward slimming of the largest formal homes without reopening second-root folklore;
- refresh route planning from present evidence instead of reusing older audit severity blindly.

## Recommended Next Themes

1. verification localization and megaguard topicization
2. large-but-correct formal-home slimming
3. naming/support-only seam clarity improvements
4. tooling governance hotspot decomposition (`check_file_matrix.py` first)

## Overall Verdict

The repo is no longer suffering from first-order architecture correctness problems. Its next-wave opportunity is **maintainability precision**: shrink the diagnostic radius of tests/guards, keep slimming large formal homes without changing their ownership, and make naming/tooling surfaces easier for future maintainers to reason about.
