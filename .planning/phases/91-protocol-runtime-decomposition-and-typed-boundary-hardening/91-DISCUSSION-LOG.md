# Phase 91 Discussion Log

**Date:** 2026-03-28
**Mode:** auto

## Auto-Selected Gray Areas

1. Protocol/runtime formal-home inward split boundary
2. Shared typed-contract convergence strategy
3. No-growth guard and verification floor
4. Protected thin-shell non-regrowth policy

## Auto Decisions

- [auto] formal homes remain owners; inward split only through support-only helpers or shared typed models.
- [auto] typed boundary debt is reduced by converging on existing shared contracts (`core/api/types.py`, `core/command/result_policy.py`) instead of inventing new wrapper-owned semantics.
- [auto] no-growth is enforced with focused meta guards, not just mypy optimism.
- [auto] protected thin shells remain projection-only; no orchestration / protocol internals may flow back outward.

## Deferred Ideas

- Redaction registry unification and diagnostics/share convergence → Phase 92.
- Quality freeze, docs-hygiene automation, and broader open-source continuity formalization → Phase 93.
