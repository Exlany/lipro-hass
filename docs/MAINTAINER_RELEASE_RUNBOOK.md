# Maintainer Release Runbook

## Scope

This repository currently follows a single-maintainer release model. Every tagged release must reuse `.github/workflows/ci.yml`; `.github/workflows/release.yml` is only the tagged security / packaging / publishing tail of that same gate.

> Continuity note / 连续性说明：this runbook defines the maintainer-unavailable drill. Do not imply hidden backup maintainers. No documented delegate exists today; if the maintainer is unavailable, freeze new tagged releases and freeze new release promises, keep `SUPPORT.md` / `SECURITY.md` / issue / PR template routing honest, and restore custody only after CODEOWNERS + runbook record the real successor or delegate.
> Current route note / 当前路线说明：maintainer continuity now follows the stable selector family `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`; today it resolves to `v1.41 active milestone route / starting from latest archived baseline = v1.40`, current status = `active / phase 136 complete; closeout-ready (2026-04-02)`, default next command = `$gsd-complete-milestone v1.41`. Latest archived evidence remains pull-only: `.planning/reviews/V1_40_EVIDENCE_INDEX.md` + `.planning/v1.40-MILESTONE-AUDIT.md`.

## Truth Sources

- Canonical package version: `pyproject.toml`, `custom_components/lipro/manifest.json`, `custom_components/lipro/const/base.py`
- Canonical runtime dependency envelope: `pyproject.toml` (full runtime floor/bounds) + `custom_components/lipro/manifest.json` (Home Assistant-installed subset)
- Canonical minimum supported Home Assistant version: `2026.3.1` from `hacs.json` (kept in sync with the `pyproject.toml` dev pin)
- Canonical public support/security paths: `README.md`, `README_zh.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md`
- Canonical troubleshooting path: `docs/TROUBLESHOOTING.md`
- Canonical release-notes summary: `CHANGELOG.md` (maintainer-facing release posture summary, not a second runbook)
- Canonical route-selector family: `.planning/baseline/GOVERNANCE_REGISTRY.json::planning_route` → `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` (registry-owned current selector family; current resolution = `v1.41 active milestone route / starting from latest archived baseline = v1.40`; current status = `active / phase 136 complete; closeout-ready (2026-04-02)`; default next = `$gsd-complete-milestone v1.41`)
- Canonical latest archived evidence index: `.planning/reviews/V1_40_EVIDENCE_INDEX.md`
- Canonical latest archived milestone audit: `.planning/v1.40-MILESTONE-AUDIT.md` (pull-only evidence verdict, not current route truth)
- Canonical firmware certification trust-root asset: `custom_components/lipro/firmware_support_manifest.json` (historical filename retained)

Private repositories and forks skip CI HACS validation because HACS only supports public GitHub repositories; do not treat a skipped HACS job as a release blocker in that case.

## Current Release Identity & Security Posture

Currently enforced release hardening in this repository:

- pinned GitHub Actions revisions in `ci.yml` / `release.yml` / `codeql.yml`
- mandatory CI reuse before packaging
- tagged checkout via `refs/tags/${RELEASE_TAG}`
- tag/version match against `pyproject.toml`
- tagged release security gate via blocking `pip-audit` on the tagged source
- fail-closed tagged `CodeQL` gate: the tag must have a completed `CodeQL` analysis and zero open alerts before publish
- release archive checksum publication via `dist/SHA256SUMS`
- published `install.sh` release asset for verified local installs
- release artifact install smoke against a temporary Home Assistant-style target tree (`configuration.yaml` + `.storage`) using `bash dist/install.sh --archive-file dist/lipro-hass-vX.Y.Z.zip --checksum-file dist/SHA256SUMS`
- published `SBOM` asset (`dist/lipro-hass-vX.Y.Z.spdx.json`)
- GitHub artifact `attestation` / `provenance` for released assets (release identity evidence, not artifact signing)
- machine verification of that provenance evidence via `gh attestation verify`
- keyless `cosign sign-blob` signatures for published assets plus machine verification via `cosign verify-blob --bundle`
- published release identity manifest (`dist/lipro-hass-vX.Y.Z.release-identity.txt`)
- scheduled / manually-runnable compatibility preview lane in `ci.yml` that upgrades preview Home Assistant dependencies, promotes deprecation warnings (`DeprecationWarning` / `PendingDeprecationWarning`) to errors, and records advisory-only outcomes without weakening the stable release contract

