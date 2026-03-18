# Support

## Start Here

- Troubleshooting first: `docs/TROUBLESHOOTING.md`
- Usage/help routing: GitHub Discussions or Issues, depending on whether the problem is a question or a confirmed bug
- Security reports: follow `SECURITY.md` and use private disclosure first
- Maintainer-only release flow: `docs/MAINTAINER_RELEASE_RUNBOOK.md`

## Version & Validation Truth

- Minimum supported Home Assistant version: `2026.3.1` (canonical source: `pyproject.toml`).
- Supported stable install paths: HACS and verified GitHub Release assets (`install.sh` + release zip + `SHA256SUMS`).
- Current release identity evidence: published `SHA256SUMS`, `SBOM`, and GitHub artifact `attestation` / `provenance` (`gh attestation verify`). This is provenance evidence, not artifact signing.
- Deferred release hardening: artifact `signing` and GitHub `code scanning` are not current hard gates.
- Preview / unsupported install paths: `ARCHIVE_TAG=main`, branch fallback, or mirror-backed installs. Use them only for maintainer-led testing and reproduction.
- Private repository / fork note: CI skips HACS validation because HACS only supports public GitHub repositories.

## Supported Versions / Support Lifecycle

- Latest tagged release: supported
- Current HACS install that matches the latest tagged release: supported
- Older tagged releases: best effort only unless the issue is a still-open security or data-loss regression
- `main` / preview installer flows: best effort only, not a stable support target

## Maintainer Model / Triage Ownership

This repository currently follows a single-maintainer review model. Backup maintainer redundancy is not yet established, so triage and release timing may be asynchronous; high-risk issues must still be recorded explicitly rather than silently deferred.

- triage owner: the maintainer listed in `.github/CODEOWNERS`
- Release custody: centralized to the same single-maintainer model until a real delegate is documented
- Maintainer unavailable posture: freeze new release promises rather than implying hidden redundancy

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
