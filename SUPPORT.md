# Support

## Start Here

| If you need... | Go here first | Notes |
| --- | --- | --- |
| Repository / documentation map | `docs/README.md` | First hop for docs index, contributor routing, and bilingual boundary |
| Usage help / expected behavior | `docs/TROUBLESHOOTING.md`, then GitHub Discussions | Start here for setup questions and “is this expected?” checks |
| Confirmed bug / regression | GitHub Issues | Include diagnostics first; add developer report only when diagnostics are insufficient |
| Security-sensitive report | `SECURITY.md` | Use private disclosure, not a public Issue |

If you only need public user / contributor routing, the table above is the fast path. Maintainer-only release / packaging / custody work lives in `docs/MAINTAINER_RELEASE_RUNBOOK.md`; keep that appendix out of the public first hop unless you are actively maintaining releases.

## Version & Validation Truth

- Minimum supported Home Assistant version: `2026.3.1` (canonical source: `pyproject.toml`).
- Canonical runtime dependency envelope: `pyproject.toml` (full runtime floor/bounds) + `custom_components/lipro/manifest.json` (Home Assistant-installed subset).
- Supported stable install paths: HACS and verified GitHub Release assets (`install.sh` + release zip + `SHA256SUMS`).
- Current release trust stack: published `SHA256SUMS`, `SBOM`, GitHub artifact `attestation` / `provenance` (`gh attestation verify`), keyless `cosign` signature bundles (`cosign verify-blob --bundle ...`), and the blocking tagged runtime `pip-audit` gate.
- Provenance evidence is not artifact signing: GitHub artifact attestation / provenance and `cosign` signing are published and verified separately.
- Tagged release hard gates are fail-closed: the tagged runtime `pip-audit` gate, tagged `CodeQL` analysis with zero open alerts, and signature verification must all pass before assets publish.
- Preview / unsupported install paths: `ARCHIVE_TAG=main`, branch fallback, or mirror-backed installs. Use them only for maintainer-led testing and reproduction.
- Remote installer default tag: `latest` when no archive/tag is pinned; this is convenience for maintainer-led remote installs, while stable public guidance still prefers HACS or verified GitHub Release assets.
- Private repository / fork note: CI skips HACS validation because HACS only supports public GitHub repositories.
- Maintainer-only `break-glass verify-only` / `non-publish rehearsal` flows live in `docs/MAINTAINER_RELEASE_RUNBOOK.md`; they verify release gates without relaxing public support or release-trust promises.
- Compatibility preview lane: `schedule` / `workflow_dispatch`-only advisory signal for maintainers. This compatibility preview lane upgrades preview Home Assistant dependencies and promotes deprecation warnings to errors, but it does not make preview installs or `main` a stable support target.

## Supported Versions / Support Lifecycle

- Latest tagged release: supported
- Current HACS install that matches the latest tagged release: supported
- Older tagged releases: best effort only unless the issue is a still-open security or data-loss regression
- `main` / preview installer flows: best effort only, not a stable support target

## Maintainer Appendix / Triage Ownership

This repository currently follows a single-maintainer review model. No documented delegate or backup maintainer exists today in `.github/CODEOWNERS`, so triage and release timing may be asynchronous; high-risk issues must still be recorded explicitly rather than silently deferred.

- triage owner: the maintainer listed in `.github/CODEOWNERS`
- release custody: centralized to the same single-maintainer model; no documented delegate exists today
- public Issues, Discussions, diagnostics escalations, developer reports, and PR summaries increase evidence depth but do not transfer release custody or create an undocumented delegate; maintainer-only continuity actions stay in `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- maintainer unavailable posture: freeze new tagged releases and new release promises, keep the private security path active, and continue support triage only as best effort
- custody restoration: only after `.github/CODEOWNERS` and `docs/MAINTAINER_RELEASE_RUNBOOK.md` record the real successor or delegate

## What Helps Most

- Exact integration version, Home Assistant version, and installation method
- Clear reproduction steps and expected-vs-actual behavior
- Sanitized logs / diagnostics
- Whether the issue is cloud API drift, MQTT behavior, OTA metadata, or Home Assistant platform behavior
- Developer report / one-click feedback as an escalation path when diagnostics are insufficient or the issue needs deep protocol/runtime inspection
- `failure_summary` / `failure_entries` from diagnostics, system health, or developer-report exports when those fields are available

## Routing Guide

- Usage questions or “is this expected?”: start with `docs/TROUBLESHOOTING.md`, then GitHub Discussions.
- Confirmed bugs/regressions: use the bug template and include diagnostics first; add developer report / one-click feedback plus `failure_summary` / `failure_entries` when diagnostics are insufficient or those fields are available.
- Security-sensitive reports: use the private path in `SECURITY.md`, not a public Issue.
- Release/packaging questions for maintainers: `docs/MAINTAINER_RELEASE_RUNBOOK.md`.

## Response Expectations

Best effort support is provided for verified bugs and well-scoped regressions. Feature requests may be deferred when they conflict with the project's architecture or maintenance budget, but unresolved high-risk issues must be documented explicitly instead of being silently carried forward.
