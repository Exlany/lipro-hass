# Phase 16 Research

**Date:** 2026-03-15
**Status:** Ready for planning
**Source:** merged repo-wide audit, governance truth, code inspection, tests, CI, and contract review

## Scope Summary

Phase 16 is not a rescue rewrite. It is a **high-standard closeout phase** for a repository that already has a strong north-star architecture and unusually mature governance. The work is therefore constrained by one core rule:

- **Do not rebuild the architecture.**
- **Do align truth, thin the remaining hotspots, tighten contracts, and reduce residual cognitive debt.**

The phase must cover all confirmed findings from the combined audit:
- governance truth drift
- toolchain truth drift
- large hotspot files
- `Any` / reflection-heavy seams
- catch-all exception overuse on critical paths
- residual naming / compat spine / helper-envelope debt
- control/service contract inconsistency
- domain/entity/OTA boundary issues
- platform/domain test-layering problems
- contributor/open-source DX gaps

## Key Findings

### 1. The architecture is fundamentally right; the main risk is drift, not direction

The repository already has a stable single north-star mainline:
- `LiproProtocolFacade` remains the formal protocol root
- `Coordinator` remains the formal runtime root
- control, runtime, protocol, domain, and assurance planes are separated and guarded

This means Phase 16 should **not** open a new architecture story. It should target truth alignment, hotspot decomposition, and endgame residual cleanup only.

**Planning implication:** every plan must explicitly avoid second-root promotion, compat re-legitimization, or broad framework churn.

### 2. Governance truth is strong, but one active contradiction exists

The most important governance contradiction is now local and explicit:
- `AGENTS.md` still says `custom_components/lipro/services/execution.py` has a coordinator private auth seam
- `KILL_LIST.md`, `PUBLIC_SURFACES.md`, and the actual code show that seam is already closed

There is also a secondary governance ambiguity around `.planning/codebase/*`:
- the codebase map is useful
- but drift has already appeared
- and it is currently easy to treat it as authoritative when it is not always up to date

**Planning implication:** plan 1 must align active truth before deeper refactors start.

### 3. Toolchain truth has minor but real semantic drift

The repository runs on Python 3.14 semantics, but the lint/type/dev surfaces still express slightly different truths:
- `pyproject.toml` requires Python `>=3.14.2`
- mypy targets `3.14`
- Ruff targets `py313`
- pre-commit defaults to `python3.13`
- devcontainer uses `3.14`

The current state is not broken, but it is a classic “high-maturity repo” smell: the tooling is green while the mental model is not fully aligned.

`pytest` marker registry also needs a firm decision: implement real slicing or remove dead declarations.

**Planning implication:** toolchain truth belongs in the earliest wave because it affects the meaning of later changes and future CI signals.

### 4. Several core files are now local monoliths

