# Maintainer Release Runbook

## Scope

This repository currently follows a single-maintainer release model. Every tagged release must reuse `.github/workflows/ci.yml`; `.github/workflows/release.yml` is only the packaging and publishing tail of that same gate.

## Truth Sources

- Canonical package version: `pyproject.toml`, `custom_components/lipro/manifest.json`, `custom_components/lipro/const/base.py`
- Canonical minimum supported Home Assistant version: `2026.3.1` from `pyproject.toml`
- Canonical public support/security paths: `README.md`, `README_zh.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md`
- Canonical troubleshooting path: `docs/TROUBLESHOOTING.md`
- Canonical v1.2 closeout evidence pointer: `.planning/reviews/V1_2_EVIDENCE_INDEX.md`
- Canonical firmware certification truth root: `custom_components/lipro/firmware_support_manifest.json`

Private repositories and forks skip CI HACS validation because HACS only supports public GitHub repositories; do not treat a skipped HACS job as a release blocker in that case.

## Current Supply-Chain Posture

Currently enforced release hardening in this repository:

- pinned GitHub Actions revisions in `ci.yml` / `release.yml`
- mandatory CI reuse before packaging
- tagged checkout via `refs/tags/${RELEASE_TAG}`
- tag/version match against `pyproject.toml`
- release archive checksum publication via `dist/SHA256SUMS`

Explicitly deferred beyond this phase (must stay recorded, not implied):

- `provenance` / artifact attestations
- published `SBOM` assets
- release artifact `signing`
- making `code scanning` a hard release gate
- richer firmware manifest metadata beyond the current local certified-truth root

## Preconditions

Before creating or publishing a tag:

1. Working tree is clean and all intended docs/code changes are committed.
2. Version truth is synchronized across `pyproject.toml`, `manifest.json`, and `const/base.py`.
3. Public navigation is synchronized across `README.md` / `README_zh.md` / `CONTRIBUTING.md` / `SUPPORT.md` / `SECURITY.md` / troubleshooting docs.
4. Residual/governance closeout tables and `.planning/reviews/V1_2_EVIDENCE_INDEX.md` are updated when the release carries architectural cleanup.
5. The following commands pass locally whenever the change scope justifies a release:

```bash
uv run ruff check .
uv run mypy
uv run python scripts/check_architecture_policy.py --check
uv run python scripts/check_file_matrix.py --check
uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py
```

## Release Path

1. Prepare the release commit and confirm changelog/release notes inputs.
2. Create the tag as `vX.Y.Z` so it matches `project.version` exactly.
3. Push the tag, or run `workflow_dispatch` with an already-existing tag.
4. Let `.github/workflows/release.yml` run:
   - `validate` reuses `.github/workflows/ci.yml`
   - `build` checks out `refs/tags/${RELEASE_TAG}`
   - the workflow verifies the tag matches `pyproject.toml`
   - assets are built from the tagged tree, not an arbitrary branch HEAD
5. Verify that the workflow uploads `dist/lipro-hass-vX.Y.Z.zip` and `dist/SHA256SUMS`.

## Post-Release Checks

- Confirm the GitHub release points at the expected tag.
- Download the zip once and verify it contains only `custom_components/lipro` under the release root.
- Spot-check README / README_zh / CONTRIBUTING / SUPPORT / SECURITY links on the rendered release page.
- If the release contains troubleshooting, public-entry, or runbook changes, ensure those docs still point at each other, at `.planning/reviews/V1_2_EVIDENCE_INDEX.md`, and at the canonical public entry points.

## Incident Notes

- Do **not** use `git push --force` or `git reset --hard` as a release recovery strategy.
- If a bad tag is published, cut a follow-up fix release with corrected assets and notes.
- Security-sensitive fixes should follow `SECURITY.md` private disclosure flow before public tagging.

## No-Silent-Defer Rule

If a known release blocker or high-risk residual is intentionally deferred, record it explicitly in the release notes or governance ledgers with owner, delete gate, and evidence. Do not silently carry it forward.
