# Phase 16 Research

**Date:** 2026-03-15
**Status:** Ready for planning
**Source:** merged repo-wide audit, governance truth, code inspection, tests, CI, contract review, and second-pass hotspot metrics

## Scope Summary

Phase 16 is not a rescue rewrite. It is a **high-standard closeout phase** for a repository that already has a strong north-star architecture and unusually mature governance. The work is therefore constrained by one core rule:

- **Do not rebuild the architecture.**
- **Do align truth, thin the remaining hotspots, tighten contracts, and reduce residual cognitive debt.**
- **Do not let secondary glue hotspots or silent defers escape the inventory.**

The phase must cover all confirmed findings from the combined audit and the second-pass metrics sweep:
- governance truth drift
- toolchain truth drift
- large hotspot files
- `Any` / `type: ignore` / reflection-heavy seams
- catch-all exception overuse on critical paths
- residual naming / compat spine / helper-envelope debt
- control/service/diagnostics/entry-lifecycle contract inconsistency
- protocol/runtime secondary glue hotspots that still sit behind the main roots
- domain/entity/OTA boundary issues
- platform/domain test-layering problems
- contributor/open-source DX gaps
- closeout discipline: no unowned high-risk carry-forward

## Key Findings

### 1. The architecture is fundamentally right; the main risk is drift, not direction

The repository already has a stable single north-star mainline:
- `LiproProtocolFacade` remains the formal protocol root
- `Coordinator` remains the formal runtime root
- control, runtime, protocol, domain, and assurance planes are separated and guarded

This means Phase 16 should optimize **truthfulness, locality, and maintainability**, not reopen architectural direction debates.

### 2. Governance truth is strong, but drift still reappears at the edges

The repository has unusually mature governance assets, but any mismatch among `AGENTS.md`, active planning docs, baseline/review truth, and `.planning/codebase/*` can still mislead maintainers.

The right Phase 16 posture is:
- keep one authority chain
- treat `.planning/codebase/*` as derived/collaboration truth with explicit limits
- forbid already-closed seams from being rewritten as active residuals

### 3. Toolchain truth still needs one executable story

The repo already runs green with `uv run`, `ruff`, `mypy`, and strong governance scripts, but the audit confirmed that marker declarations and runtime/lint target truths can drift in ways that are easy to miss and hard to explain.

Phase 16 therefore must make toolchain truth:
- single-source
- contributor-readable
- locally reproducible
- guarded, not merely documented

### 4. The primary hotspots are obvious, but not sufficient by themselves

