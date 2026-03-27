# Support

## Start Here

| If you need... | Go here first | Notes |
| --- | --- | --- |
| Repository / documentation map | `docs/README.md` | First hop for docs index, contributor routing, and bilingual boundary |
| Usage help / expected behavior | `docs/TROUBLESHOOTING.md`, then `SUPPORT.md` | Start here for setup questions and “is this expected?” checks; GitHub Discussions only apply when your current access mode exposes them or a future public mirror preserves the same route |
| Architecture or boundary change | `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`, then `CONTRIBUTING.md` | Use this path when you need to know where protocol / runtime / control / external-boundary / governance changes belong and which evidence must be updated |
| Confirmed bug / regression | `docs/TROUBLESHOOTING.md`, then the bug template | Include diagnostics first; GitHub issue forms are access-mode dependent rather than the universal default for this private-access repo |
| Security-sensitive report | `SECURITY.md` | Use private disclosure; the GitHub security UI is also access-mode-aware rather than a guaranteed public route |

Current access-mode truth: this repository is private-access. If you only need user / contributor routing, stop at the docs files above: `docs/README.md` is the docs map, `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md` explains change boundaries, `docs/TROUBLESHOOTING.md` handles troubleshooting, and `SECURITY.md` handles private disclosure. GitHub-hosted Issues / Discussions / Security UI only apply when your current access mode exposes them or when a future public mirror preserves the same contract. `docs/MAINTAINER_RELEASE_RUNBOOK.md` stays maintainer-only for release / packaging / custody work.

## Version & Validation Truth

- Minimum supported Home Assistant version: `2026.3.1` (install metadata: `hacs.json`; kept in sync with `pyproject.toml`).
- Canonical runtime dependency envelope: `pyproject.toml` (full runtime floor/bounds) + `custom_components/lipro/manifest.json` (Home Assistant-installed subset).
- Stable install contract today: verified release assets (`install.sh` + release zip + `SHA256SUMS`) that are reachable in your current access mode. If a future public mirror later exposes a matching HACS install or verified GitHub Release assets, they must follow the same tagged-release contract.
- Current release trust stack: published `SHA256SUMS`, `SBOM`, GitHub artifact `attestation` / `provenance` (`gh attestation verify`), keyless `cosign` signature bundles (`cosign verify-blob --bundle ...`), and the blocking tagged runtime `pip-audit` gate.
- Provenance evidence is not artifact signing: GitHub artifact attestation / provenance and `cosign` signing are published and verified separately.
- Tagged release hard gates are fail-closed: the tagged runtime `pip-audit` gate, tagged `CodeQL` analysis with zero open alerts, and signature verification must all pass before assets publish.
- Preview / unsupported install paths: `ARCHIVE_TAG=main`, branch fallback, or mirror-backed installs. Use them only for maintainer-led testing and reproduction.
- Remote installer default tag: `latest` when no archive/tag is pinned; this is convenience for maintainer-led remote installs, while stable guidance still prefers verified assets you can already reach. A future public mirror may later expose the same contract as HACS or verified GitHub Release assets.
- Private repository / fork note: CI skips HACS validation because HACS only supports public GitHub repositories.
- Maintainer-only `break-glass verify-only` / `non-publish rehearsal` flows live in `docs/MAINTAINER_RELEASE_RUNBOOK.md`; they verify release gates without relaxing public support or release-trust promises.
- Change-type validation guidance lives in `CONTRIBUTING.md`: `docs-only` and `governance-only` changes can use smaller guard sets, while maintainer-only `release-only` rehearsals continue through `workflow_dispatch` verify-only / non-publish runs that never publish public assets.
- Compatibility preview lane: `schedule` / `workflow_dispatch`-only advisory signal for maintainers. This compatibility preview lane upgrades preview Home Assistant dependencies and promotes deprecation warnings to errors, but it does not make preview installs or `main` a stable support target.

## Supported Versions / Support Lifecycle

- Latest tagged release installed from verified assets reachable in your current access mode: supported
- A matching HACS install on a future public mirror: supported only after that mirror actually exists
- Verified GitHub Release assets for the latest tagged release: supported when that release surface is reachable in your current access mode
- Older tagged releases: best effort only unless the issue is a still-open security or data-loss regression
- `main` / preview installer flows: best effort only, not a stable support target

## Maintainer Appendix / Triage Ownership

This repository currently follows a single-maintainer review model. No documented delegate or backup maintainer exists today in `.github/CODEOWNERS`, so triage and release timing may be asynchronous; high-risk issues must still be recorded explicitly rather than silently deferred.

### Maintainer-Unavailable Drill / 维护者不可用演练

1. When the maintainer is unavailable, freeze new tagged releases and new release promises.
2. Keep the public bug intake and the private security path visibly honest; incoming evidence does not transfer release custody or create an undocumented delegate.
3. Record the continuity gap explicitly in maintainer-facing truth instead of silently promising recovery dates.
4. Restore custody only after `.github/CODEOWNERS` and `docs/MAINTAINER_RELEASE_RUNBOOK.md` record the real successor or delegate.

- triage owner: the maintainer listed in `.github/CODEOWNERS`
- release custody: centralized to the same single-maintainer model; no documented delegate exists today
- issue/discussion traffic that is actually reachable in the current access mode, diagnostics escalations, developer reports, and PR summaries increase evidence depth but do not transfer release custody or create an undocumented delegate; the maintainer-unavailable drill stays in `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- maintainer unavailable posture: the maintainer-unavailable drill says to freeze new tagged releases and new release promises, keep the private security path active, and allow support triage only as best effort
- custody restoration: only after `.github/CODEOWNERS` and `docs/MAINTAINER_RELEASE_RUNBOOK.md` record the real successor or delegate

## What Helps Most

- Exact integration version, Home Assistant version, and installation method
- Clear reproduction steps and expected-vs-actual behavior
- Sanitized logs / diagnostics
- Whether the issue is cloud API drift, MQTT behavior, OTA metadata, or Home Assistant platform behavior
- Developer report / one-click feedback as an escalation path when diagnostics are insufficient or the issue needs deep protocol/runtime inspection
- `failure_summary` / `failure_entries` from diagnostics, system health, or developer-report exports when those fields are available

## Routing Guide

- Usage questions or “is this expected?”: start with `docs/TROUBLESHOOTING.md`, then `SUPPORT.md`; use GitHub Discussions only when that route is visible in your current access mode or a future public mirror preserves it.
- Confirmed bugs/regressions: use the bug template and include diagnostics first; GitHub issue forms apply only when they are reachable in your current access mode. Add developer report / one-click feedback plus `failure_summary` / `failure_entries` when diagnostics are insufficient or those fields are available.
- Security-sensitive reports: use the private path in `SECURITY.md`, not a public Issue.
- Maintainer-only release / packaging / custody work: `docs/MAINTAINER_RELEASE_RUNBOOK.md` (not part of the public first hop).

## Response Expectations

Best effort support is provided for verified bugs and well-scoped regressions. Feature requests may be deferred when they conflict with the project's architecture or maintenance budget, but unresolved high-risk issues must be documented explicitly instead of being silently carried forward.
