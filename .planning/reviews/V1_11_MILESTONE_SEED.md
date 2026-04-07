# v1.11 Milestone Seed

> Snapshot: `2026-03-22`
> Identity: proposal-only / pull-only planning seed for the next formal milestone.
> Authority: this seed does **not** override `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`; it exists so the next formal `$gsd-plan-phase 58` / `$gsd-execute-phase 58` can start from audited evidence instead of conversation memory.

## 1. Arbitration Summary

`v1.10` has already completed `Phase 57` and is closeout-ready. However, the current user direction is to perform another **top-architect, no-blind-spot, full-repository review** across all Python, docs, configuration, governance, and open-source surfaces. Forcing that work back into `v1.10` would lie about the milestone scope.

The next honest move is therefore to start a **new milestone** from the refreshed audit need itself:

1. `Phase 46` delivered a strong repo-wide audit baseline, but `v1.8 -> v1.10` materially changed runtime, governance, typed surfaces, and follow-up truth;
2. the repo is now more converged, so the highest-value review work is no longer “find the second root”, but “refresh the entire verdict set with current evidence and route the next wave honestly”;
3. the user explicitly requested a renewed exhaustive review covering every Python file, docs/config surfaces, naming, directory clarity, refactor residue, and open-source maturity.

## 2. Candidate Milestone

**Name:** `v1.11 Repository Audit Refresh & Next-Wave Remediation Routing`

**Why now:** the architecture is already mostly converged, `v1.10` has closed its single scoped command-result follow-up, and the highest-value remaining work is to refresh the repository-wide audit against the **current** codebase rather than keep relying on stale March 20 snapshots.

**North-star fit:**

- does not reopen a second runtime/protocol/control story
- treats previous audit assets as evidence baselines, not eternal truth
- prioritizes current file-level evidence, explicit severity, and routed remediation over vague “looks better now” claims
- keeps execution-trace assets out of long-term truth unless explicitly promoted

## 3. Candidate Requirement Basket

These IDs are tentative until promoted into the current planning truth.

- `AUD-03` — the refreshed audit must cover all repository Python / docs / config / governance surfaces with explicit file-level verdicts or scope notes, leaving no silent blind spots.
- `ARC-10` — current formal roots, hotspots, naming, directory structure, refactor residue, and old-vs-new code boundaries must receive an updated architecture verdict based on present-day code rather than historical assumptions.
- `OSS-06` — README / docs / SECURITY / SUPPORT / CONTRIBUTING / manifest / packaging / tooling surfaces must be re-audited against current open-source best practices and the repo’s actual support/release contract.
- `GOV-42` — the refreshed audit must be promoted into current planning truth and routed into `Phase 59+` remediation seeds without silent defer, fake archive claims, or milestone-scope drift.

## 4. Proposed Phase Seed

### Phase 58 — Repository audit refresh and next-wave routing

**Why first**
- it directly answers the user’s renewed “full-spectrum / all-files / all-surfaces” audit request
- it refreshes the strongest historical audit (`Phase 46`) with the repo’s current post-`v1.8 -> v1.10` reality
- it creates a clean and honest `Phase 59+` route instead of improvising one-off refactors without a fresh master verdict

**Primary outcomes**
- produce a refreshed architecture/code audit with file-level evidence and severity
- produce a refreshed governance/open-source audit covering docs, config, contributor/support/security/release surfaces
- produce a new remediation roadmap from the current repo state, not from stale historical assumptions
- freeze the new truth in roadmap / requirements / project / state and promoted phase evidence

**Core files / areas**
- `custom_components/lipro/**/*.py`
- `tests/**/*.py`
- `scripts/**/*.py`
- `README.md`, `README_zh.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md`, `pyproject.toml`, `custom_components/lipro/manifest.json`
- `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`
- `.planning/baseline/*.md`
- `.planning/reviews/*.md`

## 5. Expected Follow-up Themes

`Phase 58` itself is an audit+route phase. The likely remediation themes after it are expected to include some combination of:

- verification/localization improvements for remaining megaguards / megasuites
- hotspot slimming in still-large but formal homes
- naming / directory / support-only seam clarity improvements
- open-source discoverability and contributor-path follow-through

## 6. Next Formal Steps

1. promote `v1.11` and `Phase 58` into `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`
2. run `$gsd-plan-phase 58 --prd .planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-PRD.md --skip-research`
3. execute `$gsd-execute-phase 58`
4. route the resulting findings into `Phase 59+` remediation truth
