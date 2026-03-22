# v1.10 Milestone Seed

> Snapshot: `2026-03-22`
> Identity: proposal-only / pull-only planning seed for the next formal milestone.
> Authority: this seed does **not** override `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`; it exists so the next formal `$gsd-plan-phase 57` / `$gsd-execute-phase 57` can start from audited evidence instead of conversation memory.

## 1. Arbitration Summary

`v1.9` has already completed `Phase 56` and closed the final active residual explicitly routed to `Phase 56+`: the generic backoff helper leak. The next correct move is **not** to reopen `v1.9`, but to start a new milestone from the highest-value deferred follow-up that is already visible in the audit trail and Phase 56 closeout truth.

The narrowest, most honest next gap is no longer retry ownership but **command-result typed outcome / reason-code hardening**:

1. command-result state and failure reason strings still remain scattered across `result_policy.py`, `result.py`, runtime sender traces, and diagnostics response types;
2. Phase 50 already converged command/result ownership into `core/command`, so the repo now has a stable home to finish that contract rather than duplicating helper folklore;
3. the repo already uses canonical `reason_code` language elsewhere (`OperationOutcome`, diagnostics outcomes, anonymous-share outcomes), so command-result flows should stop being a stringly-typed outlier.

## 2. Candidate Milestone

**Name:** `v1.10 Command-Result Typed Outcome & Reason-Code Hardening`

**Why now:** the architecture is already correct, the last active residual is closed, and the highest-value remaining follow-up is to harden one still stringly-typed hotspot without reopening cross-plane retry ownership. This keeps the repo moving from “mostly converged” to “semantically explicit and easier to verify”.

**North-star fit:**

- does not reopen a second runtime/protocol root or a new public surface story
- keeps `result_policy.py` as the formal classification/polling home and `result.py` as the stable export / failure-arbitration home
- reuses the repo’s existing `reason_code` vocabulary pattern instead of inventing a second outcome language
- preserves outward behavior for runtime command delivery and diagnostics query services while making the internal contract narrower and more typed

## 3. Candidate Requirement Basket

These IDs are tentative until promoted into the current planning truth.

- `ERR-12` — command-result polling and failure arbitration must use one typed outcome / reason-code vocabulary instead of scattered raw state and failure-reason strings.
- `TYP-14` — runtime sender traces and diagnostics query response types must share the same command-result state contract without widening public behavior.
- `GOV-41` — roadmap / requirements / project / state truth, baseline notes, promoted evidence, and focused guards must explicitly record the new command-result typed-contract home.

## 4. Proposed Phase Seed

### Phase 57 — Command-result typed outcome and reason-code hardening

**Why first**
- it is the highest-value deferred follow-up explicitly named after Phase 56 closeout
- it finishes a long-running typed-failure theme without reopening retry-budget ownership
- it is small enough to execute as one focused phase with three narrow plans

**Primary outcomes**
- define a shared typed vocabulary for command-result states, verification results, and failure reasons
- remove the remaining raw-string drift across `result_policy.py`, `result.py`, runtime sender traces, and diagnostics response typing
- keep service/runtime outward semantics stable while raising type honesty and failure-contract readability
- freeze the new truth in focused tests, baselines, review docs, and promoted phase evidence

**Core files**
- `custom_components/lipro/core/command/result_policy.py`
- `custom_components/lipro/core/command/result.py`
- `custom_components/lipro/core/coordinator/runtime/command/sender.py`
- `custom_components/lipro/services/diagnostics/types.py`
- `custom_components/lipro/services/diagnostics/handlers.py`
- `tests/core/test_command_result.py`
- `tests/core/coordinator/runtime/test_command_runtime.py`
- `tests/core/test_init_service_handlers_debug_queries.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`

## 5. Deferred Follow-ups

These remain worthwhile, but they do **not** outrank Phase 57:

- retry-budget stratification across command/runtime/MQTT
- any later benchmark no-regression lane refinements unrelated to the command-result contract
- broader repo-wide `Any` contraction outside the command-result family

## 6. Next Formal Steps

1. promote `v1.10` and `Phase 57` into `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`
2. run `$gsd-plan-phase 57 --skip-research`
3. execute `$gsd-execute-phase 57`
4. update baseline / review truth so the typed command-result contract is frozen in machine-checkable form
