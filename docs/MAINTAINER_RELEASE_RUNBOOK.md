# Maintainer Release Runbook

## Scope

This repository currently follows a single-maintainer release model. Every tagged release must reuse `.github/workflows/ci.yml`; `.github/workflows/release.yml` is only the tagged security / packaging / publishing tail of that same gate.

> Continuity note / 连续性说明：do not imply hidden backup maintainers. If the maintainer is unavailable, freeze new tagged releases and keep `SUPPORT.md` / `SECURITY.md` routing honest.

## Truth Sources

- Canonical package version: `pyproject.toml`, `custom_components/lipro/manifest.json`, `custom_components/lipro/const/base.py`
- Canonical runtime dependency envelope: `pyproject.toml` (full runtime floor/bounds) + `custom_components/lipro/manifest.json` (Home Assistant-installed subset)
- Canonical minimum supported Home Assistant version: `2026.3.1` from `pyproject.toml`
- Canonical public support/security paths: `README.md`, `README_zh.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md`
- Canonical troubleshooting path: `docs/TROUBLESHOOTING.md`
- Canonical v1.2 closeout evidence pointer: `.planning/reviews/V1_2_EVIDENCE_INDEX.md`
- Canonical firmware certification truth root: `custom_components/lipro/firmware_support_manifest.json`

Private repositories and forks skip CI HACS validation because HACS only supports public GitHub repositories; do not treat a skipped HACS job as a release blocker in that case.

## Current Release Identity & Security Posture

Currently enforced release hardening in this repository:

- pinned GitHub Actions revisions in `ci.yml` / `release.yml`
- mandatory CI reuse before packaging
- tagged checkout via `refs/tags/${RELEASE_TAG}`
- tag/version match against `pyproject.toml`
- tagged release security gate via blocking `pip-audit` on the tagged source
- release archive checksum publication via `dist/SHA256SUMS`
- published `install.sh` release asset for verified local installs
- published `SBOM` asset (`dist/lipro-hass-vX.Y.Z.spdx.json`)
- GitHub artifact `attestation` / `provenance` for released assets (release identity evidence, not artifact signing)
- machine verification of that provenance evidence via `gh attestation verify`
- published release identity manifest (`dist/lipro-hass-vX.Y.Z.release-identity.txt`)

Explicitly deferred beyond this phase (must stay recorded, not implied):

- release artifact `signing`
- making GitHub `code scanning` an additional hard release gate on top of the current tagged runtime security gate
- richer firmware manifest metadata beyond the current local certified-truth root

GitHub artifact attestation / provenance proves how release assets were produced and can be verified; it does **not** mean repository-managed artifact signing is already in place.

## Preconditions

Before creating or publishing a tag:

1. Working tree is clean and all intended docs/code changes are committed.
2. Version truth is synchronized across `pyproject.toml`, `manifest.json`, and `const/base.py`.
3. Public navigation is synchronized across `README.md` / `README_zh.md` / `CONTRIBUTING.md` / `SUPPORT.md` / `SECURITY.md` / troubleshooting docs.
4. Residual/governance closeout tables and `.planning/reviews/V1_2_EVIDENCE_INDEX.md` are updated when the release carries architectural cleanup.
5. Release custody, freeze conditions, and rollback posture are reviewed before the tag is pushed; do not assume a delegate exists when the repository is still in a single-maintainer model.
6. The following commands pass locally whenever the change scope justifies a release:

```bash
uv run ruff check .
uv run mypy
uv run python scripts/check_architecture_policy.py --check
uv run python scripts/check_file_matrix.py --check
uv run pytest -q tests/meta/test_governance*.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py
```

## Release Freeze / Custody Truth

- **Release custody:** release custody remains centralized in the current maintainer listed by `.github/CODEOWNERS`; do not imply backup maintainer redundancy that does not yet exist.
- **Freeze conditions:** do not cut or republish a tag if CI reuse, the tagged release security gate, release identity verification, or public support/security wording is out of sync.
- **Rollback posture:** do not use `git push --force` or `git reset --hard` as a release recovery strategy; supersede a bad tag with a follow-up release and explicit notes instead.
- **Maintainer unavailable:** if the maintainer is unavailable, freeze new tagged releases, keep security disclosure paths active, and record the continuity gap explicitly rather than silently bypassing gates.

## Release Path

1. Prepare the release commit and confirm changelog/release notes inputs.
2. Create the tag as `vX.Y.Z` so it matches `project.version` exactly.
3. Push the tag, or run `workflow_dispatch` with an already-existing tag.
4. Let `.github/workflows/release.yml` run:
   - `validate` reuses `.github/workflows/ci.yml`
   - `security_gate` reruns blocking runtime `pip-audit` on the tagged source
   - `build` checks out `refs/tags/${RELEASE_TAG}`
   - the workflow verifies the tag matches `pyproject.toml`
   - assets are built from the tagged tree, not an arbitrary branch HEAD
   - the workflow generates GitHub artifact attestations, verifies them with `gh attestation verify`, and writes the release identity manifest
5. Verify that the workflow uploads `dist/lipro-hass-vX.Y.Z.zip`, `dist/install.sh`, `dist/SHA256SUMS`, `dist/lipro-hass-vX.Y.Z.spdx.json`, and `dist/lipro-hass-vX.Y.Z.release-identity.txt`.

## Post-Release Checks

- Confirm the GitHub release points at the expected tag.
- Download the zip once and verify it contains only `custom_components/lipro` under the release root.
- Download `SHA256SUMS`, `install.sh`, the published `SBOM`, and the release identity manifest, then confirm the release page also exposes the GitHub artifact attestation / provenance record.
- Spot-check README / README_zh / CONTRIBUTING / SUPPORT / SECURITY links on the rendered release page.
- If the release contains troubleshooting, public-entry, or runbook changes, ensure those docs still point at each other, at `.planning/reviews/V1_2_EVIDENCE_INDEX.md`, and at the canonical public entry points.

## Continuity / Incident Procedures

### Triage Ownership

- Repository triage, release custody, and support-routing truth remain owned by the maintainer listed in `.github/CODEOWNERS`.
- High-risk issues must be recorded explicitly in governance assets or release notes when they cannot be resolved immediately.

### Security / Emergency Access

- Security-sensitive fixes must still follow `SECURITY.md` private disclosure flow before public tagging.
- Do not invent extra credentials, emergency maintainers, or unpublished handoff promises; if recovery depends on unavailable access, freeze the release and document the blocker.

### Bad Tag Follow-Up

- If a bad tag is published, cut a follow-up fix release with corrected assets and notes.
- Record the incident in release notes or governance truth when it materially affects support posture.

### Support Window / EOL Posture

- The latest tagged release and a matching HACS install are the only stable support targets.
- Preview paths such as `ARCHIVE_TAG=main`, branch fallback, or mirror installs remain best effort only.

## No-Silent-Defer Rule

If a known release blocker or high-risk residual is intentionally deferred, record it explicitly in the release notes or governance ledgers with owner, delete gate, and evidence. Do not silently carry it forward.
