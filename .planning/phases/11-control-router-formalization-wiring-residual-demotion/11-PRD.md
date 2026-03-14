# Phase 11 PRD: Control Router Formalization & Wiring Residual Demotion

## Background

Phase 10 closed protocol drift isolation and host-neutral core boundaries. The highest remaining architecture debt discovered in the 2026-03-14 repo-wide re-audit is that `custom_components/lipro/control/service_router.py` is still only a forwarding shell over `custom_components/lipro/services/wiring.py`.

This means the repository narrative says the formal control-plane home is `custom_components/lipro/control/`, but the actual HA service callback orchestration still lives in a legacy carrier. That is the clearest remaining split between governance truth and implementation truth.

## Problem Statement

Today:
- `custom_components/lipro/control/service_router.py` mainly re-exports names from `custom_components/lipro/services/wiring.py`
- `custom_components/lipro/services/wiring.py` still owns the primary orchestration for public and developer service callbacks
- tests historically depended on `services/wiring.py`, but this phase now requires test truth to migrate to the formal router rather than preserving test-driven compat
- governance/docs already identify `services/wiring.py` as a residual, but the code has not yet fully inverted the ownership

## Desired Outcome

Make `custom_components/lipro/control/service_router.py` the real implementation home for HA service routing, while keeping `custom_components/lipro/services/wiring.py` only as an explicit compat shell for any remaining legacy seams—not as a test-driven implementation carrier.

## Requirements

### CTRL-01 Formal Router Ownership
- `custom_components/lipro/control/service_router.py` must own the actual callback implementations and helper wrappers that define the control-plane service routing surface.
- `custom_components/lipro/services/wiring.py` may remain only as an explicit compatibility layer and re-export shell.
- No production registration path may require `services/wiring.py` as the source of truth.

### CTRL-02 Behavior Preservation
- Existing public and developer services must keep the same behavior, signatures, and response shapes.
- Tests must migrate to the formal router; compat must not be retained merely to satisfy old patch paths.
- No user-visible service contract regression is allowed.

### CTRL-03 Governance Synchronization
- Update roadmap/state/project/developer architecture and review ledgers to reflect the new ownership truth.
- Update file/residual documentation so `services/wiring.py` is explicitly described as compat-only.
- Add or update tests that prove registrations flow through the formal router and that repository tests no longer rely on `services/wiring.py` as patch-first truth.

## Acceptance Criteria

1. `custom_components/lipro/control/service_router.py` contains the real service-routing implementation logic rather than only alias assignments.
2. `custom_components/lipro/services/wiring.py` becomes a thin compatibility shell with no primary orchestration logic.
3. `custom_components/lipro/services/registrations.py` continues to bind to control-plane router handlers with no behavior drift.
4. Repository init/service tests validate the same behavior while targeting `control.service_router` as the formal patch seam.
5. `uv run ruff check .`, `uv run mypy`, and `uv run pytest tests -q` all pass.
6. Governance docs clearly reflect the residual demotion and delete-gate status.

## Non-Goals

- Deleting `services/wiring.py` in this phase
- Reworking protocol-plane or runtime-plane public contracts
- Redesigning service schemas or developer capability policy
- Broad service feature expansion unrelated to router ownership

## Evidence From Re-Audit

- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/CONCERNS.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `docs/developer_architecture.md`
- `custom_components/lipro/control/service_router.py`
- `custom_components/lipro/services/wiring.py`
- `custom_components/lipro/services/registrations.py`