The most obvious hotspots are:
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/control/service_router.py`
- `custom_components/lipro/config_flow.py`
- `custom_components/lipro/entities/firmware_update.py`

These files are not “bad” in the sense of broken design; they are “too much truth in one place.” They still bundle behavior that would be easier to maintain if split into explicit collaborators:
- strategy
- exception translation
- payload/shape normalization
- orchestration glue
- public orchestration vs private helper behavior

**Planning implication:** hotspot work should be split into at least three groups: control/service, protocol/runtime, and domain/entity/OTA.

### 5. Type success is ahead of semantic typing maturity

`uv run mypy` is green, but several areas still rely on:
- `Any`
- `cast`
- `getattr`
- `callable` checks
- private-member delegation as pseudo-contracts

This is concentrated in:
- `core/api`
- `core/protocol`
- `control`
- support/diagnostics neighbors

The most important phase-16 typing target is not “remove all Any” but:
- tighten live seams that still hide contract drift
- convert reflection-based contracts into explicit `Protocol` / typed alias / `TypedDict`

**Planning implication:** typing work should be coupled to hotspot decomposition, not treated as a standalone beautification pass.

### 6. Exception semantics remain too broad on important paths

There are still too many `except Exception` blocks in:
- protocol façade helpers
- coordinator runtime flows
- diagnostics/support helpers
- config flow
- MQTT/runtime-adjacent helpers

Some of these are legitimate circuit-breaker points, but many do not yet clearly encode:
- retry intent
- swallow vs rethrow intent
- auth vs transport vs vendor error classification
- structured logging rationale

**Planning implication:** exception tightening should be coupled with hotspot extraction so that error-mapping becomes a dedicated collaborator concern instead of scattered glue.

### 7. Residual debt is now mostly cognitive debt

The most important remaining residuals are:
- `_ClientBase`
- `_ClientPacingMixin`
- `_ClientAuthRecoveryMixin`
- `_ClientTransportMixin`
- endpoint mixin family and exports
- `LiproMqttClient` legacy naming
- `get_auth_data()` compat fallback
- power helper compat envelope

The repository has already prevented these from reclaiming formal-root status, but they still create misleading affordances for future maintainers.

**Planning implication:** residual cleanup should focus on locality, naming honesty, export narrowing, and delete-gate clarity — not broad rename theater.

### 8. Control/service formal contracts are close, but not yet uniform

The most important control/service findings are:
- `send_command` still does not cleanly use the same auth/error execution chain as the better-hardened service paths
- share/developer-report payload shapes need more stable formal contracts
- dynamic import / reflection-based runtime-access behavior still exists in places where explicit contracts would be clearer
- `config_flow.py` repeats auth/login orchestration patterns that should converge on reusable helpers

**Planning implication:** control/service work should be one cohesive plan group, not scattered as “minor cleanups.”

### 9. Domain/entity/OTA still have residual boundary blur

The most important domain/entity findings are:
- `LiproDevice` still exposes too much duplicated public surface
- `CapabilitySnapshot` still supports two cognitive consumption modes (`platforms` and `is_xxx`)
- `entities/base.py` carries a dead seam and caches `device_info` too eagerly
- `firmware_update.py` still carries domain/service policy weight that should be further isolated
- OTA refresh still repeats local manifest loading in an async hot path

**Planning implication:** the domain/entity/OTA cluster deserves its own plan group, separate from protocol/runtime hotspot work.

### 10. Test layering and contributor DX are the final maintenance multipliers

The last set of issues are not architecture failures, but they directly affect long-term maintainability:
- some platform tests are still more “device facade behavior tests” than real adapter tests
- OTA policy assertions are still too close to platform homes in some cases
- contributor onboarding still leans on high-context governance assets
- troubleshooting and release-runbook guidance deserve clearer homes
- `scripts/develop` is too destructive for a multi-integration local setup

**Planning implication:** test-layer correction and DX/open-source follow-through should be a dedicated final wave, because they stabilize the repo after core truth and hotspot work settle.

## Validation Architecture

Phase 16 already has strong existing infrastructure. No new framework adoption is needed.

### Existing validation assets to reuse

- Governance/meta guards:
  - `tests/meta/test_governance_guards.py`
  - `tests/meta/test_public_surface_guards.py`
  - `tests/meta/test_dependency_guards.py`
  - `tests/meta/test_version_sync.py`
- Focused control/support/core suites:
  - `tests/services/*`
  - `tests/core/test_developer_report.py`
  - `tests/core/test_init.py`
  - `tests/core/test_control_plane.py`
  - `tests/core/test_system_health.py`
- Domain/entity/platform suites:
  - `tests/core/device/*`
  - `tests/platforms/*`
  - `tests/entities/*`
  - `tests/core/ota/*`
- Global quality gates:
  - `uv run ruff check .`
  - `uv run mypy`
  - `uv run python scripts/check_architecture_policy.py --check`
  - `uv run python scripts/check_file_matrix.py --check`

### Validation design principles

1. **Plan-local verification first** — each plan must have a small, relevant command set.
2. **Wave-end governance gate** — every wave re-runs lint + typing + architecture/governance checks.
3. **High-risk seams get focused suites** — control/service, protocol/runtime, domain/entity/OTA each need their own verify path.
4. **No fake gates** — benchmark/advisory tooling may be documented, but not presented as hard gates unless truly enforced.
5. **Execution should remain under ~120 seconds for quick feedback** where possible.

### Expected validation shape

- Wave 1 should validate governance/toolchain truth without touching behavior-heavy logic.
- Wave 2 should validate control/service + protocol/runtime decomposition with focused suites and type checks.
- Wave 3 should validate domain/entity/OTA + test-layer correction + DX docs, then re-run full governance and full-suite gates.

## Recommended Plan Split

The phase should be planned as **6 plans across 3 waves**.

### Wave 1 — Truth alignment before refactor

1. **16-01: governance truth calibration and codebase-map policy arbitration**
   - Align `AGENTS.md`, active planning docs, residual truth, and codebase-map policy.
   - Decide whether `.planning/codebase/*` is authoritative, derived cache, or explicitly non-authoritative.
   - Update guards/docs accordingly.

2. **16-02: toolchain truth alignment and local DX contract cleanup**
   - Align Python/Ruff/pre-commit/devcontainer truths.
   - Resolve dead marker/tooling declarations.
   - Make `scripts/develop` safer and sync contributor-facing DX wording.

### Wave 2 — Control/protocol/runtime tightening

3. **16-03: control/service contract unification and response-shape stabilization**
   - Unify service auth/error mainline.
   - Normalize share/developer-report/runtime-access contracts.
   - Reduce dynamic import / reflection use in control-facing seams.
   - Slim `config_flow.py` auth orchestration duplication where it directly supports the same contract goals.

4. **16-04: protocol/runtime hotspot decomposition, typing narrowing, and exception semantics tightening**
   - Continue thinning `core/api/client.py`, `core/protocol/facade.py`, `core/coordinator/coordinator.py`.
   - Narrow live `Any` seams while extracting collaborators.
   - Tighten or document catch-all exception semantics.
   - Reduce residual helper spine and compat envelopes where safe.

### Wave 3 — Domain/entity/OTA stabilization and maintenance DX

5. **16-05: domain/entity/OTA surface rationalization**
   - Reduce `LiproDevice` overexposure.
   - Converge capability-consumption story.
   - Slim `firmware_update.py` further toward projection/action-bridge role.
   - Eliminate low-value dead seams in entity base/descriptors where appropriate.

6. **16-06: test-layer correction and open-source maintenance follow-through**
   - Correct platform/domain/OTA test home boundaries.
   - Add troubleshooting / contributor navigation / maintainer release runbook truth.
   - Align support/onboarding docs with the actual governance-heavy repository shape.

## Risks

### 1. Governance edits can accidentally create a second contradiction

Updating multiple active truth docs together is correct, but if done partially it can create more drift than it removes.

**Mitigation:** cluster governance truth updates into one plan with explicit file inventory and guard verification.

### 2. Hotspot decomposition can turn into refactor sprawl

These hotspots touch central orchestration paths; without sharp boundaries, work can spread across too many files.

**Mitigation:** every hotspot plan must explicitly list what stays in the root/facade and what moves out.

### 3. Typing cleanup can become cosmetic instead of structural

Replacing `Any` with random aliasing or `cast` churn would increase noise without reducing risk.

**Mitigation:** only plan typing work where it strengthens a live contract.

### 4. Residual cleanup can accidentally reopen rename campaigns

Residual endgame is semantically important, but large rename drives will burn time and destabilize tests.

**Mitigation:** keep Phase 16 focused on locality, exports, delete gates, and contract honesty; defer physical rename stories unless preconditions are met.

### 5. Domain/entity cleanup can break platform expectations

The entity/platform layer is stable but interconnected; careless cleanup can regress HA-facing behavior.

**Mitigation:** preserve adapter-facing public semantics and pair domain cleanup with focused platform regression tests.

## Verification Strategy

### Quick gate (all waves)

- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`

### Wave-focused suites

- **Wave 1:** governance/meta/version-sync focused suites
- **Wave 2:** services/core control suites + targeted protocol/runtime tests
- **Wave 3:** domain/entity/platform/OTA suites + governance recheck

### End-of-phase gate

- `uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing`
- `uv run pytest tests/snapshots/ -v`
- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`

### Manual-only checks that should be planned explicitly

- governance docs tell one coherent story when read together
- contributor guidance is actually lighter-weight and clearer than before
- troubleshooting/runbook placement is prominent enough for humans, not just grep-able for tests
- local develop flow no longer destroys unrelated integrations in `config/custom_components`

## Recommended Planning Constraints

- Do not create a new root for governance, support, runtime, or protocol.
- Do not broaden public surfaces to make refactoring easier.
- Do not merge unrelated cleanup into “while we are here” opportunism.
- Prefer delete-gated residual reduction over broad symbolic churn.
- Keep must-haves explicit and phase-goal backward verifiable.

---

*Phase: 16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame*
*Research completed: 2026-03-15*
