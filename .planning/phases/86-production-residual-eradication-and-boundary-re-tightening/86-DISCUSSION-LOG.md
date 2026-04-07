# Phase 86: Production residual eradication and boundary re-tightening - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `86-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-03-27
**Phase:** 86-production-residual-eradication-and-boundary-re-tightening
**Areas discussed:** compatibility cleanup, runtime hotspot split depth, truth-sync scope

---

## Compatibility cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Remove compat shells now | Delete `_safe_read_json()` and bool `submit_share_payload()` shim; migrate callers/tests to typed outcomes in the same phase | ✓ |
| Keep temporary bridge | Retain bool/alias bridge for one more phase to reduce immediate churn | |
| Add another adapter | Introduce a new compatibility wrapper while moving callers gradually | |

**User's choice:** Auto-selected recommended option: remove compat shells now.
**Notes:** This matches the existing `Phase 85` audit route and the user's standing preference to clean meaningful non-blocking residuals instead of carrying silent debt.

---

## Runtime hotspot split depth

| Option | Description | Selected |
|--------|-------------|----------|
| Inward split only | Keep `runtime_infra.py` as formal home, but extract concern-local collaborators/support helpers to reduce file density | ✓ |
| Leave file as-is | Only touch ledgers/tests and defer all runtime_infra cleanup | |
| Re-root runtime infra | Move ownership to a new outward module/root | |

**User's choice:** Auto-selected recommended option: inward split only.
**Notes:** This preserves single-root runtime truth while still addressing maintainability debt. It also honors the user's “don’t split for the sake of splitting” rule.

---

## Truth-sync scope

| Option | Description | Selected |
|--------|-------------|----------|
| Code + adjacent tests + ledgers | Update production targets, matching tests, and audit/review truth in one phase | ✓ |
| Code only | Change production code now and leave ledgers/docs for later cleanup | |
| Ledgers only | Route production changes forward again without code cleanup | |

**User's choice:** Auto-selected recommended option: code + adjacent tests + ledgers.
**Notes:** This prevents another round of “code fixed but governance truth stale” regressions.

---

## the agent's Discretion

- Exact support module layout for `runtime_infra.py`
- Whether share-client caller migration lands in direct callers or adjacent topicized tests first
- Any directly beneficial small cleanup that naturally falls out of residual deletion

## Deferred Ideas

- Giant assurance suite topicization stays in `Phase 87`
- Governance freeze / milestone closeout stays in `Phase 88`
