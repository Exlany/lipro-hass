# Phase 114 Research

## Objective
Close `OSS-14` and `SEC-09` by making the repository's public/docs/metadata/security surfaces honest about what is truly reachable, what is access-gated, and what remains an external blocker.

## Key findings

### 1. Docs are mostly honest; machine-visible metadata is lagging
- `README.md`, `README_zh.md`, `SUPPORT.md`, and `SECURITY.md` already say the repository is `private-access` and treat GitHub Issues / Discussions / Releases / Security UI as conditional follow-up surfaces.
- `custom_components/lipro/manifest.json` and `pyproject.toml` still present GitHub URLs without carrying the access-mode caveat in machine-readable form. Even if the linked docs are honest, the metadata still reads like unconditional public entrypoints.
- Existing tests freeze the old expectation that metadata ends with `docs/README.md` / `SUPPORT.md` / `SECURITY.md`; Phase 114 must evolve those tests rather than silently drifting around them.

### 2. Security/privacy wording is stronger than the actual payload semantics
- Anonymous-share wording says `anonymous` / `anonymized`, but payloads still keep a stable `installation_id` and vendor diagnosis identifiers such as `iot_name`. This is better described as sanitized / pseudonymous telemetry.
- Developer-report wording says `redacted`, but the report intentionally keeps identifying diagnostics fields to help local debugging. The docs should distinguish local report semantics from upload sanitization semantics.
- README wording around remembered password hashes currently understates risk. The stored value is a credential-equivalent secret for hashed login, not merely a harmless verification digest.

### 3. Developer service discoverability is incomplete
- Docs list developer services as if they are always part of the service surface.
- `custom_components/lipro/control/service_registry.py` only registers them when a debug-mode runtime entry exists.
- Phase 114 should tighten the wording to say these are debug-mode-gated developer services.

### 4. Governance truth still has local drift
- `ROADMAP.md` and `STATE.md` contain stale progress-table rows that still imply `Phase 113` / `Phase 114` are not started even though the route contract says `Phase 113 complete / Phase 114 discussion-ready`.
- `AUTHORITY_MATRIX.md` and the current machine-readable route tests are slightly misaligned about `.planning/MILESTONES.md` participation in the live selector family.
- Phase 114 should fix obvious drift but avoid inventing a new selector family.

### 5. External blockers must remain explicit
- There is still no guaranteed non-GitHub private fallback disclosure route that works outside repository access.
- There is still no documented delegate / backup maintainer in `.github/CODEOWNERS`.
- The repository cannot solve GitHub visibility, mirror availability, or custody delegation purely with local code/doc changes.

## Recommended execution shape

### Wave 1 — wording and disclosure honesty
- Update `README.md`, `README_zh.md`, `SUPPORT.md`, `SECURITY.md`, `custom_components/lipro/services.yaml`, and `scripts/lint` so wording matches real access-mode, privacy, and debug-mode truth.
- Tighten `custom_components/lipro/flow/credentials.py` validation wording and control-character posture if it can be done without breaking login semantics.
- Keep service IDs and runtime behavior stable; this wave is about truthful semantics, not feature churn.

### Wave 2 — metadata + machine-checkable guard normalization
- Update `custom_components/lipro/manifest.json`, `pyproject.toml`, `.planning/baseline/GOVERNANCE_REGISTRY.json`, and related issue/contact routing surfaces to the chosen docs-first/access-mode-honest contract.
- Add `tests/meta/test_phase114_open_source_surface_honesty_guards.py` to freeze:
  - access-mode wording
  - security fallback blocker honesty
  - developer-service debug-mode gating language
  - privacy terminology for anonymous share / developer diagnostics
  - `scripts/lint` help-text truth
- Adjust existing governance/version-sync tests to the new machine truth.

### Wave 3 — route/verification closeout
- Repair current progress-table / route drift in planning docs as part of the phase closeout.
- Update `PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md`, `MILESTONES.md`, `tests/meta/governance_current_truth.py`, and the verification matrix to move from `Phase 114 discussion-ready` to `Phase 114 complete`.
- Write `114-VERIFICATION.md`, `114-SUMMARY.md`, and `114-AUDIT.md`.
- Because `Phase 114` is the last phase of `v1.31`, the natural next route after closeout is milestone completion.

## Repo-internal fixes vs external blockers

### Repo-internal and in-scope
- wording truth for access-mode, privacy, and developer-service gating
- metadata/docs registry alignment
- machine-checkable guard coverage for Phase 114
- progress-table and route-truth drift repair

### External blockers that must stay blockers
- public mirror / HACS / public GitHub route availability
- repo-external guaranteed private disclosure channel
- real documented delegate / backup maintainer / custody transfer

## Best-practice comparison
- Strong already: docs-first routing, explicit single-maintainer truth, structured release trust story, bilingual docs, machine-checkable governance.
- Behind elite open-source repos: repo-external disclosure fallback, maintainer redundancy, simplified contributor first-hop, non-GitHub documentation hosting, and lower governance-density for casual readers.
