# Phase 114: Open-source reachability honesty and security-surface normalization - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-31
**Phase:** 114-open-source-reachability-honesty-and-security-surface-normalization
**Areas discussed:** access-mode truth, security fallback honesty, continuity wording, privacy terminology, developer-service gating

---

## Access-mode truth

**User/maintainer direction:** public docs and metadata must not over-promise reachability; private-access truth stays explicit.
**Notes:** docs-first route remains canonical; maintainer-only routes stay separate.

## Security fallback honesty

**User/maintainer direction:** if no guaranteed non-GitHub private fallback exists, keep it as an explicit blocker instead of inventing one.
**Notes:** external/platform availability is out of repo scope.

## Privacy and diagnostics wording

**User/maintainer direction:** tighten wording around anonymous share, developer report, and password-hash storage so disclosure strength matches the real payload/credential semantics.
**Notes:** do not break existing service IDs or payload contracts unless required by truth.

## the agent's Discretion

- choose the narrowest truthful wording and guard shape
- choose whether metadata keeps current URLs or is softened to docs-first landings
- choose how to split Phase 114 plans into waves

## Deferred Ideas

- public mirror / public GitHub surface availability
- real backup maintainer / delegate appointment
- repo-external private disclosure channel
