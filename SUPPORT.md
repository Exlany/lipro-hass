# Support

## Start Here

- Troubleshooting first: `docs/TROUBLESHOOTING.md`
- Usage/help routing: GitHub Discussions or Issues, depending on whether the problem is a question or a confirmed bug
- Security reports: follow `SECURITY.md` and use private disclosure first
- Maintainer-only release flow: `docs/MAINTAINER_RELEASE_RUNBOOK.md`

## Version & Validation Truth

- Minimum supported Home Assistant version: `2026.3.1` (canonical source: `pyproject.toml`).
- Private repository / fork note: CI skips HACS validation because HACS only supports public GitHub repositories.

## Maintainer Model

This repository currently follows a single-maintainer review model. Triage and release timing may therefore be asynchronous, but high-risk issues should still be recorded explicitly rather than silently deferred.

## What Helps Most

- Exact integration version, Home Assistant version, and installation method
- Clear reproduction steps and expected-vs-actual behavior
- Sanitized logs / diagnostics
- Whether the issue is cloud API drift, MQTT behavior, OTA metadata, or Home Assistant platform behavior
- Developer report / one-click feedback when the issue needs deep protocol or runtime inspection

## Routing Guide

- Usage questions or “is this expected?”: start with `docs/TROUBLESHOOTING.md`, then GitHub Discussions.
- Confirmed bugs/regressions: use the bug template and include diagnostics.
- Security-sensitive reports: use the private path in `SECURITY.md`, not a public Issue.
- Release/packaging questions for maintainers: `docs/MAINTAINER_RELEASE_RUNBOOK.md`.

## Response Expectations

Best effort support is provided for verified bugs and well-scoped regressions. Feature requests may be deferred when they conflict with the project's architecture or maintenance budget, but unresolved high-risk issues must be documented explicitly instead of being silently carried forward.
