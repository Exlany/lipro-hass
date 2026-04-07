# Phase 41 Repo Inventory

## Scope Map

- `custom_components/lipro/**` — architecture, module boundaries, naming, residuals, hotspots
- `tests/**` — topology, boundary coverage, realism, E2E blind spots
- `scripts/**` — governance/tooling helpers, complexity hotspots, local-vs-CI parity
- `.github/**` — CI/release/security/issue-pr workflows and public collaboration contract
- `README*` / `CONTRIBUTING.md` / `SECURITY.md` / `SUPPORT.md` / `docs/**` — first-contact, support, disclosure, bilingual, maintainer burden
- `.planning/baseline/**` / `.planning/reviews/**` — governance truth and residual authority
- `.planning/phases/**` — execution trace workspace, not default long-term truth

## Identity Legend

- **Active truth**：north-star docs + current planning truth + baseline/reviews
- **Archived evidence**：milestone snapshots, milestone audits, evidence indexes
- **Execution trace**：phase plans, contexts, research, summary, verification, validation
- **Repo hygiene noise**：cache, coverage, egg-info, local virtualenv, pycache

## Baseline Metrics

- Tracked files: `1253`
- `.planning/**`: `643`
- `.planning/phases/**`: `602`
- Repo-wide Python files: `515`
- Scanned `custom_components/lipro` + `scripts`: `280` files / `42167` LOC
- Broad `except Exception` in production: `0`
- `TODO/FIXME`: `0`

## Downstream Audit Routing

- `41-02-ARCHITECTURE-CODE-AUDIT.md` consumes source topology + baseline/reviews for architecture/code verdicts
- `41-03-TOOLCHAIN-OSS-AUDIT.md` consumes tests/tooling/docs/public touchpoints for OSS/toolchain verdicts
- `41-AUDIT.md` and `41-REMEDIATION-ROADMAP.md` synthesize both shards under this shared identity legend
