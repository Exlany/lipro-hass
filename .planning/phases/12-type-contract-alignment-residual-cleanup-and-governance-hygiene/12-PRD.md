# Phase 12 PRD: Type Contract Alignment, Residual Cleanup & Governance Hygiene

## Background

Phase 11 has already closed the repository's previously blocking test/governance desynchronization: `uv run pytest -q` passes, Phase 11 governance truth is aligned, `services/wiring.py` has been deleted, and the repository no longer needs to keep compatibility shells merely to satisfy stale tests.

A fresh re-review of the current baseline shows that the remaining debt is now narrower and more structural:
- the repository is not yet fully green because `uv run mypy` still fails
- several explicitly registered compat seams still remain open
- some developer/configuration artifacts have drifted behind implementation truth
- contributor-facing open-source governance still has contract gaps relative to CI

The earlier audit report also contained several findings that are now obsolete. Those fixed items must **not** be reopened as Phase 12 work.

## Re-Verified Current Truth

### Still Valid

1. `uv run mypy` is still red on the current baseline, with errors concentrated in coordinator/runtime public typing, REST facade return contracts, diagnostics surface typing, and platform setup call sites.
2. Explicit compat seams remain registered and active: `core.api.LiproClient`, `LiproProtocolFacade.get_device_list`, `LiproMqttFacade.raw_client`, `DeviceCapabilities` legacy alias, and `_ClientBase`/related compat spine remnants.
3. `custom_components/lipro/control/service_router.py` remains a control-plane hotspot (~459 LOC), while `core/coordinator/coordinator.py` (~711 LOC) and `core/api/status_service.py` (~456 LOC) are still high-temperature files.
4. Broad `except Exception` usage remains materially present in the repository and should continue to be narrowed where formal contracts now exist.
5. Documentation/configuration drift remains real: `docs/developer_architecture.md` still states outdated coordinator size; `custom_components/lipro/quality_scale.yaml` still references `tests/test_config_flow.py` and an outdated known-limitations count; `.devcontainer.json` still points to `venv/bin/python` instead of `.venv`.
6. Contributor/open-source governance gaps remain: `CONTRIBUTING.md` and `.github/pull_request_template.md` still omit the CI `security` job from the explicit contributor contract; `.github/CODEOWNERS` is still single-maintainer; no top-level `CODE_OF_CONDUCT.md` or `SUPPORT.md` exists; and no shell-script static gate (for example shellcheck) is wired into CI.

### Already Fixed / Must Not Be Replanned

1. Device refresh tests are now aligned to the canonical `get_devices(offset, limit)` path.
2. OTA certification tests are now aligned to `manifest_truth`.
3. Phase 11 governance guards no longer conflict with the audit snapshot; after `Phase 12` planning reopened the milestone, that snapshot is now intentionally recorded as `superseded_snapshot` rather than an active mismatch.
4. `services/wiring.py` has already been deleted and must not be reintroduced.
5. `_ClientEndpointsMixin` aggregate export has already been removed from the active endpoint surface and should not be treated as an active Phase 12 production residual.

## Problem Statement

The repository already has a strong architecture and governance framework, but the remaining gaps are now concentrated in four areas:
- static typing no longer fully matches the formal public surface story
- registered compat seams remain available as future misuse vectors
- a few developer/configuration artifacts still document stale truths
- contributor-facing governance is not yet fully aligned to actual CI and community expectations

This means the next phase should be a **precision cleanup phase**, not another broad architectural rewrite.

## Desired Outcome

Make the repository's static typing, residual surface inventory, developer docs/configuration, and contributor-facing governance align with the already-established north-star single mainline — while explicitly refusing to reopen already-fixed Phase 11 issues.

## Requirements

### TYP-01 Public Type Contract Convergence
- `LiproCoordinator` protocol and `Coordinator` implementation must converge on the same public contract, especially around device mutability/read-only semantics and OTA query return types.
- Platform/entity setup call sites must type-check against the formal runtime/coordinator surface without ad-hoc widening.
- `uv run mypy` must pass on the repository baseline.

### TYP-02 REST / Diagnostics Typed Return Cleanup
- `custom_components/lipro/core/api/client.py` and typed service protocols must agree on returned shapes instead of leaking `dict[str, Any]`/`object` fallbacks where canonical typed structures already exist.
- `custom_components/lipro/control/diagnostics_surface.py`, `custom_components/lipro/services/diagnostics/helpers.py`, and adjacent surfaces must narrow their runtime/container typing so mutation and lookup operations are type-safe.

### CMP-01 Residual Compat Surface Narrowing
- Continue closing or shrinking the remaining explicit compat seams: `core.api.LiproClient`, `LiproProtocolFacade.get_device_list`, `LiproMqttFacade.raw_client`, `DeviceCapabilities`, and API compat spine remnants such as `_ClientBase`.
- Do not preserve compat merely for old tests or old narrative convenience; if a compat seam remains, it must stay explicitly documented with a crisp delete gate.
- Already-closed items (`services/wiring.py`, `_ClientEndpointsMixin` aggregate export) must remain closed.



### CMP-02 Core API Skeleton Slimming
- `core/api` must move further away from the historical de-mixin skeleton by shrinking `_ClientBase` / compat spine responsibilities where the formal façade + collaborator split already exists.
- This cleanup must not restore dynamic exports, ghost child surfaces, or a second API mainline.

### HOT-01 Hotspot Decomposition & Boundary Tightening
- `core/api/client.py`, `core/coordinator/coordinator.py`, `core/api/status_service.py`, and `control/service_router.py` should be thinned only along already-formal boundaries.
- Broad `except Exception` handling should continue to be narrowed where contract/runtime boundaries are explicit and behavior can stay stable.

### GOV-09 Documentation & Configuration Truth Calibration
- Update active developer/configuration artifacts so they no longer encode stale facts about file size, test paths, interpreter path, or README limitation counts.
- Keep governance truth sourced from active docs and avoid reopening historical execution artifacts as authority.

### GOV-10 Contributor Contract & Community Hygiene
- Align contributor-facing documentation with real CI by explicitly accounting for the `security` job or documenting why it is intentionally excluded from the contributor checklist.
- Decide and document the project stance on community files (`CODE_OF_CONDUCT.md`, `SUPPORT.md`) and shell-script static checking.
- Any governance enhancement should stay lightweight and consistent with the project's current maintenance model.

## Acceptance Criteria

1. `uv run mypy` passes with no errors.
2. Remaining compat seams are either removed or further narrowed, and all still-active seams are reflected in governance truth with explicit delete gates.
3. `docs/developer_architecture.md`, `custom_components/lipro/quality_scale.yaml`, and `.devcontainer.json` reflect current repository reality.
4. Contributor-facing governance documents clearly align with CI/security expectations and record the project's decisions on community/support/shell tooling.
5. `uv run ruff check .` and `uv run pytest -q` continue to pass after the cleanup.

## Non-Goals

- Reopening already-fixed Phase 11 test migrations or governance snapshot fixes
- Reintroducing deleted compatibility shells
- Creating a second architecture story line beside the existing north-star mainline
- Broad new feature work unrelated to type/residual/governance cleanup

## Evidence From Current Re-Review

- `custom_components/lipro/runtime_types.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/control/diagnostics_surface.py`
- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/device/capabilities.py`
- `docs/developer_architecture.md`
- `custom_components/lipro/quality_scale.yaml`
- `.devcontainer.json`
- `CONTRIBUTING.md`
- `.github/pull_request_template.md`
- `.github/workflows/ci.yml`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