Still deferred beyond this phase (must stay recorded, not implied):

- richer firmware manifest metadata beyond the current local certified-truth root

GitHub artifact attestation / provenance proves how release assets were produced and can be verified; it does **not** replace artifact signing. `cosign` signing is a second, separate proof layer.

## Preconditions

Before creating or publishing a tag:

1. Working tree is clean and all intended docs/code changes are committed.
2. Version truth is synchronized across `pyproject.toml`, `manifest.json`, and `const/base.py`.
3. Public navigation is synchronized across `README.md` / `README_zh.md` / `CONTRIBUTING.md` / `SUPPORT.md` / `SECURITY.md` / troubleshooting docs.
4. Residual/governance closeout tables, `CHANGELOG.md`, the latest archived evidence pointer, and the latest archived milestone audit are updated when the release carries architectural cleanup or release-route wording changes.
5. Release custody, custody-restoration rules, freeze conditions, and rollback posture are reviewed before the tag is pushed; do not assume a delegate exists unless `.github/CODEOWNERS` and this runbook explicitly document one.
6. The following commands pass locally whenever the change scope justifies a release:

```bash
uv run ruff check .
uv run mypy
uv run python scripts/check_architecture_policy.py --check
uv run python scripts/check_file_matrix.py --check
uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py
uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py
```

## Release Freeze / Custody Truth

- **Release custody:** release custody remains centralized in the current maintainer listed by `.github/CODEOWNERS`; no documented delegate exists today, so do not imply backup maintainer redundancy that does not yet exist.
- **Custody restoration:** only resume tagged releases after `.github/CODEOWNERS`, `SUPPORT.md`, `SECURITY.md`, and this runbook record the real successor or delegate.
- **Freeze conditions:** do not cut or republish a tag if CI reuse, the tagged release security gate, the tagged `CodeQL` gate, signature verification, release identity verification, or public support/security wording is out of sync. Compatibility preview failures are advisory signals for the next tag, not silent permission to weaken the stable contract.
- **Rollback posture:** do not use `git push --force` or `git reset --hard` as a release recovery strategy; supersede a bad tag with a follow-up release and explicit notes instead.
- **Maintainer unavailable:** if the maintainer is unavailable, freeze new tagged releases and freeze new release promises, keep security disclosure paths active, and record the continuity gap explicitly rather than silently bypassing gates; support triage may continue only as best effort.

## Break-Glass Verify-Only / Non-Publish Rehearsal

- **`break-glass verify-only`**: maintainer-only path to rerun governance, security, signing, and identity verification on a tagged tree without publishing or republishing public assets.
- **`non-publish rehearsal`**: maintainer-only dry run of the release sequence that proves CI reuse, security/code-scanning gates, artifact generation, and release-identity writing while stopping before public asset publication.
- Manual `workflow_dispatch` runs of `.github/workflows/release.yml` default to verify-only / non-publish rehearsal; leave `publish_assets=false` to validate the full path without public publication, and set it to `true` only when intentionally publishing an already-existing tag after the same gates pass.
- These modes never relax the stable install contract, support-routing truth, or release-trust gates; they only validate that the same gates would pass for a real tagged release. The separate compatibility preview lane in `ci.yml` remains `schedule` / `workflow_dispatch` only and advisory.
- If a rehearsal or verify-only run discovers a blocker, record it explicitly; do not silently downgrade to preview paths or publish partially verified assets.

## Release Path

