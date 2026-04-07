# v1.9 Milestone Seed

> Snapshot: `2026-03-22`
> Identity: proposal-only / pull-only planning seed for the next formal milestone.
> Authority: this seed does **not** override `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`; it exists so the next `$gsd-new-milestone` / `$gsd-plan-phase 56` can start from audited evidence instead of conversation memory.

## 1. Arbitration Summary

`v1.8` has already completed `Phase 51 -> 55`. The next correct move is **not** to reopen `v1.8`, but to formalize the only explicit `Phase 56+` residual still recorded in the governance truth: the generic exponential-backoff helper leak that still makes `request_policy.py` act like a cross-plane utility root.

The repo already closed the larger request-policy ownership story in `Phase 52` and companion-helper formalization in `Phase 54`; what remains is narrower and more honest:

1. move the generic exponential backoff primitive to a neutral shared home;
2. stop non-API consumers from importing that primitive from `request_policy.py`;
3. freeze the new truth in baselines, review ledgers, and focused tests.

## 2. Candidate Milestone

**Name:** `v1.9 Shared Backoff Neutralization & Cross-Plane Retry Hygiene`

**Why now:** the architecture is already correct, and the highest-value remaining carry-forward is no longer a broad hotspot sweep but a small truth-hygiene fix: `RequestPolicy` should own API-specific pacing / busy / `429` decisions, not generic exponential backoff reuse for command/runtime/MQTT callers.

**North-star fit:**

- does not reopen a second protocol/runtime root or public surface
- keeps plane-specific retry semantics local while allowing a single neutral primitive
- treats residual closure as governance truth, not conversation-only cleanup
- preserves `RequestPolicy` as a formal API-policy home instead of a generic utility root

## 3. Candidate Requirement Basket

These IDs are tentative until promoted into the current planning truth.

- `RES-13` — the generic exponential backoff primitive must move to a neutral shared helper home; `request_policy.py` must stop acting as the cross-plane utility export for command/runtime/MQTT callers.
- `ARC-09` — command-result polling, runtime command verification, and MQTT setup backoff may share a neutral primitive, but must retain plane-local semantics and ownership boundaries.
- `GOV-40` — baseline/review docs, file inventory, promoted evidence, and meta guards must explicitly record the new neutral backoff home and the closure of the `Generic backoff helper leak` residual family.

## 4. Proposed Phase Seed

### Phase 56 — Shared backoff neutralization and cross-plane retry hygiene

**Why first**
- it is the only active residual family explicitly routed to `Phase 56+`
- it is small enough to finish cleanly in one phase without opening a new architecture story
- it unblocks future follow-ups such as typed command-result endgame or retry-budget stratification

**Primary outcomes**
- add a neutral shared backoff helper home under `core/utils/`
- rewire command/runtime/MQTT consumers to that neutral home
- keep `RequestPolicy` focused on API-specific policy truth only
- close the residual in governance truth and freeze it with focused regression guards

**Core files**
- `custom_components/lipro/core/utils/backoff.py`
- `custom_components/lipro/core/api/request_policy.py`
- `custom_components/lipro/core/api/request_policy_support.py`
- `custom_components/lipro/core/command/result_policy.py`
- `custom_components/lipro/core/coordinator/runtime/command/retry.py`
- `custom_components/lipro/core/mqtt/setup_backoff.py`
- `tests/core/api/test_api_request_policy.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`

## 5. Deferred Follow-ups

These remain worthwhile, but they do **not** outrank Phase 56:

- command-result typed outcome / reason-code endgame
- retry-budget stratification across command/runtime/MQTT
- any later production `Any` hotspot burn-down that is not already explicitly active in the residual ledger

## 6. Next Formal Steps

1. promote `v1.9` and `Phase 56` into `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`
2. run `$gsd-plan-phase 56 --skip-research`
3. execute `$gsd-execute-phase 56`
4. update review/baseline truth so the residual is closed in machine-checkable form
