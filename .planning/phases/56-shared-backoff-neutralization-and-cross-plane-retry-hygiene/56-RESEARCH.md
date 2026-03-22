# Phase 56 Research

status: passed

## Question

- generic exponential backoff primitive should live where, once `RequestPolicy` is no longer allowed to act as a cross-plane utility export?

## Findings

1. `RESIDUAL_LEDGER.md` already routes the `Generic backoff helper leak` to `Phase 56+`; this is not speculative work but a pre-registered residual closeout.
2. The current callers span three distinct planes (`command`, `runtime`, `mqtt`), so keeping the primitive under `core/api/request_policy.py` is an ownership lie even if behavior is correct.
3. The repository already has `core/utils/retry_after.py` for a neutral retry-related primitive; `core/utils/backoff.py` is therefore the narrowest, most honest home for pure exponential-delay math.
4. The right abstraction level is a pure helper function, not a shared retry policy object or backoff manager.

## Decision

- Create `custom_components/lipro/core/utils/backoff.py` as the neutral primitive home.
- Keep `RequestPolicy` focused on API-local rate-limit / busy / pacing truth.
- Use focused unit/meta guards to freeze the new import direction and residual closure.

## Non-Goals

- No unification of retry semantics across command/runtime/MQTT.
- No new public surface or package export.
- No larger typed outcome redesign for command-result flows.