The expected primary hotspots remain:
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/control/service_router.py`
- `custom_components/lipro/config_flow.py`
- `custom_components/lipro/entities/firmware_update.py`

These still deserve first-class attention, but a second-pass audit showed that stopping here would leave too much glue debt behind.

### 5. Second-pass metrics reveal uncovered secondary hotspots that should not escape Phase 16 inventory

Second-pass repo metrics over tracked production Python surfaced the following signals:
- tracked production Python files: `245`
- `Any` references: `1001`
- `except Exception`: `42`
- `type: ignore`: `6`
- `getattr(...)`: `66`
- `import_module(...)`: `5`

After comparing the current Phase 16 plan inventory against those metrics, the following secondary hotspots stood out as high-value additions:
- control glue: `control/entry_lifecycle_controller.py`, `control/diagnostics_surface.py`, `control/telemetry_surface.py`
- developer/share glue: `core/utils/developer_report.py`, `core/anonymous_share/manager.py`, `services/share.py`
- runtime/MQTT glue: `core/coordinator/runtime/mqtt_runtime.py`, `core/mqtt/connection_manager.py`, `core/coordinator/runtime/status/executor.py`, `core/coordinator/runtime/command/sender.py`
- API/protocol glue: `core/api/request_policy.py`, `core/api/status_fallback.py`, `core/api/auth_service.py`, `core/api/mqtt_api_service.py`, `core/protocol/contracts.py`, `core/protocol/boundary/rest_decoder.py`
- command glue: `core/command/dispatch.py`

Not all of these require dramatic refactors, but they should be explicitly inventoried so that Phase 16 does not claim “closeout” while leaving obvious high-risk glue seams floating outside the plan.

### 6. Type success is ahead of semantic typing maturity

The repository already passes `mypy`, but the surviving `Any`, `type: ignore`, `cast`, `getattr`, and `import_module` counts show that “type green” and “type contract honest” are not the same thing.

Phase 16 typing work should therefore:
- focus on live seams, not broad cosmetic replacement
- reduce `Any`/reflection where it affects real orchestration or public contracts
- record before/after metrics for touched hotspots so that “improvement” is measurable

### 7. Exception semantics remain too broad on important paths

Critical protocol/runtime/control/device-update paths still contain broad catch patterns. Some may remain legitimate at circuit-breaker or shutdown boundaries, but many now deserve explicit arbitration.

Phase 16 should treat this as a contract problem, not just a lint smell:
- which errors trigger reauth?
- which errors are user-facing input failures?
- which errors are expected capability absences?
- which errors are truly unexpected and telemetry-worthy?

### 8. Residual debt is now mostly cognitive debt, but cognitive debt still matters

The repo is no longer dominated by broken architecture. The remaining residual problem is mostly that legacy names, fallback helpers, local compat envelopes, or helper spines can still imply a story that is no longer architecturally true.

That means Phase 16 should prefer:
- locality
- honesty
- explicit delete gates
- explicit residual disposition

over symbolic churn or rename campaigns.

### 9. Control/service formal contracts are close, but not yet uniform

The first-pass audit already identified `service_router.py`, `runtime_access.py`, `config_flow.py`, and diagnostics/service seams. The second pass confirms the missing pieces are mostly around:
- entry lifecycle
- diagnostics/telemetry surfaces
- developer-report/share assembly
- maintenance/device-lookup service glue

These should be folded into the same `16-03` contract-unification story rather than deferred into a future mini-phase.

### 10. Protocol/runtime secondary glue is the most likely source of a false closeout

The biggest risk of a misleading “Phase 16 complete” result is not the main roots themselves; it is the cluster of still-wide collaborators immediately behind them:
- request policy and fallback helpers
- decoder/contract modules
- MQTT runtime and connection glue
- command sender/status executor seams

If Phase 16 closes the roots but leaves those collaborators wide and undocumented, the repo will look cleaner while remaining more fragile than it appears.

### 11. Domain/entity/OTA work still matters, but it should stay domain-shaped

The domain/entity/OTA side is not the largest risk area anymore, but it still matters for correctness and maintainability:
- `LiproDevice` should not keep accumulating convenience passthroughs
- capability consumption should converge on one story
- `firmware_update.py` should keep shrinking toward projection + action bridge
- platform tests should prove adapters, not domain policy

### 12. Phase 16 needs a no-carry-forward exit bar, not just plan completeness

A purely narrative closeout would still allow “looks better” outcomes that leave unowned residual risk. The phase should therefore exit only if it can prove:
- no confirmed high-risk hotspot remains outside the plan inventory or explicit governance docs
- no silent defer remains
- touched hotspots record before/after indicators for key debt signals
- every remaining residual is clearly disposed with owner, phase, delete gate, and evidence

## Validation Architecture

### Existing validation assets to reuse

- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- governance/meta suites:
  - `tests/meta/test_dependency_guards.py`
  - `tests/meta/test_public_surface_guards.py`
  - `tests/meta/test_governance_guards.py`
  - `tests/meta/test_version_sync.py`
  - `tests/meta/test_toolchain_truth.py`
- focused suites for control/service, protocol/runtime, device/OTA, platforms, and snapshots

### Validation design principles

1. **Every wave must have a truth gate** — no wave should continue after governance/toolchain/public-surface drift.
2. **Every hotspot plan must have a contract gate** — focused suites + typing + governance checks where architecture truth changes.
3. **Every touched hotspot must have measurable improvement** — touched hotspot files should record before/after counts for `Any`, `except Exception`, `type: ignore`, and line count.
4. **Residual closeout must be itemized** — remaining items must land in a closeout table, not vague prose.
5. **No fake gates** — if a validation is manual, it should be named as manual instead of hidden behind green automation.
6. **Stop-the-line rules must be explicit** — governance/public-surface/dependency failures block the current wave; flaky tests get bounded retries only.

### Expected validation shape

- Wave 1 validates governance/toolchain truth without touching behavior-heavy logic.
- Wave 2 validates control/service + protocol/runtime decomposition with focused suites, typing, and governance fail-fast.
- Wave 3 validates domain/entity/OTA + test-layer correction + DX docs, then performs a second-pass repo audit and full closeout gate.

## Recommended Plan Split

The phase should remain **6 plans across 3 waves**, but with stronger explicit coverage.

### Wave 1 — Truth alignment before refactor

1. **16-01: governance truth calibration and codebase-map policy arbitration**
   - Align `AGENTS.md`, active planning docs, residual truth, and codebase-map policy.
   - Decide whether `.planning/codebase/*` is authoritative, derived cache, or explicitly non-authoritative.
   - Update guards/docs accordingly.

2. **16-02: toolchain truth alignment and local DX contract cleanup**
   - Align Python/Ruff/pre-commit/devcontainer truths.
   - Resolve dead marker/tooling declarations.
   - Make `scripts/develop` safer and sync contributor-facing DX wording.
   - Add a non-destructive smoke/manual gate for local-develop behavior.

### Wave 2 — Control/protocol/runtime tightening

3. **16-03: control/service contract unification and response-shape stabilization**
   - Unify service auth/error mainline.
   - Normalize share/developer-report/runtime-access contracts.
   - Pull `entry_lifecycle_controller.py`, diagnostics/telemetry surfaces, maintenance/device-lookup, and adjacent share/developer-report glue into the same typed-contract cleanup.
   - Slim `config_flow.py` auth orchestration duplication where it directly supports the same contract goals.

4. **16-04: protocol/runtime hotspot decomposition, typing narrowing, and exception semantics tightening**
   - Continue thinning `core/api/client.py`, `core/protocol/facade.py`, `core/coordinator/coordinator.py`.
   - Pull `request_policy.py`, `status_fallback.py`, `auth_service.py`, `mqtt_api_service.py`, `protocol/contracts.py`, `rest_decoder.py`, `mqtt_runtime.py`, `connection_manager.py`, and runtime send/status collaborators into the same hotspot inventory.
   - Narrow live `Any`/`type: ignore` seams while extracting collaborators.
   - Tighten or document catch-all exception semantics and synchronize governance matrices.

### Wave 3 — Domain/entity/OTA stabilization and maintenance DX

5. **16-05: domain/entity/OTA surface rationalization**
   - Reduce `LiproDevice` overexposure.
   - Converge capability-consumption story.
   - Slim `firmware_update.py` further toward projection/action-bridge role.
   - Synchronize dependency/public/file/residual matrices alongside domain cleanup.

6. **16-06: test-layer correction and open-source maintenance follow-through**
   - Correct platform/domain/OTA test home boundaries.
   - Add troubleshooting / contributor navigation / maintainer release runbook truth.
   - Align support/onboarding docs with the actual governance-heavy repository shape.
   - Execute the second-pass repo audit and close residuals through explicit disposition tables; no silent carry-forward is acceptable.

## Risks

### 1. Governance edits can accidentally create a second contradiction
Mitigation: cluster governance truth updates and verify them with scripts/meta guards.

### 2. Hotspot decomposition can turn into refactor sprawl
Mitigation: list what stays in each root/facade and what moves out.

### 3. Typing cleanup can become cosmetic instead of structural
Mitigation: require before/after metrics and contract-level justification.

### 4. Residual cleanup can accidentally reopen rename campaigns
Mitigation: keep focus on locality, exports, delete gates, and honesty; defer physical renames.

### 5. Domain/entity cleanup can break platform expectations
Mitigation: pair domain cleanup with focused platform regression tests.

### 6. Secondary hotspots can survive outside the plan inventory
Mitigation: explicitly list secondary hotspots inside `16-03` and `16-04`; do not rely on broad objective wording alone.

### 7. Teams can keep moving with broken truth gates unless stop-the-line rules are explicit
Mitigation: governance/public-surface/dependency failures block the current wave; flaky tests retry at most twice; persistent failures force rollback to the last wave-end green point.

## Verification Strategy

### Quick gate (all waves)

- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`

### Wave-focused suites

- **Wave 1:** governance/meta/version-sync/toolchain suites + `scripts/develop` smoke/manual gate
- **Wave 2:** services/core control suites + targeted protocol/runtime tests + governance fail-fast
- **Wave 3:** domain/entity/platform/OTA suites + docs/release truth checks + closeout re-audit

### Debt audit gate

- `rg -n 'except Exception|type: ignore' custom_components/lipro`
- `rg -n '@pytest\.mark\.(github|integration|slow)' tests || true`
- `rg -n '\bAny\b' custom_components/lipro/control custom_components/lipro/core/api custom_components/lipro/core/protocol custom_components/lipro/core/coordinator custom_components/lipro/entities custom_components/lipro/services`
- Compare the output against touched hotspots, residual ledger, kill list, and verification matrix.

### Stop-the-line rules

- `dependency/public-surface/governance/file-matrix` failures block the current wave immediately.
- `⚠️ flaky` tests may be retried at most **2** times.
- If a wave-end gate still fails after bounded retries/fixes, execution must roll back to the last wave-end green point instead of carrying broken truth forward.

### End-of-phase gate

- `uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing`
- `uv run pytest tests/snapshots/ -v`
- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- debt audit gate + residual closeout table review

### Manual-only checks that should be planned explicitly

- governance docs tell one coherent story when read together
- contributor guidance is actually lighter-weight and clearer than before
- `scripts/develop` is non-destructive to unrelated integrations
- no high-risk hotspot remains outside the plan inventory or explicit governance docs
- no silent defer survives phase closeout

## Recommended Planning Constraints

- Do not create a new root for governance, support, runtime, or protocol.
- Do not broaden public surfaces to make refactoring easier.
- Do not merge unrelated cleanup into “while we are here” opportunism.
- Prefer delete-gated residual reduction over broad symbolic churn.
- Keep must-haves explicit and phase-goal backward verifiable.
- Record before/after debt indicators for touched hotspots.
- Do not let any high-risk hotspot escape explicit plan ownership.
- No silent defers: every remaining item must be owned, gated, and evidenced.

---

*Phase: 16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame*
*Research completed: 2026-03-15 via repo audit + second-pass metrics review*
