# Phase 58 PRD — Repository Audit Refresh & Next-Wave Routing

## Objective

Perform a fresh, exhaustive, file-aware audit of the entire `lipro-hass` repository from a top-architect perspective. The phase must look at production Python, tests, scripts, docs, configuration, governance assets, and open-source project surfaces, then convert the refreshed verdict into a formal remediation route.

## Scope

### In scope
- every Python file under `custom_components/lipro/**`, `tests/**`, and `scripts/**`
- root docs and project-entry assets: `README.md`, `README_zh.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md`, `CHANGELOG.md`
- root config / packaging assets: `pyproject.toml`, `.pre-commit-config.yaml`, `.devcontainer.json`, `custom_components/lipro/manifest.json`, `custom_components/lipro/quality_scale.yaml`, translations, service yaml, blueprint yaml/json where relevant
- governance truth: `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`, `.planning/baseline/*`, `.planning/reviews/*`

### Out of scope
- starting a broad code refactor without a refreshed master verdict
- reopening already closed residual families unless current code proves the closure narrative false
- inventing upstream promises, new maintainers, or unsupported support/release claims

## Deliverables

1. A refreshed architecture/code audit with strengths, risks, naming verdicts, directory verdicts, old/new code residue findings, hotspot census, and severity-ranked issues
2. A refreshed governance/open-source audit covering docs, contribution/support/security/release posture, packaging/tooling clarity, and discoverability
3. A refreshed remediation roadmap that turns the audit into `Phase 59+` follow-up seeds
4. Current-story truth updates proving `v1.11 / Phase 58` exists as the new audit-routing milestone
5. Phase closeout evidence (`58-SUMMARY.md`, `58-VERIFICATION.md`)

## Locked Decisions

- Use current repository files as truth; do not rely on stale conversation memory
- Judge against international open-source best practices, Home Assistant integration norms, and the repo’s declared north-star architecture
- Prefer evidence tables, scored verdicts, and explicit route recommendations over narrative-only prose
- Keep the outcome honest: if an area is “good but still large”, say so instead of forcing a fake residual or fake perfection claim

## Acceptance Criteria

- the phase produces a fresh audit package with no silent blind spots
- the phase clearly distinguishes strengths, closed debts, active risks, and later-route opportunities
- the next-wave route is explicit enough that `Phase 59+` can be planned without rereading the whole repository from scratch
- current-story docs and promoted evidence point to the new audit phase honestly

## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/phases/41-full-spectrum-architecture-code-quality-and-open-source-audit/41-REMEDIATION-ROADMAP.md`
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-02-ARCHITECTURE-CODE-AUDIT.md`
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-SUMMARY.md`
- `.planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-SUMMARY.md`
- `.planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-SUMMARY.md`