1. Prepare the release commit and confirm changelog/release notes inputs.
2. Create the tag as `vX.Y.Z` so it matches `project.version` exactly.
3. Push the tag, or run `workflow_dispatch` with an already-existing tag (`publish_assets=false` keeps the run in verify-only / non-publish rehearsal mode; set `publish_assets=true` only when you explicitly intend to publish that existing tag).
4. Let `.github/workflows/release.yml` run:
   - `validate` reuses `.github/workflows/ci.yml`
   - `security_gate` sets up the tagged Python runtime explicitly, then reruns blocking runtime `pip-audit` on the tagged source
   - `code_scanning_gate` waits for a tagged `CodeQL` analysis and fails if open alerts remain
   - `build` checks out `refs/tags/${RELEASE_TAG}`
   - the workflow verifies the tag matches `pyproject.toml`
   - assets are built from the tagged tree, not an arbitrary branch HEAD
   - the workflow smoke-tests the published install path by running `bash dist/install.sh --archive-file dist/lipro-hass-vX.Y.Z.zip --checksum-file dist/SHA256SUMS` inside a temporary Home Assistant-style target tree (`configuration.yaml` + `.storage`)
   - the workflow generates GitHub artifact attestations, verifies them with `gh attestation verify`, signs assets with `cosign sign-blob`, verifies signatures with `cosign verify-blob --bundle`, and writes the release identity manifest
5. Verify that the workflow uploads `dist/lipro-hass-vX.Y.Z.zip`, `dist/install.sh`, `dist/SHA256SUMS`, `dist/lipro-hass-vX.Y.Z.spdx.json`, `dist/lipro-hass-vX.Y.Z.release-identity.txt`, plus their matching `.sigstore.json` bundles.

## Post-Release Checks

- Confirm the GitHub release points at the expected tag.
- Download the zip once and verify it contains only `custom_components/lipro` under the release root.
- Download `SHA256SUMS`, `install.sh`, the published `SBOM`, the release identity manifest, and the matching `.sigstore.json` bundles, then confirm the release page also exposes the GitHub artifact attestation / provenance record.
- Spot-check one asset with `cosign verify-blob --bundle ...` and confirm the certificate identity matches `.github/workflows/release.yml` for the tagged release path only, even when the workflow was manually re-run for that same tag.
- Spot-check README / README_zh / CONTRIBUTING / SUPPORT / SECURITY links on the rendered release page.
- Review the workflow summary and confirm the release artifact install smoke passed against the temporary Home Assistant-style target tree before trusting the published zip/install pair.
- If the release contains troubleshooting, public-entry, or runbook changes, ensure those docs still point at each other, at the stable current-selector family, at the latest archived evidence pointer, at the latest archived milestone audit, and at the canonical public entry points.

## Maintainer-Unavailable Drill / Continuity Drill Checklist

1. Confirm the primary custodian is still the maintainer listed in `.github/CODEOWNERS`.
2. Confirm no documented delegate has been added silently; if none exists, keep single-maintainer wording intact.
3. If the maintainer is unavailable, freeze new tagged releases and freeze new release promises, keep `SECURITY.md` private disclosure routing active, and avoid promising recovery dates in public support channels.
4. Restore release custody only after `.github/CODEOWNERS` and this runbook both document the delegate and the recovery path.
5. Confirm `.github/ISSUE_TEMPLATE/bug.yml` and `.github/pull_request_template.md` still preserve the same single-maintainer / no-hidden-delegate wording; do not imply unpublished backup maintainers or custody transfer paths there.

## Continuity / Incident Procedures

### Triage Ownership

- Repository triage, release custody, and support-routing truth remain owned by the maintainer listed in `.github/CODEOWNERS`.
- No documented delegate currently exists; do not claim custody transfer until CODEOWNERS + runbook are updated together.
- High-risk issues must be recorded explicitly in governance assets or release notes when they cannot be resolved immediately.

### Security / Emergency Access

- Security-sensitive fixes must still follow `SECURITY.md` private disclosure flow before public tagging.
- Do not invent extra credentials, emergency maintainers, or unpublished handoff promises; if recovery depends on unavailable access, freeze new tagged releases and new release promises, keep the private disclosure path plus best-effort support intake active, and document the blocker.

### Bad Tag Follow-Up

- If a bad tag is published, cut a follow-up fix release with corrected assets and notes.
- Record the incident in release notes or governance truth when it materially affects support posture.

### Support Window / EOL Posture

- The latest tagged release, a matching HACS install, and verified GitHub Release assets built from that tag are the stable support targets.
- Preview paths such as `ARCHIVE_TAG=main`, branch fallback, or mirror installs remain best effort only.

## No-Silent-Defer Rule

If a known release blocker or high-risk residual is intentionally deferred, record it explicitly in the release notes or governance ledgers with owner, delete gate, and evidence. Do not silently carry it forward.
